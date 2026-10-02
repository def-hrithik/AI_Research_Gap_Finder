"""
Application settings — 08 §9.
Pydantic-settings with startup validation. Fail-fast with readable messages.
"""

from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All env-configurable settings from 08 §9.1.

    Loaded from process env + .env file. Startup validation fails fast
    with a readable message listing every problem.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    environment: str = "development"
    log_level: str = "INFO"
    log_format: str = "console"
    data_dir: str = "./data"
    database_url: str = "sqlite:///./data/rgf.db"

    # --- CORS ---
    cors_origins: str = "http://localhost:5173"
    cors_origin_regex: str = ""
    frontend_url: str = ""
    backend_url: str = ""

    # --- Auth ---
    api_key: str = ""
    allow_debug_responses: bool = False

    # --- Upload limits ---
    max_upload_mb: int = 25
    max_pdf_pages: int = 80
    max_papers_per_project: int = 30
    min_chars_per_page: int = 200

    # --- Rate limiting ---
    rate_limit_enabled: bool = True
    rate_limit_default: str = "120/minute"
    rate_limit_upload: str = "10/minute"
    rate_limit_search: str = "20/minute"
    rate_limit_analyze: str = "5/minute"

    # --- Jobs ---
    analysis_max_concurrency: int = 2
    auto_analyze_on_ingest: bool = True

    # --- LLM ---
    llm_provider: str = "openai_compatible"
    llm_api_key: str = ""
    llm_model: str = ""
    llm_base_url: str = ""
    llm_timeout_s: int = 60
    llm_max_retries: int = 2
    llm_max_concurrency: int = 4

    # --- Embeddings ---
    embedding_model: str = "BAAI/bge-m3"
    embedding_dim: int = 1024
    embedding_batch_size: int = 16
    embedding_device: str = "auto"
    embedding_lazy_load: bool = False
    embedding_max_tokens: int = 1024
    hf_home: str = "./data/hf"

    # --- Reranker ---
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_enabled: bool = True
    rerank_batch_size: int = 16
    rerank_max_length: int = 512
    rerank_candidates: int = 50
    rerank_top_k: int = 10
    rerank_min_score: float = 0.20
    rerank_weight: float = 0.85
    prior_weight: float = 0.15

    # --- Retrieval ---
    retrieval_dense_top_k: int = 40
    retrieval_bm25_top_k: int = 40
    rrf_k: int = 60
    section_boost_enabled: bool = True
    query_rewrite_mode: str = "rules"
    bm25_cache_projects: int = 8
    min_evidence_chunks: int = 2
    max_chunks_per_paper: int = 3
    context_max_tokens: int = 6000
    paper_context_max_tokens: int = 8000

    # --- Chunking ---
    chunk_target_tokens: int = 350
    chunk_max_tokens: int = 600
    chunk_min_tokens: int = 60
    chunk_overlap_sentences: int = 2

    # --- Qdrant ---
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_local_path: str = ""
    qdrant_collection: str = "rgf_chunks"
    qdrant_upsert_batch: int = 128

    # --- Analysis ---
    contradiction_max_pairs: int = 8
    future_cluster_distance: float = 0.25
    gap_max_per_category: int = 3
    gap_max_total: int = 15
    gap_w_papers: float = 0.35
    gap_w_entail: float = 0.25
    gap_w_verified: float = 0.10
    gap_w_retrieval: float = 0.15
    gap_w_type: float = 0.15
    gap_cap_explicit: float = 0.90
    gap_cap_explicit_single: float = 0.60
    gap_cap_synth_presence: float = 0.85
    gap_cap_synth_absence: float = 0.65
    gap_type_factor_synth_presence: float = 0.6
    gap_type_factor_synth_absence: float = 0.4
    absence_refute_min_score: float = 0.5

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        if self.frontend_url and self.frontend_url not in origins:
            origins.append(self.frontend_url)
        return origins

    @property
    def data_path(self) -> Path:
        return Path(self.data_dir)

    @property
    def uploads_path(self) -> Path:
        return self.data_path / "uploads"

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "test", "production"}
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}, got '{v}'")
        return v

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        allowed = {"openai_compatible", "anthropic", "fake"}
        if v not in allowed:
            raise ValueError(f"LLM_PROVIDER must be one of {allowed}, got '{v}'")
        return v

    @field_validator("query_rewrite_mode")
    @classmethod
    def validate_rewrite_mode(cls, v: str) -> str:
        allowed = {"off", "rules", "llm"}
        if v not in allowed:
            raise ValueError(f"QUERY_REWRITE_MODE must be one of {allowed}, got '{v}'")
        return v

    @model_validator(mode="after")
    def validate_startup(self) -> "Settings":
        """Startup validation rules — 08 §9.2. Fail fast with readable messages."""
        errors: list[str] = []

        # Exactly one of QDRANT_URL / QDRANT_LOCAL_PATH
        has_url = bool(self.qdrant_url)
        has_local = bool(self.qdrant_local_path)
        if has_url == has_local:
            errors.append(
                "Exactly one of QDRANT_URL or QDRANT_LOCAL_PATH must be set "
                f"(got url={'set' if has_url else 'empty'}, local={'set' if has_local else 'empty'})"
            )

        # LLM key + model required unless fake
        if self.llm_provider != "fake":
            if not self.llm_api_key:
                errors.append(f"LLM_API_KEY is required when LLM_PROVIDER={self.llm_provider}")
            if not self.llm_model:
                errors.append(f"LLM_MODEL is required when LLM_PROVIDER={self.llm_provider}")

        # Weight sums
        rerank_sum = round(self.rerank_weight + self.prior_weight, 4)
        if rerank_sum != 1.0:
            errors.append(
                f"RERANK_WEIGHT + PRIOR_WEIGHT must equal 1.0 (got {rerank_sum})"
            )

        gap_sum = round(
            self.gap_w_papers + self.gap_w_entail + self.gap_w_verified
            + self.gap_w_retrieval + self.gap_w_type,
            4,
        )
        if gap_sum != 1.0:
            errors.append(f"GAP_W_* weights must sum to 1.0 (got {gap_sum})")

        # Chunk ordering
        if not (self.chunk_min_tokens < self.chunk_target_tokens < self.chunk_max_tokens):
            errors.append(
                f"CHUNK_MIN ({self.chunk_min_tokens}) < CHUNK_TARGET ({self.chunk_target_tokens}) "
                f"< CHUNK_MAX ({self.chunk_max_tokens}) required"
            )

        if errors:
            msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(msg)

        return self


def get_settings() -> Settings:
    """Create and validate settings. Called once at startup."""
    return Settings()
