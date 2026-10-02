# 06 — API Specification

Authoritative for: endpoints, request/response contracts, error codes, status handling. Schemas referenced as `05 §x` live in `05_DATA_MODEL.md` and are **not** redefined here. Frontend mapping lives in `14_FRONTEND_BACKEND_INTEGRATION.md`.

Priority tags: **P0** = needed for the MVP demo · **P1** = should ship in MVP if time allows · **P2** = stretch / after MVP (see `10`, `12`).

## 1. Conventions

| Item | Rule |
|---|---|
| Base path | **`/api`** (canonical, matches 02/05). The existing `realApi.ts` hard-codes `baseURL: '/api/v1'` — this is a **known conflict**; resolution = change that one line in `realApi.ts` (see 14 §3 and Errata in 10). The backend does **not** also serve `/api/v1`. |
| Format | JSON, UTF-8, `snake_case`, ISO-8601 UTC timestamps, IDs per 05 §1 (`prj_…`, `pap_…`, `chk_…`, `gap_…`, `run_…`, `job_…`) |
| Page numbers | 1-indexed (05 §1) |
| Scores | 0–1 floats, 2 decimals. (The frontend uses 0–100; conversion happens in the mapper, never in the API.) |
| Enums | UPPERCASE exactly as 05 §2 (`EXPLICIT`, `SYNTHESIZED`, `LIMITATION`, …) |
| Missing text | Literal `"Not explicitly stated in the provided paper."` (`NOT_STATED`) |
| Request ID | Client may send `X-Request-ID` (≤64 chars `[A-Za-z0-9_-]`); otherwise server generates `req_<6hex>`. Always echoed in the `X-Request-ID` response header, in every error body, and in every log line. |
| Content types | Requests: `application/json` or `multipart/form-data` (upload only). Responses: `application/json` (+ `text/markdown`, `application/pdf` where stated). |
| Auth | **None in MVP.** Placeholder: if env `API_KEY` is set, every `/api/*` request except health must send `X-API-Key`; mismatch → `401 UNAUTHORIZED`. This is **demo-grade only** — a key embedded in a Vite bundle is public. Real auth is roadmap (12). |
| CORS | `CORS_ORIGINS` / `CORS_ORIGIN_REGEX` (15 §6). Exposed headers: `X-Request-ID`, `Retry-After`, `Location`. |
| Tenancy | Single-tenant MVP: all projects are visible to every caller. |

### 1.1 List envelope & pagination

All list endpoints accept `limit` (default 50, max 200) and `offset` (default 0), and return:

```json
{ "items": [ ... ], "total": 137, "limit": 50, "offset": 0 }
```

Sort params where supported: `sort=<field>` and `order=asc|desc`. Unknown sort field → `422 VALIDATION_ERROR`.

### 1.2 Error envelope (05 §5.16)

```json
{ "error": { "code": "DUPLICATE_PAPER", "message": "This PDF already exists in the project.",
             "details": { "existing_paper_id": "pap_91ac27de" }, "request_id": "req_a1b2c3" } }
```

`message` is human-safe (never a stack trace, path, SQL, prompt text, or API key). `details` is optional structured context. Stack traces go to server logs only.

### 1.3 Status codes

| Code | Use |
|---|---|
| 200 | Successful read / synchronous operation (incl. search with `insufficient_evidence=true` — **not an error**) |
| 201 | Resource created synchronously (`POST /api/projects`) |
| 202 | Work accepted and running as a **job** (upload, analyze) — body has `job_id`, header `Location: /api/jobs/{job_id}` |
| 204 | Successful delete |
| 400 | Malformed request (bad JSON, bad multipart) |
| 401 | `UNAUTHORIZED` (only when `API_KEY` configured) |
| 404 | `*_NOT_FOUND` |
| 409 | State conflict (`DUPLICATE_PAPER`, `PAPERS_NOT_READY`, `NO_INDEXED_PAPERS`, `ANALYSIS_IN_PROGRESS`) |
| 413 | `FILE_TOO_LARGE` |
| 415 | `UNSUPPORTED_MEDIA_TYPE` |
| 422 | `VALIDATION_ERROR` and domain validation (`PAPER_NOT_IN_PROJECT`, …) |
| 429 | `RATE_LIMITED` (with `Retry-After`) |
| 500 | `INTERNAL_ERROR` |
| 502 | `LLM_UNAVAILABLE`, `LLM_INVALID_OUTPUT` |
| 503 | `VECTOR_STORE_UNAVAILABLE`, `MODELS_NOT_READY` |
| 504 | `LLM_TIMEOUT` |

### 1.4 Error code catalog

