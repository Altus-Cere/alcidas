"""AlcidasAgent — Hermes AIAgent subclass with ALCIDAS defaults.

Injects:
- ALCIDAS system prompt (ephemeral_system_prompt)
- Model routing: Claude claude-opus-4-6 primary, GPT-4o fallback
- Per-owner Honcho memory scoping via user_id
- No trajectory saving (we don't run RL)

Do not add business logic here — keep it in alcidas/skills/.
"""
from typing import Any, Dict, List, Optional

# upstream/hermes must be on sys.path (bootstrapped by alcidas/core/main.py).
from run_agent import AIAgent

from alcidas.core.prompt_builder import build_alcidas_system_prompt

# Primary model: Claude Opus 4.6 via Anthropic
_PRIMARY_MODEL = "anthropic/claude-opus-4-6"

# Fallback model: GPT-4o via OpenRouter when Anthropic is rate-limited
_FALLBACK_MODEL: Dict[str, Any] = {
    "model": "openai/gpt-4o",
    "provider": "openai",
}


class AlcidasAgent(AIAgent):
    """AIAgent pre-configured for ALCIDAS operations.

    Callers should pass `user_id` (owner's Telegram chat ID or phone number)
    so Honcho memory is isolated per owner — critical for multi-tenant deployments.

    Example::

        agent = AlcidasAgent(
            user_id="telegram:123456789",
            session_id="uzy-2024-03-15",
        )
        response = await agent.run("Show me this week's labor cost.")
    """

    def __init__(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        extra_system_prompt: Optional[str] = None,
        **kwargs,
    ):
        alcidas_prompt = build_alcidas_system_prompt()
        if extra_system_prompt:
            alcidas_prompt = f"{alcidas_prompt}\n\n{extra_system_prompt}"

        # Merge ALCIDAS defaults; caller kwargs take precedence so
        # AlcidasGatewayRunner can still override model per-session.
        defaults: Dict[str, Any] = dict(
            model=_PRIMARY_MODEL,
            fallback_model=_FALLBACK_MODEL,
            ephemeral_system_prompt=alcidas_prompt,
            save_trajectories=False,  # RL pipeline not used in ALCIDAS
            platform="telegram",
        )
        defaults.update(kwargs)

        super().__init__(
            user_id=user_id,
            session_id=session_id,
            **defaults,
        )
