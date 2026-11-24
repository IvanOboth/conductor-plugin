---
name: council
description: Multi-provider, subscription-clean council across Gemini 4 Neon (high), Claude Opus 5.5 (high) / optional Fable 5.2 (high), and GPT-6.2 Sol (high). Supports Mode A (fast 3-family read-only PR audit with /10 round scorecard tables) and Mode B (blind Round 1 investigation, anonymized Round 2 cross-model peer review, and Round 3 consensus verdict & dissent ledger). Use for /council, $council, "run the council", "council review", "multi-model consensus", "peer-review deliberation", hard architecture forks, ambiguous root causes, or high-risk PR audits.
---

# Council — Multi-Provider Review & Peer-Review Consensus

Run an independent, subscription-clean council across three distinct model families — **Gemini 4 Neon (`high`)**, **Claude Opus 5.5 (`high`)** (plus optional **Fable 5.2 (`high`)** for frontend/UX taste or high-ambiguity strategy), and **GPT-6.2 Sol (`high`)** — with zero extra API billing and zero anchoring bias.

Built on two modes:

1. **Mode A — Review Council (fast, Theo-style PR/diff audit):** All 3 model families review the exact same PR or diff read-only in parallel -> `/10` scorecard table posted in the PR description -> orchestrator fixes real blockers and re-scores across bounded rounds while fighting scope creep.
2. **Mode B — Consensus Deliberation Council (3-round blind peer review):** For hard architecture forks, ambiguous root causes, and major design bets:
   - **Round 1 (Blind Investigation & Proposal):** Every member independently inspects the codebase/evidence and writes its own root-cause theory and concrete plan — 100% blind to the other models.
   - **Round 2 (Anonymized Cross-Model Peer Review):** Every member receives all Round 1 proposals anonymized as `Proposal A`, `Proposal B`, `Proposal C` (model names and provider cues stripped so nobody defers to prestige), critiques concrete flaws/blind spots, ranks proposals, and votes `ENDORSE`, `ENDORSE WITH AMENDMENTS`, or `OBJECT`.
   - **Round 3 (Consensus Verdict & Dissent Ledger):** The orchestrator synthesizes the agreed consensus and surviving amendments, explicitly surfaces every unresolved dissent for Ivan, and outputs a crisp verdict table (or a Bench HTML decision ledger for major calls).

Read [references/peer-review-protocol.md](references/peer-review-protocol.md) for the exact Round 1/2/3 prompt templates, anonymization checklist, Mode A `/10` rubric, and scorecard/ledger formats.

---

## When to use / When NOT to use

