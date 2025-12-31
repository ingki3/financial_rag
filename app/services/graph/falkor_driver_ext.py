"""FalkorDB driver extensions for Graphiti.

Graphiti's built-in `FalkorDriver` uses the async FalkorDB client but does not
pass per-query timeouts to `Graph.query(...)`. When the graph grows, some
fulltext queries (e.g., `db.idx.fulltext.queryRelationships`) can time out.

This module provides a drop-in `FalkorDriverWithTimeout` that:
- Applies a **per-query TIMEOUT** (ms) to all graph queries.
- Optionally sets client socket timeouts.
"""

from __future__ import annotations

import logging
import datetime as dt
from typing import Any

from graphiti_core.driver.falkordb_driver import FalkorDriver, FalkorDriverSession

logger = logging.getLogger(__name__)

def _convert_datetimes(obj: Any) -> Any:
    """graphiti_core의 convert_datetimes_to_strings가 `import datetime`로 인해 타입 오류가 날 수 있어,
    여기서 안전하게 datetime을 문자열로 변환한다.
    """
    if isinstance(obj, dict):
        return {k: _convert_datetimes(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_datetimes(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_convert_datetimes(v) for v in obj)
    if isinstance(obj, dt.datetime):
        return obj.isoformat()
    return obj


class FalkorDriverSessionWithTimeout(FalkorDriverSession):
    def __init__(self, graph, query_timeout_ms: int | None):
        super().__init__(graph)
        self._query_timeout_ms = query_timeout_ms

    async def run(self, query: str | list, **kwargs: Any) -> Any:
        # Same behavior as upstream, but pass `timeout=` to graph.query().
        if isinstance(query, list):
            for cypher, params in query:
                q = str(cypher)
                p = _convert_datetimes(params) if params is not None else None
                try:
                    await self.graph.query(q, p, timeout=self._query_timeout_ms)  # type: ignore[arg-type]
                except Exception as e:
                    logger.error(f"FalkorDB session.run failed:\nQUERY={q}\nPARAMS={p}\nERROR={e}")
                    raise
        else:
            q = str(query)
            p = _convert_datetimes(dict(kwargs)) if kwargs else None
            try:
                await self.graph.query(q, p, timeout=self._query_timeout_ms)  # type: ignore[arg-type]
            except Exception as e:
                logger.error(f"FalkorDB session.run failed:\nQUERY={q}\nPARAMS={p}\nERROR={e}")
                raise
        return None


class FalkorDriverWithTimeout(FalkorDriver):
    """FalkorDriver that enforces a per-query timeout (ms) for all queries."""

    def __init__(self, *args, query_timeout_ms: int | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._query_timeout_ms = query_timeout_ms
        if self._query_timeout_ms:
            logger.info(f"FalkorDriver query timeout set to {self._query_timeout_ms}ms")

    def clone(self, database: str):  # type: ignore[override]
        """
        IMPORTANT: force **single graph** usage.

        Graphiti-core calls `driver.clone(group_id)` for multi-tenant isolation.
        In FalkorDB driver, `database` maps to the *graph name*.
        If we return a new driver with `database=group_id`, FalkorDB will create a new graph per ticker (e.g., TSLA).

        Project requirement: keep a single graph instance (`default_db`) and partition by `group_id` property.
        So we intentionally ignore the requested database and keep using `self._database`.
        """
        return self

    async def execute_query(self, cypher_query_, **kwargs: Any):
        # Override to pass `timeout=` to FalkorDB.
        graph = self._get_graph(self._database)
        params = _convert_datetimes(dict(kwargs))
        try:
            result = await graph.query(cypher_query_, params, timeout=self._query_timeout_ms)  # type: ignore[arg-type]
        except Exception as e:
            if 'already indexed' in str(e):
                logger.info(f'Index already exists: {e}')
                return None
            logger.error(f'Error executing FalkorDB query: {e}\n{cypher_query_}\n{params}')
            raise

        header = [h[1] for h in result.header]
        records = []
        for row in result.result_set:
            record = {}
            for i, field_name in enumerate(header):
                record[field_name] = row[i] if i < len(row) else None
            records.append(record)
        return records, header, None

    def session(self, database: str | None = None):
        # Force single-graph usage regardless of requested `database`.
        return FalkorDriverSessionWithTimeout(self._get_graph(self._database), self._query_timeout_ms)


