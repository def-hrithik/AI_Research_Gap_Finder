"""
ID generation — 05 §1.
Prefixed, URL-safe identifiers for all entities.
"""

import secrets


def new_id(prefix: str) -> str:
    """Generate a prefixed 8-hex-char ID. E.g. new_id('gap') → 'gap_a1b2c3d4'.

    Args:
        prefix: Entity prefix (prj, pap, ana, evd, gap, ctr, fut, rep, job, run, req).

    Returns:
        '{prefix}_{8 random hex chars}'.
    """
    return f"{prefix}_{secrets.token_hex(4)}"


def chunk_id(paper_id: str, index: int) -> str:
    """Deterministic chunk ID — 05 §1.

    Args:
        paper_id: The parent paper ID (e.g. 'pap_a1b2c3d4').
        index: 0-based chunk index within the paper.

    Returns:
        'chk_{paper_id}_{index:04d}' e.g. 'chk_pap_a1b2c3d4_0014'.
    """
    return f"chk_{paper_id}_{index:04d}"