| Situation | Use `/council`? | Route instead |
|---|---|---|
| High-risk PR (auth, payments, money, RBAC, migrations, public APIs, multi-file refactor) needing independent multi-family sign-off | **YES — Mode A** | — |
| Ambiguous root cause / production mystery where an early guess would anchor a single model | **YES — Mode B** | — |
| Irreversible architecture fork, schema contract, or major product/system design bet | **YES — Mode B** | — |
| Major frontend/UX architecture or design-system fork | **YES — Mode B** (seat Fable 5.2 alongside or in place of Opus) | — |
| **Filmmaking** (story rooms, scripts, dialogue, shot lists, Seedance blocks, take reviews, rough cuts) | **NEVER** | **Gemini 4 Neon only** (Ivan's 21 Nov 2026 rule) |
| Trivial 1-file bug fix, rename, copy edit, or obvious CRUD | **NEVER** | Inline edit + standard single cross-family review |
| Routine feature or epic execution | **NEVER** | [`/conductor-gemini`](../conductor-gemini/SKILL.md) (Antigravity) or [`/conductor`](../conductor/SKILL.md) (Claude/Codex) |
| Video/audio playback inspection | **NEVER** (Codex cannot watch video or hear audio) | Gemini 4 Neon native `read_file` or `ask-gemini --file` |

---

## Non-negotiable guardrails

1. **Subscription-clean routing only (zero extra API billing):**
   - **Gemini 4 Neon (`high`):** `ask-gemini -m gemini-4-neon-high --no-fallback` (Google AI Ultra subscription). Always pass `--no-fallback` so it never silently switches to the paid API (`\$3/\$15` per Mtok, no tools). Never pass `--write`.
   - **Claude Opus 5.5 (`high`):** `ask-claude --plan -m opus` (Claude subscription via Orca selected account; strips `ANTHROPIC_*` proxy vars automatically).
   - **Optional Claude Fable 5.2 (`high`):** `ask-claude --plan -m fable` (add when frontend/UX taste or ambiguous strategy is central; never silently substitute for a missing non-Claude provider).
   - **GPT-6.2 Sol (`high`):** `ask-codex -m gpt-6.2-sol --effort high` (ChatGPT/Codex subscription). Always pass `-m` and `--effort high` explicitly; never rely on `~/.codex/config.toml` defaults, and never default to `xhigh`.
   - **NEVER use Antigravity `/swarm` Opus** (which bills against Google AI Ultra quota instead of Claude subscriptions).
2. **Fail honestly — never substitute:**
   - If a provider fails, times out, or is out of quota, record `UNAVAILABLE (<reason>)` in the scorecard or ledger.
   - **NEVER silently substitute** a second model from an already-represented family (e.g., never run two Claude seats or two Codex seats and claim a 3-family council).
   - A 2-family council may proceed only if explicitly labelled `DEGRADED (2/3 families — <missing> unavailable)`; if full 3-family quorum is required for the decision, stop and tell Ivan.
3. **Zero file edits during active review or investigation:**
   - While any council delegate is inspecting the repository (any Mode A round, or Mode B Rounds 1–2), **nobody — neither delegates nor the orchestrator — may edit, stage, checkout, rebase, or write files inside the repo**. Every member must evaluate the exact same commit SHA and diff.
   - Store all council prompts, briefs, and outputs **outside the git checkout** under `~/runs/council/<YYYY-MM-DD-slug>/` so untracked scratch files never pollute `git status` or `git diff`.
   - Note on `ask-codex` read-only safety: on the bench, `ask-codex --readonly` is refused by the wrapper (a read-only sandbox there can answer from the prompt alone without reading the repo). Omit `--readonly` and explicitly include **"Do not edit, write, or create any repository files."** in the Codex prompt (or use `--prompt-only` strictly when 100% of context is attached in `--context` and no repo inspection is needed). Verify `git status --short` is unchanged after every round.
4. **Fight scope creep across rounds (Mode A):**
   - Round 1 surfaces real bugs, edge cases, contract breaks, and security/correctness flaws with `file:line` citations.
   - Round 2+ verifies fixes against prior findings and flags **only regressions or genuinely severe blockers introduced by the fix**. Reject newly invented style nits, refactors, or unrelated feature requests.
   - Stop by Round 2 (hard ceiling Round 3 only if a Round 2 fix introduced a regression); surface any remaining split directly to Ivan.
5. **Orchestrator owns judgment:**
   - Verify every claimed blocker in the actual code before acting on it. Council members are independent advisors — they never file issues, push commits, or override Ivan's decision authority.

---

## Subscription-clean CLI invocations

Prepare a clean run directory outside the repo first:

```bash
RUN_DIR="$HOME/runs/council/$(date -u +%Y-%m-%d)-<slug>"
mkdir -p "$RUN_DIR"
```

Launch all three independent family seats **in parallel in a single turn** (each as its own background command or fresh-context read-only subagent — never poll in a loop; wait for completion notifications):

```bash
# Seat 1: Gemini 4 Neon (high) — Google AI Ultra subscription (read-only by default; --no-fallback mandatory)
ask-gemini -m gemini-4-neon-high --no-fallback \
  --context "$RUN_DIR/brief.md" \
  --output "$RUN_DIR/r1-gemini.md" \
  "Follow the instructions in the context file. Read-only inspection only; do not edit files."

# Seat 2: Claude Opus 5.5 (high) — Claude subscription (read-only plan mode)
ask-claude --plan -m opus \
  --context "$RUN_DIR/brief.md" \
  "Follow the instructions in the context file. Read-only inspection only; do not edit files." \
  > "$RUN_DIR/r1-opus.md"

# Seat 3: GPT-6.2 Sol (high) — ChatGPT/Codex subscription (explicit model + effort; no --readonly on bench)
ask-codex -m gpt-6.2-sol --effort high \
  --context "$RUN_DIR/brief.md" \
  --output "$RUN_DIR/r1-sol.md" \
  "Follow the instructions in the context file. Do not edit, write, or create any repository files."

# Optional Seat 4 (frontend/UX taste or high-ambiguity strategy): Claude Fable 5.2 (high)
ask-claude --plan -m fable \
  --context "$RUN_DIR/brief.md" \
  "Follow the instructions in the context file. Read-only inspection only; do not edit files." \
  > "$RUN_DIR/r1-fable.md"
```

**Fresh-context symmetry across parent harnesses:**
- Running from **Antigravity (Gemini 4 Neon)**, **Claude Code (Opus/Fable)**, or **Codex (Sol)**: you may either invoke all 3 seats via the CLI commands above (giving every seat identical fresh-context isolation from the same `brief.md`), OR run your own family's seat via a fresh read-only child (`invoke_subagent` in Antigravity, `Agent` with `model: "opus", effort: "high"` in Claude Code) fed **only** `brief.md` — never your conversational history or hypotheses.
- Never leak the orchestrator's preferred theory into `brief.md`.

---

## Mode A — Review Council (fast PR / diff audit)

Use Mode A for high-risk PRs and multi-file diffs where you want fast, calibrated `/10` verification from all 3 families.

1. **Freeze snapshot & write brief:** Record `BASE_SHA` and `HEAD_SHA` (`git rev-parse HEAD`), confirm `git status --short` is clean (or snapshot exact unstaged diff), and write `$RUN_DIR/r1-brief.md` with: PR goal/acceptance criteria, exact diff range (`git diff <base>...<head>`), files changed, and the Mode A Round 1 prompt from [references/peer-review-protocol.md](references/peer-review-protocol.md#mode-a-review-prompts-and-10-rubric).
2. **Parallel read-only Round 1:** Launch Gemini 4 Neon, Claude Opus 5.5, and GPT-6.2 Sol in parallel (add Fable 5.2 if UI/UX craft is central). **Touch zero repo files while they run.**
3. **Verify & triage:** Check `git status --short` is unchanged. Read all 3 outputs and verify every cited blocker against the real code. Sort into:
   - **Fix now** (confirmed bugs, security/data/contract defects, broken invariants)
   - **Dismissed / out-of-scope** (false positives, style preferences, unrequested scope expansion — state why in 1 line)
4. **Apply fixes & run Round 2 (if any score < 8 or any confirmed blocker existed):**
   - Commit the fixes on the PR branch (`ROUND2_SHA`), verify tests pass, and write `$RUN_DIR/r2-brief.md` containing: prior findings + disposition, the incremental diff (`git diff <r1-sha>..<r2-sha>`), and the **anti-scope-creep Round 2 prompt**.
   - Launch all 3 seats in parallel read-only. Stop after Round 2 (or at most Round 3 if a Round 2 fix caused a confirmed regression).
5. **Post the `/10` scorecard in the PR description:** Update the PR body (or post a summary comment if not authorized to edit the PR body) using the exact scorecard format below:

```markdown
## Council Review Scorecard

| Round | Commit | Gemini 4 Neon (`high`) | Claude Opus 5.5 (`high`) | GPT-6.2 Sol (`high`) | Outcome |
|---|---|---|---|---|---|
| Round 1 | `abc1234` | 7/10 — 2 blockers | 8/10 — 1 blocker | 7/10 — 2 blockers | Fixes applied |
| Round 2 | `def5678` | 9/10 — LGTM | 9/10 — LGTM | 9/10 — LGTM | Ship-ready |

- **Blockers fixed:** <1-line bullet per verified blocker with file:line>
- **Dismissed / scope-creep rejected:** <1-line bullet if any, with brief reason>
- **Coverage note:** `3/3 families (subscription-clean)` *(or `DEGRADED (2/3 families — <provider> UNAVAILABLE: <reason>)`)*
```

*(Add a `Claude Fable 5.2 (high)` column only when Fable was explicitly seated.)*

---

## Mode B — Consensus Deliberation Council (3-round blind peer review)

Use Mode B for ambiguous root causes, irreversible architecture choices, and high-stakes design bets where anchoring bias is the main enemy.

### Round 1 — Blind Independent Investigation & Proposal

1. Write `$RUN_DIR/r1-brief.md` with **strictly neutral framing**: the symptom or decision fork, exact `HEAD` SHA, observable facts/logs, hard constraints, and non-goals. **Do not include your own hypothesis or preferred option.**
2. Launch all 3 family seats in parallel (read-only, zero repo edits). Each member independently investigates the codebase and writes its proposal to `$RUN_DIR/r1-<model>.md` following the Round 1 schema in [references/peer-review-protocol.md](references/peer-review-protocol.md#round-1-blind-investigation-prompt).
3. Wait until every running seat finishes (or cleanly times out / fails honestly) before starting Round 2. Verify `git status --short` is unchanged.

### Round 2 — Anonymized Cross-Model Peer Review

1. **Randomize and strip identities:** Assign each surviving Round 1 proposal a random label (`Proposal A`, `Proposal B`, `Proposal C`, plus `Proposal D` if Fable was seated). Save the secret mapping ONLY in `$RUN_DIR/mapping.json` — never include it in Round 2 inputs.
2. **Sanitize every proposal** using the anonymization checklist in [references/peer-review-protocol.md](references/peer-review-protocol.md#anonymization-checklist): strip model names, provider signatures, CLI wrapper banners (`--- Claude Response ---`), scratch filenames, and self-identifying metadata.
3. Assemble `$RUN_DIR/r2-packet.md` containing the neutral brief + all anonymized proposals (`Proposal A`, `Proposal B`, `Proposal C`) + the Round 2 Peer Review prompt.
4. Launch all active family seats in parallel (read-only) with `$RUN_DIR/r2-packet.md`. Each member critiques concrete flaws and blind spots in every proposal (including its own, which it evaluates on equal footing), ranks them (`1st / 2nd / 3rd`), and casts an explicit vote per proposal:
   - **`ENDORSE`** — solid as written
   - **`ENDORSE WITH AMENDMENTS`** — right direction; list exact required changes
   - **`OBJECT`** — fundamental flaw; state exact blocking defect and evidence (`file:line` or counterexample)

### Round 3 — Consensus Verdict & Dissent Ledger

1. Unmask `mapping.json` and read every Round 2 critique and vote. Independently check every contested `file:line` claim against the codebase.
2. Synthesize the final output (see exact template in [references/peer-review-protocol.md](references/peer-review-protocol.md#round-3-consensus-verdict-and-dissent-ledger)):
   - **Verdict & Quorum Status:** Consensus reached / Split decision / Degraded quorum.
   - **Unmasked Vote Matrix:** Every member's vote and ranking across `Proposal A/B/C` (now mapped to model names).
   - **Adopted Plan & Surviving Amendments:** The concrete winning approach plus every amendment endorsed across families.
   - **Dissent Ledger (never buried):** Every surviving `OBJECT` vote or unresolved architectural tradeoff, stating who dissented, their strongest concrete argument, what assumption separates the sides, and the decision needed from Ivan.
3. **Presentation:**
   - For bounded architecture or debugging forks, return the concise Verdict & Dissent Ledger directly in-chat.
   - For major irreversible bets, multi-surface system designs, or executive review, publish a self-contained desktop-and-phone HTML decision ledger under `<repo>/.conductor/reports/<YYYY-MM-DD-council-slug>.html` following [references/report-design.md](../conductor/references/report-design.md), publish via `~/bin/report-link.py`, and give Ivan the verified `https://bench.tailb5d047.ts.net/reports/...` URL (labelled **private — Tailscale access required**).
