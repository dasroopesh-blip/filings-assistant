# Tasks: Filings Assistant

- [x] 1. Project scaffold, tooling, config (pyproject, ruff, Makefile, .env)
- [x] 2. Common layer: config, logging, Bedrock client (+mock), retry, storage
- [x] 3. Domain models (Filing, Chunk, SearchHit, IngestJob)
- [x] 4. SEC EDGAR ingestion: fetch → store (Postgres) → enqueue (+ offline samples)
- [x] 5. Worker: chunk → embed (Titan) → index (OpenSearch k-NN)
- [x] 6. Search: keyword (BM25), semantic (k-NN), hybrid (RRF)
- [x] 7. MCP server + shared tool registry
- [x] 8. Agentic reasoning loop (Claude) with citations + guardrails
- [x] 9. Local dev: docker-compose (OpenSearch + Postgres) + smoke test
- [x] 10. Terraform: VPC, OpenSearch, RDS, SQS+DLQ, Lambda, IAM, KMS, budgets
- [x] 11. Docs: README, ARCHITECTURE, DESIGN, TERRAFORM_GUIDE + this spec
- [x] 12. Unit tests: chunker, RRF/search, agent, config, tools
- [ ] 13. Future: SageMaker reranker, evaluation harness, Fargate agent API
```
