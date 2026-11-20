# Report design contract and evidence

Reference for [Conductor](../SKILL.md)'s **Run review HTML** deliverable. Reread this file from disk before authoring or substantially revising any run report; an older report, template or injected copy is not the design authority.

## Report design contract

Use a light editorial document: warm off-white ground, dark ink, restrained sage accent. Lead with the outcome or decision and the next action, then develop the reasoning. Do not invent a decision when none is needed. Use a clear title, short standfirst and descriptive section headings; compact anchor navigation helps long reports.

## Help Ivan understand

A report has two jobs: say what was done and help Ivan understand what is going on. Explain the problem or trigger, how the relevant parts interact, what changed, and why that produces the outcome. For proposals, distinguish the intended effect from observed results. Use plain language, short explanations and concrete examples; introduce technical terms only when needed and explain them on first use. Keep implementation detail available as supporting evidence.

Always consider a visual while outlining the report. Prefer a diagram or flowchart for a multi-step process, decision, dependency, ownership boundary or cause-and-effect relationship; use before/after views to explain a meaningful change. Put it beside the explanation it supports, with a short caption stating the takeaway. A trivial update may be clearer in a sentence; do not add a decorative diagram to meet a quota.

Keep each visual focused on one question, with a clear reading direction, short plain-language labels and labelled arrows where their meaning is not obvious. Show only the parts needed to understand the point; split complex systems into smaller views. Ensure labels remain readable on a phone, and include a brief text explanation so the diagram is not the only way to understand it. Prefer inline SVG or HTML/CSS that works offline.

Before delivery, check: can Ivan explain what happened, why it happened and what it means without reading the raw logs or knowing the codebase? If not, simplify the explanation or add the missing visual.

Keep prose around 65–75 characters wide, body text at least 16px with 1.55–1.75 line height, generous section spacing and a distinct heading hierarchy. System fonts work offline; a restrained serif heading can add character. Use whitespace and thin rules for structure. Avoid repeated rounded cards, giant boxed flow steps, dashboard badges, decorative metrics and dense full-width prose. Reserve panels for content that benefits from grouping.

Use tables only for genuine comparisons. At phone widths, provide labelled stacked rows or a deliberate scrollable table with readable column widths; never squeeze labels and paths into one-word or one-character columns. Prefer compact numbered sequences for simple process explanations. Diagrams must communicate a relationship more clearly than prose.

Keep the conclusion, decisions, material failures and risks visible. Put raw logs, long reviewer transcripts and secondary file anchors in labelled native details/summary disclosures. Evidence should support a specific claim; do not fill the report with redundant screenshots or recordings of the report itself. Preserve provenance and uncertainty when restyling an existing report.

Use semantic headings, visible keyboard focus, adequate contrast and meaningful link labels. Keep HTML/CSS self-contained and offline-capable; avoid required remote fonts or rendering libraries. Check the served page at desktop and 390px phone widths, including open disclosures, long paths, navigation and overflow. Use screenshots for visual review; DOM checks alone do not establish readability. Route design/taste to the Claude lane and verify mechanics independently.

## Report content, screenshots and Bench metadata

- **Diagrams:** use them wherever they beat prose — decision trees for choices made, before/after architecture, lane/data flow. Inline SVG or styled HTML/CSS preferred; mermaid via CDN script is acceptable (the file is local, no CSP).
- **Screenshots:** embed every verification screenshot that mattered. Base64 data URIs keep the file self-contained; drop large originals in `.conductor/reports/assets/<run-id>/` and reference them. Caption each with viewport + what it proves.
- **Discovery metadata (configured Bench only):** the `<head>` carries the `bench:*` block (`bench:type`, `bench:owner`, `bench:action`, `bench:action-url`, `bench:due`, `bench:evidence-date`, `bench:work`) so the hub can catalogue the run — see "Declare what the report needs" in `domains/career-craft/bench/REPORTS.md` for the rules. Set `bench:owner` honestly: `ivan` only when a human decision is genuinely waiting, `agent` for routine agent-owned work. Set `bench:evidence-date` to the date of the newest evidence embedded in the report, not the date you wrote it.

## Recording by surface

Apply the evidence gate below first. For flows it selects for video, use the tool for the surface and the run assets directory:

  - **Web:** first apply the evidence gate; when video is warranted, follow the Browser video evidence contract; prefer direct MP4 on verified 0.37.1. Reuse existing Playwright capture where it covers the flow.
  - **Native Android/iOS:** follow `mobile-app-testing` for device selection, durable recorder ownership, fresh UI observations, final-artifact provenance and cleanup. Mobile Next recording APIs or a durable owned ADB recorder are valid; the recorder need not belong to the orchestrator if the device lane owns its lifetime. Use the evidence gate before capture.
  - **iOS Simulator (Mac only):** `xcrun simctl io <device-udid> recordVideo --codec h264 <assets>/<flow>.mp4` in the background, drive, then SIGINT it.
  - **Native macOS app:** `screencapture -v <assets>/<flow>.mp4` (Ctrl-C to stop) — Mac only.
  - Embed with `<video controls preload="metadata" src="assets/<run-id>/<flow>.mp4">` and retain the original when converting from WebM; direct MP4 needs no duplicate. On the bench also drop the files under `~/reports/<repo>/<run>/` so they're viewable from the phone at https://bench.tailb5d047.ts.net/reports/. When recording is genuinely infeasible, a captioned screenshot sequence is the fallback — say so in the report; never present stills as if a recording existed.

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
5. Embed `<video controls playsinline preload="metadata" src="assets/<run>/<flow>.mp4"></video>` in the run report with steps, environment/build, expected/actual result and assertions. Verify the served report and media. On Bench use `~/bin/report-link.py <report>` and deliver its verified private Tailscale URL. On Mac use the established report push and verify the Bench URL. Keep originals when creating derivatives; run Bench media conversion through `~/bin/bench-media-run -- ffmpeg ...` with bounded threads.

For bugs, capture before/after with matching steps, data and viewport when reproducible; say when the before state is unavailable. Never recreate a harmful production failure just for footage. Separate edited demonstrations from unedited verification evidence. For how-tos/journeys/features, include actor, prerequisites, step labels and successful end state; record only material approved for the intended audience.

Keep existing Playwright regression tests, assertions, traces, console/network evidence and flow-contract scorecards: they provide repeatability and diagnosis beyond video. Reuse an existing Playwright video capture if it covers the same flow; do not duplicate drivers solely for recording. Use native/device capture for native apps. When recording fails, report the actual failure and use captioned screenshots plus assertions as a declared fallback. Screenshots support visual review; the mechanics lane does not self-certify design quality.
<!-- browser-evidence:end -->
