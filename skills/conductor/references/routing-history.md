# Routing history and evidence

Cold reference for [Conductor](../SKILL.md). The active routing is the skill's **Model routing and lanes** section; this file keeps the dated benchmarks, the retired models and the reasons behind past routing changes, so the skill itself stays short. Nothing here prescribes a model for a new lane: where this file and the skill disagree, the skill wins.

## 20 Nov 2026: GPT-6.2 Sol replaces GPT-6.1 Sol; Gemini 4 Neon joins

Ivan moved every GPT-6.1 Sol (`gpt-6.1-sol`) role to GPT-6.2 Sol (`gpt-6.2-sol`) on 20 Nov 2026, with the same efforts (`high` by default, `xhigh` only as the retry after a thin `high` pass, never `max`). Evidence, bench-factory#1176: on a set of 20 known review findings, GPT-6.2 Sol caught 15 and GPT-6.1 Sol caught 6, at the same price ($2/$10 per Mtok) and a 2.8-minute median review. GPT-6.1 Sol left routing.

The same day Gemini 4 Neon (`gemini-4-neon-high` through `ask-gemini`, on the Google AI Ultra subscription; $3/$15 per Mtok on the API path) joined for three uses: the cross-family reviewer when GPT-6.2 Sol cannot run (before the Opus 5.5 fresh-context fallback), a 3–5 day non-blocking shadow review beside GPT-6.2 Sol to compare catch rates on the same diffs, and multimodal review (`ask-gemini --file`). It is never used on personal-data or vault runs. Re-rate it from the shadow trial's catches before it takes any other role.

## Review-routing changes, Oct–Nov 2026

- **18 Nov 2026 — second Opus review removed.** From 31 Oct 2026 critical Opus-authored work got an Opus 5.5 `verify-lane` judgment review in fresh context beside the Sol review. Ivan removed it on 18 Nov 2026: critical Opus-authored work now gets the Sol `high` review alone, plus the orchestrator's read. The `verify-lane` still reviews critical work Sol wrote.
- **17 Nov 2026 — Sol reviews critical work at `high`.** Sol at xhigh showed no benefit over high on the bench: 2 of 139 vs 2 of 203 final-round blocks, at about 40% more tokens per review (measured on GPT-6.1 Sol). `xhigh` stays only as the retry after a thin `high` pass.
- **17 Nov 2026 — Codex-down reviewer.** Fable 5.2 as the reviewer in Sol's place cost a lot of tokens (bench-factory#955); Opus 5.5 `high` in fresh context took the role. Since 20 Nov 2026 Gemini 4 Neon comes first, and Opus is the fallback.
- **17 Nov 2026 — Fable epic orchestration became opt-in** (`~/intake-triage/EPIC_FABLE`); Opus 5.5 `high` orchestrates every epic by default.
- **12 Nov 2026 — `high` is the ceiling for Opus 5.5 review lanes** (Ivan: "opus reviews at xhigh are unnecessary, high is good enough"). Review lanes could run at `xhigh` from 31 Oct to 12 Nov 2026.
- **19 Oct 2026 — Opus 5.5 implementation and execution moved from `medium` to `high`.**

## Model ratings snapshot (22 Sep – 10 Nov 2026)

Rankings, higher = better. **Cost** is cost *per task*, not price per token — a model that finishes in a quarter of the tokens is cheaper at twice the price. **Reasoning** covers plans, reviews and judgment calls. **Autonomy** is how far a model gets unsupervised in a terminal, a browser or an ops loop. **Steerability** is whether it does what the work order said, no more and no less. **Taste** covers UI/UX, code quality, API design and copy in a UI. **Writing** is prose a human reads and judges the author by. The `gpt-6.1-sol` row predates GPT-6.2 Sol; GPT-6.2 Sol has not been rated on these axes.

| model       | cost/task | reasoning | autonomy | steerability | taste | writing |
|-------------|-----------|-----------|----------|--------------|-------|---------|
| opus-5.5    | 9         | 9.3       | 9.3      | 7.5 †        | 9 †   | 8.5 †   |
| fable-5.2   | 6 ¶       | 9.6 ¶     | 9.5 ¶    | 8.5 ¶        | 9 ¶   | 9 ¶     |
| gpt-6.1-sol | 9.5       | 8.9 §     | 9.1 §    | 9 §          | 5.5 § | 6.5 §   |
| gpt-6-luna  | 10        | 7.2 ‡     | 7.4 ‡    | 8.5 ‡        | 4 ‡   | 6 ‡     |

† Provisional (22 Sep 2026): the only evidence so far is Anthropic's own and early-tester quotes. Re-rate after two weeks of lanes. Adjust these numbers to your own plan and pricing; they are directional, not universal. The re-rate date of 6 Oct 2026 has passed without a re-rate; re-rate by 24 Nov 2026.

