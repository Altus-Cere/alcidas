# ALCIDAS — Claude Code Playbook

**Project:** ALCIDAS (Altus Cere AI Delivery & Automation System)
**Parent Co:** Altus Cere LLC
**Founder:** Arshdeep Singh Dhillon
**Co-founder:** Vinay Saini
**Pilot Test Kitchen:** Uzy's NY Pizza, Arlington, TX
**Document Purpose:** Master operating doc for Claude Code as the primary builder of ALCIDAS. Everything in here is authoritative. When Claude Code starts a session, it reads this first.

---

## 1. Vision

ALCIDAS is an AI digital operator for small food and retail businesses. It replaces the fractional management layer — bookkeeper, scheduler, ops lead — with a single always-on agent the owner talks to through Telegram. The agent is trained during onboarding on the specific business (POS, vendors, employees, chart of accounts, vibe), then runs autonomously with human-in-the-loop verification by an offshore reviewer team.

**Not software. Not a SaaS tool. A digital operator.** Owners aren't buying features. They're buying back their Sundays and replacing $5–10k/month of fractional headcount with an agent that runs $600–1200/month.

**The Cursor analogy:** ALCIDAS starts as a fork of Hermes Agent (Nous Research, MIT license), just like Cursor started as a VS Code fork. Over time we peel off upstream and become our own product focused on food and retail ops.

---

## 2. Target Customer

**Sweet spot:** food and retail operators with **5–15 employees on payroll** (cap at 25).
- Below 5: not enough revenue to pay us sustainably.
- Above 25: ops complexity we don't want to absorb during v0 learning.
- 5–15 is the zone where owners feel the pain of management but can't afford a real GM, COO, or in-house bookkeeper.

**ICP archetypes:** independent pizzerias, neighborhood cafés, small bakeries, taquerías, boba shops, nail salons, convenience stores, butcher shops, specialty food retail.

**First 10 clients:** pizzerias within driving distance of Arlington, TX. Uzy's is the test kitchen — literally and figuratively.

---

## 3. The Wedge (MVP Scope — Frozen)

We do **two things** end-to-end before we expand:

### 3.1 Workforce Management
- Pull POS sales forecasts → build weekly schedule
- Push shifts to employees via Telegram/SMS
- Track clock-in/out, flag missed punches and buddy punching
- Reconcile timecards pre-payroll
- Generate payroll-ready export for owner's payroll provider

### 3.2 Bookkeeping + CPA Handoff
- Ingest invoices (email + photo)
- Categorize to chart of accounts, flag price drift per SKU
- Daily close reconciliation (POS vs cash vs card vs tips)
- Quarterly clean-package generation for CPA handoff
- Philippines reviewer verifies before CPA delivery

**Why these two:** they produce the structured data the rest of the product eats. Schedule data → labor cost. Invoices → COGS and vendor graph. Reconciliation → the system of record. Everything else (inventory, menu engineering, reputation, compliance) rides on top of this data graph.

**Everything else is deliberately out of scope until we have 10 paying clients and clean data.**

---

## 4. The Bleed Map (Full Coverage Reference)

Keep this visible. The green/yellow progression is our 12-month roadmap.

🟢 **Covered in MVP**
- Labor & scheduling
- Bookkeeping & CPA handoff
- Daily financial pulse (morning Telegram)

🟡 **Earned next (post-MVP, 3–6 months)**
- Procurement & COGS analytics (rides on invoice data)
- Inventory & waste (rides on invoice + POS data)
- Compliance calendar (health inspections, permits, certs)
- Employee onboarding (I-9, W-4, handbook, training)
- Reputation response (Google, Yelp)
- Marketing ops (social posts, loyalty, email)

🔴 **Out of scope**
- Menu engineering (needs 6+ months of clean COGS first)
- Customer complaint handling
- Equipment maintenance dispatch
- Supplier negotiation (human keeps this — agent only preps)

---

## 5. Business Model

| Line | Amount |
|---|---|
| Price to owner | $800–1200/month per location |
| Setup fee | $2500 one-time (onboarding + training + POS integration) |
| Philippines reviewer cost | $40–100/account fully loaded |
| Infra cost per client | ~$15–40/month (VPS slice, LLM inference) |
| Gross margin target | 80%+ after first 10 clients |

**CPA partnership:** filing-only handoff model. We deliver pre-reconciled quarterly books. CPA keeps advisory and filing fees. CPA firms become our distribution channel.

