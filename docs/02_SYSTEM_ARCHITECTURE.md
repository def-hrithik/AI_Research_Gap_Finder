# 02 — System Architecture

## 1. High-level architecture

```mermaid
flowchart TB
  subgraph Client["Frontend (Vercel) — React 18 + Vite SPA"]
    UI[Pages/Components]
    HK[React Query hooks]
    SV["services/api.ts<br/>(mock ⇄ real switch)"]
    RA[services/realApi.ts]
    UI --> HK --> SV --> RA
  end

  subgraph API["Backend (FastAPI) — backend/app"]
    RT["api/ routes (thin)"]
    JOB[Job runner<br/>BackgroundTasks + thread pool]
    ING[ingestion/]
    EMB[embeddings/]
    RET[retrieval/]
    ANA[analysis/]
    VAL[validation/]
    LLM[llm/ provider-agnostic client]
    DB[(SQLite via SQLAlchemy)]
    RT --> JOB
    JOB --> ING --> EMB
    JOB --> ANA
    ANA --> RET
    ANA --> LLM
    ANA --> VAL
    RT --> RET
    ING --> DB
    ANA --> DB
    VAL --> DB
  end

  subgraph Stores
    QD[(Qdrant<br/>dense vectors + payload)]
    FS[(Local file store<br/>uploaded PDFs)]
  end

  EXT[LLM API<br/>configurable provider]

  RA -- "REST/JSON (HTTPS, CORS)" --> RT
  EMB --> QD
  RET --> QD
  RET --> DB
  ING --> FS
  LLM --> EXT
```

### 1.1 Responsibilities

| Layer | Responsibility | Must NOT |
|---|---|---|
| `api/` | Parse/validate request, call service, map to response schema, map exceptions → structured errors | Contain business logic |
| `ingestion/` | PDF → pages → metadata → sections → chunks | Call LLM except metadata extractor (via `llm/`) |
| `embeddings/` | Load model once, batch-encode (documents/queries) | Know about Qdrant |
| `retrieval/` | Dense, BM25, RRF, section prior, rerank, evidence selection | Call the LLM for answering |
| `analysis/` | Paper analysis, synthesis, contradictions, future work, gaps | Fetch vectors directly (use `retrieval/`) |
| `validation/` | Verify quotes/pages/chunks/support; compute confidence | Generate new claims |
| `llm/` | Provider abstraction, JSON-schema output, retries, token accounting, versioned prompts | Contain pipeline logic |
| `database/` | SQLAlchemy models/repos, Qdrant client wrapper | Contain business rules |

### 1.2 Backend directory layout (adapted; repo root also holds the frontend)

```
<repo root>
├── src/ public/ package.json vite.config.ts …     # EXISTING frontend — do not restructure
├── docs/                                           # these files
├── CLAUDE.md
└── backend/
    ├── app/
    │   ├── main.py                  # app factory, CORS, lifespan (model warmup), routers
    │   ├── config.py                # pydantic-settings, startup validation
    │   ├── api/
    │   │   ├── projects.py papers.py search.py analysis.py gaps.py reports.py jobs.py
    │   │   ├── research.py          # POST /api/research/analyze orchestration
    │   │   └── deps.py errors.py    # DI + exception handlers
    │   ├── services/                # orchestration glue (ingest_service, research_service, report_service)
    │   ├── ingestion/ pdf_parser.py section_detector.py metadata_extractor.py chunker.py
    │   ├── embeddings/ embedder.py
    │   ├── retrieval/ vector_search.py bm25.py hybrid.py reranker.py intent.py evidence_selector.py
    │   ├── analysis/ paper_analyzer.py synthesizer.py contradiction.py future_work.py gap_detector.py
    │   ├── validation/ evidence_validator.py citation_validator.py scoring.py
    │   ├── llm/ client.py providers/ prompts.py schemas_json.py
    │   ├── database/ models.py session.py repos.py qdrant.py
    │   ├── schemas/ project.py paper.py chunk.py evidence.py analysis.py gap.py contradiction.py future.py report.py job.py common.py
    │   └── core/ logging.py ids.py errors.py
    ├── scripts/ evaluate.py
    ├── eval/ benchmark.jsonl
    ├── tests/ (unit/, e2e/, fixtures/pdfs/)
    ├── requirements.txt  Dockerfile  .env.example
    └── data/ (gitignored: sqlite db, uploads, qdrant local)
```

**Conflict note:** repo root already contains Vite files, so the backend is isolated in `backend/`. Vercel must build only the frontend; add `backend/` to `.vercelignore` if Vercel scans it.

## 2. Frontend ⇄ backend interaction

