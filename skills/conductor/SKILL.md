---
name: conductor
description: Coordinate mixed-model work across Claude Code and Codex. Keep the current main agent responsible for grounding, work orders, integration and final acceptance; delegate bounded execution and independent review when worthwhile. Produce readable explanatory HTML reports with evidence chosen for the task. Use for /conductor, $conductor, "conduct this", "orchestrate at high", "mixed-model build", "use opus + codex", "use Claude and Codex", "have codex verify", "have codex write the blocks", "writing lane", "mixed-model ultracode", or a multi-stream build requiring independent implementation and review.
---

# Conductor — mixed-model orchestration

## Profile scope

This entry point selects the default mixed-model profile. For Codex-first orchestration with optional Opus and no Fable dependency, use [Conductor Core](../conductor-core/SKILL.md). For a run with no Codex lane at all — every ChatGPT account in cooldown, Codex unreachable, or the work must stay in one vendor — use [Conductor Claude](../conductor-claude/SKILL.md), which carries every role on Opus 5.5 and Fable 5.1 and replaces the cross-family gate with context-independent, cross-model review under honest coverage labels. Each profile owns model selection, fan-out and review acceptance while it is active. When `profile: conductor-core` is active, that profile owns model selection, fan-out and review acceptance throughout the run, including supporting skills and bundled-agent defaults. The mixed-model mandates below do not override it. Core shares this file's installation, report design, explanation, delivery and evidence-selection contracts; its own policy replaces Claude-specific reviewer requirements within those sections. Ordinary `$conductor` behavior is unchanged.

**What this is for.** Conductor exists to accomplish work that is too large, too long-running or too multi-stranded for one agent in one pass — a migration across a repository, a feature with design and data and copy strands, an epic that spans sessions, a research or document build that runs for hours. The unit of ambition is the *run*, not the turn. Everything below — the work orders, the lanes, the review gates, the report — is machinery for holding a large piece of work together well enough that it finishes and can be trusted. **Verification is a part of that machinery, not its purpose.** The restraint sections exist so the capacity goes where it produces work, and are not a reason to attempt less.

**The premise.** Ultracode is not a model — it's `xhigh` reasoning plus a standing "workflow everything, cost be damned" instruction. You don't need either to fan out: the `Workflow` and `Agent` tools work at any effort. Conductor gets Ultracode-grade output for a fraction of the cost by running the main loop on Opus 5.5 at `high`, invoking fan-out **on-demand**, and spending the expensive/high-judgment tokens only where judgment lives — decomposition, work orders, review, integration.

**The orchestrator never delegates three things: the plan, the work orders, the final review.** Everything else is dispatched. This holds whichever model runs the main loop.

## Model selection contract — 29 September 2026

**Opus 5.5 is the default model for almost every role and writes the code: `medium` for implementation and execution; `high` for the main loop, design, bug hunts and review.** `high` is the ceiling for Opus 5.5; when an Opus 5.5 lane at `high` falls short, move to Fable 5.1 at `high` or a cross-family attempt instead of raising effort. **GPT-6.1 Sol (`gpt-6.1-sol`) at `high` is the only GPT model for reviewing, exploring and computer use (29 Sep 2026).** It takes the cross-family review of all Claude-authored work, runtime and computer-use verification, investigation and exploration, bug exploration and the cross-family second attempt on a bug hunt, ops and business automation, and Codex overflow. It runs at `xhigh` for critical reviews and as the retry when a `high` pass came back thin, and never at `max` by default. It is strong at review and exploration and weaker at writing code, so Opus 5.5 implements. GPT-6 Luna runs at `high`. Fable 5.1 runs at `high`, for critical review, critical design, high-stakes writing, ambiguous architecture and the second attempt. Select another effort only for an explicit user request or a concrete task-specific reason recorded in the work order; role names and duration alone do not raise effort. Higher review effort still requires observed failure evidence. This policy overrides conflicting effort recommendations in supporting skills. A skill cannot change the effort of an already-running parent or worker.

This contract governs the routing sections below. Select a role before launching, and record the model, effort, task-specific reason and acceptance criteria in the work order's `routing.json`.

| Work | Model | Effort |
|---|---|---|
| Bounded routine intake candidate packets | gpt-6-luna | high |
| Codex overflow: mechanical sweeps and well-specified implementation when Claude quota is tight | gpt-6.1-sol | high |
| Well-specified implementation | claude-opus-5-5 | medium |
| Runtime mechanics and computer-use verification | gpt-6.1-sol | high |
| Stateful execution, recovery, long execution of an established plan | claude-opus-5-5 | medium |
| Investigation and exploration that does not change code | gpt-6.1-sol | high |
| Design, bug hunts, review of Fable- or GPT-authored work | claude-opus-5-5 | high |
| Bug exploration and the cross-family second attempt on a bug hunt | gpt-6.1-sol | high |
| Critical design surfaces | claude-fable-5-1 | high |
| Ambiguous architecture, sustained reasoning and synthesis | claude-fable-5-1 | high |
| Judgment review of critical Opus-authored work | claude-fable-5-1 | high |
| Cross-family review of Claude work (routine); review before an unattended merge | gpt-6.1-sol | high |
| Cross-family review of critical Claude work; retry when a `high` pass came back thin | gpt-6.1-sol | xhigh |
| Ops, runbook and business-workflow automation; agentic science | gpt-6.1-sol | high |

**Critical** means any of: it deploys to production or changes production data; it touches auth, payments, money or personal data; it is a schema or data migration or otherwise hard to reverse; it is a client-facing deliverable (proposal, deck, flagship UI surface); or it changes the routing and agent configuration. Decide it per work order and record it in `routing.json`. Critical Opus-authored work gets GPT-6.1 Sol at `xhigh` for the cross-family review and Fable 5.1 at `high` for the judgment review; routine work gets the GPT-6.1 Sol `high` cross-family review plus the orchestrator's own read of the diff.

Long horizon means hours of work or continuity across sessions; duration and file count alone do not select a model. Route by the work's bottleneck. Higher review effort requires observed failure evidence and a separately recorded reason. The reviewer is always a different model from the author, and cross-family review needs a different family: a GPT model reviewing GPT work (GPT-6.1 Sol on Luna output, for example) is same-family and is labelled so, and Opus 5.5 does not adversarially review its own work. For Fable- or GPT-authored work, the review lane is Opus 5.5 at `high`. GPT-6.1 Sol reviews, explores and verifies runtime behaviour; it does not judge design or write the plan. Luna never reviews.

Luna intake is advisory: use the constrained packet runner through the Codex ChatGPT login. It cannot dispatch workers, change labels, advance intake state or hold merge authority. Scripts handle empty rounds; ambiguity goes to the capable orchestrator. The runner and live collector/poller integration are tracked in IvanOboth/ivan-oboth#85; a skill edit alone does not change scheduled jobs.

The launcher selects the orchestrator model. Conductor guides that orchestrator's worker selection. Orca supplies worktrees and terminals; the command passed to the terminal determines the worker model. Pass model and effort explicitly, never rely on parent defaults. Use configured agent frontmatter or a CLI when the available Agent tool cannot set effort. Workers receive bounded orders and no recursive fan-out unless explicitly budgeted. Existing lanes retain their launch settings.

## One source and current instructions

This is the shared Conductor skill for Claude Code and Codex. The maintained source is `skills/conductor/SKILL.md` in the Conductor plugin repository. Personal entry points use a directory link or a minimal discovery file that reads that source; edit the resolved source, not separate harness variants. Use `scripts/link-personal-skills.py` from the checkout to establish local links. On every new report or substantial report revision, reread the current Report design contract and evidence gate from disk before authoring and before publication. A previously injected skill, older report or saved template may contain stale instructions; do not use it as the current design authority. This cannot update text already loaded into another running session: that session needs to reread the source.

## Installation paths

For a plugin installation, use `${CLAUDE_PLUGIN_ROOT}` for bundled scripts. For a checkout linked through personal skill entry points, resolve this SKILL.md symlink and use its plugin root (the directory containing `skills/`, `scripts/` and `agents/`); set `CLAUDE_PLUGIN_ROOT` to that resolved directory in shell calls using the examples below. The legacy copy installer rewrites these script paths to its installation directory. Do not infer the plugin root from the working repository.

Bench-specific report commands and metadata below apply only on Ivan’s configured Bench. On other hosts, use the configured report delivery surface, preserve its access boundary and verify the served file; do not require Ivan’s private vault, hostname or report helper.

## Harness-specific tools, shared contract

The current main agent remains the orchestrator, whether it is Claude or Codex. The plan, work orders, report requirements, evidence policy and acceptance gates below are shared. A skill does not change the model running the parent session. Use only the tools available in that harness, within its actual concurrency and permission limits; no table below grants capabilities or authorization.

- **Claude Code parent:** use its available Agent/Workflow tools for Claude lanes and `ask-codex` for Codex execution. Named bundled agents are optional and may be used only when installed. Claude-only APIs, options and background notifications in the examples apply to this path.
- **Codex parent:** use collaboration agents for bounded Codex execution when available, and `ask-claude --plan --model <model> --context <order>` for independent Claude review. Use `ask-claude --accept-edits` only for an authorized writable lane with exclusive file ownership. Specify the model according to the routing policy and the installed bridge contract. Codex does not acquire Claude Agent/Workflow tools by reading this skill. A Codex child is the same model family, not an independent cross-family reviewer.
- **Waiting:** use the actual harness completion mechanism. Claude background jobs may notify automatically; Codex must resume a running tool session with its wait/poll API when required. Do useful independent work while waiting, and keep Ivan informed. Do not assume a shell bridge delivers native agent notifications.
- **Safety and ownership:** preserve dirty user changes and serialize overlapping writes. Respect the user's authorized scope for commits, pushes, PRs, issue comments, messages and deployments; a closing checklist does not grant permission. Never deploy to production without explicit authorization.
- **Independent review:** check the implementing family with the other family. For a Codex-authored change, another Codex review is mechanics-only. For visual quality, use Claude to judge screenshots; inspect the actual artifacts and run objective acceptance checks in the main loop.

