---
name: conductor
description: Ultracode-grade mixed-model orchestration WITHOUT the Ultracode premium. The main loop stays the orchestrator (any model, run at `high`) and never delegates the plan, the work orders, or the final review — everything else is dispatched to cheaper/specialist lanes. Opus 5 takes design-sensitive and judgment work (at high/max effort; Fable only as escalation); GPT-5.6 Sol (codex CLI) takes mechanical execution, independent second-opinion review, checks, and browser verification with screenshots. Use whenever the user says /conductor, "conduct this", "orchestrate at high", "optimized ultracode", "mixed-model ultracode", "use opus + codex", "have codex verify", or asks for a multi-stream build where token cost should be optimized without losing review quality. Prefer this over plain Ultracode when the task has clearly separable design vs mechanical vs verification lanes.
effort: high
---

# Conductor — mixed-model orchestration at `high`

**The premise.** Ultracode is not a model — it's `xhigh` reasoning plus a standing "workflow everything, cost be damned" instruction. You don't need either to fan out: the `Workflow` and `Agent` tools work at any effort. Conductor gets Ultracode-grade output for a fraction of the cost by keeping the main loop at `high`, invoking fan-out **on-demand**, and spending the expensive/high-judgment tokens only where judgment lives — decomposition, work orders, review, integration.

**The orchestrator never delegates three things: the plan, the work orders, the final review.** Everything else is dispatched. This holds whichever model runs the main loop.

## When to invoke (on-demand, not always)

Reach for conductor's fan-out when the work has **separable lanes** — design vs mechanical vs verification — or a **work-list to pipeline** over, or a **finding that needs independent verification** before it ships. For a single-file edit, a lookup, or tightly-coupled work where lanes would thrash the same files, skip it and work inline (or use plain all-Claude `Workflow` for tightly-coupled fan-out). Don't force a task to split that doesn't want to.

## Sizing the fan-out

**Lane count follows the work, not a habit.** The three lane *kinds* (design / mechanical / verification) and the three bundled lane *agents* are a taxonomy and a menu — not a quota. One `design-lane` definition can be dispatched twelve times in one run. If the work-list has 20 independent items, that's 20 agents, not 3.

**The size guideline is a ceiling, not a target.** `large` means *up to* 50, never *aim for* 50. Five items get five agents; twenty get twenty; one coupled change gets one. Derive the count from the work-list you actually scouted, then check it against the ceiling — never the reverse. Both directions are failures, and they cost differently: under-fanning silently drops coverage, over-fanning burns tokens and buys nothing. Splitting five items into twenty agents by inventing sub-tasks, or stacking redundant verifiers on a finding nobody disputes, is the same error as batching twenty files into four agents.

Match the count to the shape of the work:

| Shape | Sizing |
|---|---|
| Independent items (files, endpoints, findings, sources) | **One agent per item.** Don't batch items into a single agent to keep the count down — that's how coverage gets silently dropped. |
| Adversarial verification of a finding | 3 refuters, or 3 distinct lenses when the finding can fail in more than one way |
| Competing approaches worth weighing | 3-5 independent attempts + judges, not one attempt iterated |
| Discovery of unknown size (bugs, edge cases) | Loop until 2 consecutive rounds find nothing new — a fixed count misses the tail |
| One coupled change | 1 agent. Splitting coupled work costs more than it saves. |

**Spend the width where the agents are cheap.** A 30-file mechanical sweep is the *right* place for a wide fan-out — `gpt-5.6-sol` via codex, or `opus` at `effort: 'low'`, one agent per file. Cheap per-agent cost is exactly what makes breadth affordable; hedging to 4 agents there buys nothing and leaves 26 files unexamined. Reserve narrowness for expensive lanes (`xhigh`/`max` judgment), not cheap ones.

**Wide also survives interruption better.** On resume, cached results stop at the first agent that didn't finish and everything started after it re-runs — so many small agents preserve far more progress than a few long ones.

**The real limits** (none of which is 3):

| Limit | Value |
|---|---|
| Session size guideline | `small` <5 · `medium` <15 (default) · `large` <50 · `unrestricted`. **Advice, not a cap** — a task that calls for more overrides it. Set via `workflowSizeGuideline` in settings or `/config`. |
| Concurrent agents | up to 16 (fewer on limited cores). Excess **queues** — passing 100 items still completes all 100. |
| Total agents per run | 1,000 |
| Items per `parallel()`/`pipeline()` call | 4,096 (hard error above, never silent truncation) |
| Token budget | A "+500k"-style directive is a hard ceiling; `agent()` throws once spent |

