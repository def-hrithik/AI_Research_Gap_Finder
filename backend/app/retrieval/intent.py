"""
Research intent detection and section-aware prior — 03 §8.1.
Rule-based detection mapping query patterns to section boosts.
"""

import re
from typing import Any

# Intent trigger patterns and section prior boosts — 03 §8.1
INTENT_RULES: list[tuple[str, list[str], dict[str, float]]] = [
    (
        "LIMITATIONS",
        [
            r"\blimitation",
            r"\bshortcoming",
            r"\bweakness",
            r"\bdrawback",
            r"\bfail",
            r"\bchallenge",
            r"\bconstraint",
        ],
        {
            "LIMITATION": 0.15,
            "DISCUSSION": 0.10,
            "FUTURE_WORK": 0.08,
            "CONCLUSION": 0.08,
        },
    ),
    (
        "METHODOLOGY",
        [
            r"\bmethod",
            r"\bapproach",
            r"\btechnique",
            r"\barchitecture",
            r"\balgorithm",
            r"\bmodel used\b",
            r"\bhow do they\b",
        ],
        {
            "METHODOLOGY": 0.15,
            "RELATED_WORK": 0.08,
            "RESULTS": 0.05,
        },
    ),
    (
        "FUTURE_WORK",
        [
            r"\bfuture work\b",
            r"\bfuture direction",
            r"\bfuture research\b",
            r"\bopen problem",
            r"\bnext step",
            r"\bsuggested\b",
        ],
        {
            "FUTURE_WORK": 0.15,
            "LIMITATION": 0.10,
            "CONCLUSION": 0.08,
        },
    ),
    (
        "DATASET",
        [
            r"\bdataset",
            r"\bdata\b",
            r"\bcorpus\b",
            r"\bbenchmark",
            r"\bsample size\b",
        ],
        {
            "DATASET": 0.15,
            "METHODOLOGY": 0.10,
            "RESULTS": 0.05,
        },
    ),
    (
        "RESULTS",
        [
            r"\bresult",
            r"\bperformance\b",
            r"\baccuracy\b",
            r"\bimprove",
            r"\boutperform",
            r"\bmetric",
            r"\bscore\b",
        ],
        {
            "RESULTS": 0.15,
            "DISCUSSION": 0.08,
            "ABSTRACT": 0.05,
        },
    ),
    (
        "PROBLEM",
        [
            r"\bproblem\b",
            r"\bmotivation\b",
            r"\bobjective\b",
            r"\bgoal\b",
            r"\baim\b",
        ],
        {
            "INTRODUCTION": 0.12,
            "ABSTRACT": 0.10,
        },
    ),
]


def detect_intent(query: str) -> tuple[str, dict[str, float]]:
    """Detect research intent and compute section boost prior.

    Returns:
        tuple of (primary_intent_name, chunk_type_boost_dict).
    """
    q_lower = query.lower()
    matched_intents: list[str] = []
    combined_boosts: dict[str, float] = {}

    for intent_name, triggers, boosts in INTENT_RULES:
        if any(re.search(pat, q_lower) for pat in triggers):
            matched_intents.append(intent_name)
            for c_type, boost in boosts.items():
                combined_boosts[c_type] = max(combined_boosts.get(c_type, 0.0), boost)

    primary_intent = matched_intents[0] if matched_intents else "GENERAL"
    return primary_intent, combined_boosts


def get_section_boost(
    chunk_type: str,
    has_limitation_cue: bool,
    has_future_cue: bool,
    intent_prior: dict[str, float],
    primary_intent: str,
) -> float:
    """Calculate the soft section prior boost for a chunk.

    Base boost from intent_prior + 0.05 cue bonus if cue matches intent.
    """
    boost = intent_prior.get(chunk_type, 0.0)

    # Cue bonus (03 §8.1): +0.05 for matching intent
    if primary_intent == "LIMITATIONS" and has_limitation_cue:
        boost += 0.05
    elif primary_intent == "FUTURE_WORK" and has_future_cue:
        boost += 0.05

    return min(0.20, boost)
