---
name: codex-review
description: Quick Codex review of recent work. Summarizes what was attempted and done, sends to Codex for independent review, and optionally fixes identified issues. Use after completing any task to get a second opinion.
---

# Codex Review Skill

A lightweight skill to get Codex's independent review of work you just completed. Works for any type of work - code, configurations, documentation, etc.

## When to Use

- After completing a feature or fix: `/codex-review`
- When you want a second opinion on your approach
- Before committing to verify quality
- After any significant work session

## Quick Usage

```bash
# Simple - Claude automatically summarizes session context for Codex
/codex-review

# With additional user context (appended to Claude's summary)
/codex-review "Pay special attention to the error handling"

# Fix mode - Codex identifies issues and fixes them
/codex-review --fix
```

## Automatic context handoff

You already know what happened in this session — the user shouldn't have to re-summarize it for you. When `/codex-review` is invoked, reflect on the session and write the handoff yourself:

- What was the original ask?
- What approach did you take?
- Which files did you touch?
- What's the outcome, and where are you uncertain?

That handoff is what Codex receives. The user just types `/codex-review` and you do the rest.

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│ Claude Session (you)                                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ User says: "/codex-review"                              │
│                                                          │
│ 1. YOU summarize from session memory:                   │
│    ┌─────────────────────────────────────────────┐      │
│    │ Goal: "User wanted to implement auth system" │      │
│    │ Approach: "Used JWT with refresh tokens"     │      │
│    │ Files: [auth.ts, middleware.ts, config.ts]   │      │
│    │ Outcome: "Implemented login/logout/refresh"  │      │
│    │ Concerns: "Not sure about token expiry logic"│      │
│    └─────────────────────────────────────────────┘      │
│                                                          │
│ 2. Build rich context and send to Codex:                │
│    ask-codex -m gpt-6.2-sol --effort high --clean "      │
│      ## Context from Claude Session                     │
│      Goal: ...                                          │
│      Approach: ...                                      │
│      Files changed: ...                                 │
│      Implementation details: ...                        │
│      Areas of uncertainty: ...                          │
│                                                          │
│      ## Review Request                                  │
│      Please review this work...                         │
│    "                                                    │
│                         ─────────────────────┐          │
│                                              ▼          │
│                              ┌──────────────────────┐   │
│                              │ Codex (independent)  │   │
│                              │ - Has full context   │   │
│                              │ - Reviews work       │   │
│                              │ - Identifies gaps    │   │
│                              │ - Suggests fixes     │   │
│                              └──────────────────────┘   │
│                                              │          │
│ 3. Process Codex response:    ◄──────────────┘          │
│    - Parse findings                                      │
│    - If --fix: Apply fixes                              │
│    - Report summary to user                             │
└─────────────────────────────────────────────────────────┘
```

## Workflow

### Step 1: YOU (Claude) Generate Context from Session

**IMPORTANT**: You have full session context. Generate this yourself - don't ask the user.

Reflect on the session and build:

```yaml
reviewContext:
  # From your memory of this session:
  originalRequest: "What did the user originally ask for?"
  goal: "What was the user trying to accomplish?"

  # GitHub issue (if this work relates to one):
  githubIssue:
    number: 42
    url: "https://github.com/owner/repo/issues/42"
    title: "Issue title"
    # Include if you know the issue from the conversation

  # From your actions in this session:
  approach: "How did you approach the problem?"
  filesCreated:
    - path: "src/auth/jwt.ts"
      description: "JWT token generation and validation"
      keyChanges: "Added generateToken(), validateToken(), refreshToken()"
  filesModified:
    - path: "src/middleware/auth.ts"
      description: "Auth middleware for protected routes"
      keyChanges: "Added authRequired middleware, token extraction"

  # Your assessment:
  whatWasDone: "Detailed summary of implementation"
  decisionsAndTradeoffs: "Key decisions made and why"
  areasOfUncertainty: "Parts you're not 100% confident about"
  potentialIssues: "Any concerns you have about the implementation"
