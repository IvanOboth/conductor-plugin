# Report design contract and evidence

Reference for [Conductor](../SKILL.md)'s **Run review HTML** deliverable. Reread this file and the skill's browser-evidence block from disk before authoring or substantially revising any run report; an older report, template or injected copy is not the design authority.

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

Apply the evidence gate in the skill's **Browser video evidence** block first. For flows it selects for video, use the tool for the surface and the run assets directory:

  - **Web:** first apply the evidence gate; when video is warranted, follow the Browser video evidence contract; prefer direct MP4 on verified 0.37.1. Reuse existing Playwright capture where it covers the flow.
  - **Native Android/iOS:** follow `mobile-app-testing` for device selection, durable recorder ownership, fresh UI observations, final-artifact provenance and cleanup. Mobile Next recording APIs or a durable owned ADB recorder are valid; the recorder need not belong to the orchestrator if the device lane owns its lifetime. Use the evidence gate before capture.
  - **iOS Simulator (Mac only):** `xcrun simctl io <device-udid> recordVideo --codec h264 <assets>/<flow>.mp4` in the background, drive, then SIGINT it.
  - **Native macOS app:** `screencapture -v <assets>/<flow>.mp4` (Ctrl-C to stop) — Mac only.
  - Embed with `<video controls preload="metadata" src="assets/<run-id>/<flow>.mp4">` and retain the original when converting from WebM; direct MP4 needs no duplicate. On the bench also drop the files under `~/reports/<repo>/<run>/` so they're viewable from the phone at https://bench.tailb5d047.ts.net/reports/. When recording is genuinely infeasible, a captioned screenshot sequence is the fallback — say so in the report; never present stills as if a recording existed.

## Browser video evidence

The evidence gate (**Choose evidence before recording**) and the browser recording procedure stay in [the skill itself](../SKILL.md#browser-video-evidence), between the `browser-evidence` markers: bench-factory's `tools/browser-evidence/install.py` copies that block from `skills/conductor/SKILL.md` into the installed browser skills. Apply it before any recording below.