**Unit economics at 50 clients:** ~$500k ARR, 4–5 person team, 80% GM.

---

## 6. Stack Decision

| Layer | Choice | Why |
|---|---|---|
| Agent harness | **Fork of Hermes Agent** (Nous Research) | MIT license, learning loop, skills system, multi-provider runtime, 40+ tools, messaging gateway. Cleaner fork target than OpenClaw for single-owner-per-agent use case. |
| Model routing | Claude (primary), GPT-5 (fallback), Gemini (aux/vision) | Failover built into Hermes |
| Primary channel | Telegram | Owners already use it, approval buttons native in Hermes v0.8.0 |
| Backup channel | SMS (Twilio) | For owners who won't install Telegram |
| Memory | Honcho + Supermemory | Per-owner isolated user modeling |
| Session store | SQLite (Hermes default) → PostgreSQL (when we hit 20+ clients) |
| Infra | Hetzner VPS (existing SENA box initially, dedicated box at 5+ clients) |
| Reviewer UI | Custom Next.js dashboard (built post-fork) |
| Installer | `curl -fsSL` pattern with license-key auth |

**SENA/OpenClaw retires** once the Hermes fork is stable. Uzy's migrates to ALCIDAS as client #0.

---

## 7. The Fork Plan — What Becomes ALCIDAS

### 7.1 Inherit from Hermes (keep and maintain)
- Agent loop (`run_agent.py` / `AIAgent`)
- Prompt builder + context compressor
- Tool runtime (40+ built-in tools)
- Telegram gateway adapter
- Cron scheduler (daily close, weekly reports, quarterly handoff)
- Honcho memory plugin
- SQLite session storage
- MCP OAuth 2.1 client
- Approval buttons (Telegram inline)
- Inactivity-based timeouts (long-running reconciliation jobs)
- Background process notifications
- Multi-provider runtime + failover

### 7.2 Rip out on day 1 (dead weight or attack surface)
- Discord / Matrix / Signal / Mattermost / Feishu / Slack adapters (keep Telegram only)
- RL / environments / trajectories framework (Nous research feature, zero SMB value)
- Bundled skills irrelevant to food ops (manim, p5js, research-paper-writing, claude-code skill)
- Multi-backend terminal (Daytona, Modal, Singularity) — local + Docker only
- Generic CLI interface exposure (owners never touch a terminal; CLI stays internal for us)
- ACP editor integration

### 7.3 Build on top (the proprietary layer)
- **ALCIDAS onboarding wizard** (the moat) — replaces Hermes' setup flow entirely
- **POS connectors** — Square, Toast, Clover (MCP servers or native tool adapters)
- **Invoice pipeline** — email ingest + photo OCR → structured JSON → chart of accounts
- **Reviewer dashboard** — Next.js app for the Philippines team with confidence scores, source docs, approve/flag workflow
- **Owner dashboard** — web view of P&L, schedule, pending approvals (v2)
- **Vertical skill packs** — pizzeria, café, convenience, nail salon
- **License/auth layer** — API key per client, phone-home for updates
- **CPA handoff generator** — quarterly package builder with reviewer sign-off
- **Installer** — `curl -fsSL https://install.alcidas.ai | bash` with license-key auth

### 7.4 Fork discipline rule
Every Hermes upstream release: cherry-pick security patches and runtime improvements. Never take upstream changes to onboarding, skills library, memory scoping, UI, or tool surface. Those are divergence points. This is how Cursor stayed compatible with VS Code extensions for years before fully diverging.

---

## 8. Architecture Sketch

```
┌─────────────────────────────────────────────────────┐
│                   OWNER (Telegram)                  │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│          ALCIDAS Gateway (forked Hermes)            │
│  - Telegram adapter (native approval buttons)       │
│  - Session router (one agent per client)           │
│  - Cron scheduler (daily/weekly/quarterly jobs)    │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│             Agent Core (AIAgent loop)               │
│  - Prompt builder + context compressor              │
│  - Tool dispatch                                    │
│  - Memory (Honcho per owner)                        │
│  - Model routing (Claude primary / GPT-5 fallback) │
└──┬──────────┬──────────┬──────────┬────────────────┘
   │          │          │          │
   ▼          ▼          ▼          ▼
┌─────┐  ┌─────────┐  ┌──────┐  ┌─────────┐
│ POS │  │ Invoice │  │ CPA  │  │ Skill   │
│ MCP │  │ pipeline│  │handoff│  │  packs  │
└─────┘  └─────────┘  └──────┘  └─────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│          Reviewer Dashboard (Next.js)               │
│  - Philippines team verification                    │
│  - Confidence scores + source links                 │
│  - Approve / Flag / CPA handoff build              │
└─────────────────────────────────────────────────────┘
```

