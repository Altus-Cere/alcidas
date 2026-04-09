"""AlcidasGatewayRunner — Hermes GatewayRunner locked to Telegram-only.

Enforces:
- Only the Telegram adapter is permitted to connect
- Config is built from build_alcidas_gateway_config() unless overridden
- Boot-time assertion that no non-Telegram platform is enabled

Usage::

    from alcidas.core.gateway import AlcidasGatewayRunner
    import asyncio

    runner = AlcidasGatewayRunner()
    asyncio.run(runner.run())
"""
import logging

# upstream/hermes must be on sys.path (bootstrapped by alcidas/core/main.py).
from gateway.run import GatewayRunner
from gateway.config import GatewayConfig, Platform

from alcidas.core.config import build_alcidas_gateway_config, assert_telegram_only

logger = logging.getLogger(__name__)


class AlcidasGatewayRunner(GatewayRunner):
    """GatewayRunner pre-configured for ALCIDAS (Telegram-only).

    If no config is passed, builds one from environment variables via
    build_alcidas_gateway_config(). Always asserts Telegram-only at boot.
    """

    def __init__(self, config: GatewayConfig = None):
        if config is None:
            config = build_alcidas_gateway_config()

        assert_telegram_only(config)
        logger.info(
            "ALCIDAS gateway starting — Telegram-only mode, "
            "%d platform(s) configured",
            len([p for p, c in config.platforms.items() if c.enabled]),
        )

        super().__init__(config=config)

    def _create_adapter(self, platform: Platform, platform_config):
        """Override: reject any non-Telegram adapter at instantiation time."""
        if platform != Platform.TELEGRAM:
            raise RuntimeError(
                f"AlcidasGatewayRunner: attempted to create adapter for "
                f"{platform.value!r}. Only Telegram is permitted."
            )
        return super()._create_adapter(platform, platform_config)
