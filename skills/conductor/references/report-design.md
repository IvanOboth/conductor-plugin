# Report design contract and evidence (v2 — Craft Editorial Precision)

Reference for [Conductor](../SKILL.md)'s **Run review HTML** deliverable and all Bench HTML reports for Ivan. Reread this file and the skill's browser-evidence block from disk before authoring or substantially revising any report; an older report, template, or injected copy is not the design authority.

> **v2 Overhaul (27 Nov 2026 — independently audited with Claude Opus 5.5 & Claude Fable 5.2):** Retires the legacy warm-cream `#F7F4EE` + sage-green `#365B4B` boxed-card aesthetic. Reports are now authored as **modern editorial articles** aligned with the **Craft Insights Precision Mark** identity: Paper White ground, Obsidian ink, hairline structural rules instead of PowerPoint boxes, Signal Vermilion used sparingly as a precision mark, and **at most one full-bleed Obsidian turn band** where the verdict or thesis pivots.

## 1. Colour, ground, and visual rhythm

- **Primary ground — Paper White `#FAFBFD`** (never beige/cream `#F7F4EE`, never legacy sage green `#365B4B`).
- **Ink:** Obsidian `#111113` primary text, Graphite `#45464D` secondary prose, Muted Steel `#6B707B` metadata/captions. Hairline rules: `#DCDDE2` standard, `#111113` strong (`2px` group headers), `#2C2D33` on dark bands.
- **Secondary bands:**
  - **Warm Stone `#F4F2EC`** — at most one third of the page, reserved for evidence/audit/appendix bands.
  - **Cool Paper `#F1F3F6`** — only for code/data wells. **Never place Warm Stone and Cool Paper directly adjacent.**
- **One dark turn band (strictly max 1 per report):** Full-bleed **Obsidian `#111113`** ground with `#F4F5F8` / `#A9ABB4` text placed at the decisive thesis or verdict pivot (if a report has two dark bands, it has no turn). **Volt Lime `#DFF738`** appears *only* inside this Obsidian band (56px top mark, one highlighted phrase/figure, or underline — never as a large fill and never on light paper).
- **Signal Vermilion `#E04F16` (≤ 5% of any screen):** Contrast on Paper White is ~3.8–3.9:1, which fails WCAG AA for body-size text. Use `#E04F16` *strictly* for the `6px` kicker square (Precision Mark dot), `2px` reading progress bar, `2px` top rules on recommended rows, `28–32px` key-figure ticks, and large display numerals (`≥ 24px`). For links and small emphasis text, use darkened **`#B23C0C`** (5.6:1 contrast on Paper White) or Obsidian with a subtle underline.
- **Semantic status colours (all ≥ 4.5:1 on Paper White; zero sage green):**
  - Positive / Verified: Deep Pine `#17704F` (tint `#E9F3EE`)
  - Caution / Pending: Ochre `#8F5B00` (tint `#F8F0E0`)
  - Risk / Blocker: Cool Crimson `#A3182A` (tint `#F8E8EA`) — cooler than vermilion so risk never reads as brand accent
  - Info / Reference: Deep Indigo `#161B5C` (tint `#EAEEFA`)
- **Section pacing:** Generous vertical breathing room (`96px–112px` on desktop, `56px–64px` on mobile) separated by whitespace and a single `1px` hairline rule.

## 2. Five anti-patterns banned forever

1. **No 4-sided rounded cards, drop shadows, or tinted callout boxes** — group with a `2px solid #111113` top rule, hairline dividers, and whitespace (`border-radius: 0` on structural containers).
2. **No filled heading bars, legacy sage green (`#365B4B`), or cream ground (`#F7F4EE`).**
3. **No italic accent words or gradient text in headings** — place emphasis in the serif standfirst instead.
4. **No `"01 / 02 / 03"` slide eyebrows, monospace-as-label decoration, or pill-shaped status badges** — use plain uppercase sans kickers with a `6px` Vermilion square and `7px` square status markers.
5. **No Vermilion body text and no Volt Lime anywhere outside the Obsidian turn band.**