- All HTTP from the SPA goes through `src/services/realApi.ts` (Axios). `VITE_USE_MOCK=false` activates it.
- Base URL from an env var (**VERIFY** the existing name in `src/services/`; if none, add `VITE_API_BASE_URL`).
- Backend JSON is the **canonical contract** (docs/05, 06). Where existing `src/types` differ, add mapper functions in `realApi.ts` (preferred) rather than bending backend schemas. Only add *optional* fields to `src/types`.
- Long operations: frontend polls `GET /api/jobs/{job_id}` (React Query `refetchInterval` while `RUNNING`).
- CORS: backend allows `CORS_ORIGINS` (localhost:5173 + the Vercel domain).
- Source viewing: `sources[]`/`evidence[]` carry `paper_id`, `page`, `section`, `chunk_id`, text → frontend can open Paper Details at the page.

```mermaid
sequenceDiagram
  participant FE as React SPA
  participant API as FastAPI
  participant J as Job runner
  participant Q as Qdrant
  participant L as LLM
  FE->>API: POST /api/projects/{id}/papers/upload (multipart)
  API-->>FE: 202 {paper_id, job_id}
  API->>J: schedule ingest
  loop poll
    FE->>API: GET /api/jobs/{job_id}
    API-->>FE: {status, stage, progress}
  end
  J->>Q: upsert chunk vectors
  FE->>API: POST /api/research/analyze {project_id, query, paper_ids, depth}
  API-->>FE: 202 {job_id}
  J->>L: staged LLM calls (JSON schema)
  J-->>API: persist result
  FE->>API: GET /api/jobs/{job_id}
  API-->>FE: {status: SUCCEEDED, result: {...}}
```

## 3. Ingestion pipeline

```mermaid
flowchart TD
  A[Upload multipart] --> B{Validate<br/>type, size, magic bytes}
  B -- fail --> E1[415/413 error]
  B --> C[sha256 → duplicate check]
  C -- dup --> E2[409 DUPLICATE_PAPER]
  C --> D[Save file to DATA_DIR/uploads]
  D --> J[(Create Paper PARSING + Job)]
  J --> P[pdf_parser: pages, blocks, fonts]
  P --> Q{Extractable text?}
  Q -- no --> E3[FAILED: SCANNED_PDF_NO_TEXT / EMPTY_PDF]
  Q --> M[metadata_extractor<br/>PyMuPDF meta + DOI regex + LLM on page 1-2]
  M --> S[section_detector<br/>font/regex headings → canonical sections]
  S --> K[chunker<br/>section-bounded, page-preserving]
  K --> EM[embedder: batch BGE-M3]
  EM --> UP[Qdrant batch upsert + SQLite chunks]
  UP --> BM[invalidate project BM25 cache]
  BM --> DONE[Paper INDEXED]
```

Each stage updates `Paper.status` and `Job.stage/progress`. Failure at any stage sets `FAILED` + `error{code,message}`; partial artifacts (Qdrant points, chunk rows) are rolled back (delete by `paper_id`).

## 4. Retrieval pipeline

Detailed in `03_RAG_ARCHITECTURE.md`. Summary:

```mermaid
flowchart LR
  Q[Query] --> I[Intent + rewrite]
  I --> D[Dense top-k]
  I --> B[BM25 top-k]
  D --> R[RRF]
  B --> R
  R --> S[Section-aware prior]
  S --> C[Cross-encoder rerank]
  C --> T{Threshold<br/>gate}
  T -- below --> X[insufficient_evidence]
  T -- ok --> E[Top evidence chunks]
```

## 5. Analysis pipeline

```mermaid
flowchart TD
  subgraph S1[Stage 1-2 per paper — cached]
    A1[Select section chunks] --> A2[LLM: paper analysis JSON<br/>each field cites chunk_id + quote]
    A2 --> A3[Quote/page verification]
  end
  S1 --> M[Evidence matrix build — deterministic]
  M --> T[Stage 4: Theme detection LLM]
  M --> L[Stage 5: Limitation + future-work aggregation LLM]
  M --> C[Stage 6: Contradiction candidates + LLM adjudication]
  T & L & C --> G[Stage 7: Gap detection]
  G --> V[Stage 8: Evidence validation + scoring]
  V --> R[Stage 9: Report generation]
```

Stage numbering vs. brief: Stage 2 (evidence extraction) is **implemented inside Stage 1's output contract + deterministic verification** (no separate LLM call) to limit LLM calls; query-focused evidence extraction for `/api/search` is the retrieval pipeline. See 04 for details.

### LLM call budget (N papers, `standard` depth)

| Stage | Calls | Cached |
|---|---|---|
| Metadata (ingest) | N | with paper |
| Paper analysis | N | per paper+prompt_version |
| Theme detection | 1 | per paper-set hash |
| Limitation/future aggregation | 1 | per paper-set hash |
| Contradiction | 1–2 | per paper-set hash |
| Gap detection | 1–3 (per category group) | per paper-set hash |
| Entailment validation | 1–3 (batched) | — |
| Report | 1 | — |
| **Total new analysis** | ≈ **N + 10** | |

