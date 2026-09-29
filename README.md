# Conductor

Orchestration for Claude Code and Codex, with mixed-model and Codex-first profiles.

The main loop stays the orchestrator at `high` effort and never delegates three things: **the plan, the work orders, the final review.** Since 29 Sep 2026 the default Conductor profile routes implementation and most other lanes to Opus 5.5 (effort ceiling `high`). GPT-6.1 Sol at `high` is the only GPT model in routing: the main cross-family reviewer of Claude-authored work, runtime and computer-use verification, bug exploration and investigation, ops and business-workflow automation, and the Codex overflow when Claude quota is tight. Critical reviews run it at `xhigh`, which is also the retry when a `high` pass comes back thin. It replaces GPT-6 Astra and GPT-6 Sol, which are no longer routed. Fable 5.1 at `high` handles critical review, critical design and high-stakes writing. GPT-6 Luna takes bounded high-volume items such as intake packets. A change is critical when it deploys to production or changes production data; touches auth, payments, money or personal data; is a schema or data migration; is hard to reverse; is a client-facing deliverable; or changes the routing and agent configuration itself. Every Codex lane names its model with `-m gpt-6.1-sol` and its effort with `--effort`, and needs Codex CLI 0.159.0 or later. Conductor Core runs on GPT-6.1 Sol with optional Opus 5.5 contributions and explicit same-model review coverage. Conductor Claude runs every role on Opus 5.5 and Fable 5.1, for runs with no Codex quota at all.

## Conductor Claude

Use `/conductor-claude` in Claude Code when there is no Codex lane to dispatch to: every ChatGPT account is in cooldown, Codex is unreachable on the host, or the work must stay inside one vendor. Check first — `codex-account pick` exiting 3 means every account is cooling down, while a silent `ask-codex` is usually a wrapper or sandbox failure, not a quota failure.