## Orca lanes or one session?

Decided 17 Sep 2026, measured on the live bench. Tokens are the same either way — each lane is a fresh context — so the real cost is lifecycle and integration, not spend. An Orca lane leaves a 330–530 MB Claude session plus its MCP children (Playwright, Chrome) running until someone closes it, and it ends at a draft PR nobody integrates once the orchestrator is gone. On 17 Sep the bench carried 235 live Orca terminals, 227 of them silent for 7+ days (28 Claude sessions, 13 Codex, 32 Playwright MCP, 19 Chrome), swap 11 of 15 GB used with 17 GB RAM free, and 152 worktrees against 84 on 14 Sep.

- **Default: one session.** Epics and the night shift run as a conductor run right here — `Agent`/`Workflow` lanes, `isolation: "worktree"` for writers (auto-cleaned when unchanged), cross-family review, merge behind the gates, one review page. The run ends its lanes when they finish and integrates in the same run.
- **Orca lanes only** when Ivan wants to watch or steer a lane live, or when the lane must outlive the orchestrator (a multi-hour build). Orca's value is visibility and steering, not parallelism.
- **Lifecycle rule for every Orca lane:** the terminal closes when its lane-report is written (`orca terminal close --terminal "$ORCA_TERMINAL_HANDLE" --json` as the lane's last command; the poller does this itself since #94, `POLLER_KEEP_TERMINAL=1` to keep one open); the worktree is removed after its PR merges (`orca worktree rm --worktree path:<path> --run-hooks --json`, never `--force` on a dirty tree); an evidence page is produced (`tools/evidence-page.py`).
- The idle reaper closes what slips through (terminals idle > 24 h) and the dashboard shows the terminal budget. Acceptance: a week after install the terminal count stays flat while the night shift runs, and every lane in the Orca sidebar is live or closed within an hour of its report.

## When to invoke (on-demand, not always)

Reach for conductor's fan-out when the work has **separable lanes** — design vs mechanical vs writing vs verification — or a **work-list to pipeline** over, or a **finding that needs independent verification** before it ships. For a single-file edit, a lookup, or tightly-coupled work where lanes would thrash the same files, skip it and work inline (or use plain all-Claude `Workflow` for tightly-coupled fan-out). Don't force a task to split that doesn't want to.

## Turn-by-turn or Workflow — pick the orchestration mode

Once lanes are earned, choose who holds the plan. There are two modes, and both are legitimate:

- **Turn-by-turn** — you are the orchestrator. Lanes go out as `Agent` calls (they show in the footer's agent switcher) or background `Bash` → `ask-codex` (they show as shell calls in the transcript). You decide the next step after each result, and each result lands in your context.
- **`Workflow`** — a script is the orchestrator. The runtime runs `agent()`/`parallel()`/`pipeline()` in the background, intermediate results stay in script variables, and only the final return reaches your context. It shows as a phased progress line in the task panel and in `/workflows`.

| Signal | Mode |
|---|---|
| 1–2 lanes, or 3 lanes of different kinds with no shared shape | Turn-by-turn |
| The next lane's order depends on a judgment you make after reading the previous result (a spec check, a design choice, a failed lane) | Turn-by-turn — a Workflow takes no mid-run input |
| A single Codex lane, or Codex lanes you want to adjust between | Turn-by-turn (`Bash` → `ask-codex`) |
| An enumerated work-list of 3+ independent items (files, issues, endpoints, sources) | **Workflow** — `pipeline()` one agent per item |
| Findings that must be adversarially verified before they are reported | **Workflow** — review → verify pipeline, so a finding verifies as soon as its review lands |
| Competing drafts or approaches to be judged against each other | **Workflow** — `parallel()` attempts + judge agents |
| A fix-until-green or find-until-dry loop | **Workflow** — the loop lives in the script |
| A run long enough that an interruption would hurt | **Workflow** — completed agents resume from cache in the same session |

Codex lanes inside a Workflow go through a thin wrapper agent (`model: 'opus'`, `effort: 'low'`) that runs `ask-codex -m <model> --effort <level>` via Bash and returns the report — the wrapper adds a small Claude cost, which a work-list of 3+ items repays in resume and visibility. Mixed runs are normal: scout and hold the judgment calls turn by turn, then hand the enumerated wave to a Workflow, then review its result turn by turn. Never dispatch a pinned taste or judgment lane (`design-lane`, `verify-lane`) to scout — reading config files and finding consumers is your grep, whichever mode you are in.

## What earns an agent (gate this before sizing anything)

Sizing answers *how many*. This answers *whether* — and it runs first. Getting this wrong is more expensive than getting the count wrong, because a wasted agent costs its full run and returns nothing.

**Scouting is your job, not a lane.** Step 1 says scout the code yourself, and it means with `Grep`, `Glob`, `Read`, and `Bash` — not by dispatching agents to go look. Delegated discovery is the single most common waste in a conductor run: the agents burn a full context each, come back with prose you then have to re-verify, and answer worse than the grep you could have run in two seconds. **If a grep, find, `ls`, `git log`, or file read would answer it, run the command.** An orchestrator that doesn't know the codebase yet is not ready to write work orders — and reading it yourself is what makes the work orders precise enough for cheap lanes to succeed.

**Every agent needs a deliverable contract.** Before dispatching, name the artifact that comes back: a file written, a diff applied, a report at a known path, a verdict with citations. An agent told to "investigate X and report findings" has no completion condition — it wanders, then goes idle without delivering. If you can't state what lands when it's done, you don't have a work order yet.

**An agent must be worth more than it costs.** An agent pays a fixed overhead every time: loading context, understanding the order, reporting back. That overhead only earns out when the item needs real reading, reasoning, or writing. **If an item is one tool call — a single mutation, one CLI invocation, a two-second edit — run it inline no matter how many items there are.** Four `npx convex run` calls are four seconds of your own turn; four agents to make those same calls is four agent-lifetimes to save nothing. This is orthogonal to coupling: items can be perfectly independent and still not worth an agent each.

**Work that's already parallel downstream doesn't need agent parallelism.** Async provider jobs (renders, builds, CI, queued API work) run concurrently on their own side. Submitting N of them is N calls; the concurrency lives in the provider. Agents assigned to "wait for" those jobs are idle agents — submit, then read the results when they land.

**Name the real reason when you go inline.** "It's a coupled chain" and "each item is one tool call" are different arguments, and only one of them is usually true. Reaching for *coupled* when the reason is *small* mislabels the case and generalizes badly — 20 independent file edits can be described as "an ordered chain" if you squint, and that's how genuinely parallel work gets serialized. State which it is.

**Fan out over a work-list you already have — never to produce one.** Discovery is one cheap step you run yourself (`grep -rl`, `git diff --name-only`); the fan-out is what happens *to the items it returns*. Spawning agents to find the items inverts that and pays the most for the least.

Three questions before any dispatch:

1. **Could a shell command answer this?** → Run the command.
2. **What artifact does this agent return?** → No answer means no dispatch.
3. **Is this discovery or execution?** → Discovery is yours. Execution and verification fan out.
4. **Is the item bigger than the agent's overhead?** → One tool call per item means inline, however many items there are.

A run whose agents mostly *looked things up* has the shape inverted. The scouting is cheap and yours; the expensive parallelism belongs downstream of it.

## Sizing the fan-out

**Lane count follows the work, not a habit.** The four lane *kinds* (design / mechanical / writing / verification) and the four bundled lane *agents* are a taxonomy and a menu — not a quota. One `design-lane` definition can be dispatched twelve times in one run. If the work-list has 20 independent items, that's 20 agents, not 3.

**The size guideline is a ceiling, not a target.** `large` means *up to* 50, never *aim for* 50. Five items get five agents; twenty get twenty; one coupled change gets one. Derive the count from the work-list you actually scouted, then check it against the ceiling — never the reverse. Both directions are failures, and they cost differently: under-fanning silently drops coverage, over-fanning burns tokens and buys nothing. Splitting five items into twenty agents by inventing sub-tasks, or stacking redundant verifiers on a finding nobody disputes, is the same error as batching twenty files into four agents.

Match the count to the shape of the work:

| Shape | Sizing |
|---|---|
| Independent items (files, endpoints, findings, sources) — **already enumerated** | **One agent per item.** Don't batch items into a single agent to keep the count down — that's how coverage gets silently dropped. |
| Finding out *what* the items are | **Zero agents.** That's a grep, and it's yours. |
| Adversarial verification of a finding | 3 refuters, or 3 distinct lenses when the finding can fail in more than one way |
| Competing approaches worth weighing | 3-5 independent attempts + judges, not one attempt iterated |
| Open-ended hunting where the *answer set* is unknown (bugs, edge cases, security holes) | Loop until 2 consecutive rounds find nothing new — a fixed count misses the tail. Distinct from scouting: no grep answers "what bugs exist", but a grep does answer "which files exist". |
| One coupled change | 1 agent. Splitting coupled work costs more than it saves. |
| Many items, but each is a single tool call (mutations, CLI invocations, one-line edits) | **0 agents — inline.** Independent ≠ worth an agent. Agent overhead exceeds the work. |
| Jobs that run async on a provider (renders, builds, CI) | **0 agents.** Submit them, then read results. The provider is the parallelism. |

**Spend the width where the agents are cheap.** A 30-file mechanical sweep is the *right* place for a wide fan-out — `opus` at `effort: 'low'` (`bulk-lane`), or `gpt-6.1-sol` at `high` via codex as the overflow (`gpt-6-luna` at `high` when the sweep only classifies or extracts), one agent per file. Cheap per-agent cost is exactly what makes breadth affordable; hedging to 4 agents there buys nothing and leaves 26 files unexamined. Keep the expensive lanes (Fable 5.1 and `high` judgment) narrow instead.

**Wide also survives interruption better.** On resume, cached results stop at the first agent that didn't finish and everything started after it re-runs — so many small agents preserve far more progress than a few long ones.

**The real limits** (none of which is 3):

| Limit | Value |
|---|---|
| Session size guideline | `small` <5 · `medium` <10 (default; `small` on Pro) · `large` <50 · `unrestricted` — per the Claude Code workflows docs. **Advice, not a cap** — a task that calls for more overrides it. Set via `workflowSizeGuideline` in settings or `/config workflowSizeGuideline=large`; the Workflow tool's own description and the `Running in background` line name the value actually in force — read it there rather than trusting a config file's claim. |
| Concurrent agents | up to 16 (fewer on limited cores). Excess **queues** — passing 100 items still completes all 100. |
| Total agents per run | 1,000 |
| Items per `parallel()`/`pipeline()` call | 4,096 (hard error above, never silent truncation) |
| Token budget | A "+500k"-style directive is a hard ceiling; `agent()` throws once spent |

Claude Code flags runs above 25 agents (or your chosen guideline's count) or ~1.5M projected tokens as `Large workflow` in the task panel. That warning is advisory — it doesn't pause anything. If the work-list justifies the count, proceed; if you bound coverage for cost (top-N, sampling, no-retry), **`log()` what you dropped** so a partial sweep never reads as a complete one.

The restraint elsewhere in this skill — "don't force a task to split", "don't dispatch what a few tool calls would finish" — is about *unnecessary* splits and orchestrator laziness. It is not a reason to under-serve genuinely parallel work. But it applies with full force to discovery: width is for executing and verifying a known work-list, never for assembling one.

## Long-horizon runs

A run that spans hours or sessions fails for different reasons than a run that fits in one turn. It does not usually fail on reasoning; it fails because state was held only in a context that ended. Three things make a large run survive.

**The work-list is an artifact, not a memory.** Write it to a file — the items, their owners, their status (queued / running / done / blocked), and the deliverable path for each. A run that keeps its plan only in the orchestrator's context loses the plan at compaction, at a usage limit, or when a session ends. When the work-list is on disk, any later session — or you after compaction — resumes by reading it.

**Phase the ambition, don't flatten it.** An epic is waves, not one enormous fan-out. Wave 1 establishes the contract (the schema, the shared component, the interface everything else depends on) and is usually one or two lanes. Wave 2 fans wide over the items that now have a stable contract to write against. Wave 3 integrates and verifies. Dependencies between waves are the reason phases exist; `Workflow`'s `phase()` names them, and `pipeline()` lets an item's later stage start as soon as its earlier stage lands rather than waiting for the slowest sibling.

**Checkpoint at boundaries.** At the end of each wave, persist what exists: commit the lanes that landed, update the work-list, and write what remains. Interrupted work that was committed is recoverable; interrupted work held in a lane's context is gone. This is why long write lanes commit incrementally rather than saving everything for a final message, and why many small lanes beat a few long ones — on resume, cached results stop at the first unfinished lane and everything after it re-runs.

**Resuming.** A `Workflow` resumes with `resumeFromRunId`: completed `agent()` calls with unchanged prompts return cached results instantly and only edited or new calls re-run. Stop the prior run before resuming it. For a run that outlived its session entirely, the work-list file plus the committed branches are the resume point — read them, re-scout what changed, and dispatch only what remains.

**Context handoff (issue #17).** A run that outlives its context window ends in compaction, which keeps the session alive but reduces the plan, the decisions and the process rules to a summary. Hand off before that. The `context-watch` hook (installed with the plugin, or by `scripts/install-context-hook.py` for a linked checkout) reads this session's usage after every tool call. At 70% (`CONDUCTOR_HANDOFF_PCT`) it tells you, again at 85% (`CONDUCTOR_HANDOFF_NOW_PCT`) and every 5 points after, and it blocks one stop per level. At 70%, decide: if the run finishes within the remaining context, carry on. Otherwise:

1. **Checkpoint.** Finish or stop the step in flight and start no new wave. Background `Agent`/`Workflow` lanes report to this session, so let them land, or stop them and list them as open. Codex lanes can keep running: the successor reads their `--output` file. Commit what landed, update the work-list, and update the run's status comment (if it has one) to say a successor is taking over. This is the old session's last issue edit.
2. **Write the continuation order** at `.conductor/work-orders/<run>-continue.md` (next to the original order; mikono #896's `issue-896-continue.md` is the model). It tells the successor to load this skill and read the original order, the work-list and any shared contract, then gives: **state at handoff** (merged, open and not-started items, each with its PR or branch, head SHA and next action; anything running and where its report will land); **decisions already taken** (do not reopen); **follow-ups filed**; **where status is reported** (the status comment id and how to edit it, Orca comments); **resources this run owns** (dev servers, browser sessions, test deployments, worktrees) and who closes them; **process rules learned in this run** (the commands, helper scripts and traps that cost time); **owed at the end** (review HTML, closing comment, session log). It ends with the unattended-lane paragraph, because the successor usually runs without Ivan watching. The order must stand alone: the successor knows only what it says and what is on disk.
3. **Run `conductor-handoff --order <path>`.** It opens an Orca terminal in the same worktree with this session's model, effort and permission mode, sends `/<skill> Read <order> …`, records the handoff in `.conductor/handoffs.jsonl`, renames this tab "(handed off)" and silences the watch. Without Orca it exits 3 and prints the command for Ivan to run. It refuses a fourth handoff in two hours: a run that keeps handing off is not converging, so stop and tell Ivan.
4. **Stand down.** From this session: no merges, pushes, deploys, issue or comment edits, or dispatches. Answer the successor's questions. Forward any late lane result with `orca terminal send --terminal <new terminal> --text "…" --enter` (the handle is printed and in `handoffs.jsonl`), and tell Ivan in two lines (the context %, the new terminal, the order file). Leave the old tab open for Ivan to read; it is renamed "(handed off)" and the idle reaper closes it after 24 hours.

The successor is a new conductor run on the same work-list: it re-scouts what changed, then dispatches only what remains.

**Scope honestly as it grows.** A long run discovers work. New items go on the work-list with a status, not silently into a lane. If the run will not finish within the budget or the window, say so while there is still time to choose what gets dropped, and `log()` what was dropped so a partial result never reads as a complete one.

## Model routing

Rankings, higher = better. **Cost** is cost *per task*, not price per token — a model that finishes in a quarter of the tokens is cheaper at twice the price. **Reasoning** covers plans, reviews and judgment calls. **Autonomy** is how far a model gets unsupervised in a terminal, a browser or an ops loop. **Steerability** is whether it does what the work order said, no more and no less. **Taste** covers UI/UX, code quality, API design and copy in a UI. **Writing** is prose a human reads and judges the author by.

| model       | cost/task | reasoning | autonomy | steerability | taste | writing |
|-------------|-----------|-----------|----------|--------------|-------|---------|
| opus-5.5    | 9         | 9.3       | 9.3      | 7.5 †        | 9 †   | 8.5 †   |
| fable-5.1   | 5         | 9.2       | 8.8      | 8.5          | 9     | 9       |
| gpt-6.1-sol | 9.5       | 8.9 §     | 9.1 §    | 9 §          | 5.5 § | 6.5 §   |
| gpt-6-luna  | 10        | 7.2 ‡     | 7.4 ‡    | 8.5 ‡        | 4 ‡   | 6 ‡     |

† Provisional (22 Sep 2026): the only evidence so far is Anthropic's own and early-tester quotes. Re-rate after two weeks of lanes. Adjust these numbers to your own plan and pricing; they are directional, not universal.

‡ Provisional (23 Sep 2026): GPT-6 Luna was released on 22 Sep 2026. These ratings are provisional internal routing estimates, not vendor or Artificial Analysis scores; steerability, taste and writing are unmeasured. Re-rate by 7 Oct 2026.

§ Provisional (29 Sep 2026): from OpenAI's 29 Sep charts (vendor-reported, via Vellum) for GPT-6.1 Sol. Taste and writing are unmeasured. Re-rate by 13 Oct 2026.

**What changed on 22 Sep 2026:** Opus 5.5 (`claude-opus-5-5`) replaced Opus 5 and became the default model for almost every lane. The `opus` alias resolves to it.

**The evidence.** Opus 5.5 costs $4/$20 per Mtok, with cache reads at $0.20 against Fable 5.1's $10/$50 and $0.25. On Anthropic's table it beats Fable 5.1 on every row: Terminal-Bench 4.0 66.4 vs 55.8, FrontierCode 54.4 vs 50.3, CursorBench 57.8 vs 51.8, GDPval-AA 1846 vs 1735, HLE 67.7 vs 65.6, OSWorld 2.0 81.8 vs 80.7. Those Opus figures are at `max` effort (Terminal-Bench at `xhigh`). Against GPT-6.1 Sol the published comparisons are OSWorld 2.0 (Opus 5.5 81.8 at `max` vs GPT-6.1 Sol 71.4 at `max`) and AutomationBench, where GPT-6.1 Sol scores 35.4–36.0% against Opus 5.5 `medium`'s 33.2%. Independent evidence so far comes only from Artificial Analysis: Opus 5.5 tops its Intelligence Index, and four of its five effort levels sit on the cost/intelligence frontier, below Fable 5.1's cost at the same score. No SWE-bench Pro, Arena or practitioner steerability data exists yet.

**Effort.** Anthropic's Terminal-Bench cost curve sets the effort. Opus 5.5 at `medium` scores about 57% for about $3 per attempt. At `high` it scores 64.2% for $3.88. `xhigh` adds about two points for double the cost, and `max` scores lower than `xhigh`. So:

| effort   | send it |
|----------|---------|
| `low`    | Opus 5.5 mechanical sweeps with exact anchors, where only repo idiom is at stake |
| `medium` | Opus 5.5 implementation, execution, investigation that changes code, and volume writing |
| `high`   | Opus 5.5 main loop, design, bug hunts and review; every Fable 5.1 lane; every GPT-6.1 Sol lane by default; every Luna lane |
| `xhigh`  | GPT-6.1 Sol only: critical cross-family reviews, and the retry when a `high` pass came back thin. Never Opus 5.5, and never `max` by default |

**`high` is the ceiling for Opus 5.5.** Do not assign it `xhigh` or `max`. When an Opus 5.5 lane at `high` falls short, the next step is Fable 5.1 at `high` or a cross-family attempt. Opus 5.5 thinks more per effort level than Opus 5 did, so set effort explicitly on every lane and do not carry old `xhigh` settings forward. Never run Fable at `low` for anything that must look something up. Read `~/.codex/config.toml` for the Codex default rather than assuming it, and pass `--effort` per lane.

**Where GPT-6.1 Sol fits (29 Sep 2026).** GPT-6.1 Sol (`gpt-6.1-sol`) is the only GPT model for reviewing, exploring and computer use. It is strong at review and exploration and weaker at writing code, so Opus 5.5 implements. It runs at `high` by default, at `xhigh` for critical reviews and as the retry when a `high` pass came back thin, and never at `max` by default. It takes:
- the cross-family review of all Claude-authored work: routine at `high`, critical at `xhigh` beside Fable 5.1 at `high`, and the review before an unattended merge (the bench poller reviews with it at `high`);
- runtime mechanics and computer-use verification on web, CLI, simulator and native GUI, via `codex-computer-use` and `mobile-app-testing`;
- bug exploration and the cross-family second attempt on a bug hunt;
- investigation and exploration lanes that do not change code;
- ops, runbook and business-workflow automation, and agentic science;
- Codex overflow (mechanical sweeps and well-specified implementation when Claude quota is tight), and availability insurance. It implements only as that overflow, or in Conductor Core, where every worker is Codex.

The evidence (OpenAI's 29 Sep charts via Vellum, vendor-reported): DeepSWE v1.1 75.2% at `high` for about $1.50 a task; OSWorld 2.0 (computer use) 71.4% at `max` for about $1.30 a task, with no `high` figure published; AutomationBench 35.4–36.0% for about $0.30, against Opus 5.5 `medium`'s 33.2%; GDP.pdf 32.0% at `high`; a factual error rate of 7.7% at `low`. It costs $2/$10 per Mtok. None of these results establish performance at our configured efforts except where the effort is named.

**Retired 29 Sep 2026:** GPT-6 Astra and GPT-6 Sol left routing, and GPT-6.1 Sol replaces both. It beats GPT-6 Sol everywhere at the same price (DeepSWE 75.2% vs 68.8%, OSWorld 2.0 71.4% vs 64.4%, factual errors 7.7% vs 11.4%) and comes within about two points of Astra, or beats it, at a fifth to a seventh of the cost (DeepSWE 74.8% at about $7.70, OSWorld 2.0 73.5% at about $9.30, GDP.pdf 32.2%); Astra's one remaining lead, AutomationBench 41.4%, does not justify keeping it.

GPT-6.1 Sol needs **Codex CLI 0.159.0 or later**. The server rejects 0.156.1 under a ChatGPT login ("not supported when using Codex with a ChatGPT account"); this was verified on 29 Sep 2026 on all three ChatGPT accounts after upgrading. Check `codex --version` before the first lane. It runs on ChatGPT Pro quota: Codex lanes spend quota in a 5-hour window rather than dollars, so Codex is also the place for volume when Claude quota is tight. Treat its window under a ChatGPT login as 272K until measured (the API window is 1.05M); raise it per lane with `codex exec -c model_context_window=…` (in `ask-codex`, `-c` means `--context`), or split the order at about 200K. Its report format must be evidence, not claims.

**Where Luna fits (added 23 Sep 2026).** GPT-6 Luna (`gpt-6-luna`) is the cheap Codex tier, in the Codex model list under a ChatGPT login with a 272K window. It costs $0.10/$0.50 per Mtok. OpenAI's vendor figures report DeepSWE 66.6 at $0.22 per task and OSWorld 2.0 52.7 at $0.27 per task; Artificial Analysis reports $0.07 per index task. Luna takes bounded, high-volume work: intake candidate packets, classifying or extracting over many items, and first-pass checks whose result a stronger model reads; it never reviews. It runs at `high`, because a Luna task costs cents and OpenAI says it gains most from effort.

**Always pass the Codex model.** The Codex default is set per account home (`~/.codex/config.toml` or a rotated account's own home), and different homes can default to different models. The bench account homes default to `gpt-6.1-sol` at `high` (29 Sep 2026), but the Mac and new homes may not. A lane that leaves out `-m` gets whichever model its account defaults to. Every Codex lane names its model and effort: `ask-codex -m gpt-6.1-sol --effort high`, or `codex exec -m gpt-6.1-sol -c model_reasoning_effort=high`.

**Where Fable 5.1 fits.** Anthropic's rule is to start with Opus 5.5 and move to Fable 5.1 when Opus 5.5 still falls short on demanding reasoning or long-horizon work. No published measure yet puts Fable ahead. Fable keeps high-stakes voice writing (until an eval says otherwise), the judgment review of critical Opus-authored work (a different model from the author), critical design surfaces, ambiguous architecture, and the second attempt when Opus 5.5 has missed.

**How to apply:**

- These are defaults, not limits. If a lane's output doesn't meet the bar, re-run it at higher effort or on another model without asking. Judge the output, not the price tag.
- When axes conflict for anything that ships: **the axis the lane is about (reasoning for plans and reviews, autonomy for execution) > steerability > taste > cost per task**.
- **Effort first, up to the ceiling.** Before escalating Opus 5.5 → Fable 5.1, re-run the same lane at the next effort up to `high`. Past `high`, change the model instead.
- **Orchestrator:** Opus 5.5 at `high`. It holds the plan, the work orders and the final review, and it stays Claude: it needs the 1M window, the Claude Code harness and the skills, and cross-family review only exists if the reviewing lanes are the other family.
- **Implementation, refactors, migrations, terminal, CI and infra:** Opus 5.5 at `medium`, or `high` when the lane is hard. GPT-6.1 Sol is weaker at writing code: use it at `high` for well-specified implementation and mechanical sweeps only as Codex overflow when Claude quota is tight, and keep design judgment with Claude. Ops-, runbook- or business-automation-shaped lanes go to GPT-6.1 Sol at `high`.
- **Investigation and exploration** (tracing a behaviour, reading logs, mapping a subsystem) that does not change code: GPT-6.1 Sol at `high`. Opus 5.5 at `medium` when the lane must change code. Scouting for your own work orders stays yours (see **What earns an agent**).
- **Mechanical sweeps:** Opus 5.5 at `low` via `bulk-lane`, one lane per item. GPT-6.1 Sol at `high` is the overflow, and Luna at `high` takes sweeps that only classify or extract.
- **Messy repo-level bug hunts:** Opus 5.5 at `high`. GPT-6.1 Sol at `high` explores and gives the cross-family second attempt; Fable 5.1 at `high` when both have missed.
- **Long-horizon lanes** (hours, or across sessions): Opus 5.5 at `medium`/`high` for execution of an established plan, with the unattended-lane paragraph in the order (see **The loop**, step 2). Use Fable 5.1 at `high` for ambiguous architecture or deep research, or when Opus 5.5 has fallen short. Documents, spreadsheets and decks built from a blank page default to Opus 5.5, with Fable as the escalation. Hours of runtime, a large repository or a long document do not alone choose the model.
- **User-facing design** (UI, copy in a UI, API design): Opus 5.5 at `high` via `design-lane`; Fable 5.1 at `high` when the surface is critical. Opus 5.5 falls back on stock styles when given no direction: a cream or off-white background, italic accent words in headings, numbered "01 / 02 / 03" section labels, monospace labels and pill-shaped buttons. The order bans them unless the project's design system already uses them; check what it chose instead and extend the list. Never send design to GPT-6.1 Sol.
- **Writing, high stakes** (a counterparty email, a proposal, an investor or board document, anything that carries the user's name and gets judged): Fable 5.1 at `high` via `write-lane`, until an eval shows Opus 5.5 matches it. Opus 5.5 at `high` is the cheaper alternative for long structured documents.
- **Writing, volume or structured** (film prompt packages and generated-video blocks, storyboards, shot lists, internal docs, first drafts, routine mail): Opus 5.5 at `medium`, with an instruction in the order to write plain, literal sentences and no mannered prose. Anything that leaves the building gets an edit pass. Every writing order states audience, register, length ceiling, the one thing the reader must do, banned phrases and a voice sample.
- **Reviews:** review with a different model from the author. Routine Opus-authored work: GPT-6.1 Sol at `high` via `codex-review` plus your own read of the diff. Critical Opus-authored work: GPT-6.1 Sol at `xhigh` plus Fable 5.1 at `high` (`verify-lane`). Fable- or GPT-authored work: Opus 5.5 at `high`. Every review order asks: "List only problems that block merge: file, line, why it is wrong, and how to show it fails. Mark anything you could not confirm." Raise review effort only after an observed failure, with a recorded reason; a GPT-6.1 Sol `high` pass that came back thin is such a failure, and the retry runs at `xhigh`.
- **Runtime verification (mechanics):** GPT-6.1 Sol at `high` on any surface you can hand steps and an assertion: web, CLI, simulator, native GUI. It is the other family and runs on quota. It confirms the thing functioned; the screenshots come back to Claude to judge whether it looks right.
- **Runtime verification (judgment while driving):** Opus 5.5 driving `agent-browser`, or GPT-6.1 Sol at `high` when the flow is mechanical and Codex quota is free.
- **High-volume bounded work** (intake packets, classifying or extracting over many items, first-pass checks): Luna at `high`. A stronger model reads its output before anything acts on it.
- **Cross-family routing is also availability insurance.** A setup with every lane on one family has a single point of failure.
- **Never use Haiku or Sonnet** for judgment work.
- **Never pay for Fast mode on a dispatched lane.** It buys the same intelligence at a premium for faster tokens. Keep it for interactive work a human is watching.

## The lanes

| Lane | Model | Transport | Send it |
|------|-------|-----------|---------|
| Judgment | Orchestrator (Opus 5.5, main loop, `high`) | main loop | Plan, work orders, reviewing every lane's output, integration, the user-facing summary |
| Design | Opus 5.5 (`high`) / Fable 5.1 (`high`, critical surfaces and escalation) | Bundled `design-lane` agent, or Workflow `agent(prompt, {model: 'opus', effort: 'high'})` | Components, visual grammar, copy with taste — anything where "looks right" is the acceptance test. The order names the stock patterns to avoid |
| Execution | Opus 5.5 (`medium`; `high` when the lane is hard) | Bundled `exec-lane` agent (opus/medium), or Workflow `agent(prompt, {model: 'opus', effort: 'medium'})` | Implementation, refactors, migrations, terminal, CI and infra, test authoring, wiring a defined API |
| Mechanical sweep | Opus 5.5 (`low`); GPT-6.1 Sol (`high`) as overflow | Bundled `bulk-lane` agent, one lane per item; overflow via `Bash` → `ask-codex -m gpt-6.1-sol --effort high` | Renames and contract sweeps with exact anchors |
| Bounded high-volume | GPT-6 Luna (`high`) | `Bash` → `ask-codex -m gpt-6-luna --effort high`, one lane per batch | Intake candidate packets, classifying or extracting over many items, first-pass checks; a stronger model reads the output before anything acts on it. Never review, verification or judgment calls |
| Investigation and exploration | GPT-6.1 Sol (`high`) | `Bash` → `ask-codex -m gpt-6.1-sol --effort high` | Tracing a behaviour, reading logs, mapping a subsystem, bug exploration and the cross-family second attempt on a bug hunt; the report cites file:line. Lanes that must change code go to Opus 5.5 |
| Ops execution | GPT-6.1 Sol (`high`) | `Bash` → `ask-codex -m gpt-6.1-sol --effort high` (writes to the working tree) | Ops-, runbook- or business-automation-shaped work. Well-specified implementation only as Codex overflow when Claude quota is tight; otherwise Opus 5.5 writes the code |
| Long reasoning | Fable 5.1 (`high`) | `Agent` with `model: "fable"`, or Workflow `agent(prompt, {model: 'fable', effort: 'high'})` | Ambiguous architecture, deep research, sustained reasoning and synthesis; the second attempt when Opus 5.5 has missed |
| Long execution | Opus 5.5 (`medium`/`high`); GPT-6.1 Sol (`high`) when ops-shaped | `Agent`/Workflow with the unattended-lane paragraph in the order | Execute an established plan across modules, tools or sessions |
| Writing (high stakes) | Fable 5.1 (`high`) | Bundled `write-lane` agent (`fable`/`high`) | Counterparty email, proposal, investor or board document — anything that carries the user's name and gets judged |
| Writing (volume) | Opus 5.5 (`medium`) | Bundled `exec-lane` agent (opus/medium) | Film prompt packages and generated-video blocks, storyboards, shot lists, internal docs, first drafts, routine mail — the orchestrator holds the brief and edits the draft; external copy gets an edit pass before it ships |
| Judgment review | Fable 5.1 (`high`) — `verify-lane` for critical Opus-authored work; Opus 5.5 (`high`) for Fable- or GPT-authored work | `Agent` with the bundled `verify-lane` agent, or `model: "opus"` | Adversarial review of a diff, a plan or a finding against its acceptance criteria; verdict + ranked findings with file:line |
| Diff review (cross-family) | GPT-6.1 Sol (`high`); `xhigh` for critical changes and for the retry when a `high` pass came back thin | `codex-review` skill (or `Bash` → `ask-codex -m gpt-6.1-sol --effort high`; `--effort xhigh` when critical) | Cross-family review of Claude-authored work on anything that ships — alone for routine work, beside Fable 5.1 at `high` for critical Opus-authored work |
| Runtime verification (mechanics) | GPT-6.1 Sol (`high`) | `mobile-app-testing` for native Android/iOS; `codex-computer-use` for web/other GUI | Run the app, capture task-selected evidence and independently assert the result. The mobile skill covers physical and virtual devices, project profiles, sign-in, native recording and cleanup. |
| Runtime verification (judgment while driving) | Opus 5.5 (`high`); GPT-6.1 Sol (`high`) when the flow is mechanical and Codex quota is free | `Agent` with `model: "opus"` driving `agent-browser` (own `--session`); `mobile-app-testing` or `codex-computer-use` for the GPT-6.1 Sol case, with the decision rule in the order | Flows with no pre-statable step list, where the next click depends on reading what's on screen |

The signature move: each lane is checked by the **other model family**. The GPT-6.1 Sol review and verification lanes have dedicated skills — reach for `codex-review` for diffs, `mobile-app-testing` for native Android/iOS, and `codex-computer-use` for other running surfaces rather than hand-rolling the invocation.

**Codex's runtime reach widened (verified 2026-08-07)** and the routing follows it. The bundled `computer-use` plugin registers a `node_repl` MCP server that `codex exec` loads, so a headless shell-out now reads accessibility trees, clicks, types, and screenshots *arbitrary macOS apps* — native apps, menu-bar flows, Xcode/Simulator GUI steps, Chrome under the real logged-in profile. Surfaces that used to be unverifiable without a human are now codex-lane work; send any runtime check you can state as steps + an assertion there, whatever the surface. What did **not** move is authority: GPT-6.1 Sol's taste is a provisional 5.5, so it confirms mechanics and you judge the pixels — and its cost per task is low enough that the verify lane runs on every run, not only the cheap ones. "Verified" from a codex lane means *it functioned*, never *it looks right*.

**Optional bundled agents.** When the Conductor plugin is installed, it supplies five pre-tuned lane agents with `model:` and `effort:` already set — `design-lane` (opus/high), `exec-lane` (opus/medium), `bulk-lane` (opus/low), `verify-lane` (fable/high — the adversarial review of Opus-authored work), `write-lane` (fable/high). The `opus` alias resolves to Opus 5.5. Use them via the `Agent` tool when you want the effort pinned regardless of session effort; the plain `Agent` tool has no `effort` parameter of its own, so a subagent dispatched without one of these inherits the session's effort.

## Native mobile verification

For Android/iOS application testing, read the bundled [mobile-app-testing skill](../mobile-app-testing/SKILL.md) and the target project's mobile profile before writing the device order. Default runtime execution to **gpt-6.1-sol** at `high`, including screen interpretation, authentication, state and recovery. Pass model and effort explicitly (`-m gpt-6.1-sol --effort high`). If the orchestrator is already GPT-6.1 Sol and owns the device, execute the run directly rather than creating a duplicate lane.

GPT-6.1 Sol owns the device session, scoped tests/fixes, native recordings, independent saved-state assertions and cleanup. Claude provides UI judgment under the current routing contract; the orchestrator reads the artifacts and retains final acceptance. Give one agent exclusive control of each device and mutable fixture. Mobile Next can drive physical or ADB-connected virtual devices; Genymotion supplies a cloud runtime. Inventory existing capability before asking for Mac SSH or adding a provider.

The work order names the artifact/build, backend/tenant, authentication reference, cases and assertions, platforms, ownership, evidence choice, authorized fixes/resources and cleanup. Native execution is a verification lane and is not covered by an implementation lane's instruction to avoid the UI. A built APK, unit tests or a mobile browser do not replace native results. Preserve failed runs and state final-build coverage precisely. Missing runtime access or visual-review quota remains an explicit gap; continue independent authorized work without claiming a pass. The mobile skill supplies device/recovery procedures; Conductor remains the evidence and report-design authority.

## Orchestrator calibration (read before sizing lanes)

Opus 5.5 behaviours to counter in the orders you write:

- **Unattended lanes can end a turn after a progress update.** Put the unattended-lane paragraph (see **The loop**, step 2) at the end of every dispatched order. Treat a lane's text-only ending as a report, not proof the work is done: check its work-list, and name the open items when you send it back.
- **It thinks more per effort level than Opus 5 did.** Set effort explicitly on every lane, never above `high`, and lower effort rather than prompting for less thinking. Remove "think carefully" instructions; effort is the control.
- **It gets to work quickly.** On tasks spread across mail, documents, sheets or records, tell it to look through the relevant sources before it changes anything.
- **It paces itself to elapsed time.** For a fan-out, put a time budget in each order ("aim to finish within 20 minutes") and set it somewhat above what you want spent. The budget is advisory, so keep your own timeout.
- **Delete self-verification scaffolding.** "Double-check your output", "add a final verification step" or "spawn a verifier" in a work order produces over-verification, not more rigour. Your own cross-family gate (§3) is the verification that matters, and it stays.
- **Give it the whole task and the finish line.** One order carries the complete task and a "Done means: …" line naming the observable end state (every endpoint uses the new client, the old client is deleted, the suite passes). Never ask a lane to write its reasoning out in the reply; on Opus 5.5 that can trip the `reasoning_extraction` refusal.
- **Ask for the report you want to read.** Lanes mark anything they could not confirm and say where they looked. An audit or migration fan-out gives each item its own lane, and the orchestrator checks each lane's evidence before accepting it and finishes with one table (item, result, evidence). The orchestrator's own close to the user uses three headings: **Needs you**, **Changed**, **Found**.
- **Cap the fan-out you hand a lane.** If a lane could recurse, say so in the order: *"do this yourself; do not spawn subagents"*, or give an explicit ceiling. The **What earns an agent** gate applies to you as orchestrator too.
- **Scope discipline in the order.** State what NOT to touch, and that the lane should flag a concern in a sentence rather than re-scope the work.

Fable 5.1 behaviours to counter in its orders: it may issue one tool call per turn ("request every independent item in one response"), it rewrites whole files for small edits ("targeted edits only"), and at `low` it answers from memory.

## The loop

**1. Plan (orchestrator).** Decompose into work orders. A work order that produces good results from a non-orchestrator model is *precise*: exact file paths and line anchors, the data contracts involved, the acceptance check ("the roster renders 4 rows at 390px with no horizontal scroll"), and what NOT to touch. Vague orders waste the cheap model's run and your review time. Scout the code yourself first — the 10 minutes grounding anchors is what makes the cheap lanes cheap.

**2. Dispatch (parallel).** Note the run's start time so the closing telemetry window is tight. If the run has a tracking issue, flip its label to in-flight (`gh issue edit <n> -R <owner>/<repo> --add-label status:running`). Optionally register the run so it shows as active on a dashboard — skip silently if you don't run one:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/conductor-report.py" --start \
    --run-id <YYYY-MM-DD-slug> --repo <repo> --issue "<repo>#<n>" --title "<short title>"
```

Every dispatched order ends with a time budget ("aim to finish within 20 minutes", set somewhat above what you want spent; keep your own timeout) and then this unattended-lane paragraph, verbatim. It is Anthropic's wording from the Opus 5.5 prompting guide. It goes in every dispatched lane's order, Claude or Codex, and never in the main loop, where the user may be there to answer:

> A standing instruction from the user, the person you are working for. It is about how your turns end. A message with no tool call in it ends your turn, and the work stops there until you are asked to continue. The user has seen you end turns in four ways while work they asked for was still owed, and does not want any of them. One: a long summary of what was done that closes by announcing the next step and has no tool call, so the next thing never starts. Two: an offer to carry on with something unless the user would prefer otherwise, which stops to wait for an answer the user was not going to give. Three: a list of decisions for the user when, by your own account, none of them blocks the rest of the work. Four: deciding that this is a good place to report, because the turn has been long or a milestone is done. Status notes are welcome, and so are your recommendations on open decisions, but put them in the same message as your next tool call and carry on with whatever does not depend on the user's answer. If you notice yourself inviting the user to redirect you or offering to wait, delete it and do the next thing. The stops the user does want are the ones where nothing can move without them, or where the thing blocking you is deliberately protected from you. This does not override the need for confirmation on risky or destructive actions.

Then launch independent lanes in the same turn:

- Claude lanes (execution, design, long-horizon, writing, review) via the `Agent` tool (`model: "opus"` / `"fable"`, or the bundled `design-lane` / `bulk-lane` / `verify-lane` / `write-lane` agents) or a `Workflow` script (`agent(prompt, {model: 'opus', effort: 'medium'})`; `effort: 'high'` for hard, design and review lanes). Pick the mode with **Turn-by-turn or Workflow** above; Workflow is also where you can set per-lane effort inline.
- Codex lanes via `Bash` with `run_in_background: true`:
  ```bash
  ask-codex -m gpt-6.1-sol --effort high --context work-order.md --output <scratchpad>/codex-N-report.md "Execute this work order. Your final message is the report: files changed, evidence, what you did not do."
  ```
  Write the work order to a file first (`--context` carries it) and pass `-m` and `--effort` every time — the config default is not the lane's. Use `-m gpt-6.1-sol --effort xhigh` for critical reviews and for the retry when a `high` pass came back thin, and `-m gpt-6-luna --effort high` for bounded high-volume lanes. `--output` makes the CLI save the final message to a known path; stdout is session-log noise, the report file is the deliverable. Verification lanes need a permitted write-capable execution mode (verify the wrapper and active configuration; do not assume a sandbox default) at `-m gpt-6.1-sol --effort high` — they write the screenshots or recordings selected by the evidence gate; do not pass `--readonly`: on the bench a read-only lane can succeed while reviewing only the prompt instead of the files. For a volume-writing lane the work order is the brief (audience, register, length ceiling, the reader's one action, banned phrases, a voice sample, and the block/section structure to keep) and `--output draft.md` is the deliverable.
- To run a GPT model (GPT-6.1 Sol or Luna) *inside* a `Workflow` (the `model:` param only accepts Claude models), spawn a thin wrapper agent (`model: 'opus'`, `effort: 'low'`) whose prompt writes a self-contained codex prompt, runs `ask-codex -m <model> --effort <level>` via Bash, and returns the result — the wrapper does no thinking of its own, so the cheapest Claude that can run a shell command is the right one.
- **File collision rule:** no two write-lanes share a file. Codex has no worktree isolation — if two write-lanes must touch the same file, serialize them or give the file to one lane and a follow-up order to the other.
- **Isolation:** writers get `isolation: "worktree"`; an Orca worktree is chosen only when the lane must be watched or steered live or must outlive the run, and then its terminal closes at lane-report.

**Claude-native background lanes: use completion notifications.** Background agents and background Bash are harness-tracked — when one finishes you are **re-invoked automatically** with its result. Writing a "bounded wait for lanes" loop, a sleep, or a repeated file-existence check buys you nothing and costs a shell command, tokens, and wall-clock per poll. Dispatch, then either work on something independent or end the turn; the notification is the wake signal.

For Codex tool sessions, follow the harness-specific waiting contract above. Other exceptions are state the harness cannot see:

- External systems with no notification path: a CI run, a deploy, a remote queue. Use `Monitor` with an until-condition, or a wakeup sized to how fast that state actually changes — not a 30-second tick.
- A codex lane whose *report file* is the deliverable and whose process has already exited. Read the file; don't wait for it.

If a lane hangs, that's a lane to stop and re-dispatch, not a lane to poll harder.

**3. Cross-verify (cheap, different eyes).** Each lane's work is checked by the *other* model family.

- Claude built UI → use `mobile-app-testing` for native Android/iOS and `codex-computer-use` for other surfaces: run the type checks, drive `agent-browser` (its own `--session` name — never the shared one) or, for a non-scriptable/native surface, `node_repl` + `@oai/sky`; capture screenshots at the viewports that matter into `<scratchpad>/verify/`, and write a findings report.
- Claude executed a change → GPT-6.1 Sol at `high` via `codex-review` reviews the diff as the cross-family pass (`xhigh` when the change is critical), and for critical Opus-authored work Fable 5.1 at `high` (`verify-lane`) gives the judgment review.
- Codex executed a refactor → an Opus 5.5 lane at `high` (or you, if small) reviews the diff for taste and idiom drift; `codex-review` can provide an additional mechanics pass.
- You **Read the screenshots yourself.** GPT-6.1 Sol confirms mechanics ("page loads, no console errors"); only you and the taste lane judge whether it *looks* right. Never accept "verified" on a visual change without seeing the pixels.
- Codex wrote the draft → you edit it against the brief, and anything external gets a `write-lane` (or Opus 5.5 `high`) pass before it ships. GPT-6.1 Sol confirms the structure held; the voice is judged by the Claude side.

**4. Review + integrate (orchestrator).** Read every lane's report and the actual diffs (`git diff --stat` then the files that matter). Rejected work goes back as a *revised work order* — say what was wrong and what correct looks like, don't re-explain the whole task. You run the final checks applicable to the requested change and authorized by the task. Skill/report edits do not imply application builds, device rental or release publication; source changes use their project gates. Verify actual output rather than accepting a lane summary.

**5. Publish the review HTML (orchestrator).** Create or update the run's HTML review file (see *Run review HTML* below) with what happened / what's proposed, decision diagrams, and the verification screenshots + recordings, then hand it to the user: on a desktop host `open` it; on a headless host (the bench — `~/reports` exists, no display) run `~/bin/sync-reports.sh` and give the **hub URL** `https://bench.tailb5d047.ts.net/reports/<repo>/<file>` — never a disk path, never `xdg-open`.

## Codex CLI facts

- Config lives at `~/.codex/config.toml` — `model` and `model_reasoning_effort` are the two keys that matter. **Read it rather than assuming its contents**; effort there is independent of the Claude session's effort. Override per-invocation with `ask-codex -m gpt-6.1-sol --effort high` (maps to `codex exec -m gpt-6.1-sol -c model_reasoning_effort=high`). **Always pass `-m` and `--effort` on every lane** (`gpt-6.1-sol` or `gpt-6-luna`); different account homes default to different models, so an omitted `-m` picks whichever model the rotated account defaults to.
- **GPT-6.1 Sol needs Codex CLI 0.159.0 or later** (`codex --version`). The server rejects 0.156.1 under a ChatGPT login ("not supported when using Codex with a ChatGPT account"); verified 29 Sep 2026 on all three ChatGPT accounts after upgrading.
- Two transports, same engine: `ask-codex` (on PATH (resolve with `command -v ask-codex`)) shells out to `codex exec`. The direct equivalents are `codex exec -m <model> -s <sandbox> "<prompt>"` (execution/verification) and `codex exec review` / `codex review` (diff review — `--uncommitted`, `--base <branch>`, `--commit <sha>` scope it).
- `ask-codex` flags: `--effort LEVEL` (per-lane reasoning effort — pass it every time; the config default is not the lane's), `--context FILE` (attach work order; a missing file is an error), `--readonly` (read-only sandbox; avoid it on the bench, where a read-only lane can succeed while reviewing only the prompt — use a write-capable mode and tell the lane not to edit; not for verification lanes, which write screenshots), `--clean` (strip session logs), `--output FILE` (codex writes its answer to a file — prefer this over parsing stdout), `-m MODEL` (pass it every time: `gpt-6.1-sol` or `gpt-6-luna`). Sandbox modes on `codex exec`: `read-only`, `workspace-write`, `danger-full-access` (only when permitted and the task must act outside the working tree). Inspect the active wrapper/configuration rather than assuming a default; native device orders follow the mobile skill’s permissions preflight.
- Wrapper quirk: with `--clean`, the answer can print *after* the `--- End Codex Response ---` marker — read the tail of output, or better, use `--output`/report-files and skip stdout parsing entirely.
- Codex CAN run shell commands (tests, `agent-browser` incl. `record start/stop`, `open`, `screencapture`, simulators) inside its sandbox in write mode — the cheap path for **computer-use verification headlessly** (see the `codex-computer-use` skill). It also carries the Playwright MCP headlessly. **On the bench** the same lane runs via `ssh bench codex exec …` with agent-browser + Playwright MCP (Chrome sandboxed under the `agent-chrome` AppArmor profile); `sky`/native GUI and the iOS Simulator stay Mac-only; **For native Android/iOS, use `mobile-app-testing`.** Discover available acceleration and devices; Mobile Next can drive physical phones or ADB-visible virtual devices such as Genymotion. Do not retry software emulation indefinitely on a host without usable acceleration.
- **GUI computer use is reachable headlessly too.** `codex exec` loads the `node_repl` MCP server from the bundled `computer-use` plugin, giving it `@oai/sky` — accessibility tree, clicks, typing, per-app screenshots on any macOS app. `codex exec -m gpt-6.1-sol -c model_reasoning_effort=high -s danger-full-access` is the working invocation (full access because the artifacts dir is usually outside the repo, and the CU service hands back `file://` screenshot paths the lane must copy). The Codex **desktop app** (`@Computer` / `@AppName`) is now only the *interactive* front door to the same engine — reserve it for flows a human should watch. Caution: `sky` drives the user's real desktop, so prefer `agent-browser`/Playwright for ordinary web QA and name the off-limits windows in the work order.
- Long runs: launch with `run_in_background: true` and a generous timeout; you get notified on completion. Multiple codex lanes run fine in parallel.
- Parallel *write* lanes need isolation: codex has no worktree isolation of its own, so two codex write-lanes touching the same file collide. Serialize them, or run each via an `Agent`/`Workflow` wrapper with `isolation: 'worktree'`.

## Run review HTML (mandatory deliverable)

Every conductor run produces a refined HTML review file on top of the in-session summary. On other hosts, verify delivery through their configured artifact surface; the following commands apply only on Ivan’s configured Bench. On Bench, run `~/bin/report-link.py <report-path>`, browser-check the exact served URL, and deliver the HTTPS link labelled **private — Tailscale access required**. Follow `domains/career-craft/bench/REPORTS.md`; `open` and local paths do not deliver a report on headless Linux. Written for *review*, not as a log: executive, skimmable, easy to understand at a glance.

- **Location + reuse:** `<repo>/.conductor/reports/` (create it; ensure `.conductor/` is gitignored). Key the file by issue when the run has one — `issue-<n>.html` — else by run-id (`<YYYY-MM-DD-slug>.html`). **Update-in-place rule:** if a report already exists for this session or this issue, update that file (revise proposals, append the new run as a dated section) instead of minting a new one.
- **Content:** what was asked; what happened *or what's being proposed*; decisions made and why (including options rejected); per-lane outcomes; evidence; residual risk and next steps. If the run is a proposal rather than a build, the HTML is the proposal document.
- **Diagrams:** use them wherever they beat prose — decision trees for choices made, before/after architecture, lane/data flow. Inline SVG or styled HTML/CSS preferred; mermaid via CDN script is acceptable (the file is local, no CSP).
- **Screenshots:** embed every verification screenshot that mattered. Base64 data URIs keep the file self-contained; drop large originals in `.conductor/reports/assets/<run-id>/` and reference them. Caption each with viewport + what it proves.
- **Video when warranted (Ivan, 13 Sep 2026):** apply the evidence gate below. Record only testing of changed application behavior; static reports, research and skill work use screenshots or command evidence. For selected flows, use the tool for the surface and the run assets directory:
- Web recording: first apply the evidence gate; when video is warranted, follow the Browser video evidence contract; prefer direct MP4 on verified 0.37.1. Reuse existing Playwright capture where it covers the flow.
  - **Native Android/iOS:** follow `mobile-app-testing` for device selection, durable recorder ownership, fresh UI observations, final-artifact provenance and cleanup. Mobile Next recording APIs or a durable owned ADB recorder are valid; the recorder need not belong to the orchestrator if the device lane owns its lifetime. Use the evidence gate before capture.
  - **iOS Simulator (Mac only):** `xcrun simctl io <device-udid> recordVideo --codec h264 <assets>/<flow>.mp4` in the background, drive, then SIGINT it.
  - **Native macOS app:** `screencapture -v <assets>/<flow>.mp4` (Ctrl-C to stop) — Mac only.
  - Embed with `<video controls preload="metadata" src="assets/<run-id>/<flow>.mp4">` and retain the original when converting from WebM; direct MP4 needs no duplicate. On the bench also drop the files under `~/reports/<repo>/<run>/` so they're viewable from the phone at https://bench.tailb5d047.ts.net/reports/. When recording is genuinely infeasible, a captioned screenshot sequence is the fallback — say so in the report; never present stills as if a recording existed.
- **Discovery metadata (configured Bench only):** the `<head>` carries the `bench:*` block (`bench:type`, `bench:owner`, `bench:action`, `bench:action-url`, `bench:due`, `bench:evidence-date`, `bench:work`) so the hub can catalogue the run — see "Declare what the report needs" in `domains/career-craft/bench/REPORTS.md` for the rules. Set `bench:owner` honestly: `ivan` only when a human decision is genuinely waiting, `agent` for routine agent-owned work. Set `bench:evidence-date` to the date of the newest evidence embedded in the report, not the date you wrote it.
- Styling: follow the Report design contract below; light, readable, editorial, and responsive.

## Report design contract

Use a light editorial document: warm off-white ground, dark ink, restrained sage accent. Lead with the outcome or decision and the next action, then develop the reasoning. Do not invent a decision when none is needed. Use a clear title, short standfirst and descriptive section headings; compact anchor navigation helps long reports.

### Help Ivan understand

A report has two jobs: say what was done and help Ivan understand what is going on. Explain the problem or trigger, how the relevant parts interact, what changed, and why that produces the outcome. For proposals, distinguish the intended effect from observed results. Use plain language, short explanations and concrete examples; introduce technical terms only when needed and explain them on first use. Keep implementation detail available as supporting evidence.

Always consider a visual while outlining the report. Prefer a diagram or flowchart for a multi-step process, decision, dependency, ownership boundary or cause-and-effect relationship; use before/after views to explain a meaningful change. Put it beside the explanation it supports, with a short caption stating the takeaway. A trivial update may be clearer in a sentence; do not add a decorative diagram to meet a quota.

Keep each visual focused on one question, with a clear reading direction, short plain-language labels and labelled arrows where their meaning is not obvious. Show only the parts needed to understand the point; split complex systems into smaller views. Ensure labels remain readable on a phone, and include a brief text explanation so the diagram is not the only way to understand it. Prefer inline SVG or HTML/CSS that works offline.

Before delivery, check: can Ivan explain what happened, why it happened and what it means without reading the raw logs or knowing the codebase? If not, simplify the explanation or add the missing visual.

Keep prose around 65–75 characters wide, body text at least 16px with 1.55–1.75 line height, generous section spacing and a distinct heading hierarchy. System fonts work offline; a restrained serif heading can add character. Use whitespace and thin rules for structure. Avoid repeated rounded cards, giant boxed flow steps, dashboard badges, decorative metrics and dense full-width prose. Reserve panels for content that benefits from grouping.

Use tables only for genuine comparisons. At phone widths, provide labelled stacked rows or a deliberate scrollable table with readable column widths; never squeeze labels and paths into one-word or one-character columns. Prefer compact numbered sequences for simple process explanations. Diagrams must communicate a relationship more clearly than prose.

Keep the conclusion, decisions, material failures and risks visible. Put raw logs, long reviewer transcripts and secondary file anchors in labelled native details/summary disclosures. Evidence should support a specific claim; do not fill the report with redundant screenshots or recordings of the report itself. Preserve provenance and uncertainty when restyling an existing report.

Use semantic headings, visible keyboard focus, adequate contrast and meaningful link labels. Keep HTML/CSS self-contained and offline-capable; avoid required remote fonts or rendering libraries. Check the served page at desktop and 390px phone widths, including open disclosures, long paths, navigation and overflow. Use screenshots for visual review; DOM checks alone do not establish readability. Route design/taste to the Claude lane and verify mechanics independently.

## Review gates (non-negotiable)

- No lane's work is "done" until you've read its diff or its screenshots — reports are claims, not evidence.
- Anything user-facing (copy, layout, empty states) gets a taste-lane (Opus 5.5 at `high`, or Fable 5.1) or orchestrator eye before it ships, regardless of which lane built it. Prose that leaves the building gets a `write-lane` or Opus edit pass regardless of which lane drafted it.
- Verification lives in *your* gates, not in the work orders. A lane that was told to self-verify has told you nothing you can audit — read the diff or the pixels yourself.
- If a codex lane's diff smells like it fought the codebase (new helpers duplicating existing ones, style drift), stop dispatching that class of work to it and either tighten the work order or move the work to a taste lane. Note what happened for the session summary.
- Completion gates match the task: use relevant project checks and runtime evidence for application changes; source/installer checks and static report verification for skill edits. Push, merge and deployment still require task authorization.

## Closing step: run-report

When available and authorized, close through the **`run-report`** skill: post the run report (what/tests/evidence/decisions/cost) as a comment on the run's issue/PR — include the review HTML's path in that comment — flip `status:*` labels, and append the telemetry ledger. A run without a report is invisible work.

If `run-report` is unavailable, use `${CLAUDE_PLUGIN_ROOT}/scripts/conductor-report.py` (resolve the installation path as described above) for configured telemetry and the same evidence/report contract. Do not send comments or change labels without authorization. If the run has no GitHub issue and no ledger configured, `run-report` degrades to the in-session summary plus the review HTML — that is a valid close, not a failure.

## Worked example (shape, not script)

> Task: "Add CSV export to the admin actions view, and make sure nothing regressed."

1. You scout: the view is `admin/actions/+page.svelte`, data comes from `getOrgActions`, export needs a new query arg or client-side serialization — decide client-side, cap honesty note required.
2. Dispatch in one turn: **`exec-lane` (Opus 5.5, `medium`)** — implement the CSV serialization + download button per work order with exact anchor lines; **taste lane** — n/a this time (no design surface beyond a button — the work order specifies the exact button grammar to reuse).
3. On completion: **codex-review (`-m gpt-6.1-sol --effort high`)** reviews the diff as the cross-family pass, and **codex (`-m gpt-6.1-sol --effort high`, workspace-write)** verifies: typecheck, load the page via agent-browser, export a CSV, assert row count matches the on-screen count, screenshot the button placement to `verify/`. Evidence choice: screenshots plus download row-count assertion, because the downloaded data establishes correctness; add video only if a changed interaction needs demonstration.
4. You: Read the screenshot (button grammar right?), read the diff, run the final gates, summarize.
5. You: write/update `.conductor/reports/issue-<n>.html` — decision diagram (client-side vs query-arg export, and why), the diff summary, the button screenshot, and, if the evidence gate selected it, the export-flow video (MP4; retain any WebM source) from the verify lane — then hand it over — `open` on a desktop, the hub URL on the bench: "here's the HTML review: https://bench.tailb5d047.ts.net/reports/mikono/issue-<n>.html"

## Appendix — running under a proxied orchestrator (optional)

Skip this section unless you route Claude Code's main loop through a local proxy to a non-Claude model (e.g. CLIProxyAPI serving GPT-6.1 Sol). **Detect it:** run `echo "$ANTHROPIC_BASE_URL"` — a `127.0.0.1` URL means proxied mode. This inverts the usual arrangement: the proxied model holds the judgment lanes and does most execution itself; Claude becomes the dispatched taste / second-family lane.

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
  `--model opus` for taste/design lanes; `--model claude-fable-5-1` when the lane needs top-shelf judgment or is a high-stakes writing lane. Write the work order to a file first; launch long lanes with `run_in_background: true` and a generous timeout — the report file is the deliverable. Same file-collision rule as codex lanes: these shell-outs write to the shared working tree with no isolation.
- **Codex lanes are unchanged** but become *same-family* with the orchestrator. Cross-family verification therefore routes the other way: send diff-taste review and anything user-facing to a Claude shell-out lane, and treat `codex-review` as a mechanics-only second pass, not the independent perspective.
- Everything else holds: the orchestrator still never delegates the plan, work orders, or final review; still Reads screenshots itself; still runs the end gates and closes with `run-report`.

<!-- browser-evidence:start -->
## Browser video evidence

## Choose evidence before recording

Ivan’s 13 September 2026 instruction: video is for meaningful application evidence, not a mandatory artifact for every Conductor run. Record video only when an application has been changed and the recording demonstrates testing of that change. Name the application change, test steps, expected result and independent assertion evidence in the work order. A report being opened in a browser is not an application change.

Do not record report opening, scrolling, resizing, publication checks, static document/design reviews, research, proposals, skill edits, or CLI-only work. For a static HTML report refresh, use desktop/phone screenshots and DOM/layout assertions; a browser being involved does not make video necessary. Use command output, tests or source evidence for nonvisual work. Static application changes may use screenshots when motion or interaction adds no evidence.

Each verification order states the evidence choice and reason. Only orders requiring video need a recording path. Keep required application-flow recordings and their assertions; do not reduce regression coverage. The recording procedure below applies only after this gate selects video. This scope supersedes blanket recording language in older Conductor examples and browser/verification instructions for Conductor work.

This contract supersedes older WebM conversion mandates elsewhere in this skill; WebM examples remain valid optional formats.

For a flow selected for video by the evidence gate, use agent-browser and specify a named session, initial state, steps, expected observable result, recording path and assertion evidence. Record representative application flows, not every unit test or edit iteration.

Read `agent-browser --version`, `agent-browser record --help`, and `agent-browser skills get agent-browser` for the installed command contract. Verified with 0.37.1: recording preserves the current page, DOM and login state, writes MP4 directly (H.264), and requires system ffmpeg. Older versions differ; do not assume they preserve context or support MP4. Use `agent-browser doctor` after upgrades. Upgrade through the installed package manager; avoid changing the default Node runtime for unrelated tools.

1. Use an owned `--session <lane>` on every command. Establish safe demo data/auth and the intended viewport before recording. Keep auth files outside report roots.
2. Start `agent-browser --session <lane> record start <assets>/<flow>.mp4` before the actions that matter. Omit the optional URL to preserve the current page. To capture navigation itself, start on an initialized page then issue `open <url>` separately. Wait for a visible rendered frame before very short flows; an empty capture is not evidence.
3. Drive real actions with fresh snapshot refs. Assert the result independently: visible state, persisted data, row count, download contents or a test assertion. Video alone is not a pass.
4. Stop with `agent-browser --session <lane> record stop`, including failure paths, and close only the owned session. Check exit status, nonempty output, ffprobe duration/codec, and actual playback. Preserve failed-flow evidence.
5. Embed `<video controls playsinline preload="metadata" src="assets/<run>/<flow>.mp4"></video>` in the run report with steps, environment/build, expected/actual result and assertions. Verify the served report and media. On Bench use `~/bin/report-link.py <report>` and deliver its verified private Tailscale URL. On Mac use the established report push and verify the Bench URL. Keep originals when creating derivatives; run Bench media conversion through `~/bin/bench-heavy-run -- ffmpeg ...` with bounded threads.

For bugs, capture before/after with matching steps, data and viewport when reproducible; say when the before state is unavailable. Never recreate a harmful production failure just for footage. Separate edited demonstrations from unedited verification evidence. For how-tos/journeys/features, include actor, prerequisites, step labels and successful end state; record only material approved for the intended audience.

Keep existing Playwright regression tests, assertions, traces, console/network evidence and flow-contract scorecards: they provide repeatability and diagnosis beyond video. Reuse an existing Playwright video capture if it covers the same flow; do not duplicate drivers solely for recording. Use native/device capture for native apps. When recording fails, report the actual failure and use captioned screenshots plus assertions as a declared fallback. Screenshots support visual review; the mechanics lane does not self-certify design quality.
<!-- browser-evidence:end -->
