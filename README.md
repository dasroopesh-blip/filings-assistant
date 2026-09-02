# Filings Assistant

An **Agentic RAG assistant over public SEC EDGAR filings**. Ask natural-language
questions about company filings (10-K / 10-Q / 8-K) and get **grounded, cited**
answers — no hallucinated numbers, every claim traceable to a source filing.

Built as three layers on top of a standard ingestion pipeline:

1. **Search / RAG** — Bedrock Titan embeddings + Amazon OpenSearch (k-NN vector
   search + BM25 keyword search, fused with Reciprocal Rank Fusion).
2. **MCP server** — exposes the capabilities (`ingest`, `hybrid_search`, …) as
   [Model Context Protocol](https://modelcontextprotocol.io) tools any client can call.
3. **Agentic AI** — a Bedrock Claude Sonnet reasoning loop that plans, calls
   those tools, and synthesizes a cited answer.

> **Domain note.** This is a financial-services demo. It reports *what filings
> disclose* and does **not** provide investment advice. Citations + data lineage
> are first-class because auditability matters in regulated contexts.

> Engineering patterns (resilience utilities, Terraform module style, tooling)
> are derived from the companion `verticalbroker-aws-platform` repo.

---

## Architecture at a glance

```
Ingestion (write path)                 Query (read path)
─────────────────────                  ─────────────────
SEC EDGAR                              User question
   │ fetch                                │
   ▼                                      ▼
Postgres (source of truth)            Agent (Claude, Bedrock)
   │ enqueue                              │  plans + calls tools
   ▼                                      ▼
SQS  ──►  Worker (Lambda)             MCP tools ──► Hybrid search
              │ chunk + embed (Titan)               (OpenSearch: k-NN + BM25)
              ▼                                      │
        OpenSearch (k-NN + text) ◄──────────────────┘
                                                     ▼
                                          Cited answer
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for full diagrams and
[`docs/DESIGN.md`](docs/DESIGN.md) for the decisions and rationale.

---

## Quick start (local, $0)

Everything runs on your laptop. Two ways to run:

### Option 1 — fully in-memory (no Docker, no AWS)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run the whole pipeline offline (mock Bedrock, in-memory store + queue):
python scripts/smoke_test.py
```

This ingests offline sample filings, embeds + indexes them, runs hybrid search,
and produces an agent answer with citations — proving the wiring end to end.

### Option 2 — local OpenSearch + Postgres (Docker)

```bash
make docker-up            # start OpenSearch + Postgres
cp .env.example .env      # then set FA_RUN_MODE=aws + localhost hosts

# Ingest a filing and index it, then ask a question:
make ingest ARGS="--ticker AAPL --form 10-K --limit 1 --run-worker"
make ask Q="What supply chain risks does Apple disclose?"

make docker-down          # stop the stack
```

> **Offline sandbox?** If the SEC API or Bedrock is unreachable, the code
> automatically falls back to bundled sample filings and a deterministic mock
> embedder/answerer, so the pipeline always runs.

---

## Using real AWS (Bedrock + OpenSearch)

1. Enable **model access** in the Bedrock console for Claude Sonnet + Titan
   Embeddings V2 in your region.
2. Set in `.env`:
   ```
   FA_RUN_MODE=aws
   FA_USE_MOCK_BEDROCK=false
   AWS_REGION=us-east-1
   FA_OPENSEARCH_HOST=<your-opensearch-endpoint>
   FA_PG_HOST=<your-rds-endpoint>
   FA_QUEUE_URL=<your-sqs-url>
   ```
3. Model IDs are configurable (`FA_BEDROCK_REASONING_MODEL_ID`,
   `FA_BEDROCK_EMBEDDING_MODEL_ID`) — bump versions without code changes.

---

## Deploying the infrastructure (Terraform)

The `terraform/` directory provisions the full stack. It's written to be
**beginner-friendly and heavily commented** — see
[`docs/TERRAFORM_GUIDE.md`](docs/TERRAFORM_GUIDE.md) for a learn-from-scratch walkthrough.

```bash
cp terraform/environments/dev.tfvars.example terraform/environments/dev.tfvars
# edit dev.tfvars (set budget_alert_email)

./scripts/build-lambda.sh   # build the worker deployment package
make tf-init
make tf-plan                # review what will be created
make tf-apply               # create it

make tf-destroy             # ⚠️ tear it ALL down when done (stops idle costs)
```

### 💰 Cost notes (important)

| Cost bucket | Reality |
|---|---|
| **Bedrock tokens** | Cheap — a few dollars for dev/testing. |
| **AWS infra (idle)** | The real driver: OpenSearch + RDS bill *per hour while running*. |

To stay well under budget:
- Do most work **locally** ($0).
- Use the **smallest instances** (dev defaults: `t3.small.search`, `db.t3.micro`).
- **`make tf-destroy`** between demos so nothing bills while idle.
- A **Budgets alarm** emails you at 50% and 90% of `monthly_budget_usd`.

---

## Repository layout

```
src/filings_assistant/
├── common/        # config, logging, Bedrock client, retry, storage (PG/SQS + local)
├── models/        # Pydantic domain models (Filing, Chunk, SearchHit)
├── ingestion/     # SEC EDGAR fetch → store → enqueue (+ CLI)
├── worker/        # chunk + embed + index (SQS-triggered Lambda)
├── search/        # chunker, OpenSearch store, hybrid search (RRF)
├── mcp_server/    # MCP tools + stdio server
└── agent/         # Claude reasoning loop (+ CLI)
terraform/         # modular, commented IaC (VPC, OpenSearch, RDS, SQS, Lambda, budgets)
docker/            # local OpenSearch + Postgres
docs/              # ARCHITECTURE, DESIGN, TERRAFORM_GUIDE
tests/             # unit tests (offline, no AWS)
```

## Development

```bash
make lint      # ruff + black --check + mypy
make test      # unit tests
make fmt       # auto-format
```

## License

MIT.
