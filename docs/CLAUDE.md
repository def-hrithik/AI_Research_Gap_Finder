# CLAUDE.md — AI Research Gap Finder

Master instruction file for Claude / Antigravity. Concise by design: details live in `docs/`. **Read this file, then every file in `docs/`, before touching code.**

## 1. What this project is

**AI Research Gap Finder** is an evidence-grounded literature-analysis platform. Users upload academic PDFs into a *Project*; the backend parses, chunks, embeds and indexes them, analyzes each paper, synthesizes across papers, and produces **research gaps, contradictions, future directions and citation-rich reports** — every claim traceable to `paper → page → section → chunk`.

It is **not** a generic PDF chatbot. If the evidence is not in the uploaded papers, the system says so.

## 2. Current repository state (verified by inspection)

| Item | Fact |
|---|---|
| Frontend | **React 18 + Vite + TypeScript (strict) + Tailwind + React Router + TanStack Query + Axios + Recharts + lucide-react**. It is **NOT Next.js** (the original brief said Next.js; the repo is authoritative). |
| Frontend location | Repo root (`src/`, `package.json`, `vite.config.ts`) |
| Frontend deploy | Vercel (static SPA) |
| Mock/real switch | `VITE_USE_MOCK` (default `true`); all data access via `src/services/api.ts` → `mockApi` or `src/services/realApi.ts` |
| Frontend domain model | **Project-scoped** (`/projects/:projectId/...`) |
| Backend | **Does not exist yet.** To be created in `backend/` (Python/FastAPI) |
| Known oddity | Both `vite.config.js` and `vite.config.ts` exist. Do not touch unless asked. |

> Items marked **VERIFY** in the docs could not be confirmed (`src/` was not readable during doc authoring). Resolve them in **Task 0** of `docs/10_IMPLEMENTATION_PLAN.md`.

## 3. Documentation map (source of truth)

| File | Authoritative for |
|---|---|
| `docs/01_PROJECT_OVERVIEW.md` | Purpose, scope, non-goals, terminology, success criteria |
| `docs/02_SYSTEM_ARCHITECTURE.md` | Components, pipelines, deployment, ADRs |
| `docs/03_RAG_ARCHITECTURE.md` | Chunking, embeddings, Qdrant, BM25, RRF, rerank, context, citations |
| `docs/04_RESEARCH_GAP_ENGINE.md` | Gap/contradiction/future-work logic, confidence formulas |
| `docs/05_DATA_MODEL.md` | **All schemas, enums, IDs, payloads** |
| `docs/06_API_SPECIFICATION.md` | **All endpoints, error codes, frontend integration** |
| `docs/07_LLM_PROMPTS.md` | Versioned production prompts |
| `docs/08_DEVELOPMENT_GUIDELINES.md` | Standards, env vars, logging, security |
| `docs/09_EVALUATION.md` | Benchmark, metrics, eval script |
| `docs/10_IMPLEMENTATION_PLAN.md` | Task-by-task 2-day plan |
| `docs/11_TASK_TRACKER.md` | Checkbox status — **update as you work** |
| `docs/12_ANTIGRAVITY_RULES.md` | **Agent behavior rules (mandatory)** |
| `docs/13_ROADMAP.md` | MVP vs future (do not build future items) |

## 4. Priority hierarchy

1. Existing working application behavior
2. Explicit user requirements
3. This file (`CLAUDE.md`)
4. Detailed `docs/`
5. Existing code conventions

On conflict: **do not silently choose.** State the conflict, its impact, and pick the least destructive option unless the decision materially affects architecture — then ask.

## 5. Architecture rules

- Backend: Python 3.11+, FastAPI, Pydantic v2, PyMuPDF, SQLite (SQLAlchemy) for relational data, Qdrant for vectors, `rank_bm25` for lexical search. Backend lives in `backend/`.
- Layering: `api/` (thin routes) → `services`/pipeline modules (business logic) → `database/`, `llm/`, `embeddings/`, `retrieval/`. **No business logic in routes. No retrieval logic in generation code.**
- LLM provider, embedding model, reranker, vector store location: **all env-configurable**. Never hard-code a provider.
- Frontend is integrated **only** through `src/services/realApi.ts` (+ `src/types` additions). Do not redesign or rewrite components.
- Long jobs (ingest, analysis) are **async jobs** polled via `GET /api/jobs/{job_id}`.
- Every Qdrant/BM25 query **must** filter by `project_id`.

## 6. RAG rules

- Structure-aware chunking only (never naive fixed-size splitting alone). Chunks never cross canonical section boundaries. Every chunk keeps `page`.
- Retrieval = dense (BGE-M3) + BM25 → RRF → section-aware prior → cross-encoder rerank → evidence selection. Components stay modular (`retrieval/`).
- Never send whole PDFs to an LLM; send only selected evidence chunks.
- If evidence is below threshold → return `insufficient_evidence: true`. **Never answer from model knowledge.**

## 7. Evidence & citation rules (non-negotiable)

1. Never fabricate evidence or citations. A citation may only reference a chunk that was retrieved/selected in the current run.
2. LLM must cite by `chunk_id` and supply a **verbatim quote**; code verifies the quote exists in the chunk and the page is valid.
3. Distinguish **EXPLICIT** gaps (paper states it) from **SYNTHESIZED** gaps (cross-paper inference). Never present inference as a paper's statement.
4. Confidence and evidence strength are **computed in code** from verified evidence — never trusted from the LLM.
5. Missing info → exactly: `"Not explicitly stated in the provided paper."`
6. No absolute claims ("no researcher has ever…"). Scope every absence claim: "Among the N analyzed papers…".
7. Unsupported claims are removed, not softened.

## 8. Coding rules

Type hints everywhere; Pydantic schemas for all I/O; validate all external input; env-based config validated at startup; structured logging per pipeline stage; structured errors (no stack traces to clients); prompts versioned in `llm/prompts.py` and mirrored in `docs/07`; minimal dependencies; focused diffs. See `docs/08`.

## 9. Development workflow

`READ → UNDERSTAND → PLAN → IMPLEMENT → TEST → VERIFY → DOCUMENT`

- Inspect existing code before creating files; do not duplicate.
- Run tests after every meaningful change; fix failures before the next feature.
- Update `docs/` in the same change as any architecture/schema/API change.
- Tick `docs/11_TASK_TRACKER.md` only when the task's **verification** step passes.
- Do **not** implement items from `docs/13_ROADMAP.md` beyond MVP.

## 10. Testing requirements

Unit tests for: PDF extraction, section detection, chunking, metadata extraction, embeddings (shape/dim), BM25, RRF, reranking, API schemas, gap detection, contradiction detection, evidence & citation validation. At least 3 end-to-end tests (upload→index→search; analyze→gaps; insufficient-evidence). LLM calls are mocked in unit tests via a fake provider. Run: `cd backend && pytest -q`.

## 11. Commands (target state)

```bash
# Frontend (existing)
npm install && npm run dev            # http://localhost:5173
npx tsc -b && npm run build

# Backend (to be created)
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                  # fill values; never commit .env
uvicorn app.main:app --reload --port 8000
pytest -q
python scripts/evaluate.py --benchmark eval/benchmark.jsonl
```
