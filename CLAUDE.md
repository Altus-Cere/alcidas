# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Full strategic playbook: `docs/playbook.md` (business model, milestones, bleed map, glossary, installer spec).

## What Is ALCIDAS

ALCIDAS (Altus Cere AI Delivery & Automation System) is an AI digital operator for small food/retail businesses (5–25 employees). It replaces fractional management — bookkeeper, scheduler, ops lead — with an always-on agent the owner talks to via Telegram, verified by an offshore reviewer team.

Built as a fork of **Hermes Agent** (Nous Research, MIT license) with a proprietary layer on top.

## MVP Scope (Frozen)

Only two capabilities until 10 paying clients with clean data:

1. **Workforce Management** — POS forecast → weekly schedule → Telegram push → clock-in/out → payroll export
2. **Bookkeeping + CPA Handoff** — invoice ingest → categorize → daily close → quarterly CPA package → reviewer verification

Everything else (inventory, marketing, reputation, menu engineering, compliance) is **out of scope**. Push back if asked to build outside the wedge.

## Architecture

- **Upstream fork:** `upstream/hermes/` — git subtree of Hermes Agent. **NEVER modify files here.** Overrides go in `alcidas/core/`.
- **Agent core:** Forked `AIAgent` loop with prompt builder, tool dispatch, Honcho memory (per-owner isolation)
- **Model routing:** Claude (primary), GPT-5 (fallback), Gemini (aux/vision)
- **Channel:** Telegram only (approval buttons native). SMS via Twilio as backup.
- **Session store:** SQLite → PostgreSQL at 20+ clients
- **Reviewer UI:** Next.js dashboard for Philippines team (confidence scores, source docs, approve/flag)
- **Infra:** Hetzner VPS, Docker

## Repo Structure

```
alcidas/
├── CLAUDE.md                # This file (operational rules)
├── upstream/hermes/         # Git subtree — READ ONLY
├── alcidas/
│   ├── core/                # Fork divergence layer (overrides upstream)
│   ├── onboarding/          # 15-question owner interview wizard
│   ├── connectors/          # POS (Square/Toast/Clover), invoices, payroll, accounting
│   ├── skills/              # scheduling, bookkeeping, daily_close, cpa_handoff
│   ├── memory/              # Honcho config + scoping
│   ├── auth/                # License key + phone-home
│   └── gateway/             # Telegram-only stripped gateway
├── reviewer-dashboard/      # Next.js (Philippines team)
├── owner-dashboard/         # Next.js (v2, future)
├── infra/                   # Docker, Hetzner, scripts
├── docs/
│   ├── playbook.md          # Full strategic playbook
│   ├── session-log.md       # Session continuity log
│   └── adr/                 # Architecture Decision Records
├── install.sh               # curl installer (license-key auth)
└── tests/
```

## Commands

```bash
# Add Hermes as subtree (first time)
git subtree add --prefix=upstream/hermes https://github.com/NousResearch/hermes-agent.git v2026.4.8 --squash

# Pull upstream Hermes updates (cherry-pick security/runtime only)
git subtree pull --prefix=upstream/hermes https://github.com/NousResearch/hermes-agent.git vYYYY.X.X --squash

# Run local dev
cd alcidas && python -m alcidas.gateway --dev

# Test the installer locally
bash install.sh --dev --license-key=TEST_KEY

# Run tests
pytest tests/
```

## Absolute Rules

1. **Never modify `upstream/hermes/`.** Overrides go in `alcidas/core/`. To propose an upstream patch, open a GitHub issue and stop.
2. **Never skip plan-before-code.** Brainstorm → written plan → explicit user approval → execution.
3. **Never expand beyond MVP wedge.** If a task touches inventory, marketing, reputation, or any non-green item — stop and ask.
4. **TDD enforced.** No customer-facing feature without a test first. Red → Green → Refactor.
5. **Never commit secrets.** Keys/credentials go in env vars or `.env.local` (gitignored).
6. **Every AI-categorized transaction must carry a confidence score and source document link.** The Philippines reviewer team must be able to verify.

## Fork Discipline (Section 7.4)

Every Hermes upstream release: cherry-pick security patches and runtime improvements only. **Never** take upstream changes to onboarding, skills library, memory scoping, UI, or tool surface — those are divergence points.

### Keep from Hermes
Agent loop, prompt builder, tool runtime (40+ tools), Telegram adapter, cron scheduler, Honcho memory, SQLite sessions, MCP OAuth 2.1, approval buttons, multi-provider runtime + failover.

### Rip out
Discord/Matrix/Signal/Slack/Feishu/Mattermost adapters, RL/environments/trajectories, irrelevant bundled skills, multi-backend terminal (Daytona/Modal/Singularity), generic CLI exposure, ACP editor integration.

### Build (proprietary layer)
Onboarding wizard, POS connectors, invoice pipeline, reviewer dashboard, owner dashboard, vertical skill packs, license/auth, CPA handoff generator, installer.

## Working Style

- **Commits:** atomic, conventional format (`feat:`, `fix:`, `chore:`, `refactor:`, `test:`, `docs:`)
- **PRs:** format as What / Why / How to test / Risk
- **Session log:** append to `docs/session-log.md` after every session
- **ADRs:** document architectural decisions in `docs/adr/NNNN-title.md`
- **Tags:** `vYYYY.MM.DD.N` format matching Hermes conventions
- **Questions:** one targeted question beats a wrong assumption

## Communication with Arsh

- Arsh operates at a16z partner altitude. Value-dense, not tutorials.
- Push back when he's wrong. Lead tradeoffs with business implication, then technical detail.
- Status updates under 10 lines unless depth is requested.
- Don't narrate what you're about to do. Do it, then report.

## Stop Conditions

- "pause" → stop immediately, summarize state
- 30+ minutes without a checkpoint → stop, ask for direction
- Upstream Hermes security release → stop current work, propose cherry-pick first

## Principals

Arshdeep Singh Dhillon (CEO) and Vinay Saini (co-founder). Their product decisions are final.
