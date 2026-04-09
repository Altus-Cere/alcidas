"""ALCIDAS gateway config builder.

Enforces Telegram-only platform constraint and injects ALCIDAS model routing.
Wraps upstream gateway/config.py — never modify upstream directly.
"""
import os
from typing import Optional

# upstream/hermes must be on sys.path before this import.
# Bootstrapped by alcidas/core/main.py.
from gateway.config import GatewayConfig, Platform, PlatformConfig, HomeChannel


_ALLOWED_PLATFORMS = frozenset({Platform.TELEGRAM})


def build_alcidas_gateway_config() -> GatewayConfig:
    """Return a GatewayConfig with only the Telegram adapter enabled.

    Reads from env vars:
      TELEGRAM_BOT_TOKEN   — required
      ALCIDAS_HOME_CHAT_ID — optional; owner's chat ID for cron delivery

    Raises:
      EnvironmentError  if TELEGRAM_BOT_TOKEN is missing
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise EnvironmentError(
            "TELEGRAM_BOT_TOKEN is not set. "
            "ALCIDAS requires a Telegram bot token to start."
        )

    home_chat_id = os.environ.get("ALCIDAS_HOME_CHAT_ID", "")
    home_channel: Optional[HomeChannel] = None
    if home_chat_id:
        home_channel = HomeChannel(
            platform=Platform.TELEGRAM,
            chat_id=home_chat_id,
            name="Owner",
        )

    telegram_cfg = PlatformConfig(
        enabled=True,
        token=token,
        home_channel=home_channel,
        reply_to_mode="first",
    )

    config = GatewayConfig()
    config.platforms = {Platform.TELEGRAM: telegram_cfg}
    return config


def assert_telegram_only(config: GatewayConfig) -> None:
    """Raise RuntimeError if any non-Telegram platform is enabled.

    Called at boot by AlcidasGatewayRunner as a safety guard against
    misconfigured deployments.
    """
    for platform, pcfg in config.platforms.items():
        if platform not in _ALLOWED_PLATFORMS and pcfg.enabled:
            raise RuntimeError(
                f"ALCIDAS only permits the Telegram adapter. "
                f"Found enabled platform: {platform.value!r}. "
                f"Set it to enabled: false or remove it from config."
            )
