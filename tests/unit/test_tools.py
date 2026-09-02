"""Unit tests for the shared tool registry and Bedrock tool specs."""

from __future__ import annotations

import pytest

from filings_assistant.mcp_server.tools import TOOL_SCHEMAS, ToolRegistry, bedrock_tool_specs
from filings_assistant.search.opensearch_store import InMemoryVectorStore

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _reset_store() -> None:
    InMemoryVectorStore._docs = []


def test_registry_exposes_all_schema_tools() -> None:
    registry = ToolRegistry()
    assert set(registry.names) == set(TOOL_SCHEMAS)


def test_unknown_tool_returns_error() -> None:
    result = ToolRegistry().call("does_not_exist", {})
    assert "error" in result


def test_ingest_then_search_via_tools() -> None:
    registry = ToolRegistry()
    ingest_result = registry.call("ingest_filing", {"ticker": "AAPL", "form": "10-K", "limit": 1})
    assert ingest_result["ingested"] >= 1

    search_result = registry.call("hybrid_search", {"query": "supply chain risk", "top_k": 3})
    assert search_result["count"] >= 1
    assert "citation" in search_result["results"][0]


def test_bedrock_tool_specs_shape() -> None:
    specs = bedrock_tool_specs()
    assert specs
    for spec in specs:
        assert "toolSpec" in spec
        assert "name" in spec["toolSpec"]
        assert "inputSchema" in spec["toolSpec"]