| Code | HTTP | Where raised | Retryable | Notes |
|---|---|---|---|---|
| `VALIDATION_ERROR` | 422 | any | no | `details.fields[]` = `{loc, msg}` |
| `UNSUPPORTED_MEDIA_TYPE` | 415 | upload | no | not `application/pdf` or magic bytes ≠ `%PDF-` |
| `FILE_TOO_LARGE` | 413 | upload | no | > `MAX_UPLOAD_MB` |
| `DUPLICATE_PAPER` | 409 | upload | no | same `sha256` in same project; `details.existing_paper_id` |
| `PROJECT_PAPER_LIMIT` | 409 | upload | no | > `MAX_PAPERS_PER_PROJECT` |
| `CORRUPTED_PDF` | job error | ingest job | no | PyMuPDF cannot open |
| `EMPTY_PDF` | job error | ingest job | no | 0 pages / no text blocks |
| `SCANNED_PDF_NO_TEXT` | job error | ingest job | no | OCR unsupported (ADR-9) |
| `PDF_TOO_LONG` | job error | ingest job | no | > `MAX_PDF_PAGES` |
| `EMBEDDING_FAILURE` | job error | ingest job | yes | no partial points left |
| `VECTOR_STORE_UNAVAILABLE` | 503 / job error | ingest, search, analyze | yes | |
| `METADATA_MALFORMED` | **warning only** | ingest | — | paper kept with `metadata_confidence` low; appears in `paper.warnings[]` |
| `RETRIEVAL_FAILURE` | 500 / job error | search, analyze | yes | |
| `LLM_TIMEOUT` | 504 / job error | any LLM stage | yes | after `LLM_MAX_RETRIES` |
| `LLM_UNAVAILABLE` | 502 / job error | any LLM stage | yes | provider 5xx/auth/quota |
| `LLM_INVALID_OUTPUT` | 502 / job error | any LLM stage | yes | after 1 repair attempt (07 §4) |
| `MODELS_NOT_READY` | 503 | search, ingest | yes | embedding/reranker still loading |
| `PROJECT_NOT_FOUND` `PAPER_NOT_FOUND` `CHUNK_NOT_FOUND` `GAP_NOT_FOUND` `RUN_NOT_FOUND` `REPORT_NOT_FOUND` `JOB_NOT_FOUND` | 404 | respective GET/POST | no | |
| `PAPER_NOT_IN_PROJECT` | 422 | analyze/search | no | `details.paper_ids[]` |
| `PAPERS_NOT_READY` | 409 | analyze (explicit `paper_ids`) | yes | `details.paper_ids[]` still ingesting/failed |
| `NO_INDEXED_PAPERS` | 409 | analyze/search | no | project has no `INDEXED`/`ANALYZED` papers |
| `RUN_NOT_COMPLETE` | 409 | report | yes | referenced run is not `SUCCEEDED` |
| `ANALYSIS_IN_PROGRESS` | 409 | paper analyze | yes | only when `force_refresh=true` collides with a running job; otherwise requests are de-duplicated (§1.6) |
| `JOB_FAILED` | — | — | — | not an HTTP code; job object `error.code` carries the root cause |
| `RATE_LIMITED` | 429 | any | yes | `Retry-After` header |
| `UNAUTHORIZED` | 401 | any | no | |
| `INTERNAL_ERROR` | 500 | any | maybe | generic; include `request_id` |

**Insufficient evidence is not an error.** Search and analysis return `200`/`SUCCEEDED` with `insufficient_evidence: true` and the exact text from 03 §14.

### 1.5 Long-running operations (jobs)

Ingest and analysis are **jobs** (02 §7). Contract:

1. `POST` returns **202** + `Location: /api/jobs/{job_id}` + body:
   ```json
   { "job_id": "job_8f2e11aa", "job_type": "RESEARCH_ANALYSIS", "status": "QUEUED",
     "run_id": "run_55aa01bc", "poll_url": "/api/jobs/job_8f2e11aa", "deduplicated": false }
   ```
2. Client polls `GET /api/jobs/{job_id}` every **1.5 s** (back off to 5 s after 60 s). Response includes `Retry-After: 2` while `QUEUED|RUNNING`.
3. Job lifecycle: `QUEUED → RUNNING → SUCCEEDED | FAILED | CANCELLED`. `stage` and `progress` (0–1) update as stages complete (stage names in 05 §5.15).
4. `SUCCEEDED` jobs of type `RESEARCH_ANALYSIS`/`GENERATE_REPORT` include `result` (the `ResearchAnalysisResult` of 05 §6, or the report). Large results are also retrievable via `GET /api/runs/{run_id}`.
5. `FAILED` jobs include `error {code,message,details}`. **Partial results:** a run may `SUCCEED` with `warnings[]` when a non-critical stage failed (e.g. `CONTRADICTION_STAGE_FAILED`); the failed stage's list is `[]`.
6. Restart safety: on server start, jobs left `RUNNING` become `FAILED` with code `INTERRUPTED` (02 §7).
7. Typical durations (standard depth, 5 papers, CPU): ingest 30–90 s/paper; research analysis 60–180 s depending on LLM.