‡ Provisional (23 Sep 2026): GPT-6 Luna was released on 22 Sep 2026. These ratings are provisional internal routing estimates, not vendor or Artificial Analysis scores; steerability, taste and writing are unmeasured. Re-rate by 7 Oct 2026. That date has passed without a re-rate; re-rate by 24 Nov 2026.

§ Provisional (29 Sep 2026): from OpenAI's 29 Sep charts (vendor-reported, via Vellum) for GPT-6.1 Sol. Taste and writing are unmeasured. Re-rate by 13 Oct 2026. That date has passed without a re-rate; re-rate by 24 Nov 2026.

¶ Provisional (10 Nov 2026), from vendor evidence only. The `fable-5.2` row replaces the `fable-5.1` row. Steerability, taste and writing are carried over from Fable 5.1 and are unmeasured on 5.2. Re-rate by 24 Nov 2026 from `bench-factory/tools/model-evals`.

**What changed on 10 Nov 2026:** Fable 5.2 (`claude-fable-5-2`) replaced Fable 5.1 in every Fable role, and Fable 5.1 left routing. The `fable` alias resolves to Fable 5.2 on Claude Code 2.1.322 (checked with `claude -p --model fable --output-format json`). It costs $8/$40 per Mtok, with cache reads at $0.20, 5-minute cache writes at $10 and 1-hour cache writes at $16; Fable 5.1 was $10/$50 ($0.25, $12.50, $20), and Opus 5.5 is $4/$20 ($0.20, $5, $8). It has a 1M context at standard price, 128K maximum output and all five effort levels; the API defaults to `high`, the Claude apps and Claude Code to `medium`. Anthropic's launch table (9 Nov 2026, vendor-reported, highest effort unless noted), Fable 5.2 / Fable 5.1 / Opus 5.5: FrontierCode 2.0 49.1 (`xhigh`) / 32.4 / 45.5; FrontierSWE v2 69.9 / 56.3 / 62.3; AutomationBench 51.4 / 31.4 / 42.5; Terminal-Bench-Science 74.6 / 52.6 / 58.7; WANDR agentic search 82.1 / 68.7 / 72.3; OSWorld 2.1 89.3 / 83.5 / 87.2; Remote Labor Index 41.3 (`high`) / 17.9 / 21.3; HLE with tools 74.2 / 65.6 / 67.7; Chartography 73.4 / 44.8 / 64.4. Opus 5.5 leads only an unlabelled Elo row (1800 vs 1785). Anthropic's relative cost-per-task claims: Fable 5.2 at `high` ties Opus 5.5's best FrontierCode score for about half the cost; at `medium` it matches Opus 5.5's best WANDR score for about 40% of the cost; at `low` it matches Opus 5.5's best HLE score for under a tenth. These compare with Opus 5.5 at its best-scoring effort, not at `high`, so they do not show that Fable 5.2 is cheaper per task than an Opus 5.5 `high` lane. Anthropic still recommends starting with Opus 5.5 for most coding and knowledge work. No writing benchmark was published, and GPT-6.1 Sol is not in the launch table.

**What changed on 22 Sep 2026:** Opus 5.5 (`claude-opus-5-5`) replaced Opus 5 and became the default model for almost every lane. The `opus` alias resolves to it.

**The evidence (22 Sep–31 Oct 2026, Opus 5.5 against Fable 5.1; history).** Opus 5.5 costs $4/$20 per Mtok, with cache reads at $0.20 against Fable 5.1's $10/$50 and $0.25. On Anthropic's table it beats Fable 5.1 on every row: Terminal-Bench 4.0 66.4 vs 55.8, FrontierCode 54.4 vs 50.3, CursorBench 57.8 vs 51.8, GDPval-AA 1846 vs 1735, HLE 67.7 vs 65.6, OSWorld 2.0 81.8 vs 80.7. Those Opus figures are at `max` effort (Terminal-Bench at `xhigh`). Against GPT-6.1 Sol the published comparisons are OSWorld 2.0 (Opus 5.5 81.8 at `max` vs GPT-6.1 Sol 71.4 at `max`) and AutomationBench, where GPT-6.1 Sol scores 35.4–36.0% against Opus 5.5 `medium`'s 33.2%. Independent evidence so far comes only from Artificial Analysis: Opus 5.5 tops its Intelligence Index, and four of its five effort levels sit on the cost/intelligence frontier, below Fable 5.1's cost at the same score. No SWE-bench Pro, Arena or practitioner steerability data exists yet. On the bench, Fable 5.1 lanes cost $1,222 at list price from 19 to 31 Oct 2026; the same tokens at Opus 5.5 rates cost $526, and 68% of Fable's cost was 1-hour cache writes ($20 against $8 per Mtok). `verify-lane` was 63% of Fable spend, which is why the judgment review moved to Opus 5.5 on 31 Oct 2026. No bench run has put an Opus 5.5 reviewer beside Fable on the same diff; the Fable catches recorded in run lessons (a field stored in two places, per-page report periods, workflow dead ends) are the cases to watch.

