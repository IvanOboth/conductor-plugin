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
│    ask-codex --clean "                                  │
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

Codex needs to investigate files, run tests, post issue comments, and apply fixes — so use the default `workspace-write` sandbox (don't pass `--readonly`). The prompt is intentionally lean: hand over the session context and one clear ask, then trust Codex to think.

```bash
ask-codex --effort xhigh --clean "
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

You're a second pair of eyes on work Claude just did. Your job is to find what a careful reviewer would care about *for this specific change* — not run a checklist. If the change is small, your review should be small. If the implementation is sound, say so plainly.

Things worth raising:
- Anything that would break in production (data loss, security holes, race conditions, broken migrations).
- Mismatches between the stated goal and what was actually implemented.
- Each uncertainty Claude flagged — validate the choice or push back with reasoning.
- Patterns that work locally but won't survive real load or real users.
- Simpler approaches that would make the change clearer or smaller.

Things probably not worth raising:
- Style nits the linter already covers.
- 'Could also test X' suggestions when existing tests are reasonable.
- Architectural rewrites of code that wasn't part of this change.

You can read files, grep, run tests, and verify claims directly. If the user invoked \`--fix\`, apply blocking fixes; otherwise describe them. If a GitHub issue is in scope, post your verdict as a comment when you're done.

### Output

Open with a 1–2 sentence verdict: is this ready to ship as-is?

Then include only the sections that have content — don't pad:

- **Blocking issues** — what would you stop the merge for? Use \`file:line\` plus a sentence on *why* it's blocking ('this would corrupt user data on retry' is more useful than 'P0').
- **Worth raising** — flagged but not blocking.
- **Claude's uncertainties** — address each one by name.
- **What's good** — only if something specifically stands out.
- **Fixes applied** — what you changed and why, if you changed anything.
"
```

### Step 3: Process Response

Read Codex's prose response and pull out what matters for the user-facing summary:

```yaml
codexReview:
  verdict: "Ships, but rate limiting on /refresh is worth a follow-up."
  blocking:
    - description: "JWT secret hardcoded in config — would leak if the repo goes public"
      location: "src/config/auth.ts:8"
      reasoning: "secret should come from env, not source"
  worthRaising:
    - description: "No rate limiting on /login or /refresh"
      location: "src/auth/login.ts:42"
      reasoning: "credential stuffing is the obvious attack here"
  claudeUncertainties:
    - claudeAsked: "Token rotation logic on refresh"
      codexResponse: "Logic is correct; the rotation window is fine"
  whatGood:
    - "Refresh tokens in httpOnly cookies — right call"
  fixesApplied:
    - "Moved JWT secret to NEXTAUTH_SECRET env var"
```

Severity lives in the reasoning, not in a label. If Codex didn't flag any blocking issues, leave the section out — don't fabricate one.

### Step 4: Fix Issues (if --fix flag)

If the user passed `--fix` and Codex didn't already apply fixes itself, apply the blocking ones, then re-run a quick verification pass:

```bash
ask-codex --clean "Quick check: did these fixes actually address the blocking issues? ${fixes}"
```

Codex still runs in `workspace-write` mode here — it may want to read the updated files or run tests to confirm.

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

Worth raising:
  - Consider rotating refresh tokens on use; not blocking,
    but reduces blast radius if one leaks.

Claude's uncertainties:
  - Token rotation logic — verified correct, rotation window is fine.

What's good:
  - Refresh tokens in httpOnly cookies — right call.

Files modified: src/config/auth.ts, src/auth/login.ts
```

---

## Arguments

| Argument | Description |
|----------|-------------|
| `<description>` | Optional description of what was done |
| `--files <glob>` | Specific files to include in review |
| `--fix` | Apply blocking fixes directly (Codex modifies files) |
| `--fix-all` | Apply both blocking fixes and worth-raising fixes |
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

Use `workspace-write` (the default) when the review must run tests or apply fixes; pass `--readonly` when it only reads the diff (the conductor's cross-family review of documentation, for example). Either way pass `--effort xhigh` — this is the judgment lane. The `--fix` flag is about *whether you ask Codex to apply fixes*, not about sandbox capabilities.

```bash
# Review only — Codex investigates but won't apply fixes unless told to
ask-codex --clean "Review prompt (without 'apply blocking fixes')..."

# Review + fix — Codex applies blocking fixes itself
ask-codex --clean "Review prompt (with 'apply blocking fixes')..."
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
