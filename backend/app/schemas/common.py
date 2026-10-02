"""
Schemas — common types, enums, and base models.
05 §2 enums, 06 §1.1 list envelope, 06 §1.2 error envelope.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Enums — 05 §2
# ============================================================

class ChunkType(str, Enum):
    """Canonical academic section types (03 §3)."""
    ABSTRACT = "ABSTRACT"
    INTRODUCTION = "INTRODUCTION"
    RELATED_WORK = "RELATED_WORK"
    METHODOLOGY = "METHODOLOGY"
    DATASET = "DATASET"
    RESULTS = "RESULTS"
    DISCUSSION = "DISCUSSION"
    LIMITATION = "LIMITATION"
    CONCLUSION = "CONCLUSION"
    FUTURE_WORK = "FUTURE_WORK"
    REFERENCES = "REFERENCES"
    OTHER = "OTHER"


class PaperStatus(str, Enum):
    """Paper lifecycle states (05 §2)."""
    UPLOADED = "UPLOADED"
    PARSING = "PARSING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    INDEXED = "INDEXED"
    ANALYZING = "ANALYZING"
    ANALYZED = "ANALYZED"
    FAILED = "FAILED"


class JobStatus(str, Enum):
    """Job lifecycle states (05 §2)."""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class JobType(str, Enum):
    """Types of async jobs (05 §2)."""
    INGEST_PAPER = "INGEST_PAPER"
    ANALYZE_PAPER = "ANALYZE_PAPER"
    RESEARCH_ANALYSIS = "RESEARCH_ANALYSIS"
    GENERATE_REPORT = "GENERATE_REPORT"


class GapCategory(str, Enum):
    """Research gap categories — 04 §4."""
    METHODOLOGICAL = "METHODOLOGICAL"
    DATASET = "DATASET"
    EVALUATION = "EVALUATION"
    APPLICATION = "APPLICATION"
    THEORETICAL = "THEORETICAL"
    TEMPORAL = "TEMPORAL"
    CONTRADICTION = "CONTRADICTION"
    REPRODUCIBILITY = "REPRODUCIBILITY"
    GENERALIZATION = "GENERALIZATION"
    INTERDISCIPLINARY = "INTERDISCIPLINARY"


class GapType(str, Enum):
    """Whether a gap is stated by papers or inferred (04 §5)."""
    EXPLICIT = "EXPLICIT"
    SYNTHESIZED = "SYNTHESIZED"


class EvidenceStrength(str, Enum):
    """Evidence strength levels — 04 §8."""
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    INSUFFICIENT = "INSUFFICIENT"


class ConfidenceLabel(str, Enum):
    """Human-readable confidence label — 04 §8."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Entailment(str, Enum):
    """Entailment verdict — 07 P13."""
    SUPPORTS = "SUPPORTS"
    PARTIAL = "PARTIAL"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    NOT_CHECKED = "NOT_CHECKED"


class AnalysisDepth(str, Enum):
    """Analysis thoroughness levels — 02 §5."""
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class Polarity(str, Enum):
    """Finding polarity — 07 P05."""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"


class ReasonType(str, Enum):
    """Contradiction reason types — 04 §9."""
    DIFFERENT_DATASET = "DIFFERENT_DATASET"
    DIFFERENT_METRIC = "DIFFERENT_METRIC"
    DIFFERENT_SETUP = "DIFFERENT_SETUP"
    DIFFERENT_SAMPLE_SIZE = "DIFFERENT_SAMPLE_SIZE"
    DIFFERENT_PREPROCESSING = "DIFFERENT_PREPROCESSING"
    DIFFERENT_BASELINE = "DIFFERENT_BASELINE"
    DIFFERENT_DOMAIN = "DIFFERENT_DOMAIN"
    DIFFERENT_DEFINITION = "DIFFERENT_DEFINITION"
    UNKNOWN = "UNKNOWN"


class FutureClass(str, Enum):
    """Future direction classification — 04 §10."""
    REPEATED = "REPEATED"
    UNIQUE = "UNIQUE"


class LimitationType(str, Enum):
    """Limitation category — 04 §11."""
    SMALL_DATASET = "SMALL_DATASET"
    SINGLE_DOMAIN = "SINGLE_DOMAIN"
    COMPUTE_COST = "COMPUTE_COST"
    BASELINE_COVERAGE = "BASELINE_COVERAGE"
    GENERALIZATION = "GENERALIZATION"
    INTERPRETABILITY = "INTERPRETABILITY"
    REPRODUCIBILITY = "REPRODUCIBILITY"
    DATA_QUALITY = "DATA_QUALITY"
    METRIC_VALIDITY = "METRIC_VALIDITY"
    OTHER = "OTHER"


class EvidenceRole(str, Enum):
    """Evidence role in a gap/contradiction/answer — 05 §5.5."""
    SUPPORTS_GAP = "SUPPORTS_GAP"
    CONTEXT = "CONTEXT"
    CLAIM_A = "CLAIM_A"
    CLAIM_B = "CLAIM_B"
    STATEMENT = "STATEMENT"


class OwnerType(str, Enum):
    """What entity owns an evidence row — 05 §4."""
    ANALYSIS = "ANALYSIS"
    GAP = "GAP"
    CONTRADICTION = "CONTRADICTION"
    FUTURE = "FUTURE"
    REPORT = "REPORT"
    ANSWER = "ANSWER"


class RunTarget(str, Enum):
    """Pipeline target — 06 §14.2."""
    LITERATURE = "LITERATURE"
    CONTRADICTIONS = "CONTRADICTIONS"
    GAPS = "GAPS"
    REPORT = "REPORT"
    FULL = "FULL"


class ProjectStatus(str, Enum):
    """Derived project status — 06 §13."""
    EMPTY = "EMPTY"
    PROCESSING = "PROCESSING"
    ANALYZED = "ANALYZED"
    ERROR = "ERROR"


# ============================================================
# Base response models — 06 §1
# ============================================================

T = TypeVar("T")


class ListEnvelope(BaseModel, Generic[T]):
    """Standard list response envelope — 06 §1.1."""
    items: list[T]
    total: int
    limit: int
    offset: int


class ErrorDetail(BaseModel):
    """Structured error response — 06 §1.2."""
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None = None


class ErrorEnvelope(BaseModel):
    """Error wrapper — 06 §1.2."""
    error: ErrorDetail


class TimestampMixin(BaseModel):
    """Common timestamp fields."""
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime | None = None
