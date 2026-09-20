---
name: conductor-core
description: Orchestrate Codex-first work with Astra at task-appropriate effort, work-sized parallel lanes, and optional Opus design or review. Use for Conductor Core, Codex-first orchestration, or Conductor without a Fable dependency.
---

# Conductor Core

Run the full Conductor workflow on Astra. Opus is an optional contributor; Fable is never selected. Core is a routing profile in the Conductor plugin, not a reduced-capability mode.

**Core exists to finish ambitious work, not to economise on it.** Long-running migrations, ops and automation lanes, multi-module features, epics that span sessions. Review and verification are part of that machinery, not its point. Core has no artificial worker cap for exactly this reason: the run is sized by the work.

## Profile and shared authority

Set `profile: conductor-core` in the run and each work order. This file owns Core's model routing, fan-out and review policy. The mixed-model routing tables, historical model rankings, required Claude taste passes and mandatory other-family gates in the sibling Conductor skill do not apply to Core. This includes model defaults in bundled agents and supporting skills; carry the Core profile when invoking them and use their task procedures without importing conflicting routing defaults. User instructions and actual tool permissions still govern the task.

Read the current [shared Conductor source](../conductor/SKILL.md) for **What earns an agent**, **Sizing the fan-out**, **Installation paths**, **Report design contract** (including **Help Ivan understand**), **Closing step: run-report**, and **Choose evidence before recording**. The dispatch gate there is unchanged by Core: scouting is the parent's own work, every worker returns a named artifact, and an item that is a single tool call runs inline however many there are. These remain the single source for report structure, explanation, delivery and evidence selection. Apply the Core review policy below wherever those shared sections call for Claude visual judgment. Resolve relative references from the canonical source directory, not a personal discovery bootstrap. Reread the shared report and evidence sections before authoring or revising and publishing a report.

The default `conductor` profile remains mixed-model. [Conductor Claude](../conductor-claude/SKILL.md) is Core's mirror image: the same workflow with no Codex lane at all, carried entirely on Opus 5 and Fable 5.1. Do not silently change unrelated sessions, scheduled jobs or global model settings. A continued Core run retains its profile across compaction, checkpoints and worker handoffs unless the user changes it.

## Parent and transport

Launch the parent in Codex on `gpt-6-astra` at `high` for a workflow with no Claude dependency. The parent owns grounding, the plan, work orders, integration and final acceptance. A skill cannot switch the already-running parent model. If invoked from Claude Code, explain that the current parent still consumes Claude capacity; use its available Codex bridge for workers, and preserve a resumable handoff for an Astra parent rather than promising Claude-free continuity from that session.

From a Codex parent, use native collaboration agents where they can select the requested model and effort; otherwise use the installed Codex CLI or `ask-codex` after checking its supported options. Pass model and effort explicitly on each launch. Use a fresh or scoped context when selecting worker effort instead of a full-history fork that forces inheritance. Record actual launch settings; if the harness cannot select an effort, use a supported launcher or report the mismatch rather than pretending the setting changed.

Use `ask-claude` only for a useful optional Opus lane, with the real Claude provider and explicit `claude-opus-5` at `high`. Check the installed bridge contract for effort selection; a prompt asking for High is not a launch setting. Do not use Claude wrapper agents merely to start Codex workers. Do not launch bundled `verify-lane`, `write-lane` or `design-lane` by name under Core: their fixed model/effort defaults belong to the mixed-model profile and can drift independently. Launch the required Core role explicitly instead.

Use the harness's real concurrency and completion mechanisms. Only the Claude harness has Claude Agent/Workflow APIs. Orca supplies terminals and worktrees, not model selection. One owner per writable file, mutable fixture, browser or device; serialize overlapping writes or isolate worktrees. Preserve existing dirty changes and stop only owned processes.

## Routing

| Work | Model | Effort and reason |
|---|---|---|
| Grounding, plan, work orders, integration, final acceptance | gpt-6-astra | high — orchestrator judgment |
| Exact mechanical edits and repetitive transformations | gpt-6-astra | low — established pattern and clear acceptance |
| Well-specified implementation, refactors and ordinary fixes | gpt-6-astra | medium — defined behavior and scope |
| Runtime replay with known steps and assertions | gpt-6-astra | medium — execution mechanics |
| Architecture, investigation, ambiguity and sustained synthesis | gpt-6-astra | high — resolve uncertainty |
| Stateful work, recovery, ownership and screen-dependent runtime testing | gpt-6-astra | high — reason about state and side effects |
| Adversarial review | gpt-6-astra, separate reviewer | high — challenge requirements, implementation and evidence |
| Design, UI/copy judgment and substantial writing | gpt-6-astra | high — use the brief and existing references; Opus high may contribute |

