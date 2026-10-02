"""
Core constants — 01 §8, 05 §1, 03 §14.
Single source for sentinel strings used across the codebase.
"""

# Sentinel for missing analysis fields (05 §1, 07 §3.3)
NOT_STATED: str = "Not explicitly stated in the provided paper."

# Exact insufficient-evidence response (03 §14)
INSUFFICIENT_EVIDENCE_MESSAGE: str = (
    "Insufficient evidence. The uploaded research collection does not "
    "contain enough relevant evidence to answer this question."
)

# UUID namespace for Qdrant point IDs (03 §6)
QDRANT_UUID_NAMESPACE: str = "rgf-chunks-v1"

# App version
APP_VERSION: str = "0.1.0"
