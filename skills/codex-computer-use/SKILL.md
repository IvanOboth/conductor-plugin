---
name: codex-computer-use
description: Ask Codex (GPT-6 Astra) to run local app verification that needs computer use — launching apps, driving a browser or simulator, capturing screenshots, or any independent runtime inspection outside Claude's current context. This is how GPT-6 Astra is invoked for computer-use verification. Use when the user asks Claude to have Codex or GPT-6 Astra test a flow, verify UI behavior, inspect a running app, capture screenshots, or report confirmation and feedback about implemented behavior. Do NOT use for ordinary code reading, typechecking, linting, or tests Claude can run directly.
---

# Codex Computer Use

Use Codex as a separate **local verification agent** when the task needs real UI interaction, screenshots, simulator/browser/device state, or an independent runtime check outside Claude's current context. Codex (GPT-6 Astra — computer use is its strongest suit: OSWorld 2.0 72.6, ScreenSpot-Pro 92.7) drives your machine at `--effort medium` for a stated flow, `high` when the next step depends on reading the screen; Claude reads back the screenshots and report and decides whether the behavior is right.

Do **not** reach for this for ordinary code reading, typechecking, linting, or tests Claude can run itself — those are cheaper inline. This is for when *seeing the running thing* is the acceptance test.

Launching apps, simulators, or browsers to verify the requested work is fine without asking. Ask first only if the run could disrupt the user's environment beyond that — closing their apps, changing system settings, or acting on real accounts or data.

## Three ways Codex does computer use

1. **Headless shell (default).** `codex exec` / `ask-codex` runs non-interactively and does computer use *through the shell*: `open -a`, `xcrun simctl` / Simulator, `agent-browser` or Playwright to drive a real browser, `screencapture` for pixels, `lsof`/`ps` to inspect a running server, `curl` against a local port. Scriptable, isolated, cheap — still the first choice for anything web, CLI, or simulator. Codex also carries the Playwright MCP (`mcp__playwright__browser_*`) headlessly, so it can drive an isolated browser without `agent-browser` at all. **Record flows as video, not GIF:** web → `agent-browser --session <lane> record start <dir>/<flow>.webm [url]` before the flow, `record stop` after (needs system `ffmpeg`), then `ffmpeg … -c:v libx264 -pix_fmt yuv420p -crf 23 -movflags +faststart` to mp4; iOS Simulator → `xcrun simctl io booted recordVideo`; Android emulator → `adb shell screenrecord`. The work order names the output path; the report lists it. This rung also runs on a **headless Linux server** (`ssh <host> codex exec …`, agent-browser + Playwright MCP) — rungs 2 and 3 below are macOS-only, and so are the simulators.
2. **Headless GUI computer use — `node_repl` + `@oai/sky`.** The bundled `computer-use@openai-bundled` plugin registers a `node_repl` MCP server in `~/.codex/config.toml`, and **`codex exec` loads it** — so accessibility-tree reads, clicks, typing, and per-app screenshots of *arbitrary* macOS apps are reachable from a plain Claude shell-out. Verified 2026-08-07: a headless `codex exec -s danger-full-access` bootstrapped `sky`, listed apps, and returned Finder's AX tree plus a PNG. Use it when the target has no CLI and no scriptable surface — a native app, a menu-bar flow, an Xcode/Simulator GUI step, or Chrome under the user's *real* logged-in profile.
3. **Codex desktop app (`@Computer` / `@AppName`).** The interactive front door to the same engine, at `~/.codex/computer-use/`. Reserve it for flows where a person should watch and intervene mid-run; a headless lane no longer has to hand a task back merely because it is GUI-shaped.

Take the cheapest rung that can prove the assertion: shell first, `sky` when nothing scriptable exists, the desktop app only when a human needs to be in the loop.

**Two cautions on the `sky` path.** It drives the user's *actual* desktop — the app it touches is the app they are using. For ordinary web QA prefer `agent-browser` or Playwright in their own session; reach for `sky`-on-Chrome only when the real logged-in profile is the point, and name in the work order which windows and tabs are off limits. Second, the CU service writes screenshots to its own temp dir as `file://` URLs, so the prompt must tell Codex to copy them into your artifacts directory or you get a verdict with no evidence.

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

Equivalent direct form (the reference invocation): `codex exec -s workspace-write "<prompt>"`. Use `-s danger-full-access` when Codex must act outside the repo working tree — launching a GUI app, or writing screenshots to a scratchpad path — never for acting on real accounts or data.

For a GUI target, drop to `codex exec` directly — `ask-codex` has no flag for full access (it offers only `--readonly` and workspace-write), and the lane needs to write screenshots outside the repo. This is the verified form:

```bash
codex exec -s danger-full-access "Use node_repl + @oai/sky for this. Bootstrap once with:
  globalThis.sky = (await import('@oai/sky')).sky;
<the steps, then the assertion>
For each state that matters, call sky.get_app_state({ app: '<display name or bundle id>' }), copy the file:// path at state.screenshot.url into <scratchpad>/verify/NN-label.png, and write the verdict to <scratchpad>/verify/report.md.
Touch no window other than <app>."
```

`sky` gives `get_app_state` / `list_apps` / `click` / `set_value` / `type_text` / `press_key` / `scroll` / `select_text` / `drag` / `perform_secondary_action`, all keyed on `element_index` from the accessibility tree. You do not need to spell those out — Codex loads the API from its own plugin skill; give it the target, the steps, and the assertion.

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

Keep it lean otherwise — hand over the target, the steps, and the assertion, then trust GPT-6 Astra to drive. Over-specifying every click wastes its run.

## Reporting back

Before relaying a Codex finding, look at the cited screenshot or artifact yourself and decide whether it actually shows what Codex claims. In the user-facing response, separate **what you confirmed from the pixels** from **what Codex reported but you couldn't independently see**.

Lead with the verdict against the acceptance check — did the behavior verify, yes or no — then the evidence (which screenshots, what they show). If Codex found a problem, show the screenshot that proves it, not just the prose.

If Codex found nothing wrong, say so plainly and name what it actually exercised (which flow, which viewports) so "verified" means something.

If `codex` is not installed or the run fails, report the error and offer to verify the flow yourself via `agent-browser` / the project's browser skill instead.
