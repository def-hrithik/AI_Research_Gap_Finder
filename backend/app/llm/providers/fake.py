"""
Fake LLM provider for unit tests and local dev without API keys — 07 §4.2.
Returns canned, schema-conformant responses for all prompt IDs.
"""

import json
import logging
from typing import Any, TypeVar
from pydantic import BaseModel

from app.llm.providers.base import BaseLLMProvider, LLMResult

logger = logging.getLogger("rgf.llm.fake")
T = TypeVar("T", bound=BaseModel)


class FakeLLMProvider(BaseLLMProvider):
    """Deterministic fake provider returning valid structured JSON."""

    def __init__(self, model_name: str = "fake-model"):
        self.model_name = model_name

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000,
        response_schema: type[T] | None = None,
    ) -> LLMResult:
        # Detect prompt from user_prompt or system_prompt content
        user_lower = user_prompt.lower()
        sys_lower = system_prompt.lower()

        if "metadata_extraction" in sys_lower or "bibliographic metadata" in sys_lower:
            payload = {
                "title": "Attention-Based Deep Learning for Academic Research",
                "authors": ["A. Smith", "B. Jones"],
                "year": 2023,
                "venue": "IEEE Transactions",
                "doi": "10.1109/TEST.2023.1234567",
                "abstract": "This paper explores attention-based architectures for deep learning.",
                "domain": "Artificial Intelligence",
                "field_confidence": {
                    "title": 0.95,
                    "authors": 0.90,
                    "year": 0.98,
                    "venue": 0.85,
                    "doi": 0.99,
                    "abstract": 0.95,
                },
            }
        elif "grounded_answer" in sys_lower or "search question" in sys_lower:
            payload = {
                "answer": "Based on the provided literature, attention mechanisms significantly improve segmentation accuracy [1]. However, evaluations remain constrained to single-hospital cohorts [2].",
                "cited_sources": [1, 2],
                "insufficient_evidence": False,
            }
        elif "theme_detection" in sys_lower or "thematic clusters" in sys_lower:
            payload = {
                "themes": [
                    {
                        "theme_id": "thm_01",
                        "name": "Transformer Architectures in Medical Vision",
                        "description": "Exploration of self-attention mechanisms for radiographic imaging.",
                        "paper_ids": [],
                        "chunk_ids": [],
                    }
                ]
            }
        elif "contradiction_detection" in sys_lower or "conflicting findings" in sys_lower:
            payload = {
                "contradictions": [
                    {
                        "topic": "Impact of Data Augmentation on Out-of-Distribution Accuracy",
                        "claim_a": {
                            "text": "Extensive augmentation improves robustness to distribution shift",
                            "paper_id": "pap_demo_1",
                            "chunk_id": "chk_demo_1",
                            "quote": "extensive data augmentation significantly enhances generalization across hospital domains",
                            "polarity": "POSITIVE",
                            "metric": "accuracy",
                            "dataset": "CXR-14",
                        },
                        "claim_b": {
                            "text": "Data augmentation causes performance degradation on out-of-distribution test sets",
                            "paper_id": "pap_demo_2",
                            "chunk_id": "chk_demo_2",
                            "quote": "augmentation strategies led to a consistent drop in external validation accuracy",
                            "polarity": "NEGATIVE",
                            "metric": "accuracy",
                            "dataset": "CheXpert",
                        },
                        "comparable": True,
                        "possible_reasons": [
                            {
                                "reason_type": "DIFFERENT_DATASET",
                                "explanation": "Paper A evaluated on CXR-14 while Paper B used CheXpert with different label noise.",
                                "basis": "HYPOTHESIS",
                            }
                        ],
                    }
                ]
            }
        elif "research_gap_detection" in sys_lower or "unexplored research gaps" in sys_lower:
            payload = {
                "gaps": [
                    {
                        "title": "Lack of Multi-Center Clinical Validation in Real-World Settings",
                        "category": "GENERALIZATION",
                        "gap_type": "SYNTHESIZED",
                        "description": "All analyzed studies report evaluations exclusively conducted on single-institution datasets without multi-site verification.",
                        "affected_papers": [],
                        "supporting_chunk_ids": [],
                        "supporting_quotes": [],
                        "why_gap_exists": "Evaluation sections focus solely on benchmark accuracy on static splits without distribution-shift testing.",
                        "potential_research_direction": "Conduct prospective cross-hospital multi-center validation protocols.",
                        "suggested_research_questions": [
                            "How do attention models generalize when deployed across divergent hospital PACS environments?"
                        ],
                        "methodology_suggestion": "Stratified cross-site holdout evaluation with domain discrepancy quantification.",
                    }
                ]
            }
        elif "entailment" in sys_lower or "verdicts" in sys_lower:
            payload = {
                "verdicts": [
                    {
                        "claim_id": "claim_1",
                        "verdict": "SUPPORTS",
                        "reasoning": "The quoted text directly confirms the claim.",
                    }
                ]
            }
        else:
            # Default generic PaperAnalysis payload
            payload = {
                "research_problem": {
                    "text": "Improving segmentation accuracy on radiological imagery under limited supervision.",
                    "quotes": [],
                    "stated": True,
                },
                "research_objectives": [
                    {
                        "text": "Develop hybrid vision-transformer architecture for dense chest X-ray segmentation.",
                        "quotes": [],
                        "stated": True,
                    }
                ],
                "methodology": {
                    "text": "Dual-branch encoder integrating convolutional feature maps with multi-head self-attention.",
                    "quotes": [],
                    "stated": True,
                },
                "dataset": {
                    "text": "Evaluated on NIH ChestX-ray14 benchmark dataset.",
                    "quotes": [],
                    "stated": True,
                },
                "experimental_setup": {
                    "text": "Trained using AdamW optimizer with cosine learning rate schedule for 100 epochs.",
                    "quotes": [],
                    "stated": True,
                },
                "contributions": [
                    {
                        "text": "Novel multi-scale cross-attention module yielding improved boundary delineation.",
                        "quotes": [],
                        "stated": True,
                    }
                ],
                "key_findings": [
                    {
                        "text": "Achieved 0.912 Dice score outperforming standard U-Net baselines.",
                        "quotes": [],
                        "stated": True,
                        "polarity": "POSITIVE",
                        "subject": "Proposed Model",
                        "metric": "Dice",
                        "dataset": "NIH ChestX-ray14",
                    }
                ],
                "limitations": [
                    {
                        "text": "Evaluation restricted to single institution dataset without external cross-hospital validation.",
                        "quotes": [],
                        "stated": True,
                        "limitation_type": "SINGLE_DOMAIN",
                    }
                ],
                "future_work": [
                    {
                        "text": "Evaluate multi-center generalization and explore 3D volumetric extensions.",
                        "quotes": [],
                        "stated": True,
                    }
                ],
                "unresolved_questions": [
                    {
                        "text": "Sensitivity of self-attention weights to subtle imaging artifacts remains uncharacterized.",
                        "quotes": [],
                        "stated": True,
                    }
                ],
                "domain": "Medical Image Analysis",
            }

        raw_str = json.dumps(payload)
        return LLMResult(
            raw_text=raw_str,
            parsed=payload,
            tokens_in=len(user_prompt.split()),
            tokens_out=len(raw_str.split()),
            model=self.model_name,
            latency_ms=10,
        )
