"""ALCIDAS skill allowlist.

Controls which Hermes bundled skills are permitted in ALCIDAS deployments.
Skills not in this allowlist are added to the disabled set at boot.

To add a skill: add its directory name to ALCIDAS_ALLOWED_SKILLS and
document why it's needed in the comment.
"""
from typing import Set

# Skills permitted in ALCIDAS. These are Hermes skill directory names
# (the leaf name under skills/<category>/<name>/).
ALCIDAS_ALLOWED_SKILLS: Set[str] = {
    # Research & document handling
    "arxiv",             # Research papers for regulatory/industry reference
    "nano-pdf",          # PDF parsing for invoices and CPA packages
    "ocr-and-documents", # OCR for handwritten receipts and paper invoices

    # GitHub (internal tooling / reviewer dashboard deploys)
    "github-auth",
    "github-issues",
    "github-pr-workflow",

    # Software development (internal use by Arsh/Vinay only)
    "plan",
    "test-driven-development",
    "systematic-debugging",
    "subagent-driven-development",
    "requesting-code-review",

    # MCP
    "native-mcp",        # MCP OAuth 2.1 tool surface
}

# Skills that are ALWAYS blocked regardless of config — these are the RL/
# red-teaming/gaming skills that have no place in a business operator.
ALCIDAS_BLOCKED_SKILLS: Set[str] = {
    "godmode",           # Red-teaming — never in production
    "hermes-atropos-environments",  # RL training environments
    "pokemon-player",
    "minecraft-modpack-server",
    "ascii-video",
    "manim-video",
    "songwriting-and-ai-music",
    "find-nearby",       # Consumer leisure feature
    "xitter",            # Social media — out of MVP scope
    "polymarket",        # Prediction markets — not relevant
}


def get_alcidas_disabled_skills(all_available_skills: Set[str]) -> Set[str]:
    """Return the set of skill names to disable for ALCIDAS.

    Computes: all_available - ALCIDAS_ALLOWED_SKILLS, then adds ALCIDAS_BLOCKED_SKILLS.

    Args:
        all_available_skills: set of all skill names discovered on disk.

    Returns:
        Set of skill names that should be disabled.
    """
    not_allowed = all_available_skills - ALCIDAS_ALLOWED_SKILLS
    return not_allowed | ALCIDAS_BLOCKED_SKILLS