`quick`: skip contradiction + validation LLM pass (deterministic checks only). `deep`: also per-gap targeted re-retrieval for absence claims.

## 6. Gap-detection pipeline & validation (summary)

Full logic in `04_RESEARCH_GAP_ENGINE.md`. Order: collect explicit limitations/future work → build matrix + facets → LLM proposes candidate gaps citing `chunk_id`+quote → **code verifies every evidence item** → entailment check (LLM batch) → drop/downgrade → **code computes confidence/evidence_strength** → persist.

```mermaid
flowchart LR
  C[LLM candidate gaps] --> V1[Chunk exists?]
  V1 --> V2[Page valid?]
  V2 --> V3[Quote ⊂ chunk text?]
  V3 --> V4[Entailment SUPPORTS?]
  V4 --> V5[Independent papers count]
  V5 --> SC[Compute confidence + strength]
  SC --> F{Evidence ≥ minimum?}
  F -- no --> DROP[Remove gap]
  F -- yes --> OUT[Persist + return]
```

## 7. Async processing model (MVP)

- FastAPI `BackgroundTasks` + a bounded `ThreadPoolExecutor` (`ANALYSIS_MAX_CONCURRENCY`) — CPU-bound parsing/embedding runs in threads; LLM calls use async client with semaphore.
- Job state persisted in SQLite (`jobs` table); on startup, jobs left `RUNNING` are marked `FAILED(INTERRUPTED)`.
- Embedding model and reranker are loaded **once** (lifespan) and guarded by a lock/semaphore.
- Upgrade path (documented, not built): Redis + RQ/Celery.

## 8. Deployment architecture

```mermaid
flowchart LR
  Browser --> V["Vercel<br/>static React SPA"]
  Browser -- HTTPS+CORS --> B["Backend container<br/>Render/Railway/VM<br/>FastAPI + BGE-M3 + reranker"]
  B --> QC[(Qdrant Cloud<br/>or Docker qdrant)]
  B --> LLMX[LLM provider API]
  B --- VOL[(Persistent volume<br/>sqlite + uploads + HF cache)]
```

| Concern | Decision |
|---|---|
| Frontend | Vercel; env `VITE_USE_MOCK=false`, API base URL env |
| Backend | Single Docker container, `uvicorn` 1 worker (models are in-process; multi-worker multiplies RAM) |
| **Memory** | BGE-M3 (~2.3 GB weights) + reranker (~2.3 GB) → plan **≥ 8 GB RAM** on CPU hosts. Free tiers (≤ 512 MB–2 GB) **will not work**. Mitigations: `RERANKER_ENABLED=false`, hosted embedding provider behind the same `Embedder` interface, or a GPU/VM host. |
| Model download | Bake HF models into image or mount persistent HF cache (`HF_HOME`) to avoid cold-start downloads |
| Qdrant | Local dev: `docker run -p 6333:6333 qdrant/qdrant` (or embedded `QDRANT_LOCAL_PATH`); prod: Qdrant Cloud URL + API key |
| Persistence | Volume for `data/` (SQLite + PDFs). Ephemeral disks lose data — use Postgres via `DATABASE_URL` if the host is ephemeral |
| Secrets | Host env vars only; `.env` never committed |
| Health | `GET /api/health` (liveness), `GET /api/health/ready` (Qdrant + models + DB) |

## 9. Architecture decision records (ADRs)

| ID | Decision | Rationale | Alternative (deferred) |
|---|---|---|---|
| ADR-1 | Backend in `backend/`, frontend untouched | Repo root is a Vite app | Monorepo tooling |
| ADR-2 | SQLite + SQLAlchemy for relational data | Zero-ops MVP; Postgres via URL swap | Postgres from day 1 |
| ADR-3 | Qdrant dense-only; BM25 via `rank_bm25` in-process | Brief requires separate lexical stage; fits ≤ ~10⁵ chunks | Qdrant sparse vectors / BGE-M3 sparse |
| ADR-4 | Single Qdrant collection, `project_id` payload filter | Simpler ops than collection-per-project | Collection per project |
| ADR-5 | Confidence/strength computed in code | LLM self-confidence is unreliable | LLM-calibrated scores |
| ADR-6 | LLM cites `chunk_id` + verbatim quote; code verifies | Cheapest strong anti-hallucination guard | Generic NLI model |
| ADR-7 | Background tasks + persisted jobs | Meets async requirement without a broker | Celery/RQ |
| ADR-8 | Backend JSON is canonical; adapt in `realApi.ts` | Keeps frontend components unchanged | Backend mimics mock shapes |
| ADR-9 | Scanned PDFs rejected (no OCR) | Time-box; clear error | Tesseract/Docling OCR |