Claude Code flags runs above 25 agents (or ~1.5M projected tokens) as `Large workflow` in the task panel. That warning is advisory — it doesn't pause anything. If the work-list justifies the count, proceed; if you bound coverage for cost (top-N, sampling, no-retry), **`log()` what you dropped** so a partial sweep never reads as a complete one.

The restraint elsewhere in this skill — "don't force a task to split", "don't dispatch what a few tool calls would finish" — is about *unnecessary* splits and orchestrator laziness. It is not a reason to under-serve genuinely parallel work.

## Model routing

Rankings, higher = better. **Intelligence** is how hard a problem the model can be handed unsupervised. **Taste** covers UI/UX, code quality, API design, and copy. **Cost** is directional, not list price.

| model       | cost | intelligence | taste |
|-------------|------|--------------|-------|
| gpt-5.6-sol | 9    | 8.3          | 5     |
| opus-5      | 6    | 8.8          | 8.5   |
| fable-5     | 2    | 9            | 9     |

Effort is a **separate dial from model tier**, and it moves intelligence more than a tier change does. Read Opus 5's intelligence as ~8.8 at `xhigh`/`max` and ~8 at `medium`.

| effort   | send it |
|----------|---------|
| `low`    | mechanical work with exact anchors, where only repo idiom is at stake |
| `medium` | well-specified implementation against a clear contract |
| `high`   | orchestration, design lanes, ordinary review |
| `xhigh`  | hard judgment, adversarial verification, taste-critical surfaces |
| `max`    | the call that must not be wrong |

**How to apply:**

- These are defaults, not limits. If a cheaper lane's output doesn't meet the bar, re-run with more effort or a smarter model without asking. Judge the output, not the price tag — escalating costs less than shipping mediocre work.
- Cost is a tie-breaker only. When axes conflict for anything that ships: **intelligence > taste > cost**.
- **Effort, not tier, is the first knob.** Before escalating opus → fable, re-run the same lane at higher effort. Before dropping opus → codex for cost, drop effort first.
- **Bulk / mechanical** (clear-spec implementation, data analysis, migrations, refactors with exact anchors): `gpt-5.6-sol` via codex. When the mechanical work still needs repo idiom to land right, `opus` at `low`/`medium` is the cheap Claude alternative — don't reach for `fable` for bulk.
- **User-facing** (UI, copy, API design) needs taste ≥ 7: `opus` (default) or `fable`.
- **Reviews of plans/implementations**: `opus` at `xhigh`/`max` is the default judgment lane. Escalate to `fable` when Opus at `max` has already missed, or when taste *is* the whole deliverable. Add `gpt-5.6-sol` as an extra *independent* (different-family) perspective — a cross-family review catches what same-family review misses, and that is the entire value of the codex verify lane.
- **Never use Haiku** for judgment work.
- **Never pay for Fast mode on a dispatched lane.** Same intelligence at 2× the price, just faster tokens — it's for interactive work where a human is watching, never for a background agent.

## The lanes

| Lane | Model | Transport | Send it |
|------|-------|-----------|---------|
| Judgment | Orchestrator (main loop, `high`) | main loop | Plan, work orders, reviewing every lane's output, integration, the user-facing summary |
| Design | Opus 5 (default) / Fable (escalation) | `Agent` with `model: "opus"` (or the bundled `design-lane` agent), or Workflow `agent(prompt, {model: 'opus', effort: 'xhigh'})` | Components, visual grammar, copy with taste — anything where "looks right" is the acceptance test |
| Execution | GPT-5.6 Sol | `Bash` → `ask-codex` (writes to the working tree) | Well-specified mechanical work: refactors, migrations, test authoring, wiring a defined API, sweeps with clear anchors |
| Diff review | GPT-5.6 Sol | `codex-review` skill (or `Bash` → `ask-codex --readonly`) | Adversarial second-opinion review of a diff — the independent, different-family pass before it ships |
| Runtime verification (mechanics) | GPT-5.6 Sol | `codex-computer-use` skill | Cheap unattended confirmation that the *running* app works — launch it, drive `agent-browser`/simulator, capture screenshots into a directory you then Read, assert against the acceptance check |
| Runtime verification (judgment) | Opus 5 | `Agent` with `model: "opus"` driving `agent-browser` (own `--session`) | Multi-step flows where "did this actually work correctly" needs judgment, not just a green console |

