"""ALCIDAS gateway entry point.

Run with:
    python -m alcidas.core.main

Or (once installed):
    alcidas-gateway

Bootstraps sys.path so upstream/hermes/ is importable, then starts
AlcidasGatewayRunner.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path


def _bootstrap_upstream_path() -> None:
    """Add upstream/hermes/ to sys.path so hermes modules are importable.

    Supports two layouts:
    1. Running from repo root: upstream/hermes/ relative to this file's
       great-grandparent (alcidas/core/main.py → alcidas/ → repo root).
    2. ALCIDAS_UPSTREAM_PATH env var override for Docker/production.
    """
    override = os.environ.get("ALCIDAS_UPSTREAM_PATH")
    if override:
        upstream = Path(override).resolve()
    else:
        # alcidas/core/main.py → alcidas/core/ → alcidas/ → repo root
        repo_root = Path(__file__).resolve().parent.parent.parent
        upstream = repo_root / "upstream" / "hermes"

    if not upstream.exists():
        raise FileNotFoundError(
            f"upstream/hermes not found at {upstream}. "
            f"Set ALCIDAS_UPSTREAM_PATH to the correct path, "
            f"or run from the repo root."
        )

    upstream_str = str(upstream)
    if upstream_str not in sys.path:
        sys.path.insert(0, upstream_str)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("alcidas")

    _bootstrap_upstream_path()

    # Imports deferred until after path bootstrap
    from dotenv import load_dotenv
    load_dotenv(override=False)  # load .env if present, env vars take precedence

    from alcidas.core.gateway import AlcidasGatewayRunner

    logger.info("Starting ALCIDAS gateway...")
    runner = AlcidasGatewayRunner()
    asyncio.run(runner.run())


if __name__ == "__main__":
    main()
