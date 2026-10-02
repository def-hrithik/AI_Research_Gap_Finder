"""
Pydantic schemas for LLM structured outputs — 07 §2, 07 §5.
Enforces strict typing, field length caps, and enum validation.
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class FieldConfidence(BaseModel):
    title: float = 0.0
    authors: float = 0.0
    year: float = 0.0
    venue: float = 0.0
    doi: float = 0.0
    abstract: float = 0.0


class MetadataOut(BaseModel):
    """P01 — metadata_extraction@1.0.0 output schema."""
    title: str | None = None
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    abstract: str | None = None
    domain: str | None = None
    field_confidence: FieldConfidence = Field(default_factory=FieldConfidence)


class QuoteItem(BaseModel):
    chunk_id: str
    quote: str


class StatementOut(BaseModel):
    text: str
    quotes: list[QuoteItem] = Field(default_factory=list)
    stated: bool = True


class FindingStatementOut(StatementOut):
    polarity: str = "POSITIVE"
    subject: str | None = None
    metric: str | None = None
    dataset: str | None = None


class LimitationStatementOut(StatementOut):
    limitation_type: str = "OTHER"


class PaperAnalysisOut(BaseModel):
    """P02 — paper_analysis@1.0.0 output schema."""
    research_problem: StatementOut
    research_objectives: list[StatementOut] = Field(default_factory=list)
    methodology: StatementOut
    dataset: StatementOut
    experimental_setup: StatementOut
    contributions: list[StatementOut] = Field(default_factory=list)
    key_findings: list[FindingStatementOut] = Field(default_factory=list)
    limitations: list[LimitationStatementOut] = Field(default_factory=list)
    future_work: list[StatementOut] = Field(default_factory=list)
    unresolved_questions: list[StatementOut] = Field(default_factory=list)
    domain: str | None = None


class ThemeOut(BaseModel):
    theme_id: str
    name: str
    description: str
    paper_ids: list[str] = Field(default_factory=list)
    chunk_ids: list[str] = Field(default_factory=list)


class ThemesOut(BaseModel):
    """P10 — theme_detection@1.0.0 output schema."""
    themes: list[ThemeOut] = Field(default_factory=list)


class ContradictionReason(BaseModel):
    reason_type: str
    explanation: str
    basis: str = "HYPOTHESIS"  # STATED_IN_PAPERS | HYPOTHESIS


class ClaimSide(BaseModel):
    text: str
    paper_id: str
    chunk_id: str
    quote: str
    polarity: str
    metric: str | None = None
    dataset: str | None = None


class ContradictionItemOut(BaseModel):
    topic: str
    claim_a: ClaimSide
    claim_b: ClaimSide
    comparable: bool = True
    possible_reasons: list[ContradictionReason] = Field(default_factory=list)


class ContradictionsOut(BaseModel):
    """P11 — contradiction_detection@1.0.0 output schema."""
    contradictions: list[ContradictionItemOut] = Field(default_factory=list)


class GapCandidateOut(BaseModel):
    title: str
    category: str
    gap_type: str  # EXPLICIT | SYNTHESIZED
    description: str
    affected_papers: list[str] = Field(default_factory=list)
    supporting_chunk_ids: list[str] = Field(default_factory=list)
    supporting_quotes: list[str] = Field(default_factory=list)
    why_gap_exists: str
    potential_research_direction: str
    suggested_research_questions: list[str] = Field(default_factory=list)
    methodology_suggestion: str


class GapCandidatesOut(BaseModel):
    """P12 — research_gap_detection@1.0.0 output schema."""
    gaps: list[GapCandidateOut] = Field(default_factory=list)


class EntailmentVerdict(BaseModel):
    claim_id: str
    verdict: str  # SUPPORTS | PARTIAL | NOT_SUPPORTED
    reasoning: str = ""


class EntailmentOut(BaseModel):
    """P13/P14 entailment output schema."""
    verdicts: list[EntailmentVerdict] = Field(default_factory=list)


class AnswerOut(BaseModel):
    """P18 — grounded_answer@1.0.0 output schema."""
    answer: str
    cited_sources: list[int] = Field(default_factory=list)
    insufficient_evidence: bool = False