Effort follows the task's uncertainty. Low does not own architecture or subjective acceptance. Move work to Medium or High when its assumptions stop being mechanical. Escalate beyond High when a concrete unresolved problem warrants it, using supported effort levels and recording why. Core has no fixed retry count or escalation budget: persist through meaningful progress, change the approach when evidence disproves it, and checkpoint genuine external blockers. Repeating unchanged failed calls is not progress.

## Fan-out follows the work

Ivan's instruction, 14 September 2026: do not artificially restrict Core's capability to conserve Claude-style quota. There is **no Core worker-count cap, two-worker default, token ceiling, or fixed Opus-call allowance**. Honor explicit user budgets and real harness, provider and machine limits.

Scout the task yourself with file reads, searches and commands. Fan out over a known work-list, not to discover the work-list. Each worker must return a concrete artifact and acceptance evidence. Small single-command work stays inline because an agent would add overhead, not because the run needs to stay small.

For substantial independent items, give each item an owned lane. Use the available concurrency and queue the rest without dropping coverage. Group items only when they share necessary context or are too small individually. Use independent review lenses or competing approaches when the uncertainty earns them; do not invent redundant lanes to meet a target. The number of roles is not a limit on the number of agents.

Delegated fan-out is allowed when it serves a known sub-work-list; the parent names that scope, ownership and any real resource constraints so children do not duplicate assignments. A global work-list tracks queued, running, completed and blocked items. Continue all agreed coverage as capacity becomes available. Respect Bench heavy-work admission and device/server ownership; a machine admission deferral is not permission to bypass it with parallel retries.

## Work orders and checkpoints

Give each lane the relevant source anchors, task contract, file ownership, deliverable path and acceptance criteria. Include `profile`, `model`, `effort`, `reason`, `review_family`, and known provider availability in `routing.json` or the work order's structured routing section. State evidence choice and why; record video only when the shared evidence gate selects it. A lane receives enough context to reason, without automatically inheriting the entire parent transcript.

Persist completed artifacts, remaining work, actual launch settings, test results and outstanding state changes at useful boundaries. Before replacing an interrupted worker, stop its writes and inspect its diff and remote side effects. Resume only what remains. Timeout or lost output does not prove a mutation or provider job failed.

## The loop

The full run. Steps 1, 4 and 5 belong to the parent and are never delegated.

**1. Plan — parent.** Scout the code yourself with reads, searches and commands; delegated discovery costs a full context per worker and answers worse than the command you could have run. Decompose into work orders carrying exact anchors, the task contract, file ownership, the deliverable path, the acceptance criteria, and the structured routing block (`profile`, `model`, `effort`, `reason`, `review_family`). Maintain a global work-list: queued, running, completed, blocked.

**2. Dispatch — parallel.** Launch each independent item as its own lane, using the harness's real concurrency: native collaboration agents where they can select the requested model and effort, otherwise the Codex CLI or `ask-codex` with model and effort passed explicitly on every launch. Orca supplies worktrees and terminals; the command passed to the terminal determines the worker model. Use a fresh or scoped context per worker rather than a full-history fork that forces inheritance.

Queue what exceeds available concurrency instead of dropping it, and continue the agreed coverage as capacity frees. One owner per writable file, mutable fixture, browser or device; serialize overlapping writes or isolate worktrees. Respect Bench heavy-work admission — a deferral is not permission to bypass it with parallel retries.

Wait using the harness's real completion mechanism: a Codex parent resumes a running tool session with its wait/poll API; a Claude parent is re-invoked on completion and should not poll. Do useful independent work meanwhile. A timeout or lost output does not prove a mutation or a provider job failed — inspect before replacing a worker.

**3. Verify.** Relevant project checks and independent runtime assertions establish behavior; a worker's prose does not. Route the adversarial pass to a separate Astra High reviewer with the requirements and the final diff in fresh context, never the author's verdict. Add an Opus lane where its judgment improves the result and it is available. Label coverage honestly per the policy below.