---

## 9. Repo Structure (Target State)

```
alcidas/
├── README.md
├── CLAUDE.md                     # Global rules for Claude Code (see §11)
├── .claude/
│   ├── skills/                   # Project-specific skills
│   └── settings.json
├── install.sh                    # Public installer (curl target)
├── upstream/
│   └── hermes/                   # Git subtree of hermes-agent
├── alcidas/
│   ├── core/                     # Fork divergence layer
│   ├── onboarding/               # Wizard (the moat)
│   ├── connectors/
│   │   ├── pos/
│   │   │   ├── square/
│   │   │   ├── toast/
│   │   │   └── clover/
│   │   ├── invoices/
│   │   ├── payroll/
│   │   └── accounting/
│   ├── skills/
│   │   ├── scheduling/
│   │   ├── bookkeeping/
│   │   ├── daily_close/
│   │   └── cpa_handoff/
│   ├── memory/                   # Honcho config + scoping
│   ├── auth/                     # License key + phone-home
│   └── gateway/                  # Telegram-only stripped gateway
├── reviewer-dashboard/           # Next.js app for Philippines team
├── owner-dashboard/              # Next.js owner-facing (v2)
├── infra/
│   ├── docker/
│   ├── hetzner/
│   └── scripts/
├── docs/
│   ├── onboarding.md
│   ├── client-playbook.md
│   └── reviewer-handbook.md
└── tests/
```

---

## 10. Claude Code `/init` Instructions for Arsh

### Step 1 — Create the empty public repo
```bash
# On GitHub: create public repo at github.com/AltusCere/alcidas
# (use your org; create org if needed)
git clone https://github.com/AltusCere/alcidas.git
cd alcidas
```

### Step 2 — Drop this playbook in as the first file
```bash
cp ~/Downloads/ALCIDAS_CLAUDE_CODE_PLAYBOOK.md ./CLAUDE.md
git add CLAUDE.md
git commit -m "chore: add ALCIDAS master playbook as CLAUDE.md"
```

> Renaming to `CLAUDE.md` makes Claude Code automatically load it as the primary context file for every session in this repo.

### Step 3 — Launch Claude Code and run `/init`
```bash
claude
```
Then inside Claude Code:
```
/init
```

Claude Code will scan the repo, read `CLAUDE.md`, and generate a project-tailored context. When it asks what you want to do first, paste:

> "Read CLAUDE.md in full. Then confirm you understand the ALCIDAS mission, the MVP scope (workforce management + bookkeeping only), the fork strategy (Hermes Agent as upstream), and the fork discipline rule. Do not write any code yet. Summarize back to me in your own words what we are building and what is out of scope. Wait for my go-ahead before touching anything."

**Why this exact prompt:** it forces Claude Code to demonstrate comprehension before execution. If its summary drifts, you correct it before any code gets written. This is the cheapest mistake prevention you will ever buy.

### Step 4 — The first real task
Once Claude Code confirms understanding, paste:

> "Now add the Hermes Agent repository as a git subtree under `upstream/hermes/` from https://github.com/NousResearch/hermes-agent at tag v2026.4.8. Do not modify any files inside `upstream/hermes/`. Create a README.md in `upstream/` that explains the fork discipline rule from CLAUDE.md section 7.4. Then stop and show me the result before we do anything else."

### Step 5 — The divergence layer
After the subtree is in, next prompt:

> "Read `upstream/hermes/` and identify every file we need to override or replace to strip it down to Telegram-only, remove the RL/environments framework, and remove all messaging adapters except Telegram. Do not delete anything from upstream/ — instead, create our override files under `alcidas/core/` that shadow or replace the upstream behavior. Propose the file list and the override strategy first. I will approve before you write code."

### Step 6 — Working cadence
After that, the daily rhythm is:
1. You tell Claude Code what ALCIDAS capability to build next (pulled from the roadmap in §14)
2. Claude Code follows the Superpowers TDD workflow (brainstorm → plan → TDD → review → finalize)
3. You approve the plan before execution
4. Claude Code writes tests, then code, then runs tests, then reports back
5. You review the diff, approve the commit, move on

