"""End-to-end unit test of the offline pipeline (ingest → index → search → agent)."""

from __future__ import annotations

import pytest

from filings_assistant.agent.agent import FilingsAgent
from filings_assistant.ingestion.service import IngestionService
from filings_assistant.models import FilingForm
from filings_assistant.search.opensearch_store import InMemoryVectorStore
from filings_assistant.worker.processor import WorkerProcessor

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _reset_store() -> None:
    InMemoryVectorStore._docs = []


def test_full_offline_pipeline() -> None:
    stored = IngestionService().ingest("AAPL", FilingForm.FORM_10K, limit=1)
    assert stored

    indexed = WorkerProcessor().drain()
    assert indexed >= 1

    answer = FilingsAgent().ask("What supply chain risks does Apple cite?")
    assert answer.answer
    assert answer.steps >= 1


def test_ingest_is_idempotent() -> None:
    svc = IngestionService()
    first = svc.ingest("MSFT", FilingForm.FORM_10K, limit=1)
    second = svc.ingest("MSFT", FilingForm.FORM_10K, limit=1)
    assert first  # first ingest stores
    assert second == []  # duplicate checksum -> nothing new