[Claude's policy](skills/conductor-claude/SKILL.md) keeps the shared plan / work-order / final-review contract and routes mechanical work to Opus 5.5 Low, implementation to Medium, terminal and infra work to Medium (High when hard), design work to High, and ambiguity, synthesis, high-stakes writing and review of Opus-authored work to Fable 5.1 High. It replaces the cross-family gate with ranked substitutes — fresh-context artifact-only review first, cross-model Fable/Opus second, one lens per reviewer third, objective gates fourth, effort asymmetry last — and forbids the `cross-family` label, reporting `cross-model, fresh context`, `same-model, fresh context`, `objective-gate` or `orchestrator-only` instead. It adds a quota budget for the single shared pool and the failure modes a single family creates.

## Conductor Core

Use `$conductor-core` in Codex or `/conductor:conductor-core` in Claude Code. With personal skill installation, `/conductor-core` is the Claude entry point. Launch the parent in Codex on GPT-6.1 Sol High for a workflow with no Claude dependency; invoking the skill in a Claude parent does not change that parent's model.

[Core's policy](skills/conductor-core/SKILL.md) keeps the parent on GPT-6.1 Sol High and makes GPT-6.1 Sol High the primary worker for implementation, refactors, routine execution and every runtime or computer-use check. A separate fresh-context GPT-6.1 Sol reviewer at XHigh reviews GPT-6.1 Sol-authored work, labelled `same-model, fresh context`; GPT-6.1 Sol High reviews Luna-authored work, labelled same family. Opus 5.5 High is optional for useful design or cross-family review contributions. Fable is never selected. Work can complete without Claude, with honest review coverage and the same task evidence requirements.

Fan-out follows the enumerated work: no artificial worker cap, token ceiling or fixed Opus-call allowance. Real harness and machine limits still apply, and excess work queues without dropping coverage. The two profiles share the [report and evidence contracts](skills/conductor/SKILL.md#report-design-contract); the Core policy replaces mixed-model routing and mandatory Claude review gates within a Core run. Selecting Core does not migrate scheduled jobs or change the default `$conductor` profile.

## Install

```
/plugin marketplace add IvanOboth/conductor-plugin
/plugin install conductor@agent-ops
```

Then `/conductor:conductor` (or just say "conduct this" / "orchestrate at high").

**Setting up a new machine?** [`AGENT-SETUP.md`](AGENT-SETUP.md) is a runbook written for an agent rather than a human — hand it to your coding agent and it will drive the whole setup: laptop CLIs, a remote Linux VM, Tailscale, Orca, this plugin, and an acceptance run. It has hard gates around the steps that can lock you out of your own box.

> If the marketplace clone fails (it goes over SSH, which needs a key on your GitHub account): `gh repo clone IvanOboth/conductor-plugin`, then `/plugin marketplace add ./conductor-plugin`.

### One source for personal Claude and Codex skills

For a maintained local checkout, use the link-only installer:

```bash
./install.sh --link-skill
```

It installs shared Conductor, Conductor Core, Conductor Claude and mobile-app-testing entry points: Claude links to the canonical skill directories in this checkout. To install only one, run `python3 scripts/link-personal-skills.py --skill conductor-core` (or `--skill conductor-claude`, `--skill mobile-app-testing`). Conductor Claude installs to the Claude root only — a Claude-family-only profile has no meaning from a Codex parent. For Codex it writes a small discoverable `SKILL.md` that instructs the agent to read that same canonical file; the entry contains no separate policy. On the tested Codex 0.154.0 build, `skills/list` omitted symlinked skills, so a symlink alone was not a working installation. The installer honors `CLAUDE_CONFIG_DIR` and `CODEX_HOME` when configured, otherwise their normal home locations.

Prior skill directories or links are backed up privately, and failures roll back changed entries. The plugin includes the Codex UI metadata. Unknown supporting files remain preserved in the backup rather than silently merged into plugin source. CLI binaries are untouched. The checkout must remain available. Run the installer separately on each host; synchronization transports content, not this installation topology. This mode installs only the shared skill entry points, not the full plugin or its dependencies. The legacy copy installer below is a separate mode; do not use its uninstall operation to remove link-only installations.

The plugin skill is the canonical source for light editorial reports, plain-language explanations, useful diagrams/flowcharts and selective video evidence. It contains small harness-specific tool sections rather than separate Claude and Codex variants. Before revising a report, reread the source: updating a file cannot replace old skill text already injected into a running conversation. Released plugin versions remain snapshots until an updated release is installed.

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
| `skills/conductor-core` | Codex-first profile: GPT-6.1 Sol High parent and workers, Luna for bounded volume, work-sized fan-out, optional Opus, no Fable dependency |
| `skills/conductor-claude` | Claude-only profile: Opus 5.5 + Fable 5.1 lanes, substitutes for the cross-family gate, quota budget, honest coverage labels |
| `skills/codex-review` | Cross-family review of a diff, via the Codex CLI (GPT-6.1 Sol at `high` by default; `xhigh` for critical changes) |
| `skills/mobile-app-testing` | Native Android/iOS QA: GPT-6.1 Sol device execution, sign-in diagnosis, scoped fixes, evidence and cleanup; project profiles keep it reusable |
| `skills/codex-computer-use` | Codex (GPT-6.1 Sol at `high`) drives the running app and captures screenshots and video you then read |
| `skills/agent-browser` | Local browser automation CLI |
| `skills/run-report` | The closing convention — GitHub run report, labels, cost ledger |
| `agents/design-lane` | Opus 5.5 @ `high` — taste-critical surfaces; Fable 5.1 @ `high` when the surface is critical |
| `agents/bulk-lane` | Opus 5.5 @ `low` — mechanical sweeps, one lane per item; GPT-6.1 Sol at `high` is the overflow |
| `agents/exec-lane` | Opus 5.5 @ `medium` — implementation, refactors, migrations, terminal and CI work, volume writing |
| `agents/verify-lane` | Fable 5.1 @ `high` — adversarial verification of critical Opus-authored changes; routine work gets the GPT-6.1 Sol `high` review |
| `agents/write-lane` | Fable 5.1 @ `high` — high-stakes prose: counterparty mail, proposals, board and investor documents, the final edit of another lane's draft |
| `bin/ask-codex` | Codex wrapper; lands on the Bash tool's PATH automatically. `--effort LEVEL` sets the lane's reasoning effort (`low`…`max`, or `ultra` to let the lane fan out to its own subagents) |
| `bin/ask-claude` | The reverse direction — reach real Claude from a Codex session or a proxied main loop. Strips `ANTHROPIC_*` proxy vars by default so a "second opinion" can't silently be your own model answering |
| `scripts/conductor-report.py` | Telemetry — parses the session + codex rollouts, emits a cost table |

## Prerequisites

Core needs an authenticated Codex runtime for its required lanes; Claude is optional. The following Claude requirements apply to the default mixed-model profile and to optional Claude lanes, not to Core completion:

**Required for the Claude lanes**
- Claude Code with access to Opus-class models. `model: "opus"` (Opus 5.5 as of 2026-09-22) and `model: "fable"` (Fable 5.1 as of 2026-09-01) must be available on your plan, or the design/judgment/writing lanes silently fall back to your session model — which defeats the routing.

**Required for the Codex lanes** (execution, `codex-review`, `codex-computer-use`)
- Codex CLI 0.159.0 or later, installed and authenticated: `npm install -g @openai/codex`, then `codex login`. Older builds (0.156.1 checked 29 Sep 2026) are refused by the server for `gpt-6.1-sol` under a ChatGPT login. Every lane passes `-m` and `--effort`, so the routing does not depend on the `model` in `~/.codex/config.toml`; `gpt-6.1-sol` with `model_reasoning_effort = "high"` matches the default. Account homes that still default to `gpt-6-sol` get the superseded model whenever `-m` is omitted.
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
