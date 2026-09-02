"""Search service: keyword, semantic, and hybrid retrieval.

Hybrid search fuses BM25 keyword results and k-NN vector results using
Reciprocal Rank Fusion (RRF). RRF is robust because it combines *rankings*
rather than raw scores (which live on different scales between BM25 and
cosine similarity), so neither signal dominates by accident.

    RRF score(d) = sum over result lists of 1 / (k + rank_d)
"""

from __future__ import annotations

from filings_assistant.common.bedrock import BedrockClient, get_bedrock_client
from filings_assistant.common.config import Settings, get_settings
from filings_assistant.common.logging import get_logger
from filings_assistant.models import SearchHit
from filings_assistant.search.opensearch_store import VectorStore, get_vector_store

logger = get_logger("search.service")

_RRF_K = 60  # standard RRF constant; larger = flatter rank weighting


class SearchService:
    """Provides keyword, semantic, and hybrid search over the filing corpus."""

    def __init__(
        self,
        settings: Settings | None = None,
        store: VectorStore | None = None,
        bedrock: BedrockClient | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._store = store or get_vector_store(self._settings)
        self._bedrock = bedrock or get_bedrock_client(self._settings)

    def keyword_search(self, query: str, top_k: int | None = None) -> list[SearchHit]:
        """BM25 keyword search."""
        return self._store.keyword_search(query, top_k or self._settings.top_k)

    def semantic_search(self, query: str, top_k: int | None = None) -> list[SearchHit]:
        """Embed the query and run k-NN vector search."""
        embedding = self._bedrock.embed_texts([query])[0]
        return self._store.vector_search(embedding, top_k or self._settings.top_k)

    def hybrid_search(self, query: str, top_k: int | None = None) -> list[SearchHit]:
        """Fuse keyword + semantic results with Reciprocal Rank Fusion."""
        k = top_k or self._settings.top_k
        # Over-fetch each signal so fusion has candidates to work with.
        keyword_hits = self.keyword_search(query, top_k=k * 2)
        semantic_hits = self.semantic_search(query, top_k=k * 2)
        fused = _reciprocal_rank_fusion([keyword_hits, semantic_hits])
        return fused[:k]


def _reciprocal_rank_fusion(result_lists: list[list[SearchHit]]) -> list[SearchHit]:
    """Combine multiple ranked lists into one via RRF, deduping by chunk_id."""
    scores: dict[str, float] = {}
    by_id: dict[str, SearchHit] = {}
    for hits in result_lists:
        for rank, hit in enumerate(hits):
            scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1.0 / (_RRF_K + rank)
            by_id.setdefault(hit.chunk_id, hit)
    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    fused: list[SearchHit] = []
    for chunk_id, score in ordered:
        hit = by_id[chunk_id]
        # Surface the fused score so callers can display/threshold on it.
        fused.append(hit.model_copy(update={"score": round(score, 6)}))
    return fused
