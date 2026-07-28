---
name: codex-computer-use
description: Ask Codex (gpt-5.6 Sol) to run local app verification that needs computer use — launching apps, driving a browser or simulator, capturing screenshots, or any independent runtime inspection outside Claude's current context. This is how gpt-5.6 Sol is invoked for computer-use verification. Use when the user asks Claude to have Codex or gpt-5.6 Sol test a flow, verify UI behavior, inspect a running app, capture screenshots, or report confirmation and feedback about implemented behavior. Do NOT use for ordinary code reading, typechecking, linting, or tests Claude can run directly.
---

# Codex Computer Use

Use Codex as a separate **local verification agent** when the task needs real UI interaction, screenshots, simulator/browser/device state, or an independent runtime check outside Claude's current context. Codex (gpt-5.6 Sol) drives your machine; Claude reads back the screenshots and report and decides whether the behavior is right.

Do **not** reach for this for ordinary code reading, typechecking, linting, or tests Claude can run itself — those are cheaper inline. This is for when *seeing the running thing* is the acceptance test.

Launching apps, simulators, or browsers to verify the requested work is fine without asking. Ask first only if the run could disrupt the user's environment beyond that — closing their apps, changing system settings, or acting on real accounts or data.

## Two ways Codex does computer use

1. **Headless shell (default — what this skill shells out to).** `codex exec` / `ask-codex` runs non-interactively and does computer use *through the shell*: `open -a`, `xcrun simctl` / Simulator, `agent-browser` or Playwright to drive a real browser, `screencapture` for pixels, `lsof`/`ps` to inspect a running server, `curl` against a local port. This covers the large majority of "go verify the running app" tasks and is fully scriptable, so it's the path a skill uses.
2. **Desktop-app Computer Use plugin (interactive).** True GUI pointer/keyboard control of arbitrary apps lives in the **Codex desktop app** (installed at `~/.codex/computer-use/`), invoked *in the app* with `@Computer` or `@AppName` (e.g. `@Chrome`). It cannot be driven headlessly from a Claude shell-out — if a task genuinely needs a human-like click-through of a non-scriptable native app, tell the user to run it in the Codex app rather than pretending to do it here.

If shell-level verification can prove the behavior (nearly always for web/CLI/simulator work), use path 1. Only escalate to the user + path 2 when the target can't be driven any other way.

## Workflow

**1. Decide the acceptance check.** Before invoking Codex, know exactly what "verified" means: the concrete observation that proves the work is done ("the actuals page renders 4 rows at 390px with no horizontal scroll and no console errors"; "the export button downloads a CSV whose row count matches the on-screen count"). A computer-use run without a crisp assertion produces a vibe, not evidence.

**2. Write a self-contained prompt.** Codex does not share Claude's context — spell out how to launch/reach the thing, the exact steps, the assertion, and where to leave artifacts. See *Prompt requirements* below.

**3. Invoke Codex.** Default to `ask-codex` (workspace-write) so Codex can run shell commands, launch the app, and write screenshots + a report to disk:

```bash
ask-codex --clean "
<self-contained computer-use prompt — see below>
Save screenshots to <scratchpad>/verify/ as NN-label.png.
Write your findings to <scratchpad>/verify/report.md when done.
"
```

Equivalent direct form (the reference invocation): `codex exec -s workspace-write "<prompt>"`. Use `-s danger-full-access` only when Codex must act outside the repo working tree (e.g. launching a GUI app, writing screenshots to an arbitrary path) and workspace-write blocks it — never for acting on real accounts or data.

- **Long runs** (browser flows, simulator boots) routinely exceed Bash's 10-minute timeout. Launch with `run_in_background: true` and a generous timeout, or poll for the report file.
- **Artifacts, not stdout.** Codex's stdout is session-log noise. Have it save screenshots to a named directory and its findings to a report file — those are the deliverable.
- **Own browser session.** If Codex drives `agent-browser`, give it its own `--session` name; never the shared one, or it collides with Claude's session.

**4. Read the pixels yourself.** `Read` the screenshots Codex saved and its report. **Codex confirms mechanics** ("page loaded, no console errors, CSV downloaded"); **only you judge whether it *looks* right.** Never accept "verified" on a visual change without seeing the pixels. This is the whole point of computer-use verification — a text "looks good" is not evidence.

## Prompt requirements

A computer-use prompt Codex can execute unsupervised includes:

- **How to reach the target** — the dev URL (assume the server is already running unless told otherwise; don't have Codex start `pnpm dev` and hang), the app to `open`, or the simulator to boot. Include any auth: which test account, or the pre-authed session/profile to use.
- **The exact steps** — navigate here, click this, fill that. Concrete, in order.
- **The assertion** — the single observation that proves success, stated so Codex can report pass/fail against it.
- **The viewports/states that matter** — e.g. capture at 390px and 1280px; capture the empty state *and* the populated state.
- **Where to put artifacts** — screenshot directory (`NN-label.png`) and report path.
- **What not to touch** — don't submit real forms, don't act on production data, don't close the user's other apps.

Keep it lean otherwise — hand over the target, the steps, and the assertion, then trust gpt-5.6 Sol to drive. Over-specifying every click wastes its run.

## Reporting back

Before relaying a Codex finding, look at the cited screenshot or artifact yourself and decide whether it actually shows what Codex claims. In the user-facing response, separate **what you confirmed from the pixels** from **what Codex reported but you couldn't independently see**.

Lead with the verdict against the acceptance check — did the behavior verify, yes or no — then the evidence (which screenshots, what they show). If Codex found a problem, show the screenshot that proves it, not just the prose.

If Codex found nothing wrong, say so plainly and name what it actually exercised (which flow, which viewports) so "verified" means something.

If `codex` is not installed or the run fails, report the error and offer to verify the flow yourself via `agent-browser` / the project's browser skill instead.
