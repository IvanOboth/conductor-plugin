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

**Leave alone:** the gates. "What earns an agent", the fan-out sizing rules, the reviewer-is-a-different-model
rule and the work-order rules. They read as restrictive and they are the reason a fan-out
costs what you expect. If one is getting in your way, raise it rather than deleting it —
usually the work order is underspecified rather than the gate being wrong.

## Why steerability is its own column

A model can be strong on capability and still drift from the order: expand the scope,
declare a fix done with pieces missing, or delegate more than it was asked to. Encoding that
as a lower reasoning score would send hard problems to a weaker model. So steerability is a
separate axis, and it decides *which* work you route away — steerability-sensitive work,
not merely hard work. Opus 5.5's 7.5 is provisional; re-rate it from your own lanes.