**Effort evidence.** Anthropic's Terminal-Bench cost curve sets the effort. Opus 5.5 at `medium` scores about 57% for about $3 per attempt. At `high` it scores 64.2% for $3.88. `xhigh` adds about two points for double the cost, and `max` scores lower than `xhigh`.

**GPT-6.1 Sol evidence (29 Sep 2026)**, from OpenAI's charts via Vellum (vendor-reported): DeepSWE v1.1 75.2% at `high` for about $1.50 a task; OSWorld 2.0 (computer use) 71.4% at `max` for about $1.30 a task, with no `high` figure published; AutomationBench 35.4–36.0% for about $0.30, against Opus 5.5 `medium`'s 33.2%; GDP.pdf 32.0% at `high`; a factual error rate of 7.7% at `low`. It costs $2/$10 per Mtok. None of these results establish performance at our configured efforts except where the effort is named.

**Retired 29 Sep 2026:** GPT-6 Astra and GPT-6 Sol left routing, and GPT-6.1 Sol replaces both. It beats GPT-6 Sol everywhere at the same price (DeepSWE 75.2% vs 68.8%, OSWorld 2.0 71.4% vs 64.4%, factual errors 7.7% vs 11.4%) and comes within about two points of Astra, or beats it, at a fifth to a seventh of the cost (DeepSWE 74.8% at about $7.70, OSWorld 2.0 73.5% at about $9.30, GDP.pdf 32.2%); Astra's one remaining lead, AutomationBench 41.4%, does not justify keeping it.

**GPT-6 Luna evidence (23 Sep 2026).** It costs $0.10/$0.50 per Mtok. OpenAI's vendor figures report DeepSWE 66.6 at $0.22 per task and OSWorld 2.0 52.7 at $0.27 per task; Artificial Analysis reports $0.07 per index task.

**Codex's runtime reach widened (verified 2026-08-07)** and the routing follows it. The bundled `computer-use` plugin registers a `node_repl` MCP server that `codex exec` loads, so a headless shell-out now reads accessibility trees, clicks, types, and screenshots *arbitrary macOS apps* — native apps, menu-bar flows, Xcode/Simulator GUI steps, Chrome under the real logged-in profile. Surfaces that used to be unverifiable without a human are now codex-lane work; send any runtime check you can state as steps + an assertion there, whatever the surface. What did **not** move is authority: GPT-6.1 Sol's taste is a provisional 5.5, so it confirms mechanics and you judge the pixels — and its cost per task is low enough that the verify lane runs on every run, not only the cheap ones. "Verified" from a codex lane means *it functioned*, never *it looks right*.

## Prompt cache: 5 minutes, not 1 hour (1 Nov 2026)

The 1-hour cache used from 19 Oct cost more than it saved: a 1-hour write costs 2× input against 1.25× for 5 minutes, and replaying the request timings of 25–31 Oct 2026 showed 5 minutes would have cost $670 less that week (Workflow agents −$590; only `exec-lane` did better on 1 hour, by $110). A lane that waits more than 5 minutes for a typecheck slot, a test run or CI rewrites its whole context when it resumes, so keep long waits and full test suites that CI already runs out of lanes.

## Orca lanes: the 17 Sep 2026 measurement

Decided 17 Sep 2026, measured on the live bench. Tokens are the same either way — each lane is a fresh context — so the real cost is lifecycle and integration, not spend. An Orca lane leaves a 330–530 MB Claude session plus its MCP children (Playwright, Chrome) running until someone closes it, and it ends at a draft PR nobody integrates once the orchestrator is gone. On 17 Sep the bench carried 235 live Orca terminals, 227 of them silent for 7+ days (28 Claude sessions, 13 Codex, 32 Playwright MCP, 19 Chrome), swap 11 of 15 GB used with 17 GB RAM free, and 152 worktrees against 84 on 14 Sep.

## Compact in place: why (18 Nov 2026)

Why: on 17 Nov 2026 one epic run handed over 19 times in a day. Each hand-over cost about USD 9 to 10 at API prices: about USD 3 for the new session to read its way back in, USD 1 to 1.5 for the old session to write the order, and about USD 5 because the old session kept running beside its successor (a median of 53 minutes, up to 8 hours), sometimes doing the same work. The continuation order grew from 5 KB to 53 KB. A compaction costs about USD 1.0 to 1.3 on Opus 5.5 and USD 2.4 to 3.3 on Fable 5.2, and leaves a prompt about as small as a fresh session's.