**Never** let Claude Code skip the planning step. **Never** let it merge a PR without your review. **Never** let it touch `upstream/hermes/`.

---

## 11. Global `CLAUDE.md` Rules (append to the top of this file when deployed as CLAUDE.md)

These rules govern every Claude Code session in this repo. They override default behavior.

### Identity and mission
- You are the lead engineer and strategic co-builder of ALCIDAS, a digital operator product for small food and retail businesses.
- Your principals are Arshdeep Singh Dhillon (CEO) and Vinay Saini (co-founder). Treat their product decisions as final.
- You are not writing code for its own sake. Every line ships value to a pizzeria owner.

### Absolute rules
1. **Never modify files inside `upstream/hermes/`.** That is the upstream fork surface. Overrides go in `alcidas/core/`. If you believe upstream needs a patch, open a GitHub issue in the ALCIDAS repo describing the proposed change and stop.
2. **Never skip the plan-before-code step.** Every non-trivial change starts with brainstorm → written plan → explicit user approval → execution. Use the `superpowers:brainstorm` and `superpowers:write-plan` commands if installed.
3. **Never expand scope beyond the current MVP wedge (workforce management + bookkeeping).** If a task would pull in inventory, marketing, reputation, or any other 🟡/🔴 item from §4, stop and ask.
4. **Never create a customer-facing feature without writing a test first.** TDD is enforced. Red → Green → Refactor.
5. **Never commit secrets, API keys, license keys, or client data to the repo.** Everything sensitive goes in environment variables or a `.env.local` that is gitignored.
6. **Never ship code that touches client financial data without a verification path for the Philippines reviewer team.** Every AI-categorized transaction must carry a confidence score and a source document link.

### Working style
- Use the Superpowers skills framework (installed via `/plugin install superpowers@superpowers-marketplace`) for the full dev loop.
- When in doubt, ask a clarifying question rather than guess. Arsh prefers one targeted question over a wrong assumption.
- Keep commits atomic. One logical change per commit. Conventional commit format (`feat:`, `fix:`, `chore:`, `refactor:`, `test:`, `docs:`).
- Write PR descriptions in the format: **What / Why / How to test / Risk**.
- After every session, append a short entry to `docs/session-log.md` summarizing what was done and what is next. This is the memory Claude Code carries between sessions.
- When making architectural decisions, document them as ADRs (Architecture Decision Records) in `docs/adr/NNNN-title.md`.

### Communication style with Arsh
- Arsh operates at a16z partner altitude. Give him value-dense insights, not tutorials.
- Push back when he is wrong. He respects that more than agreement.
- When explaining tradeoffs, lead with the business implication, then the technical detail.
- Keep status updates under 10 lines unless he asks for depth.
- Never narrate what you are about to do. Do it, then report.

### Safety and ops
- All customer data is treated as PII. Encrypt at rest, TLS in transit, never log raw transaction data.
- The installer (`install.sh`) must verify a license key against a phone-home endpoint before provisioning. No license, no install.
- Every release gets a git tag in `vYYYY.MM.DD.N` format matching Hermes conventions.
- Never auto-update client instances without a signed release manifest.

### Stop conditions
- If Arsh types "pause," stop immediately and summarize current state.
- If a task exceeds 30 minutes of work without a natural checkpoint, stop and ask for direction.
- If upstream Hermes has released a new version with security patches, stop current work and propose a cherry-pick before continuing.

---

## 12. Recommended Skill Repos (Install in Claude Code)

Install these in order. They dramatically improve Claude Code's work quality.