### 1.6 De-duplication & caching of analysis requests

- If a job with the same `(project_id, sorted paper_ids, analysis_depth, target, query)` is `QUEUED|RUNNING`, the API returns **202** with the *existing* `job_id` and `deduplicated: true`.
- Completed stages are cached (05: `paper_analyses` unique key; `paper_set_hash`). A new run reusing cached stages reports `stats.cache_hits`. `force_refresh=true` bypasses the **run-level** cache (not the per-paper analysis cache; use `force_reanalyze_papers=true` for that).

### 1.7 Upload limits & validation

| Limit | Default | Env |
|---|---|---|
| Max file size | 25 MB | `MAX_UPLOAD_MB` |
| Files per request | 1 (frontend uploads N files with N requests → per-file progress) | — |
| Allowed type | `application/pdf` **and** first bytes `%PDF-` | — |
| Max pages | 80 | `MAX_PDF_PAGES` |
| Papers per project | 30 | `MAX_PAPERS_PER_PROJECT` |
| Filename | stored only as display metadata; on disk the file is `uploads/{paper_id}.pdf` | — |

Size is enforced while streaming (reject at limit, do not buffer whole body in memory).

## 2. Endpoint inventory

| # | Method & path | Pri | Sync? | Purpose |
|---|---|---|---|---|
| 1 | `GET /api/health` | P0 | sync | Liveness |
| 2 | `GET /api/health/ready` | P0 | sync | Readiness (DB, Qdrant, models) |
| 3 | `POST /api/projects` | P0 | sync 201 | Create project |
| 4 | `GET /api/projects` | P0 | sync | List projects |
| 5 | `GET /api/projects/{project_id}` | P0 | sync | Get project |
| 6 | `DELETE /api/projects/{project_id}` | P1 | sync 204 | Delete project + cascade |
| 7 | **`POST /api/projects/{project_id}/papers/upload`** | P0 | **202** | Upload PDF (canonical) |
| 8 | **`POST /api/papers/upload`** | P0 | **202** | Same, `project_id` as form field (alias) |
| 9 | `GET /api/projects/{project_id}/papers` | P0 | sync | List project papers (frontend) |
| 10 | **`GET /api/papers`** | P0 | sync | List papers (`project_id` filter; alias) |
| 11 | **`GET /api/papers/{paper_id}`** | P0 | sync | Paper + analysis |
| 12 | `DELETE /api/papers/{paper_id}` | P1 | sync 204 | Delete paper + vectors |
| 13 | **`POST /api/papers/{paper_id}/analyze`** | P0 | **202** | Per-paper analysis job |
| 14 | `GET /api/papers/{paper_id}/chunks` | P1 | sync | Chunks (evidence explorer/debug) |
| 15 | `GET /api/papers/{paper_id}/file` | P1 | sync | Original PDF (`#page=N` deep-link) |
| 16 | `GET /api/chunks/{chunk_id}` | P1 | sync | One chunk (+ neighbors) |
| 17 | **`POST /api/search`** | P0 | sync | Hybrid retrieval + grounded answer |
| 18 | **`POST /api/analyze/literature`** | P1 | **202** | Stages 1–5 (matrix, themes, limitations, future work) |
| 19 | **`POST /api/analyze/contradictions`** | P1 | **202** | Stages 1–6 |
| 20 | **`POST /api/analyze/gaps`** | P0 | **202** | Stages 1–8 (adds gaps + validation) |
| 21 | **`POST /api/analyze/report`** | P0 | **202** | Stage 9 on an existing run (or full run) |
| 22 | **`POST /api/research/analyze`** | P0 | **202** | **Main orchestration**, all stages incl. report |
| 23 | `GET /api/jobs/{job_id}` | P0 | sync | Poll job |
| 24 | `POST /api/jobs/{job_id}/cancel` | P2 | sync | Cooperative cancel |
| 25 | `GET /api/projects/{project_id}/runs` | P1 | sync | Run history |
| 26 | `GET /api/runs/{run_id}` | P0 | sync | Full `ResearchAnalysisResult` |
| 27 | `GET /api/projects/{project_id}/gaps` | P0 | sync | Gaps of latest (or given) run |
| 28 | `GET /api/gaps/{gap_id}` | P0 | sync | One gap |
| 29 | `GET /api/projects/{project_id}/contradictions` | P0 | sync | Contradictions of latest run |
| 30 | `GET /api/projects/{project_id}/future-directions` | P1 | sync | Future directions of latest run |
| 31 | `GET /api/projects/{project_id}/landscape` | P2 | sync | Themes/methods/datasets/limitations/directions/matrix of latest run |
| 32 | `GET /api/reports/{report_id}` | P0 | sync | Report JSON (`?format=md` → `text/markdown`) |

