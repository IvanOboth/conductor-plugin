# Council Peer-Review Protocol & Prompt Templates

Reference companion for [Council](../SKILL.md). Keep this protocol strict: blindness in Round 1, honest anonymization in Round 2, and evidence-checked synthesis in Round 3 are what turn three separate model calls into real deliberation instead of sycophantic consensus.

---

## Mode A: Review Prompts and `/10` Rubric

### Scoring Rubric (`1–10`)

| Score | Meaning | Merge signal |
|---|---|---|
| `9–10` | Clean, correct, well-tested; zero blockers (at most trivial optional nits) | Ship-ready |
| `7–8` | Sound overall, with 1–2 concrete fixable issues or missing edge-case coverage | Fix blockers, then re-score |
| `5–6` | Real correctness, security, data-integrity, or contract defects | Block until fixed |
| `1–4` | Fundamental architectural flaw, broken invariant, or unsafe change | Block and redesign |

### Mode A — Round 1 Prompt (`r1-brief.md`)

```markdown
# Council Review — Round 1 (Read-Only)

- **Repository / Branch:** <repo> @ `<HEAD_SHA>` (base: `<BASE_SHA>`)
- **PR / Task Goal:** <concise goal and acceptance criteria>
- **Diff Command:** `git diff <BASE_SHA>...<HEAD_SHA>`
- **Hard Rule:** Read-only inspection ONLY. Do not edit, create, or delete any repository files.

## Instructions

Inspect the diff and the surrounding codebase directly. Do not guess — verify every claim against the real code.

Return your review in this exact structure:
1. **Score:** `<N>/10` (one integer 1–10) and one-sentence verdict.
2. **Blockers (must fix before merge):** For each blocker give:
   - `file:line`
   - Why it is wrong (concrete bug, security/data/RBAC flaw, contract break, or missing invariant)
   - How to prove it fails (repro steps, failing case, or exact trace)
3. **Non-blocking risks / edge cases:** Maximum 3 genuinely important items; skip formatting or personal style preferences.
4. **Unverified:** Explicitly mark anything you could not confirm from the code or diff.
```

### Mode A — Round 2+ Prompt (Anti-Scope-Creep)

```markdown
# Council Review — Round <N> Re-Score (Read-Only)

- **Previous Commit:** `<PREV_SHA>` -> **Current Commit:** `<CURR_SHA>`
- **Incremental Diff:** `git diff <PREV_SHA>..<CURR_SHA>`
- **Hard Rule:** Read-only inspection ONLY. Do not edit, create, or delete any repository files.

## Prior Round Findings & Dispositions
<bulleted list of prior findings and how each was fixed or why it was dismissed>

## Instructions (Strict Anti-Scope-Creep)
1. Verify whether each previously raised blocker is actually fixed at `<CURR_SHA>`.
2. Check the incremental diff ONLY for regressions or genuinely severe blockers introduced by the fixes.
3. **Do NOT invent fresh nitpicks, style preferences, or new feature scope** that were not blockers in Round 1.
4. Return:
   - **Score:** `<N>/10`
   - **Prior Blockers Status:** `RESOLVED` / `STILL OPEN` per item
   - **New Regressions (if any):** `file:line` + concrete failure mode (or `None`)
   - **Verdict:** `LGTM` or `BLOCK`
```

---

## Mode B: 3-Round Blind Deliberation Protocol

### Round 1 — Blind Investigation Prompt (`r1-brief.md`)

Write the brief with **strictly neutral framing**: state the problem, symptoms, logs, commit SHA, constraints, and non-goals — never your suspected root cause or preferred design.

```markdown
# Council Deliberation — Round 1 (Blind Independent Investigation)

- **Repository / Commit:** <repo> @ `<HEAD_SHA>`
- **Question / Decision Fork:** <neutral problem statement>
- **Observed Facts / Evidence:** <logs, stack traces, metrics, or requirements>
- **Constraints & Non-Goals:** <hard boundaries, backwards compatibility, SLA, budget>
- **Hard Rule:** Read-only inspection ONLY. Do not edit, create, or delete any repository files.

## Instructions

Investigate the codebase independently and form your own diagnosis and concrete proposal. Do not hedge between three vague options — commit to your best grounded recommendation and show your evidence.

Return your proposal in this exact structure:
1. **Thesis (2–3 sentences):** Your root-cause diagnosis or recommended architectural choice.
2. **Codebase Evidence:** Concrete `file:line` citations proving the current behavior and constraints.
3. **Concrete Plan:** Step-by-step technical design, interfaces/data flow, and exact files or subsystems affected.
4. **Tradeoffs & Failure Modes:** What this choice makes harder, edge cases to guard, and rollback/migration safety.
5. **What Would Falsify This:** The single clearest test, measurement, or code fact that would prove your proposal wrong.
```

---

### Anonymization Checklist (Between Round 1 and Round 2)

Before building `r2-packet.md`, the orchestrator MUST sanitize every Round 1 file:

1. **Randomize labels every run:** Randomly permute the surviving proposals into `Proposal A`, `Proposal B`, `Proposal C` (and `Proposal D` if Fable was seated). Never keep a fixed order like "A is always Gemini".
2. **Store mapping privately:** Write `$RUN_DIR/mapping.json` (e.g. `{"A": "gpt-6.2-sol", "B": "gemini-4-neon-high", "C": "claude-opus-5.5"}`) and **do not pass it to any Round 2 delegate**.
3. **Strip all identity cues from proposal bodies:**
   - Remove CLI wrapper banners (`--- Claude Response ---`, `--- End Claude Response ---`, `ask-gemini: path=subscription`, Codex session headers/footers).
   - Remove any mention of model names (`Gemini`, `Claude`, `Opus`, `Fable`, `Codex`, `GPT`, `Sol`, `Anthropic`, `OpenAI`, `Google`).
   - Remove scratch file paths that contain provider names (`r1-gemini.md`, `r1-opus.md`, `r1-sol.md`).
   - Normalize top-level headings so every proposal uses the exact same `## Proposal A` / `## Proposal B` / `## Proposal C` skeleton.
4. **Preserve technical substance verbatim:** Never rewrite, soften, or editorialize a model's technical claims, code citations, or tradeoffs while anonymizing.

---

### Round 2 — Anonymized Peer Review Prompt (`r2-packet.md`)

```markdown
# Council Deliberation — Round 2 (Anonymized Peer Review)

- **Repository / Commit:** <repo> @ `<HEAD_SHA>`
- **Hard Rule:** Read-only inspection ONLY. Do not edit, create, or delete any repository files.

## Original Neutral Brief
<paste r1-brief.md problem statement & constraints>

## Anonymized Round 1 Proposals
(Author identities have been stripped and labels randomized.)

### Proposal A
<sanitized text>

### Proposal B
<sanitized text>

### Proposal C
<sanitized text>

## Instructions

Evaluate ALL proposals strictly on technical merit, codebase evidence, and operational safety. Verify contested `file:line` claims directly in the repository before criticizing or endorsing them.

Return your peer review in this exact structure:
1. **Proposal-by-Proposal Critique:** For each of Proposal A, B, C:
   - **Strongest insight:** What it got right that others missed.
   - **Concrete flaws / blind spots:** Specific technical gaps, false assumptions, or edge cases (cite `file:line`).
   - **Vote:** Exactly one of `ENDORSE`, `ENDORSE WITH AMENDMENTS`, or `OBJECT`.
   - **Required amendments or blocking objection:** Mandatory if voting `ENDORSE WITH AMENDMENTS` or `OBJECT`.
2. **Ranking:** Strict order (`1st`, `2nd`, `3rd`) with a 1-sentence reason for #1 over #2.
3. **Recommended Synthesis (optional):** Only if combining specific parts of two proposals is strictly stronger than any single proposal — state the exact boundary cleanly without kitchen-sinking.
```

---

### Round 3 — Consensus Verdict & Dissent Ledger Template

After unmasking `$RUN_DIR/mapping.json` and independently checking contested citations in the code, output:

```markdown
## Council Consensus Verdict — <Topic>

- **Quorum:** `3/3 families` *(or `DEGRADED (2/3 families — <provider> UNAVAILABLE: <reason>)`)*
- **Status:** `CONSENSUS` | `CONSENSUS WITH AMENDMENTS` | `SPLIT — DECISION NEEDED`
- **Commit Evaluated:** `<HEAD_SHA>`

### Unmasked Mapping & Vote Matrix

| Proposal | Author Model | Gemini 4 Neon (`high`) | Claude Opus 5.5 (`high`) | GPT-6.2 Sol (`high`) |
|---|---|---|---|---|
| **Proposal A** | `<model>` | `<VOTE> (#rank)` | `<VOTE> (#rank)` | `<VOTE> (#rank)` |
| **Proposal B** | `<model>` | `<VOTE> (#rank)` | `<VOTE> (#rank)` | `<VOTE> (#rank)` |
| **Proposal C** | `<model>` | `<VOTE> (#rank)` | `<VOTE> (#rank)` | `<VOTE> (#rank)` |

### Adopted Consensus Plan
- **Core direction:** <clear 2–4 line summary of winning proposal / synthesis>
- **Surviving amendments:**
  1. <concrete amendment + why it survived peer review>
  2. <concrete amendment>

### Dissent Ledger (Unresolved Disagreements)
*(Never hide or smooth over an `OBJECT` vote. Write `None — unanimous after amendments` only when genuinely unanimous.)*

| Dissenter | Objected To | Core Technical Objection (`file:line`) | Pivotal Assumption / Tradeoff for Ivan |
|---|---|---|---|
| `<model>` | `Proposal <X>` | <strongest concrete argument> | <exact judgment call needed> |

### Recommended Next Step
<1 concrete next action — e.g., proceed to `/conductor-gemini` implementation, run a falsification experiment first, or wait for Ivan's call on Dissent #1>
```

For major irreversible architecture calls, render this Verdict & Dissent Ledger as a self-contained HTML report under `<repo>/.conductor/reports/<YYYY-MM-DD-council-slug>.html` following [../../conductor/references/report-design.md](../../conductor/references/report-design.md), publish with `~/bin/report-link.py`, and hand Ivan the verified Bench URL labelled **private — Tailscale access required**.