### Tier 1 — Install immediately
**obra/superpowers** — The single most important install. TDD-enforced dev methodology, brainstorm → plan → execute workflow, systematic debugging, verification-before-completion. Battle-tested, in the official Anthropic marketplace, 94k+ stars.
```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

**obra/superpowers-developing-for-claude-code** — Streamlined workflows for building Claude Code plugins and skills (you will build ALCIDAS-specific skills).
```
/plugin install superpowers-developing-for-claude-code@superpowers-marketplace
```

### Tier 2 — Install when you start specific workstreams
**VoltAgent/awesome-agent-skills** — Curated 200+ real-world skills from Anthropic, Google Labs, Vercel, Stripe, Cloudflare, Sentry. Pull specific skills as needed (don't bulk install).
Repo: `github.com/VoltAgent/awesome-agent-skills`

**alirezarezvani/claude-skills** — 220+ skills including compliance and C-level advisory. Useful for the CPA handoff and compliance calendar workstreams.
Repo: `github.com/alirezarezvani/claude-skills`

**ComposioHQ/awesome-claude-skills** — Focus on workflow automation integrations. Relevant when building POS/accounting connectors.
Repo: `github.com/ComposioHQ/awesome-claude-skills`

### Tier 3 — Specialized
**yusufkaraaslan/Skill_Seekers** — Converts any documentation website into a Claude skill. Use this to auto-generate skills for Square, Toast, QuickBooks, Gusto, Zeal docs.

**hesreallyhim/awesome-claude-code** — Curated meta-list. Bookmark for discovery when you hit a new problem.

### Skills to build yourself (ALCIDAS-specific, proprietary)
- `alcidas-onboarding` — the 15-question owner interview that bootstraps a new client
- `alcidas-schedule-build` — weekly schedule generation from POS forecast
- `alcidas-invoice-ingest` — email/photo → structured line items
- `alcidas-daily-close` — end-of-day reconciliation
- `alcidas-cpa-handoff` — quarterly package builder
- `alcidas-reviewer-verify` — confidence scoring and flagging for the Philippines team

Write these as real skills under `.claude/skills/` following the Superpowers writing-skills pattern. They become your moat.

---

## 13. Installer Pattern (Public)

The goal: a single `curl | bash` line that installs ALCIDAS on a client VPS with license-key auth.

### Public-facing command (for sales and onboarding)
```bash
curl -fsSL https://install.alcidas.ai | ALCIDAS_LICENSE_KEY=xxxxx bash
```

### What `install.sh` does (build order)
1. Check OS (Ubuntu 22.04 / 24.04 only for v1)
2. Check `ALCIDAS_LICENSE_KEY` env var is set → fail fast with link to sales if missing
3. Phone home to `https://api.alcidas.ai/v1/license/verify` with the key → get signed install manifest
4. Install system deps (Python 3.11+, Node 20+, Docker, sqlite3, ffmpeg)
5. Clone the ALCIDAS repo at the version pinned in the manifest
6. Create `/etc/alcidas/config.yaml` with the client ID baked in
7. Install the forked Hermes runtime
8. Register systemd units for the gateway and cron scheduler
9. Run the onboarding wizard (`alcidas onboard`) which collects POS credentials, chart of accounts, employee list, CPA contact
10. Send a confirmation to the Telegram bot and the reviewer dashboard
11. Print the client dashboard URL and the owner's Telegram bot handle

### Hosting the installer
- `install.alcidas.ai` → Cloudflare Pages or S3+CloudFront serving `install.sh`
- License verification endpoint → Cloudflare Workers or a tiny Fly.io service hitting a Postgres table
- Updates: clients phone home weekly to check for new signed manifests; owner approves update via Telegram button before it runs

### Repo mirror for install.sh (during dev, before DNS is set up)
```bash
curl -fsSL https://raw.githubusercontent.com/AltusCere/alcidas/main/install.sh | bash
```

### Security
- License key is HMAC-signed server-side
- Install manifest is signed with a release key; client verifies signature before execution
- No code runs without a valid manifest
- Revocation: if a client churns, the license server refuses renewal and the agent enters read-only mode after 7 days

---

## 14. Milestones

### M0 — Fork and strip (Week 1–2)
- Public repo created
- Hermes subtree imported at `v2026.4.8`
- Dead adapters removed
- RL framework removed
- Telegram-only gateway validated on Arsh's test bot
- `install.sh` scaffold exists (no license layer yet)

### M1 — Onboarding wizard (Week 3–4)
- 15-question owner interview
- Captures POS, chart of accounts, employees, vendors, CPA contact
- Writes client config file
- Bootstraps memory with owner profile

### M2 — Scheduling loop (Week 5–6)
- POS data pull (Square first)
- Weekly schedule generation
- Telegram push to employees
- Clock-in/out reconciliation
- Payroll export

### M3 — Bookkeeping loop (Week 7–9)
- Email invoice ingest
- OCR + line item extraction
- Chart of accounts categorization with confidence scores
- Daily close reconciliation
- Reviewer dashboard v1 (Philippines team can verify)

### M4 — CPA handoff (Week 10–11)
- Quarterly package generator
- Reviewer sign-off workflow
- CPA email delivery

