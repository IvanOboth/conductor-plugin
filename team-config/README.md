# Team config

The two global agent-config files. Copy them in, then tune.

| File | Installs to | Read by |
|---|---|---|
| `CLAUDE.md` | `~/.claude/CLAUDE.md` | every Claude Code session, every project |
| `AGENTS.md` | `~/.codex/AGENTS.md` | every `codex exec` / `ask-codex` lane |

```bash
curl -fL -o ~/.claude/CLAUDE.md \
  https://raw.githubusercontent.com/IvanOboth/conductor-plugin/main/team-config/CLAUDE.md
mkdir -p ~/.codex && curl -fL -o ~/.codex/AGENTS.md \
  https://raw.githubusercontent.com/IvanOboth/conductor-plugin/main/team-config/AGENTS.md
```

**If you already have a `~/.claude/CLAUDE.md`, don't clobber it** — merge. Your existing
project conventions matter; what you want from here is the routing table and the gates.

## Install both, on both machines

`CLAUDE.md` governs Claude Code. `AGENTS.md` governs codex lanes — and a codex lane is
making its own decisions while it runs, with no sight of the Claude-side file. Skip it and
half the orchestration is unguided. Install both on your laptop *and* your VM.

## What to tune, what to leave

**Tune:** the lane assignments and the `cost` column — they should reflect what you
actually pay and what you actually work on.

**Leave alone:** the gates. "What earns an agent", the fan-out sizing rules, and the two
Opus counter-behaviours. They read as restrictive and they are the reason a fan-out
costs what you expect. If one is getting in your way, raise it rather than deleting it —
usually the work order is underspecified rather than the gate being wrong.

## Why steerability is its own column

Opus 5 has not regressed on capability — it still leads where work is messy and
repo-shaped (SWE-bench Pro 79.2%, with no GPT-6 Astra figure published; BenchLM's agentic
aggregate 77.4 vs Astra's 70.3). What degraded is
obedience: scope expansion, declaring fixes done while leaving pieces unimplemented, and
delegating to subagents more readily than prior models. Encoding that as a lower
intelligence score would send hard problems to a model that is genuinely worse at them.
So it is a separate axis, and it changes *which* work you route away — steerability-
sensitive work, not merely hard work.