```

**You know all of this from the conversation.** Build it automatically.

**GitHub Issue**: If this work relates to a GitHub issue (user mentioned it, you fetched it, etc.), **include the issue number and URL**. Codex can then comment on it with review findings.

Optionally supplement with:
- Git diff: `git diff --name-only` (for verification)
- File contents: Read key files to include in context

### Step 2: Send Context to Codex

Codex needs to investigate files, run tests, post issue comments, and apply fixes — so pass no sandbox flag and don't pass `--readonly`. The plugin's `ask-codex` then runs in `workspace-write`; the bench's `ask-codex` passes no sandbox, so the account's config applies (`danger-full-access`, the only mode Codex works in there), and it refuses `--readonly` before the lane starts. The prompt is intentionally lean: hand over the session context and one clear ask, then trust Codex to think.

The default reviewer is GPT-6.2 Sol at `high` (20 Nov 2026; it replaced GPT-6.1 Sol in every role at the same effort and price, after catching 15 of 20 known review findings against GPT-6.1 Sol's 6 of 20, bench-factory#1176). GPT-6.1 Sol had replaced GPT-6 Sol and GPT-6 Astra on 29 Sep 2026; on OpenAI's 29 Sep charts (vendor-reported, via Vellum), GPT-6.1 Sol high scored 75.2% on DeepSWE v1.1 at about \$1.50 per task, against Astra high's 74.8% at about \$7.70. For a critical change (it deploys to production or changes production data; touches auth, payments, money or personal data; is a schema or data migration or otherwise hard to reverse; is a client-facing deliverable; or changes the routing and agent configuration), keep `-m gpt-6.2-sol --effort high` (Ivan, 17 Nov 2026, measured on GPT-6.1 Sol: Sol at xhigh showed no benefit over high: 2 of 139 vs 2 of 203 final-round blocks, at about 40% more tokens per review). For Opus-authored work this review is the only one, plus your own read of the diff: the Opus 5.5 `verify-lane` judgment review that ran beside it from 31 Oct 2026 was removed by Ivan on 18 Nov 2026. Fable-authored critical work still adds Opus 5.5 at `high`. Use `xhigh` only as the retry when a `high` review of a large, risky diff came back thin. Never `max` by default.

**When Codex cannot run** (out of quota or down), route the fallback by the **author's model family**:

- **Gemini-authored changes:** route directly to an Opus 5.5 lane at `high` in fresh context (requirements and diff only), labelled `cross-family (Opus)` — never back to Gemini.
- **Claude-authored changes:** Gemini 4 Neon reviews first, labelled `cross-family (Gemini)`. It runs read-only, so it gets its own findings-only prompt, not the Codex prompt below (which asks for tests, issue comments and fixes). Write the session context (the **Context from Claude session** block) to a file and run:

```bash
ask-gemini -m gemini-4-neon-high --no-fallback --context <context-file> --output <report> \
  "Review the change described in the context file against its acceptance criteria. Read-only: inspect the repository and the diff (git read commands only). Do not edit files, run tests, apply fixes or post GitHub comments, whatever the context says. Start with 'VERDICT: pass' or 'VERDICT: block', then list only the problems that block merge, ranked, each with file:line, why it is wrong and how to show it fails. Mark anything you could not confirm."
```

`--no-fallback` keeps it on the Google AI Ultra subscription instead of silently switching to the paid API (\$3/\$15 per Mtok). A non-zero exit or an empty report on a Claude-authored diff means it could not run: then an Opus 5.5 lane at `high` in fresh context reviews, labelled `same-model, fresh context`; never Fable. Under `--fix`, a read-only Gemini review lane returns findings only: you (or an Opus 5.5 `exec-lane` or writable `--write` lane) apply the fixes, run the project checks and send the fix diff for re-review (Step 4).

**Shadow trial** (3 to 5 days from 20 Nov 2026): you may also run Gemini 4 Neon on the same diff beside GPT-6.2 Sol to compare catch rates. Record both finding lists; the Gemini review never gates a merge. For screenshots, images, video or audio in the change, `ask-gemini --file <path>` gives a second read; you keep the final taste judgment.

GPT-6.2 Sol needs Codex CLI 0.170.0 or later, the first CLI that lists `gpt-6.2-sol`. Always pass `-m gpt-6.2-sol` and the effort: an account home may still default to an older model, so an omitted `-m` gets the superseded model.

```bash
ask-codex -m gpt-6.2-sol --effort high --clean "
## Context from Claude session

