"""
Pydantic schema for the simplified LLM paper analysis output.
Used by analyze_paper_with_llm to validate Gemini's JSON response.
"""

from pydantic import BaseModel, Field


class PaperAnalysisLLMOut(BaseModel):
    """Simplified paper analysis schema that the LLM returns."""
    problem: str = ""
    methodology: str = ""
    models: list[str] = Field(default_factory=list)
    dataset: list[str] = Field(default_factory=list)
    findings: str = ""
    limitations: list[str] = Field(default_factory=list)
    futureWork: list[str] = Field(default_factory=list)
