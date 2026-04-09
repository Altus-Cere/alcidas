# ALCIDAS Session Log

---

## Session 1 — 2026-04-09 (M0: Fork and Strip)

**Work completed:**

1. **CLAUDE.md restructure** — split 28KB strategic doc into lean operational `CLAUDE.md` + full `docs/playbook.md`
2. **Hermes subtree** — imported `upstream/hermes/` at `v2026.4.8` (squashed), pushed to GitHub
3. **`upstream/README.md`** — fork discipline documented
4. **`alcidas/core/` override layer** — 6 files scaffolded:
   - `config.py` — Telegram-only GatewayConfig builder
   - `agent.py` — AlcidasAgent (Claude claude-opus-4-6 primary, GPT-4o fallback)
   - `prompt_builder.py` — ALCIDAS operator persona + confidence score hard rule
   - `gateway.py` — AlcidasGatewayRunner, double-enforces Telegram-only
   - `skills_config.py` — skill allowlist (blocks RL/gaming/social)
   - `main.py` — `python -m alcidas.core.main` entry point
5. **Smoke test passed** — bot connected to Telegram polling, `✓ telegram connected`
6. **`install.sh`** — curl-installable, Python 3.11+ check, venv, systemd service on Linux
7. **`alcidas/auth/`** — license server scaffold:
   - `server.py` — FastAPI with `/v1/license/validate` + `/v1/webhooks/stripe`
   - `license_store.py` — SQLite key store
   - `license_client.py` — gateway boot-time phone-home (fail-open)
   - `models.py` — LicenseRecord, key format `ALCD-XXXX-XXXX-XXXX-XXXX`

**Decisions made:**
- Non-Telegram adapters disabled via config (not deleted from upstream — upstream/ is read-only)
- RL framework not exposed via entry points (never invoked in ALCIDAS runtime)
- License issuance: Stripe webhook auto-generates key on `subscription.created`; fail-open on auth server outage
- Python 3.11 required (installed via winget); venv at `.venv/`

**M0 status: COMPLETE**

**Next: M1 — Onboarding wizard**

---