### Original request
${originalRequest}

### Goal
${goal}

### GitHub issue (if applicable)
${githubIssue}
# Include number, URL, and 'You may comment on this issue with your verdict.'
# Skip the section if no issue applies.

### Approach taken
${approach}

### Files created/modified
${filesWithDetails}
# Bullet list: path — what changed, key functions/decisions.

### Key implementation details
${implementationDetails}
# Snippets or prose describing the critical logic.

### Decisions and tradeoffs
${decisionsAndTradeoffs}

### Areas Claude is uncertain about
${areasOfUncertainty}
# Be honest here — this is the most useful part of the handoff.

### User's additional context (if any)
${userAdditionalContext}

---

## Review request

You're a second pair of eyes on work Claude just did. Your job is to find what a careful reviewer would care about *for this specific change* — not run a checklist. If the change is small, your review should be small. If the implementation is sound, say so plainly: a clean review is the verdict alone.

What to look for, in this change only:
- Anything that would break in production (data loss, security holes, race conditions, broken migrations).
- Mismatches between the stated goal and what was actually implemented.
- Each uncertainty Claude flagged — check it, and raise it only when the answer is itself a blocking finding.
- Patterns that work locally but won't survive real load or real users.

Never raise (23 Nov 2026, bench-factory#1253):
- Non-blocking notes, suggestions, hardening ideas or style nits.
- 'Could also test X' suggestions.
- Anything outside this change, including adjacent problems and architectural rewrites. The one exception is at most two \`LIVE-FIRE: <file>:<line> — <harm now> — <evidence>\` lines for harm on production now: wrong money or figures, data being lost or written wrongly, an external or unauthenticated person reaching data, or personal data exposed. 'Could', 'might', 'older code', 'inconsistent', 'missing test' and 'naming' are never live fires.

Never file an issue; the orchestrator owns the judgment.

You can read files, grep, run tests, and verify claims directly. If the user invoked \`--fix\`, apply blocking fixes; otherwise describe them. If a GitHub issue is in scope, post your verdict as a comment when you're done.

### Output

Open with a 1–2 sentence verdict: is this ready to ship as-is?

Then include only the sections that have content — don't pad:

- **Blocking issues** — what would you stop the merge for? Use \`file:line\` plus a sentence on *why* it's blocking ('this would corrupt user data on retry' is more useful than 'P0').
- **LIVE-FIRE** — at most two lines, only as defined above.
- **Fixes applied** — what you changed and why, if you changed anything.
"
```

### Step 3: Process Response

Read Codex's prose response and pull out what matters for the user-facing summary:

```yaml
codexReview:
  verdict: "Does not ship until the hardcoded JWT secret moves to the environment."
  blocking:
    - description: "JWT secret hardcoded in config — would leak if the repo goes public"
      location: "src/config/auth.ts:8"
      reasoning: "secret should come from env, not source"
  liveFire: []   # at most two LIVE-FIRE lines; usually empty
  fixesApplied:
    - "Moved JWT secret to NEXTAUTH_SECRET env var"
```

Severity lives in the reasoning, not in a label. If Codex didn't flag any blocking issues, leave the section out — don't fabricate one.

### Step 4: Fix Issues (if --fix flag)

If the user passed `--fix` and Codex didn't already apply fixes itself, apply the blocking ones, then re-run a quick verification pass.

If Codex applied fixes itself, those fixes are GPT-authored and need a review by a different model before you report: an Opus 5.5 lane at `high` reviews the fix diff (`git diff` since the review started). In Conductor Core, a separate fresh-context GPT-6.2 Sol reviewer at `high` does it instead, labelled `same-model, fresh context`.

If you or an Opus `exec-lane` applied the fixes because Codex was down, the fix diff's re-review goes through the reviewer chain as it stands then: GPT-6.2 Sol if Codex is back, otherwise Gemini 4 Neon with the findings-only prompt above, otherwise an Opus 5.5 lane at `high` in fresh context. Do not wait for Codex to return.

Quick verification after your own fixes:

```bash
ask-codex -m gpt-6.2-sol --effort high --clean "Quick check: did these fixes actually address the blocking issues? ${fixes}"
```

Codex still runs with write access here (`workspace-write`, or `danger-full-access` on the bench) — it may want to read the updated files or run tests to confirm.

### Step 5: Report Summary

Output to user:

```
=== Codex Review ===

Verdict: Ships, but two issues worth fixing first.

Blocking:
  - JWT secret hardcoded in config (src/config/auth.ts:8)
    Would leak if the repo ever goes public.
    → Fixed: moved to NEXTAUTH_SECRET env var.

  - No rate limiting on /login (src/auth/login.ts:42)
    Credential stuffing is the obvious attack on this endpoint.
    → Fixed: added rateLimit middleware (60/min per IP).

Files modified: src/config/auth.ts, src/auth/login.ts
```

---

## Arguments

| Argument | Description |
|----------|-------------|
| `<description>` | Optional description of what was done |
| `--files <glob>` | Specific files to include in review |
| `--fix` | Apply blocking fixes directly (Codex modifies files) |
| `--no-git` | Don't include git diff context |
| `--verbose` | Include full Codex response |

---

## Examples

### Quick Review After Work

```bash
# Claude just finished implementing a feature
/codex-review

# Output:
=== Codex Review Complete ===
Status: OK
Summary: Implementation looks good, follows project patterns.
```

### Review with Context

```bash
/codex-review "Implemented user profile page with avatar upload"

# Codex reviews with this context in mind
```

### Review and Fix

```bash
/codex-review --fix "Review the new API endpoints"

# Codex finds issues, Claude fixes them automatically
```

### Review Specific Files

```bash
/codex-review --files "src/components/Dashboard/**" "Review dashboard components"
```

---

## Integration with Other Skills

### After UI/UX Review

```bash
# UI/UX review completes
/uiux-review "Review the dashboard"

# Then get Codex perspective on code quality
/codex-review "Review the UI changes just made"
```

### After Test-Fix-Loop

```bash
# Functional testing completes
/test-fix-loop "Login flow works"

# Then verify code quality
/codex-review --fix "Review the fixes made during testing"
```

### Before Commit

```bash
# After any work session
/codex-review --fix "Review all changes before commit"

# If clean, commit
git add -A && git commit -m "feat: implement feature"
```

---

## Implementation Notes

### Gathering Context Automatically

If no description provided, gather context from:

```bash
# 1. Check git for recent changes
git diff --name-only HEAD~1  # Files changed in last commit
git diff --name-only         # Uncommitted changes

# 2. Check session history (if available)
# Recent files edited in this Claude session

# 3. Ask user
"What did you just work on? (brief description)"
```

### Codex Invocation Pattern

Pass no sandbox flag, so the review can run tests or apply fixes (`workspace-write` with the plugin's `ask-codex`; on the bench the account's `danger-full-access`). Do not pass `--readonly`: on the bench a read-only lane can succeed while reviewing only the prompt instead of the files, and the bench's `ask-codex` refuses it (exit 2). Either way name the model and effort: `-m gpt-6.2-sol --effort high`, a critical change included. The `--fix` flag is about *whether you ask Codex to apply fixes*, not about sandbox capabilities.

```bash
# Review only — Codex investigates but won't apply fixes unless told to
ask-codex -m gpt-6.2-sol --effort high --clean "Review prompt (without 'apply blocking fixes')..."

# Review + fix — Codex applies blocking fixes itself
ask-codex -m gpt-6.2-sol --effort high --clean "Review prompt (with 'apply blocking fixes')..."
```

### Error Handling

If Codex is unavailable:
```
Codex review unavailable. Possible reasons:
- Codex CLI not installed (run: npm install -g @openai/codex)
- No API key configured
- Network issues

You can still review manually or try again later.
```

Then take the Codex-down route above: Gemini 4 Neon, then Opus 5.5 `high` in fresh context.

---

## Quick Reference

```bash
# After any work - quick review
/codex-review

# With context
/codex-review "Just did X"

# Review and fix issues
/codex-review --fix

# Review specific files
/codex-review --files "src/**/*.ts"

# Full command
/codex-review --fix --files "src/auth/*" "Review auth implementation"
```