The 10 endpoints required by the brief are in **bold**; they are specified in full in §3–§12. The rest are specified compactly in §13.

Routes are thin: validate → call a `services/` function → map to schema (08 §3). Aliases (#8, #10) call the same service function as the canonical route.

## 3. `POST /api/projects/{project_id}/papers/upload` · `POST /api/papers/upload`

**Purpose:** upload one PDF and start the async ingestion job (extract → metadata → sections → chunks → embed → index).
**Request:** `multipart/form-data`
| Field | Type | Req | Notes |
|---|---|---|---|
| `file` | binary | yes | PDF, ≤ `MAX_UPLOAD_MB` |
| `project_id` | string | alias route only | `prj_…` |

**Validation:** project exists; content type + magic bytes; size; project paper cap; `sha256` duplicate check (per project).
**Success:** `202`
```json
{
  "paper": { "paper_id": "pap_91ac27de", "project_id": "prj_3a9f01bc", "title": "rao2023", "authors": [], "year": null,
             "status": "PARSING", "source": { "filename": "rao2023.pdf", "size_bytes": 1843321, "page_count": null } },
  "job_id": "job_1c2d3e4f", "poll_url": "/api/jobs/job_1c2d3e4f"
}
```
(`title` is the filename stem until metadata extraction completes.)
**Errors:** 404 `PROJECT_NOT_FOUND` · 413 `FILE_TOO_LARGE` · 415 `UNSUPPORTED_MEDIA_TYPE` · 409 `DUPLICATE_PAPER` / `PROJECT_PAPER_LIMIT` · 422 `VALIDATION_ERROR` · 429.
**Async failures** (job `FAILED`, `paper.status=FAILED`, `paper.error`): `CORRUPTED_PDF`, `EMPTY_PDF`, `SCANNED_PDF_NO_TEXT`, `PDF_TOO_LONG`, `EMBEDDING_FAILURE`, `VECTOR_STORE_UNAVAILABLE`.
**Side effects:** on success `Paper.status=INDEXED`; if `AUTO_ANALYZE_ON_INGEST=true` (default) a chained `ANALYZE_PAPER` job runs (status `ANALYZING → ANALYZED`).
**Example:**
```bash
curl -X POST http://localhost:8000/api/projects/prj_3a9f01bc/papers/upload -F "file=@rao2023.pdf"
```

## 4. `GET /api/projects/{project_id}/papers` · `GET /api/papers`

**Purpose:** list papers. **Query:** `project_id` (required on `/api/papers`), `status` (repeatable, `PaperStatus`), `q` (title/author substring), `year_from`, `year_to`, `sort` (`created_at|year|title`, default `created_at`), `order`, `limit`, `offset`, `include=analysis` (default off on lists).
**Success:** `200` list envelope of **Paper** (05 §5.2) with extra fields: `warnings: string[]`, `has_analysis: bool`.
**Errors:** 404 `PROJECT_NOT_FOUND`, 422.
```json
{ "items": [ { "paper_id": "pap_91ac27de", "project_id": "prj_3a9f01bc", "title": "Attention-Based Segmentation of Chest X-rays",
  "authors": ["A. Rao","L. Chen"], "year": 2023, "venue": "MICCAI", "doi": "10.1000/xyz123", "status": "ANALYZED",
  "has_analysis": true, "warnings": [], "metadata_confidence": 0.86, "section_detection_quality": "high",
  "source": { "filename": "rao2023.pdf", "size_bytes": 1843321, "page_count": 12 } } ],
  "total": 1, "limit": 50, "offset": 0 }
```

## 5. `GET /api/papers/{paper_id}`

**Purpose:** one paper with its latest `PaperAnalysis` (05 §5.7) when available.
**Query:** `include_evidence=true|false` (default true — analysis `evidence[]` is embedded; set false for a light payload).
**Success:** `200`
```json
{ "paper": { "...": "Paper (05 §5.2)" },
  "analysis": { "analysis_id": "ana_c1d2e3f4", "prompt_version": "paper_analysis@1.0.0", "research_problem": { "text": "…", "evidence_ids": ["evd_a1"], "stated": true }, "...": "PaperAnalysis (05 §5.7)" },
  "analysis_status": "COMPLETED" }
```
`analysis` is `null` while not analyzed; `analysis_status` ∈ `NONE | RUNNING | COMPLETED | FAILED`.
**Errors:** 404 `PAPER_NOT_FOUND`.

## 6. `POST /api/papers/{paper_id}/analyze`

**Purpose:** run (or re-run) Stage 1–2 per-paper analysis for one paper (job type `ANALYZE_PAPER`).
**Request:** `{ "force_refresh": false }` (optional body).
**Behavior:** paper must be `INDEXED` or `ANALYZED`. If a valid cached analysis exists for `(paper_id, prompt_version, llm_model)` and `force_refresh=false` → `202` job that completes immediately with `cache_hit=true`.
**Success:** `202` `JobAccepted` (§1.5).
**Errors:** 404 `PAPER_NOT_FOUND` · 409 `PAPERS_NOT_READY` (not yet indexed / failed) · 409 `ANALYSIS_IN_PROGRESS` (only with `force_refresh`) · 429.
**Job result:** `{ "paper_id": "...", "analysis_id": "...", "cache_hit": false, "validation": { "statements_total": 12, "statements_removed": 1 } }`.

## 7. `POST /api/search`

**Purpose:** research-aware hybrid retrieval over a project; optionally a grounded, cited answer (03 §1, §12–§14). **Synchronous** (typically 1–4 s retrieval, +2–8 s when `generate_answer=true`).
**Request:**
```json
{ "project_id": "prj_3a9f01bc", "query": "What limitations exist in current research?",
  "paper_ids": [], "chunk_types": null, "top_k": 10, "generate_answer": true,
  "include_text": true, "debug": false }
```
| Field | Rules |
|---|---|
| `project_id` | required, exists |
| `query` | required, 3–1000 chars after trim |
| `paper_ids` | optional ≤ 50; all must belong to project else 422 `PAPER_NOT_IN_PROJECT` |
| `chunk_types` | optional hard filter, `ChunkType[]` (section *prior* is automatic and soft) |
| `top_k` | 1–20, default `RERANK_TOP_K` |
| `generate_answer` | default true; false = retrieval only (no LLM) |
| `debug` | include score breakdown + timings (dev only; ignored in `ENVIRONMENT=production` unless `ALLOW_DEBUG_RESPONSES=true`) |

**Success:** `200` (answer shape = 03 §13; `Source` = 05 §5.6)
```json
{
  "query": "What limitations exist in current research?",
  "insufficient_evidence": false, "message": null,
  "intent": ["LIMITATIONS"],
  "answer": "Several papers report evaluation on a single hospital dataset [1][2].",
  "segments": [ { "text": "Several papers report evaluation on a single hospital dataset", "source_ids": [1,2], "partially_supported": false } ],
  "sources": [ { "source_id": 1, "paper_id": "pap_91ac27de", "paper_title": "Attention-Based Segmentation of Chest X-rays",
                 "authors": ["A. Rao","L. Chen"], "year": 2023, "page": 9, "section": "LIMITATION", "section_heading": "5.2 Limitations",
                 "chunk_id": "chk_pap_91ac27de_0014", "text": "Our evaluation is restricted to a single hospital dataset …", "score": 0.81 } ],
  "stats": { "latency_ms": 2140, "llm_calls": 2, "retrieval_ms": 610, "rerank_ms": 1430 },
  "debug": null
}
```
**Insufficient evidence (200):**
```json
{ "query": "Who won the 2022 World Cup?", "insufficient_evidence": true,
  "message": "Insufficient evidence. The uploaded research collection does not contain enough relevant evidence to answer this question.",
  "intent": ["GENERAL"], "answer": null, "segments": [], "sources": [], "stats": { "latency_ms": 780, "llm_calls": 0 } }
```
When `generate_answer=false`, `answer`/`segments` are `null` and `sources` are the selected evidence.
**Errors:** 404 `PROJECT_NOT_FOUND` · 409 `NO_INDEXED_PAPERS` · 422 · 503 `MODELS_NOT_READY`/`VECTOR_STORE_UNAVAILABLE` · 502/504 LLM codes (only when `generate_answer=true`; retrieval results are still returned with `warnings:["ANSWER_GENERATION_FAILED"]` and `answer:null` — graceful degradation) · 429.

## 8. `POST /api/research/analyze` — main orchestration

**Purpose:** run the full pipeline (03/04): per-paper analysis → synthesis → themes → limitations/future work → contradictions → gaps → validation → report. Async job. Frontend's primary "Run analysis" action.
**Request:**
```json
{ "project_id": "prj_3a9f01bc", "query": "What gaps exist in transformer-based chest X-ray segmentation?",
  "paper_ids": [], "analysis_depth": "standard", "force_refresh": false, "force_reanalyze_papers": false }
```
| Field | Rules |
|---|---|
| `project_id` | **required** (the brief's body omitted it; needed because `paper_ids: []` means "all indexed papers in the project" — see Errata, 10) |
| `query` | optional, 3–1000 chars. If omitted/blank → generic "identify research gaps" focus and the relevance gate is skipped. If given → gate (03 §11) runs first; failing it returns `insufficient_evidence=true` **without any LLM stage**. The query *focuses* prompts and the report; it is never evidence. |
| `paper_ids` | `[]` = all papers with status `INDEXED|ANALYZED`; else ⊆ project, all ready |
| `analysis_depth` | `quick` \| `standard` (default) \| `deep` (02 §5) |
| `force_refresh`, `force_reanalyze_papers` | default false |

Scope rules: papers not ready are excluded and listed in `warnings` (`PAPERS_EXCLUDED_NOT_READY`) when `paper_ids=[]`; explicit non-ready ids → 409. `< 2` papers in scope → run continues with EXPLICIT-only gaps and `warnings:["SYNTHESIS_REQUIRES_MULTIPLE_PAPERS"]` (04 §15).
**Success:** `202` `JobAccepted` (`job_type: RESEARCH_ANALYSIS`, includes `run_id`).
**Final `job.result` / `GET /api/runs/{run_id}`** = `ResearchAnalysisResult` (05 §6):
```json
{
  "run_id": "run_55aa01bc", "project_id": "prj_3a9f01bc",
  "query": "What gaps exist in transformer-based chest X-ray segmentation?",
  "analysis_depth": "standard", "papers_analyzed": 5, "papers_failed": [],
  "insufficient_evidence": false, "insufficient_evidence_message": null,
  "themes": [ { "theme_id": "thm_01", "name": "Transformer-based segmentation", "description": "…", "paper_ids": ["pap_A","pap_B"], "evidence": [] } ],
  "methodologies": [ { "name": "CNN", "frequency": 3, "paper_ids": ["pap_A","pap_B","pap_C"], "evidence": [] } ],
  "datasets": [ { "name": "CXR-8", "frequency": 2, "paper_ids": ["pap_A","pap_C"], "evidence": [] } ],
  "evidence_matrix": [],
  "limitations": [ { "limitation_type": "SINGLE_DOMAIN", "title": "Single-domain evaluation", "frequency": 3, "paper_ids": [], "evidence": [], "rank": 1 } ],
  "contradictions": [],
  "research_gaps": [ { "gap_id": "gap_7f3a1c20", "title": "Cross-domain generalization is not evaluated", "category": "GENERALIZATION", "gap_type": "SYNTHESIZED",
                       "confidence": 0.68, "confidence_label": "medium", "evidence_strength": "MODERATE", "evidence": [], "affected_papers": [] } ],
  "future_directions": [],
  "sources": [ { "source_id": 1, "paper_id": "pap_A", "page": 9, "section": "LIMITATION", "chunk_id": "chk_pap_A_0014", "text": "…", "score": 0.81 } ],
  "report_id": "rep_12ab34cd", "warnings": [],
  "stats": { "llm_calls": 14, "tokens_in": 52000, "tokens_out": 9000, "latency_ms": 74000, "cache_hits": 5 }
}
```
(Arrays abbreviated; full element schemas are 05 §5.9–§5.13.) Every `evidence[]` entry also carries `source_id` mapping into `sources[]` (05 §6).
**Errors:** 404 `PROJECT_NOT_FOUND` · 409 `NO_INDEXED_PAPERS` / `PAPERS_NOT_READY` · 422 `VALIDATION_ERROR` / `PAPER_NOT_IN_PROJECT` · 429. Runtime failures appear on the job (`LLM_*`, `VECTOR_STORE_UNAVAILABLE`).
**Example:**
```bash
curl -X POST http://localhost:8000/api/research/analyze -H 'Content-Type: application/json' \
  -d '{"project_id":"prj_3a9f01bc","query":"What limitations exist?","paper_ids":[],"analysis_depth":"standard"}'
```

## 9. Stage endpoints — `POST /api/analyze/{literature|contradictions|gaps|report}`

Partial-pipeline views over the **same** run machinery (same table `research_runs`, same stage caches). Body = `AnalysisRequest` (identical to §8). They set `research_runs.target` (see §14 addenda).

| Endpoint | `target` | Stages executed (05 §5.15 names) | Returns in `job.result` |
|---|---|---|---|
| `/api/analyze/literature` | `LITERATURE` | `PAPER_ANALYSIS, SYNTHESIS, THEMES, LIMITATIONS_FUTURE` | themes, methodologies, datasets, evidence_matrix, limitations, future_directions, sources |
| `/api/analyze/contradictions` | `CONTRADICTIONS` | + `CONTRADICTION_DETECTION` | above + contradictions |
| `/api/analyze/gaps` | `GAPS` | + `GAP_DETECTION, VALIDATION` | above + research_gaps |
| `/api/analyze/report` | `REPORT` | `REPORT` on an existing run | `{report_id, run_id, report}` |
| `/api/research/analyze` | `FULL` | all | full `ResearchAnalysisResult` |

All return `202 JobAccepted` and share §8 validation, query/gate behavior, errors, de-duplication.

**`/api/analyze/report` body:** `{ "run_id": "run_55aa01bc" }` **or** a full `AnalysisRequest` (then a `FULL` run is executed). With `run_id`: run must be `SUCCEEDED` else `409 RUN_NOT_COMPLETE` (`404 RUN_NOT_FOUND` if unknown). Report is generated **only from validated objects** (05 §5.14), job type `GENERATE_REPORT`. Optional `sections: ["landscape","methods","datasets","limitations","future_work","contradictions","gaps"]` filters report sections (maps to the existing ReportsPage checkboxes; `topics`↔`landscape`).
**Success result:** `{ "report_id": "rep_12ab34cd", "run_id": "…", "report": { …ResearchReport (05 §5.14)… } }`.

## 10. `GET /api/jobs/{job_id}`

**Success:** `200` Job (05 §5.15)
```json
{ "job_id": "job_8f2e11aa", "job_type": "RESEARCH_ANALYSIS", "status": "RUNNING", "stage": "CONTRADICTION_DETECTION",
  "progress": 0.62, "project_id": "prj_3a9f01bc", "paper_id": null, "run_id": "run_55aa01bc",
  "error": null, "result": null, "created_at": "…", "started_at": "…", "finished_at": null }
```
Failed example: `"status":"FAILED","error":{"code":"LLM_TIMEOUT","message":"The language model did not respond in time.","details":{"stage":"GAP_DETECTION"}}`.
**Errors:** 404 `JOB_NOT_FOUND`.

## 11. Run & result reads

- `GET /api/runs/{run_id}` → `ResearchAnalysisResult` (05 §6) `200`; 404 `RUN_NOT_FOUND`; if run not finished → `200` with `status` field `RUNNING` and partial arrays omitted (use job polling instead).
- `GET /api/projects/{project_id}/runs` → list envelope of `{run_id, query, analysis_depth, target, status, papers_analyzed, gap_count, created_at, finished_at}`.
- `GET /api/projects/{project_id}/gaps` — query: `run_id` (default latest `SUCCEEDED` run with gaps), `category`, `gap_type`, `min_confidence` (0–1), `sort` (`confidence|n_papers|created_at`, default `confidence`), paging. Returns envelope of **ResearchGap** (05 §5.9) incl. `confidence_breakdown` (§14). Empty list when no completed run exists (not an error) — the UI shows its empty state with a *Run analysis* action.
- `GET /api/gaps/{gap_id}` → single ResearchGap `200`; 404 `GAP_NOT_FOUND`.
- `GET /api/projects/{project_id}/contradictions` → envelope of **Contradiction** (05 §5.10).
- `GET /api/projects/{project_id}/future-directions` → envelope of **FutureDirection** (05 §5.11).
- `GET /api/projects/{project_id}/landscape` (P2) → `{ run_id, themes, methodologies, datasets, limitations, future_directions, evidence_matrix, year_distribution }`.
- `GET /api/reports/{report_id}` → ResearchReport (05 §5.14); `?format=md` → `text/markdown` body (`Content-Disposition: attachment; filename="research-report-<report_id>.md"`). The server does **not** render HTML/PDF in MVP; the frontend may convert Markdown→HTML client-side.

## 12. Papers' chunk & file endpoints (evidence explorer)

- `GET /api/papers/{paper_id}/chunks` — query `chunk_type`, `page`, paging → envelope of Chunk (05 §5.3). Excludes `REFERENCES`.
- `GET /api/chunks/{chunk_id}?neighbors=1` → `{ "chunk": Chunk, "prev": Chunk|null, "next": Chunk|null, "paper": {paper_id,title,authors,year,page_count} }`. Used to open a citation in context.
- `GET /api/papers/{paper_id}/file` → `application/pdf`, `Content-Disposition: inline`. Frontend deep-links `…/file#page={page}`. File served only from `DATA_DIR/uploads/{paper_id}.pdf` (no user-supplied path ever touches the filesystem).

## 13. Compact specs for remaining endpoints

| Endpoint | Request | Success | Errors |
|---|---|---|---|
| `GET /api/health` | — | `200 {"status":"ok","version":"0.1.0"}` | — |
| `GET /api/health/ready` | — | `200 {"status":"ready","checks":{"database":"ok","vector_store":"ok","embedding_model":"loaded","reranker":"loaded|disabled","llm":"configured"}}`; `503` same shape with failing checks | — |
| `POST /api/projects` | `{"name": "1–120 chars", "description": "≤ 2000, optional"}` | `201` Project (05 §5.1 + §14 additions) | 422 |
| `GET /api/projects` | `q`, `sort` (`updated_at|name`), paging | `200` envelope of Project | — |
| `GET /api/projects/{id}` | — | `200` Project | 404 |
| `DELETE /api/projects/{id}` | — | `204` (cascade: papers, chunks, analyses, runs, evidence, Qdrant points, uploaded files, BM25 cache) | 404, 409 `ANALYSIS_IN_PROGRESS` if jobs running |
| `DELETE /api/papers/{id}` | — | `204` | 404 |
| `POST /api/jobs/{id}/cancel` (P2) | — | `200` Job (`CANCELLED` at next stage boundary) | 404, 409 if finished |

Project example:
```json
{ "project_id": "prj_3a9f01bc", "name": "Transformers for Medical Imaging", "description": "…",
  "paper_count": 6, "indexed_paper_count": 6, "analyzed_paper_count": 5,
  "status": "ANALYZED", "gap_count": 7, "topic_count": 4,
  "created_at": "2026-10-01T09:30:00Z", "updated_at": "2026-10-01T10:02:11Z" }
```
`status` ∈ `EMPTY | PROCESSING | ANALYZED | ERROR` (derived: any paper in a non-terminal state or running job → `PROCESSING`; any `FAILED` paper and none usable → `ERROR`; latest run `SUCCEEDED` → `ANALYZED`).

## 14. Data-model addenda introduced here (must be back-ported to `05`)

`05` is the source of truth and was **not** edited. These additive, backward-compatible changes are required by the API/frontend mapping and must be applied to `05` (and tracked in `10` Appendix A) when implementation starts:

1. **Project** gains derived fields `status`, `gap_count`, `topic_count` (computed, not stored; counts from the latest `SUCCEEDED` run).
2. **`research_runs`** gains column `target` (`LITERATURE|CONTRADICTIONS|GAPS|REPORT|FULL`, default `FULL`).
3. **ResearchGap** gains `confidence_breakdown` (computed in `validation/scoring.py` from the same inputs as the confidence formula, all 0–1):
   ```json
   "confidence_breakdown": { "evidence_frequency": 0.67, "future_work_support": 0.50, "limitation_support": 0.75, "retrieval_strength": 0.81 }
   ```
   Definitions: `evidence_frequency = min(1, n_papers/3)`; `future_work_support` = share of surviving evidence whose chunk has `chunk_type=FUTURE_WORK` or `has_future_cue`; `limitation_support` = share with `chunk_type=LIMITATION` or `has_limitation_cue`; `retrieval_strength` = mean rerank score (0.5 if reranker disabled). These are **display decompositions**; `confidence` remains the 04 §8 formula. `llm_confidence_raw` is stored in the payload JSON but never returned.
4. **Source/Evidence `section`** is the `ChunkType` enum value (05 is authoritative; 03 §13's example `"Methodology"` is illustrative). Human label = `section_heading` when present.
5. **Paper** list/detail adds `warnings: string[]`, `has_analysis`, `analysis_status` (derived).
6. **Job** may carry `cache_hit`/`deduplicated` hints in `result` only; no schema change.

## 15. Frontend integration examples (conceptual)

```ts
// src/services/realApi.ts (target shape — see 14 for the full mapper set)
const apiClient = axios.create({ baseURL: `${import.meta.env.VITE_API_BASE_URL}/api` });

startAnalysis: async (projectId: string, query?: string) => {
  const { data } = await apiClient.post('/research/analyze',
    { project_id: projectId, query, paper_ids: [], analysis_depth: 'standard' });
  return data.job_id as string;
},
pollJob: async (jobId: string) => (await apiClient.get(`/jobs/${jobId}`)).data,
```
Polling uses React Query `refetchInterval: (q) => ['QUEUED','RUNNING'].includes(q.state.data?.status) ? 1500 : false`.