Replace boxed cards with editorial structures:
- **Strategy & narratives:** One `66ch` prose column paired with a `204px` sticky left section rail on desktop. Pull central claims into a left-ruled serif statement, not a shaded box.
- **Key figures:** Borderless hairline strip (`2px` Obsidian top rule, `28–32px` Vermilion tick above large `tabular-nums` numerals, half-size regular unit). On 390px phone, stack as crisp label-left / value-right ruled rows — never a cramped 2-up tile grid.
- **Comparisons:** Horizontal-hairline ledger tables only (no vertical cell borders, no zebra striping, right-aligned numbers). Mark the recommended option with a `2px` Vermilion top rule. On 390px phone, stack into labelled rows or use a segmented option switcher — zero horizontal page overflow.
- **Roadmaps:** Single hairline timeline spine with dates in a tabular left column; `"Now"` is the single Vermilion mark.
- **Call prep / run sheets:** Tabbed per person with spoken lines in large serif + one-click `Copy` button; objections/boundaries inside native `<details>` drawers.

## 3. Typography (100% offline system stacks)

- **Primary (headings, body, UI, tables):** `ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
- **Editorial serif (standfirst and spoken lines ONLY):** `ui-serif, "New York", "Iowan Old Style", Charter, Georgia, serif`
- **Monospace (paths, hashes, commands ONLY):** `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`
- **Scale & weight discipline:**
  - `h1`: `clamp(32px, 1.55rem + 2.4vw, 52px)`, weight `700`, tracking `-0.03em`, line-height `1.06`, `text-wrap: balance`
  - `h2`: `clamp(24px, 1.2rem + 1vw, 32px)`, weight `650`, tracking `-0.02em`, line-height `1.15`, `text-wrap: balance`
  - `body`: `17px` mobile / `18px` desktop, weight `400`, line-height `1.58`, `text-wrap: pretty`
  - Pair `400` against `650–700`; avoid indecisive `500`.
  - Apply `font-variant-numeric: tabular-nums lining-nums` on every numeral, table, and timeline.

## 4. Help Ivan understand

A report has two jobs: say what was done (or decided) and help Ivan understand what is going on.
- Lead with the outcome, verdict, or decision needed on **Screen 1** (even on a 390px iPhone — no cover slab pushing the answer below the fold). Do not invent a decision when none is needed.
- Explain the trigger, how parts interact, what changed, and why it produces the outcome. Distinguish intended effect from observed results. Use plain spoken English; explain technical terms on first use.
- Keep the conclusion, decisions, material failures, and risks visible. Tuck raw logs, long transcripts, full token tables, and deep file inventories into labelled native `<details>/<summary>` disclosures.
- Before delivery, check: can Ivan explain what happened, why it happened, and what it means without reading raw logs? If not, simplify the explanation or add a focused SVG plate.

## 5. Four disciplined interactions (and nothing else)

Keep JavaScript inline, vanilla, ~50–80 lines, zero external libraries, honouring `prefers-reduced-motion`:
1. **Reading progress bar:** Fixed `2px` Vermilion bar at top (`animation-timeline: scroll()` with scroll-listener fallback).
2. **Jump navigation:** Sticky left section rail on desktop highlighting the active section; on mobile (`≤ 920px`), a sleek `44–48px` sticky bottom jump bar (`padding-bottom: env(safe-area-inset-bottom)`) showing the current section and toggling a compact drawer.
3. **Segmented tabs:** Only for peer alternatives (e.g., Call 1 / Call 2 / Call 3, or Track 1 / Track 2) — never to hide part of a linear argument. Reveal all panels in `@media print`.
4. **One-click Copy button:** On spoken scripts, email text, or commands (`Copied` feedback for 1.5s).

**Banned:** scroll fade-ins, count-up number animations, parallax, carousels, and hover-only information.

## 6. Inline SVG architecture & data plates

- **Anatomy:** `2px` Obsidian top rule → bold title stating the finding → one-line subtitle with scope/unit → clean SVG graphic → `12.5px` source line.
- **No boxed flowchart nodes:** Place text directly on crisp hairline spines with small `8px` square nodes, straight/orthogonal connectors, and small open arrowheads.
- **Line & colour discipline:** `1px` (`vector-effect: non-scaling-stroke`) for structure, `2px` for highlighted data paths; neutral grey everywhere except **one accent series** (Vermilion `#E04F16` on Paper White, Volt Lime `#DFF738` on Obsidian). Label directly on the graphic — no separate legends.
- **Two drawings per complex plate:** Provide a wide SVG (`viewBox="0 0 720 ..."`) for desktop and a narrow vertical SVG (`viewBox="0 0 350 ..."`) for mobile swapped via CSS media query so labels never shrink to unreadable 4px text.