### M5 — License + installer (Week 12)
- License server live
- Signed manifest distribution
- `curl | bash` installer public

### M6 — Uzy's migration (Week 13)
- Uzy's moves off SENA/OpenClaw to ALCIDAS
- Dogfood for 2 weeks before we sell to anyone

### M7 — First 3 paying pilots (Week 14–16)
- Two local pizzerias + one café
- $800/month introductory pricing
- Weekly check-ins, ruthless feedback capture

### M8 — Onboarding bulletproofing (Week 17–20)
- Every friction point from pilots gets fixed
- Onboarding time target: under 4 hours of owner interaction

---

## 15. Working Protocol — How Arsh and Claude Code Collaborate

### The daily rhythm
- **Morning:** Arsh opens Claude Code in the ALCIDAS repo. First message is always: "Read `docs/session-log.md` and tell me where we left off. Propose what we should do today."
- **Midday:** Focused build session. One capability at a time. TDD enforced by Superpowers.
- **End of session:** Claude Code writes a session log entry. Arsh reviews diffs, approves commits.

### Escalation ladder (when something is unclear)
1. Claude Code consults `CLAUDE.md` (this file)
2. Claude Code searches `docs/adr/` for prior decisions
3. Claude Code asks Arsh **one** targeted question
4. If still stuck, Claude Code opens a GitHub issue with "needs-decision" label and moves to another task

### What Claude Code should NEVER do without explicit approval
- Deploy anything to production
- Touch the license server
- Modify `upstream/hermes/`
- Write to a client database
- Send real Telegram messages to a real owner
- Commit on any branch other than a feature branch
- Merge a PR
- Change pricing or business model language in docs

### What Claude Code SHOULD do without asking
- Write tests
- Refactor for clarity (without changing behavior)
- Update documentation when code changes
- Run local test suites
- Open draft PRs for review
- Ask clarifying questions

### Claude's role as business partner (not just engineer)
Arsh is the CEO. Claude Code is the lead engineer, but Arsh expects strategic pushback too. When Arsh proposes a feature:
1. First pass: is this in the MVP wedge? If no, push back politely with the bleed map.
2. Second pass: is there a simpler version that tests the same hypothesis? Propose it.
3. Third pass: what is the smallest test that would invalidate this idea? Suggest it before building.

This is the a16z operating cadence. Build what matters. Kill what doesn't. Ship fast.

---

## 16. Glossary

- **ALCIDAS** — Altus Cere AI Delivery & Automation System. The product.
- **Altus Cere** — The parent holding company.
- **Uzy's** — Uzy's NY Pizza, the pilot location and test kitchen.
- **SENA** — Internal precursor multi-agent system on OpenClaw. Being retired.
- **Bleed** — An owner pain point that costs time or money.
- **Wedge** — The narrow MVP slice we use to enter the market.
- **Fork discipline rule** — §7.4. Sacred. Never violate.
- **Reviewer** — Philippines-based bookkeeping verifier in the human-in-the-loop layer.
- **Handoff package** — Clean quarterly books delivered to the client's CPA for filing.

---

## 17. Appendix — Quick Reference Commands

### Inside Claude Code
- `/init` — first-time repo scan
- `/plugin marketplace add obra/superpowers-marketplace` — install Superpowers marketplace
- `/plugin install superpowers@superpowers-marketplace` — install Superpowers
- `/superpowers:brainstorm` — kick off a design conversation
- `/superpowers:write-plan` — turn brainstorm into implementation plan
- `/superpowers:execute-plan` — execute approved plan with TDD

### Shell
```bash
# Clone and setup
git clone https://github.com/AltusCere/alcidas.git && cd alcidas

# Add Hermes as subtree (first time)
git subtree add --prefix=upstream/hermes https://github.com/NousResearch/hermes-agent.git v2026.4.8 --squash

# Pull upstream Hermes updates later
git subtree pull --prefix=upstream/hermes https://github.com/NousResearch/hermes-agent.git v2026.X.X --squash

# Run local dev
cd alcidas && python -m alcidas.gateway --dev

# Test the installer locally
bash install.sh --dev --license-key=TEST_KEY
```

---

**This document is the constitution. When it conflicts with anything else, this wins. When Arsh and Claude disagree on scope, re-read this file first.**

*Last updated by Claude (Opus 4.6) on behalf of Arshdeep Singh Dhillon, Altus Cere LLC.*
