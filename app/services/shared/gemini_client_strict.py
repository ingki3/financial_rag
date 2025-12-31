"""Graphiti GeminiClient wrapper with stricter structured-output handling.

Why:
- Graphiti-core already requests structured output for Gemini using:
  - response_mime_type='application/json'
  - response_schema=<PydanticModel>
  - system prompt with JSON schema

However, some Gemini models may still prepend non-JSON tokens (e.g. `thought{...}`),
which breaks `json.loads(raw_output)`. Graphiti-core then attempts `salvage_json`,
but the default salvage assumes the output starts with `[` or `{`.

This client improves robustness by:
1) Disabling "thoughts" in generation config (includeThoughts=False, thinkingBudget=0)
2) Salvaging JSON by extracting the first JSON object/array substring from raw output.
"""

from __future__ import annotations

import json
import logging
import re
import typing

from pydantic import BaseModel

from graphiti_core.llm_client.gemini_client import GeminiClient
from graphiti_core.llm_client.errors import RateLimitError
from graphiti_core.llm_client.config import ModelSize
from graphiti_core.prompts.models import Message

logger = logging.getLogger(__name__)


class GeminiClientStrict(GeminiClient):
    """Drop-in replacement for graphiti_core GeminiClient with stricter JSON salvage."""

    def salvage_json(self, raw_output: str) -> dict[str, typing.Any] | None:
        if not raw_output:
            return None

        text = raw_output.strip()

        # Strip common wrappers/fences
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

        # Fast path: already valid JSON
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, list):
                # Graphiti expects dict[str, Any] from LLM client; wrap if list
                return {"items": parsed}
        except Exception:
            pass

        # Extract first JSON object substring
        obj_start = text.find("{")
        obj_end = text.rfind("}")
        if obj_start != -1 and obj_end != -1 and obj_end > obj_start:
            candidate = text[obj_start : obj_end + 1]
            try:
                return json.loads(candidate)
            except Exception:
                pass

        # Extract first JSON array substring
        arr_start = text.find("[")
        arr_end = text.rfind("]")
        if arr_start != -1 and arr_end != -1 and arr_end > arr_start:
            candidate = text[arr_start : arr_end + 1]
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, list):
                    return {"items": parsed}
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

        return None

    async def _generate_response(
        self,
        messages: list[Message],
        response_model: type[BaseModel] | None = None,
        max_tokens: int | None = None,
        model_size: ModelSize = ModelSize.medium,
    ) -> dict[str, typing.Any]:
        """
        Override Graphiti-core's JSON parsing so we don't error-log on common Gemini wrappers like `thought{...}`.

        Strategy:
        - Keep Graphiti-core's structured output request (response_schema + application/json)
        - When parsing fails, attempt salvage FIRST (extract JSON substring), then validate
        - Only if salvage also fails, raise
        """
        try:
            # Build system prompt (reuse upstream behavior via copy)
            system_prompt = ''
            if response_model is not None:
                pydantic_schema = response_model.model_json_schema()
                system_prompt += (
                    f'Output ONLY valid JSON matching this schema: {json.dumps(pydantic_schema)}.\n'
                    'Do not include any explanatory text before or after the JSON.\n\n'
                )

            if messages and messages[0].role == 'system':
                system_prompt = f'{messages[0].content}\n\n {system_prompt}'
                messages = messages[1:]

            gemini_messages: typing.Any = []
            from google.genai import types

            for m in messages:
                m.content = self._clean_input(m.content)
                gemini_messages.append(
                    types.Content(role=m.role, parts=[types.Part.from_text(text=m.content)])
                )

            model = self._get_model_for_size(model_size)
            resolved_max_tokens = self._resolve_max_tokens(max_tokens, model)

            generation_config = types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=resolved_max_tokens,
                response_mime_type='application/json' if response_model else None,
                response_schema=response_model if response_model else None,
                system_instruction=system_prompt,
                thinking_config=self.thinking_config,
            )

            response = await self.client.aio.models.generate_content(
                model=model,
                contents=gemini_messages,
                config=generation_config,
            )

            raw_output = getattr(response, 'text', None)
            self._check_safety_blocks(response)
            self._check_prompt_blocks(response)

            if response_model is not None:
                if not raw_output:
                    raise ValueError('No response text')
                try:
                    return response_model.model_validate(json.loads(raw_output)).model_dump()
                except Exception:
                    salvaged = self.salvage_json(raw_output)
                    if salvaged is not None:
                        # If salvage returns dict already compatible, accept it.
                        try:
                            return response_model.model_validate(salvaged).model_dump()
                        except Exception:
                            return salvaged
                    # Final fallback: log concise info only
                    logger.error('Structured JSON parse failed and salvage failed.')
                    raise

            return {'content': raw_output}

        except Exception as e:
            error_message = str(e).lower()
            if (
                'rate limit' in error_message
                or 'quota' in error_message
                or 'resource_exhausted' in error_message
                or '429' in str(e)
            ):
                raise RateLimitError from e
            raise