The signature move: each lane is checked by the **other model family**. The two GPT-5.6 Sol verification lanes have dedicated skills — reach for `codex-review` for diffs and `codex-computer-use` for the running app rather than hand-rolling the invocation.

**Bundled agents.** This plugin ships three pre-tuned lane agents with `model:` and `effort:` already set — `design-lane` (opus/xhigh), `bulk-lane` (opus/low), `verify-lane` (opus/max). Use them via the `Agent` tool when you want the effort pinned regardless of session effort; the plain `Agent` tool has no `effort` parameter of its own, so a subagent dispatched without one of these inherits the session's effort.

## Orchestrator calibration (read before sizing lanes)

- **Write work orders that assume self-verification.** Opus 5 verifies its own work unprompted. "Double-check your output", "add a final verification step", "spawn a verifier" in a work order produces over-verification and burned tokens, not more rigour — **delete that scaffolding**. Your own cross-family gate (§3) is the verification that matters, and it stays.
- **Cap the fan-out you hand a lane.** Opus 5 reaches for subagents readily. If a design lane could recurse, say so explicitly in the order: *"do this yourself; do not spawn subagents"* — or give an explicit ceiling. Same goes for you as orchestrator: don't dispatch what a few tool calls would finish inline.
- **Scope discipline in the order.** Opus 5 can widen a task it judges under-specified. State what NOT to touch *and* that it should flag a concern in a sentence rather than re-scoping the work.

## The loop

**1. Plan (orchestrator).** Decompose into work orders. A work order that produces good results from a non-orchestrator model is *precise*: exact file paths and line anchors, the data contracts involved, the acceptance check ("the roster renders 4 rows at 390px with no horizontal scroll"), and what NOT to touch. Vague orders waste the cheap model's run and your review time. Scout the code yourself first — the 10 minutes grounding anchors is what makes the cheap lanes cheap.

**2. Dispatch (parallel).** Note the run's start time so the closing telemetry window is tight. If the run has a tracking issue, flip its label to in-flight (`gh issue edit <n> -R <owner>/<repo> --add-label status:running`). Optionally register the run so it shows as active on a dashboard — skip silently if you don't run one:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/conductor-report.py" --start \
    --run-id <YYYY-MM-DD-slug> --repo <repo> --issue "<repo>#<n>" --title "<short title>"
