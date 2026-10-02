"""
Search service — 03 §12–14, 06 §8.
Coordinates hybrid retrieval, LLM grounded answer generation,
and citation validation.
"""

import logging
from sqlalchemy.orm import Session

from app.core.constants import INSUFFICIENT_EVIDENCE_MESSAGE
from app.llm.client import get_llm_client
from app.retrieval.hybrid import get_retriever
from app.schemas.llm_out import AnswerOut
from app.schemas.retrieval import SearchFilters, SearchResponse, SourceItem

logger = logging.getLogger("rgf.services.search")

# System prompt for grounded answer generation (07 §5 P18)
GROUNDED_ANSWER_SYSTEM_PROMPT = """
You are a precise, evidence-grounded academic assistant.
Answer the user's question using ONLY the provided numbered sources.
Every factual claim must cite its source using bracket notation like [1] or [2].
If the sources do not contain enough evidence, state:
"Insufficient evidence. The uploaded research collection does not contain enough relevant evidence to answer this question."
Output a JSON object with:
{ "answer": str, "cited_sources": [int], "insufficient_evidence": bool }
"""


async def execute_search(
    project_id: str,
    query: str,
    db: Session,
    filters: SearchFilters | None = None,
    generate_answer: bool = True,
    top_k: int = 10,
) -> SearchResponse:
    """Execute hybrid search and optional LLM answer generation."""
    retriever = get_retriever()

    # 1. Hybrid retrieval pipeline
    sources, insufficient_evidence, intent, stats = retriever.retrieve(
        project_id=project_id,
        query=query,
        db=db,
        filters=filters,
        top_k=top_k,
    )

    if insufficient_evidence or not sources:
        return SearchResponse(
            query=query,
            intent=intent,
            answer=INSUFFICIENT_EVIDENCE_MESSAGE,
            sources=[],
            insufficient_evidence=True,
            stats=stats,
        )

    # 2. Answer generation pass
    if not generate_answer:
        return SearchResponse(
            query=query,
            intent=intent,
            answer="",
            sources=sources,
            insufficient_evidence=False,
            stats=stats,
        )

    # Construct context from sources
    context_blocks: list[str] = []
    for s in sources:
        context_blocks.append(
            f"[{s.source_id}] {s.paper_title} (Page {s.page}, {s.section_heading or s.section}):\n{s.text}"
        )

    user_prompt = f"Question: {query}\n\nSOURCES:\n" + "\n\n".join(context_blocks)

    llm = get_llm_client()
    try:
        ans_out, llm_res = await llm.complete_json(
            system_prompt=GROUNDED_ANSWER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema=AnswerOut,
            temperature=0.0,
            max_tokens=1200,
        )
        answer_text = ans_out.answer
        if ans_out.insufficient_evidence:
            return SearchResponse(
                query=query,
                intent=intent,
                answer=INSUFFICIENT_EVIDENCE_MESSAGE,
                sources=[],
                insufficient_evidence=True,
                stats=stats,
            )
    except Exception as exc:
        logger.warning("LLM answer generation failed (%s); returning synthesized summary", exc)
        # Fallback to extractive summary from top sources
        top_snippets = [f"{s.paper_title} ({s.section}): {s.text[:150]}... [{s.source_id}]" for s in sources[:3]]
        answer_text = "Key findings from relevant papers:\n\n" + "\n\n".join(top_snippets)

    return SearchResponse(
        query=query,
        intent=intent,
        answer=answer_text,
        sources=sources,
        insufficient_evidence=False,
        stats=stats,
    )
