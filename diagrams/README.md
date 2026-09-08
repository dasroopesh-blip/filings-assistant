# Diagrams

Architecture diagrams for the Filings Assistant, in [draw.io](https://app.diagrams.net)
format (`.drawio`). Open them at [app.diagrams.net](https://app.diagrams.net)
(File → Open) or with the draw.io / diagrams.net editor. Naming mirrors the
companion `verticalbroker-aws-platform` repo (`NN-name.drawio`).

Each file documents a **High-Level Design (HLD)** or a per-component
**Low-Level Design (LLD)**.

| # | File | Level | Component |
|---|------|-------|-----------|
| 01 | `01-system-architecture-hld.drawio` | **HLD** | Whole system: ingestion + query flows across Bedrock, OpenSearch, SageMaker; cross-cutting security/observability |
| 02 | `02-ingestion-pipeline-lld.drawio` | LLD | Ingestion: SEC EDGAR → Postgres (truth) → SQS → worker → Titan embed → OpenSearch (numbered steps, idempotency, DLQ) |
| 03 | `03-search-ranking-funnel-lld.drawio` | LLD | Ranking funnel: Stage 1 retrieve (BM25 + kNN) → Stage 2 RRF fuse → Stage 3 SageMaker rerank |
| 04 | `04-agent-mcp-lld.drawio` | LLD | Agentic AI + MCP: query understanding, bounded tool-use loop, shared tool registry, injection-safe tool schemas |
| 05 | `05-multi-tenancy-isolation-lld.drawio` | LLD | Isolation by `tenant_id` across storage/search/tools/**LLM**; Bedrock-stateless note; injection example; proof tests |
| 06 | `06-vpc-network-infra-lld.drawio` | LLD | VPC/subnets, Terraform modules, security groups, KMS, managed services, dev-vs-prod cost posture |

## How these map to the code & docs

- **01 HLD** ↔ `docs/ARCHITECTURE.md` (System overview)
- **02** ↔ `ingestion/`, `worker/`, `common/storage.py`
- **03** ↔ `search/service.py`, `search/opensearch_store.py`, `search/reranker.py`, `docs/SEARCH_EXCELLENCE.md`
- **04** ↔ `agent/`, `mcp_server/`
- **05** ↔ `common/tenant.py`, `docs/MULTI_TENANCY.md`, `tests/unit/test_tenant_isolation.py`
- **06** ↔ `terraform/` (all modules), `docs/TERRAFORM_GUIDE.md`

## Conventions

- **Blue** = OpenSearch / retrieval · **Purple** = Bedrock/SageMaker (ML) ·
  **Green** = application services · **Orange** = SEC/SQS · **Red** = data-of-record / security · **Yellow** = auth/control/observability.
- Dashed arrows = optional / asynchronous / fallback paths.