## 7. The 390px iPhone verification bar

Verify every served report with real screenshots at **1440px desktop** and **390px mobile**:
1. **Screen 1 answers:** Kicker, `h1`, serif standfirst, and top verdict/action are visible without scrolling past a giant banner.
2. **Zero horizontal page overflow:** `document.documentElement.scrollWidth <= window.innerWidth` at 390px (including with disclosures open).
3. **Readable mobile typography:** `17px` body, `20px` side margins, nothing below `12.5px`, `-webkit-text-size-adjust: 100%`.
4. **Thumb-safe targets:** `≥ 44px` tap targets on tabs, disclosures, copy buttons, and mobile jump bar; `scroll-margin-top` on headings.
5. **Full-bleed turns, stacked figures:** The Obsidian turn band runs edge to edge; key figures stack as ruled rows.

## 8. Canonical v2 CSS tokens

```css
:root {
  --paper: #FAFBFD;        --white: #FFFFFF;       --stone: #F4F2EC;     --chrome: #F1F3F6;
  --obsidian: #111113;     --ink: #111113;         --ink-2: #45464D;     --ink-3: #6B707B;
  --on-dark: #F4F5F8;      --on-dark-2: #A9ABB4;
  --rule: #DCDDE2;         --rule-strong: #111113; --rule-dark: #2C2D33;
  --signal: #E04F16;       /* rules, 6px square, ticks, >=24px numerals */
  --signal-text: #B23C0C;  /* 5.6:1 links & small emphasis */
  --volt: #DFF738;         /* Obsidian turn band ONLY */
  --ok: #17704F;           --ok-bg: #E9F3EE;
  --warn: #8F5B00;         --warn-bg: #F8F0E0;
  --risk: #A3182A;         --risk-bg: #F8E8EA;
  --info: #161B5C;         --info-bg: #EAEEFA;
  --sans: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --serif: ui-serif, "New York", "Iowan Old Style", Charter, Georgia, serif;
  --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  --measure: 66ch;
}
```

## 9. Screenshots, recordings, and Bench metadata

- **Screenshots:** Embed verification screenshots that prove a claim. Store large originals under `.conductor/reports/assets/<run-id>/` and reference them cleanly (`report-link.py` only ships assets under `.conductor/reports/`). Caption each with viewport + what it proves.
- **Discovery metadata (configured Bench only):** Include `<meta name="bench:...">` tags (`bench:type`, `bench:owner`, `bench:action`, `bench:action-url`, `bench:due`, `bench:evidence-date`, `bench:work`) in `<head>` per `domains/career-craft/bench/REPORTS.md`. Set `bench:owner` honestly (`ivan` only when a human decision is genuinely waiting) and `bench:evidence-date` to the newest evidence embedded.
- **Recording by surface:** Apply the evidence gate in [Conductor](../SKILL.md#browser-video-evidence) before recording.
  - **Web:** prefer direct MP4 on verified 0.37.1; reuse existing Playwright capture where it covers the flow.
  - **Native Android/iOS:** follow `mobile-app-testing` for device selection, durable recorder ownership, fresh UI observations, final-artifact provenance, and cleanup.
  - **iOS Simulator / macOS (Mac only):** `xcrun simctl io <device-udid> recordVideo --codec h264 <assets>/<flow>.mp4` or `screencapture -v`.
  - Embed with `<video controls preload="metadata" src="assets/<run-id>/<flow>.mp4">`. When recording is genuinely infeasible, state so honestly and use a captioned screenshot sequence.

## Browser video evidence

The evidence gate (**Choose evidence before recording**) and the browser recording procedure stay in [the skill itself](../SKILL.md#browser-video-evidence), between the `browser-evidence` markers: bench-factory's `tools/browser-evidence/install.py` copies that block from `skills/conductor/SKILL.md` into the installed browser skills. Apply it before any recording above.
