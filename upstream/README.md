# upstream/

This directory contains vendored upstream dependencies managed as git subtrees.

## upstream/hermes/

**Source:** [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
**Pinned at:** `v2026.4.8`
**License:** MIT

Hermes Agent is the foundation ALCIDAS forks from — the agent loop, prompt builder, tool runtime, Telegram gateway, cron scheduler, Honcho memory, and multi-provider model routing.

## Fork Discipline Rule

**`upstream/hermes/` is read-only.** No file inside this directory may be modified directly.

When a new Hermes release drops:

1. **Cherry-pick:** security patches and runtime improvements only.
2. **Never take** upstream changes to onboarding, skills library, memory scoping, UI, or tool surface — these are ALCIDAS divergence points.
3. **Override, don't edit:** all customizations live in `alcidas/core/` and shadow or replace upstream behavior.
4. **Test after every pull:** run the full test suite before committing a subtree update.

```bash
# Pull upstream updates (replace tag with the new version)
git subtree pull --prefix=upstream/hermes https://github.com/NousResearch/hermes-agent.git vYYYY.X.X --squash
```

If you believe upstream needs a bug fix or patch, open a GitHub issue in the ALCIDAS repo describing the proposed change. Do not modify files in this directory.