**4. Review and integrate — parent.** Read the diff, the artifacts and the actual verification output before accepting anything. Send rejected work back as a revised order stating what was wrong and what correct looks like. Merge the lanes yourself, resolve conflicts yourself, and run the gates the change actually calls for. Checkpoint completed artifacts, remaining work, actual launch settings and outstanding state changes at useful boundaries.

**5. Publish — parent.** Write or update the run's review HTML per the shared Report design contract with per-lane coverage labels, deliver it through the configured report surface, and close through `run-report` where available and authorized.

## Running the team

- **State the lane's boundaries in the order.** Scope, ownership, deliverable, acceptance, and whether the lane may fan out. Delegated fan-out is allowed when it serves a known sub-work-list; the parent names that scope and ownership so children do not duplicate assignments.
- **Workers checkpoint.** A lane that dies on a provider limit leaves no report. Long write lanes commit or persist their artifact as they go.
- **Raise the window for a long lane.** Astra's Codex context is 272K by default; raise it per lane with `-c model_context_window=…` or split the order at ~200K.
- **No self-verification scaffolding in orders.** Verification lives in step 3, which is the parent's.
- **When you bound coverage for a real limit, record what you dropped** so a partial sweep never reads as a complete one.


## Long-horizon runs

The shared **Long-horizon runs** section governs: persist the work-list as a file, phase an epic into waves rather than one flat fan-out, checkpoint at wave boundaries, and resume from what landed rather than from memory. Read it there.

Core-specific deltas: raise `model_context_window` for a long lane or split its order at ~200K, since Astra's Codex window is 272K by default. An `ultra` lane — Astra fanning out to its own subagents — is for a self-contained long-horizon order that caps its own fan-out and names its worker budget, never for a wave the parent is already fanning out. A provider limit or an Orca terminal loss is an interruption to resume from, not a reason to restate the plan from scratch: the committed branches and the work-list file are the resume point.


## Optional Opus, complete without Claude

Spend Opus on a design direction, screenshot/copy critique or specific cross-family question when it can improve the result. Keep the order focused; the number of useful checks follows the work. Fable is neither a default nor an escalation or overflow target in Core.

Use known availability where the harness exposes it. If unknown, the first Opus request should do useful work rather than burn a separate probe. A Fable-specific limit does not establish Opus availability, and switching models cannot bypass an exhausted shared allowance.

On a Claude quota or authentication failure, record the reason and any reset information, mark Claude unavailable for this run and continue on Astra. Do not retry the unavailable provider repeatedly, switch accounts or silently enable paid extra usage/API billing. Reconsider availability when new evidence arrives, a known reset occurs, or the user asks. Handle ordinary transient failures according to their actual cause; they are not automatically quota failures.

Opus unavailability does not create an approval gate or block otherwise accepted work. If Codex itself becomes unavailable, checkpoint the run and state the blocker; Core does not promise unlimited provider capacity or silently move all work to Claude.

## Review and acceptance

The implementing worker's self-report is a claim. The orchestrator reads the diff, relevant artifacts and actual verification output before acceptance. Use a separate Astra High reviewer for substantive work, with the requirements and final diff in fresh context; avoid feeding it the author's verdict as the answer. The reviewer should seek counterexamples, missing requirements and unsupported evidence. Recheck after fixes when the findings or changed scope warrant it.

Keep review coverage precise: `same-family` for Astra checking Astra, `cross-family` for a real Opus review of Astra work or Astra review of Opus work, and `orchestrator-only` for inline work without a separate reviewer. Different effort levels do not create different model families. An optional Opus design critique does not turn the entire implementation into cross-family-reviewed code; name what it covered.

Relevant project checks and independent runtime assertions establish behavior; review prose and screenshots alone do not prove correctness. For UI, Astra can implement and judge against the existing design system, explicit visual references and acceptance criteria, while checking accessibility and task flows. Prefer Opus judgment when useful and available; when absent, deliver the work with an honest same-family design-review label. Do not claim equivalent design quality or defer solely because Claude is missing.

For substantial writing, Astra drafts and reviews against the audience, voice sample and brief; optional Opus editing improves the result when available. Missing a Claude prose pass is not a Core completion blocker. Existing authorization to send, publish, merge or deploy remains required; Core does not broaden it.

Unresolved acceptance failures remain failures regardless of model availability. Report what was exercised, what was not verified, and remaining risks without claiming a pass by substitution. Use the shared HTML report and delivery contract with these coverage labels. Static skill/report work uses command evidence and screenshots, not video of opening the report.
