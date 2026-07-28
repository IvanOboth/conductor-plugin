---
name: run-report
description: The closing convention for any substantial agent run (conductor, feature implementation, nightly shift, cloud routine). Use at the END of a run to publish the run report to GitHub, flip status labels, and append the telemetry ledger. Trigger when a run wraps, when the user says "close out the run", "run report", "log this run", or when another skill's instructions say to invoke run-report as its final step.
---

# run-report — the closing convention

Every substantial agent run ends the same way, regardless of which executor did the work. This feeds the review queue and the cost ledger in one step.

**Every step below is independently optional.** Do the ones the environment supports and skip the rest silently — a missing GitHub issue, missing labels, or an unconfigured ledger is not a failure. The minimum valid close is the in-session summary plus any artifact the run produced.

## The steps (in order)

### 1. Comment the run report on the GitHub issue or PR

*Skip if the run has no tracking issue and creating one isn't warranted — a docs edit or a local experiment doesn't need one.*

Post ONE comment on the issue/PR the run belongs to. Structure:

```markdown
## Run report — <run-id: YYYY-MM-DD-slug>

**What was done** — 2-5 bullets, plain language.

**Tests & verification** — what was run and the result (typecheck, unit,
browser drive). "Not verified" is a valid, honest entry.

**Evidence** — screenshots pasted inline (`gh` upload → markdown images
render in comments). Link the full report (Playwright HTML / video) if one exists.

**Artifacts** — the deliverable pages themselves, one per line as REPO-RELATIVE
paths. Mandatory whenever the run produced or updated an HTML artifact (brief,
design direction, review page, report). COMMIT the artifact to the repo — an
artifact only on local disk is invisible to anyone reviewing remotely.

**Decisions needed** — explicit questions, one per line, or "None".

**Cost** — paste the table from the telemetry step, if you ran it.
```

Post via `gh issue comment <n> -R <owner>/<repo> --body-file <report.md>` (REST fallback if GraphQL is rate-limited: `gh api repos/<owner>/<repo>/issues/<n>/comments -X POST -F body=@<report.md>`).

### 2. Attach heavy evidence

Screenshots ≤ a few images: paste inline in the comment. Full Playwright reports, videos, long logs: commit to the repo's reports location, then LINK from the comment. Never leave evidence only on local disk when the run is tracked remotely.

### 3. Flip the labels

*Skip if the repo doesn't use these labels — don't create a label taxonomy the project never asked for.*

- Work ready for the user's decision/merge → add `status:review` + `needs-review`, remove `status:running`/`status:active`.
- Fully merged/accepted → `status:done`.
- Stuck → `status:blocked`, and the Decisions section says exactly what's needed.

### 4. Append the telemetry ledger

*Skip if you aren't tracking run cost.*

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/conductor-report.py" \
  --run-id <YYYY-MM-DD-slug> --repo <repo> --issue "<repo>#<n>" \
  --skill <invoking-skill> --outcome <review|done|blocked> \
  --since <run start ISO, UTC>
```

It parses the session transcript + subagent sidechains + codex rollouts in the window, appends one line to the ledger (`~/.claude/telemetry/conductor-runs.jsonl` by default — override with `--ledger PATH`), and prints a markdown cost table. Paste that table into the step-1 comment's **Cost** section, so run the script BEFORE posting or edit the comment afterwards. Pass `--since` as the time this run actually began; the codex glob picks up any rollout in the window, so a tight window keeps unrelated codex sessions out.

Use `--dry-run` to print the table without writing to the ledger.

## Rules

- The report is evidence, not a claim: every "done" line must be backed by a diff, a test result, or a screenshot referenced in the same comment.
- Quick lookups and conversational sessions don't need this. A run that changed code, produced a deliverable, or spawned lanes does.
- If a repository holds sensitive or personal data, it can host reporting tooling without ever being an execution target — keep runs against such a repo to the ledger step only.
