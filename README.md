# Conductor

Mixed-model orchestration for Claude Code — Ultracode-grade output without the Ultracode premium.

The main loop stays the orchestrator at `high` effort and never delegates three things: **the plan, the work orders, the final review.** Everything else is dispatched to the lane that fits it — Claude for design and judgment, the Codex CLI for mechanical execution and cross-family verification. Every lane's work is then checked by the *other* model family, because same-family review misses what a different family catches.

## Install

```
/plugin marketplace add IvanOboth/conductor-plugin
/plugin install conductor@agent-ops
```

Then `/conductor:conductor` (or just say "conduct this" / "orchestrate at high").

**Setting up a new machine?** [`AGENT-SETUP.md`](AGENT-SETUP.md) is a runbook written for an agent rather than a human — hand it to your coding agent and it will drive the whole setup: laptop CLIs, a remote Linux VM, Tailscale, Orca, this plugin, and an acceptance run. It has hard gates around the steps that can lock you out of your own box.

> If the marketplace clone fails (it goes over SSH, which needs a key on your GitHub account): `gh repo clone IvanOboth/conductor-plugin`, then `/plugin marketplace add ./conductor-plugin`.

### Without the plugin system

If you'd rather have the files in your own `~/.claude` tree:

```bash
gh repo clone IvanOboth/conductor-plugin
cd conductor-plugin && ./install.sh          # --dry-run to preview, --uninstall to remove
```

It copies the skills and agents into place, puts `ask-codex` and `ask-claude` on your PATH, and rewrites `${CLAUDE_PLUGIN_ROOT}` (which only resolves inside a real plugin) to absolute paths. You lose automatic updates — re-run it after a `git pull`.

For a whole team, commit this to the project's `.claude/settings.json` instead:

```json
{
  "extraKnownMarketplaces": {
    "agent-ops": { "source": { "source": "github", "repo": "<owner>/conductor-plugin" } }
  },
  "enabledPlugins": { "conductor@agent-ops": true }
}
```

## What's in the box

| Component | What it is |
|---|---|
| `skills/conductor` | The orchestration loop: model routing, lane table, dispatch, cross-verify, review HTML |
| `skills/codex-review` | Co-equal cross-family review of a diff, via the Codex CLI (GPT-6 Astra at `xhigh`) |
| `skills/codex-computer-use` | Codex (GPT-6 Astra) drives the running app and captures screenshots and video you then read |
| `skills/agent-browser` | Local browser automation CLI |
| `skills/run-report` | The closing convention — GitHub run report, labels, cost ledger |
| `agents/design-lane` | Opus 5 @ `xhigh` — taste-critical surfaces |
| `agents/bulk-lane` | Opus 5 @ `low` — mechanical work that still needs repo idiom |
| `agents/verify-lane` | Opus 5 @ `max` — adversarial verification |
| `agents/write-lane` | Fable 5.1 @ `high` — high-stakes prose: counterparty mail, proposals, board and investor documents, the final edit of a codex-written draft |
| `bin/ask-codex` | Codex wrapper; lands on the Bash tool's PATH automatically. `--effort LEVEL` sets the lane's reasoning effort (`low`…`max`, or `ultra` to let the lane fan out to its own subagents) |
| `bin/ask-claude` | The reverse direction — reach real Claude from a Codex session or a proxied main loop. Strips `ANTHROPIC_*` proxy vars by default so a "second opinion" can't silently be your own model answering |
| `scripts/conductor-report.py` | Telemetry — parses the session + codex rollouts, emits a cost table |

## Prerequisites

Conductor degrades gracefully — a missing piece disables that lane, it doesn't break the skill. But you get the full value only with all of these:

**Required for the Claude lanes**
- Claude Code with access to Opus-class models. `model: "opus"` and `model: "fable"` (Fable 5.1 as of 2026-09-01) must be available on your plan, or the design/judgment/writing lanes silently fall back to your session model — which defeats the routing.

**Required for the Codex lanes** (execution, `codex-review`, `codex-computer-use`)
- Codex CLI installed and authenticated: `npm install -g @openai/codex`, then `codex login`. Set `model = "gpt-6-astra"` in `~/.codex/config.toml` (the routing assumes it; GPT-5.6 Sol is retired from every lane as of 2026-09-05).
- Without it, cross-family verification degrades to Claude reviewing Claude — precisely the failure mode this plugin exists to avoid. Conductor will still run; the independence guarantee will not.
- Check your own effort setting: `~/.codex/config.toml` → `model` and `model_reasoning_effort`. These are independent of the Claude session's effort.

**Required for browser verification**
- `npm install -g agent-browser` (used by both the Claude and Codex verification lanes).

**Optional**
- `gh` CLI, authenticated — only for `run-report`'s GitHub steps. Without it, run-report closes with the in-session summary and the review HTML, which is a valid close.
- Python 3 — for the telemetry ledger, and for `ask-claude --stream` (which pipes Claude's stream-JSON through a small Python filter). Everything else works without it.

## Model routing

The routing table lives in `skills/conductor/SKILL.md` and is the plugin's own source of truth — it isn't read from your `CLAUDE.md`. The short version: **effort is the first knob, not the model tier.** Re-run a lane at higher effort before escalating to a more expensive model, and drop effort before dropping to a cheaper family. Cost is per task, not per token, and a tie-breaker only; when the axes conflict for anything that ships, the axis the lane is about (reasoning for plans and reviews, autonomy for execution) > steerability > taste > cost per task.

Adjust the table to your own pricing and plan — it's directional, not universal.

## Cost note

Conductor spends less than Ultracode by spending deliberately, not by spending little. Dispatched lanes bill to *your* account: Opus lanes against your Claude plan, codex lanes against your OpenAI account. A large fan-out is still a large bill.

## License

MIT