```

Then launch independent lanes in the same turn:

- Design lanes via the `Agent` tool (`model: "opus"` / `"fable"`, or the bundled `design-lane` agent) or a `Workflow` script (`agent(prompt, {model: 'opus', effort: 'xhigh'})`). Workflow when there's fan-out/pipelining — it's also where you can set per-lane effort inline; plain `Agent` for 1-2 lanes.
- Codex lanes via `Bash` with `run_in_background: true`:
  ```bash
  ask-codex --context work-order.md "Execute this work order. Write a summary of files changed to <scratchpad>/codex-N-report.md when done."
  ```
  Write the work order to a file first (`--context` carries it); have codex leave its report at a known path — its stdout is session-log noise, the report file is the deliverable. For verification lanes add `--readonly` and have it save screenshots to a named directory.
- To run GPT-5.6 Sol *inside* a `Workflow` (the `model:` param only accepts Claude models), spawn a thin wrapper agent (`model: 'fable'`, `effort: 'low'`) whose prompt writes a self-contained codex prompt, runs `ask-codex` via Bash, and returns the result.
- **File collision rule:** no two write-lanes share a file. Codex has no worktree isolation — if two write-lanes must touch the same file, serialize them or give the file to one lane and a follow-up order to the other.

**3. Cross-verify (cheap, different eyes).** Each lane's work is checked by the *other* model family.

- Claude built UI → `codex-computer-use` verifies the running app: run the type checks, drive `agent-browser` (its own `--session` name — never the shared one), capture screenshots at the viewports that matter into `<scratchpad>/verify/`, and write a findings report.
- Codex executed a refactor → an Opus 5/Fable lane (or you, if small) reviews the diff for taste and idiom drift; for a heavier independent pass on the diff itself, use `codex-review`.
- You **Read the screenshots yourself.** GPT-5.6 Sol confirms mechanics ("page loads, no console errors"); only you and the taste lane judge whether it *looks* right. Never accept "verified" on a visual change without seeing the pixels.

**4. Review + integrate (orchestrator).** Read every lane's report and the actual diffs (`git diff --stat` then the files that matter). Rejected work goes back as a *revised work order* — say what was wrong and what correct looks like, don't re-explain the whole task. You run the final typecheck/push/build gates yourself; lanes lie less than summaries but gates don't lie at all.

**5. Publish the review HTML (orchestrator).** Create or update the run's HTML review file (see *Run review HTML* below) with what happened / what's proposed, decision diagrams, and the verification screenshots + recordings, then `open` it for the user.

## Codex CLI facts

- Config lives at `~/.codex/config.toml` — `model` and `model_reasoning_effort` are the two keys that matter. **Read it rather than assuming its contents**; effort there is independent of the Claude session's effort. Override per-invocation with `ask-codex -m MODEL` or `codex exec -c model_reasoning_effort=xhigh`.
- Two transports, same engine: `ask-codex` (bundled at `${CLAUDE_PLUGIN_ROOT}/bin/ask-codex`, on PATH once the plugin is installed) shells out to `codex exec`. The direct equivalents are `codex exec -s <sandbox> "<prompt>"` (execution/verification) and `codex exec review` / `codex review` (diff review — `--uncommitted`, `--base <branch>`, `--commit <sha>` scope it).
- `ask-codex` flags: `--context FILE` (attach work order), `--readonly` (read-only sandbox — always use for pure investigation/review), `--clean` (strip session logs), `--output FILE` (codex writes its answer to a file — prefer this over parsing stdout), `-m MODEL` (override). Sandbox modes on `codex exec`: `read-only`, `workspace-write` (default), `danger-full-access` (only when it must act outside the working tree).
- Wrapper quirk: with `--clean`, the answer can print *after* the `--- End Codex Response ---` marker — read the tail of output, or better, use `--output`/report-files and skip stdout parsing entirely.
- Codex CAN run shell commands (tests, `agent-browser`, `open`, `screencapture`, simulators) inside its sandbox in write mode — this is how it does **computer-use verification headlessly** (see the `codex-computer-use` skill). Full GUI pointer/keyboard control of arbitrary apps is a **Codex desktop-app plugin** (`@Computer` / `@AppName`), not reachable from a headless shell-out.
- Long runs: launch with `run_in_background: true` and a generous timeout; you get notified on completion. Multiple codex lanes run fine in parallel.
- Parallel *write* lanes need isolation: codex has no worktree isolation of its own, so two codex write-lanes touching the same file collide. Serialize them, or run each via an `Agent`/`Workflow` wrapper with `isolation: 'worktree'`.

## Run review HTML (mandatory deliverable)

Every conductor run produces a refined HTML review file on top of the in-session summary — the close of a run includes "here's the HTML review: `<path>`" and an `open <path>` so it's on screen. Written for *review*, not as a log: executive, skimmable, easy to understand at a glance.

- **Location + reuse:** `<repo>/.conductor/reports/` (create it; ensure `.conductor/` is gitignored). Key the file by issue when the run has one — `issue-<n>.html` — else by run-id (`<YYYY-MM-DD-slug>.html`). **Update-in-place rule:** if a report already exists for this session or this issue, update that file (revise proposals, append the new run as a dated section) instead of minting a new one.
- **Content:** what was asked; what happened *or what's being proposed*; decisions made and why (including options rejected); per-lane outcomes; evidence; residual risk and next steps. If the run is a proposal rather than a build, the HTML is the proposal document.
- **Diagrams:** use them wherever they beat prose — decision trees for choices made, before/after architecture, lane/data flow. Inline SVG or styled HTML/CSS preferred; mermaid via CDN script is acceptable (the file is local, no CSP).
- **Screenshots:** embed every verification screenshot that mattered. Base64 data URIs keep the file self-contained; drop large originals in `.conductor/reports/assets/<run-id>/` and reference them. Caption each with viewport + what it proves.
- **Video/GIF where possible:** when a runtime-verification lane drives a flow, record it — chrome MCP `gif_creator`, Playwright context video, or macOS `screencapture -v` — save to the assets dir and embed (`<img>` for GIF, `<video controls>` for mp4). When recording isn't feasible, fall back to a captioned screenshot sequence of the flow.
- **Styling:** dark, refined, data-dense — match the executive register (headings distinct from body, monospace for paths/metrics). One self-contained file; it must render offline except for an optional mermaid CDN tag.

## Review gates (non-negotiable)

- No lane's work is "done" until you've read its diff or its screenshots — reports are claims, not evidence.
- Anything user-facing (copy, layout, empty states) gets a taste-lane (Opus 5 at `xhigh`, or Fable) or orchestrator eye before it ships, regardless of which lane built it.
- Verification lives in *your* gates, not in the work orders. A lane that was told to self-verify has told you nothing you can audit — read the diff or the pixels yourself.
- If a codex lane's diff smells like it fought the codebase (new helpers duplicating existing ones, style drift), stop dispatching that class of work to it and either tighten the work order or move the work to a taste lane. Note what happened for the session summary.
- Same end-gates as any build: project typecheck, push, and browser verification before telling the user it's done.

## Closing step: run-report

Every conductor run ends by invoking the **`run-report`** skill: post the run report (what/tests/evidence/decisions/cost) as a comment on the run's issue/PR — include the review HTML's path in that comment — flip `status:*` labels, and append the telemetry ledger. A run without a report is invisible work.

If the run has no GitHub issue and no ledger configured, `run-report` degrades to the in-session summary plus the review HTML — that is a valid close, not a failure.

## Worked example (shape, not script)

> Task: "Add CSV export to the admin actions view, and make sure nothing regressed."

1. You scout: the view is `admin/actions/+page.svelte`, data comes from `getOrgActions`, export needs a new query arg or client-side serialization — decide client-side, cap honesty note required.
2. Dispatch in one turn: **codex (write)** — implement the CSV serialization + download button per work order with exact anchor lines; **taste lane** — n/a this time (no design surface beyond a button — the work order specifies the exact button grammar to reuse).
3. On completion: **codex (readonly)** — verify: typecheck, load the page via agent-browser, export a CSV, assert row count matches the on-screen count, screenshot the button placement to `verify/`.
4. You: Read the screenshot (button grammar right?), read the diff, run the final gates, summarize.
5. You: write/update `.conductor/reports/issue-<n>.html` — decision diagram (client-side vs query-arg export, and why), the diff summary, the button screenshot, and the export-flow GIF from the verify lane — then `open` it: "here's the HTML review."

## Appendix — running under a proxied orchestrator (optional)

Skip this section unless you route Claude Code's main loop through a local proxy to a non-Claude model (e.g. CLIProxyAPI serving GPT-5.6 Sol). **Detect it:** run `echo "$ANTHROPIC_BASE_URL"` — a `127.0.0.1` URL means proxied mode. This inverts the usual arrangement: the proxied model holds the judgment lanes and does most execution itself; Claude becomes the dispatched taste / second-family lane.

- **The `Agent`/`Workflow` `model:` param cannot reach Claude models** through such a proxy — it has only the proxy's auth, so `model: "opus"` silently remaps and `model: "fable"` errors. Never dispatch a taste lane via `Agent`/`Workflow` in this mode; it would be the same model reviewing itself.
- **Taste/design/judgment lanes go via an env-stripped shell-out to real Claude**, which uses your own Claude login directly (never add Claude auth to the proxy):
  ```bash
  env -u ANTHROPIC_BASE_URL -u ANTHROPIC_AUTH_TOKEN -u ANTHROPIC_MODEL \
      -u ANTHROPIC_DEFAULT_OPUS_MODEL -u ANTHROPIC_DEFAULT_SONNET_MODEL \
      -u ANTHROPIC_DEFAULT_HAIKU_MODEL -u ANTHROPIC_SMALL_FAST_MODEL \
      -u CLAUDE_CODE_SUBAGENT_MODEL \
    claude --model opus --dangerously-skip-permissions \
      -p "$(cat work-order.md)

Write your report to <scratchpad>/claude-N-report.md when done." \
      --output-format text < /dev/null
  ```
  `--model opus` for taste/design lanes; `--model claude-fable-5` when the lane needs top-shelf judgment. Write the work order to a file first; launch long lanes with `run_in_background: true` and a generous timeout — the report file is the deliverable. Same file-collision rule as codex lanes: these shell-outs write to the shared working tree with no isolation.
- **Codex lanes are unchanged** but become *same-family* with the orchestrator. Cross-family verification therefore routes the other way: send diff-taste review and anything user-facing to a Claude shell-out lane, and treat `codex-review` as a mechanics-only second pass, not the independent perspective.
- Everything else holds: the orchestrator still never delegates the plan, work orders, or final review; still Reads screenshots itself; still runs the end gates and closes with `run-report`.
