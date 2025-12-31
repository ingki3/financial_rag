import os
from pathlib import Path
from typing import Any, Dict

import yaml


class PromptLoader:
    def __init__(self, prompt_dir: str = "app/prompts"):
        # Make prompt_dir robust to current working directory by resolving relative paths
        # from the project root (two levels up from app/utils/).
        p = Path(prompt_dir)
        if p.is_absolute():
            self.prompt_dir = str(p)
        else:
            project_root = Path(__file__).resolve().parents[2]
            self.prompt_dir = str((project_root / prompt_dir).resolve())

    def load_prompt(self, prompt_name: str) -> Dict[str, Any]:
        """
        Loads a YAML prompt file.
        Args:
            prompt_name: The name of the prompt file (without extension).
        Returns:
            Dict containing the prompt data.
        """
        file_path = os.path.join(self.prompt_dir, f"{prompt_name}.yaml")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error loading prompt {prompt_name}: {str(e)}")


prompt_loader = PromptLoader()


