# Working agreements

Global agent config. Install to `~/.claude/CLAUDE.md` — it applies to every project.

Tune the **lane assignments** and the **cost** column to what you actually pay and what
you actually work on. Leave the *gates* alone — "what earns an agent", the fan-out sizing
rules, and the Opus counter-behaviours. Those are what keep the bill predictable, and
they are the parts most tempting to delete because they read as restrictive.

## Orchestration

Run the main loop at **`high`** effort. Ultracode is not a model — it is `xhigh` reasoning
on the main loop *plus* a standing "author a Workflow for everything, cost be damned"
instruction. Neither is required to fan out: `Workflow` and `Agent` are available at
**any** effort level. Invoke them **on demand** — only when a task genuinely benefits
from decomposition, parallel fan-out, or independent verification.

### Model routing

Rankings, higher = better. **Cost** is cost *per task*, not price per token — a model
that finishes in a quarter of the tokens is cheaper at twice the price. **Reasoning** is
neutral problem-solving: plans, reviews, judgment calls. **Autonomy** is how far a model
gets unsupervised in a terminal, a browser or an ops loop. **Steerability** is whether it
does what the work order said, no more and no less — it is what most often decides
whether a dispatched lane comes back usable. **Taste** covers UI/UX, code quality, API
design, and copy-in-a-UI. **Writing** is prose a human reads and judges the author by —
emails, proposals, long documents, scripts, prompt packages — a separate axis because a
model can have taste in code and still write slop.

| model       | cost/task | reasoning | autonomy | steerability | taste | writing |
|-------------|-----------|-----------|----------|--------------|-------|---------|
| gpt-6-astra | 8         | 8.8       | 9.5      | 9.5          | 6     | 7       |
| opus-5      | 5         | 8.5       | 8.2      | 6            | 8.5   | 8       |
| fable-5.1   | 5         | 9.2       | 8.8      | 8.5          | 9     | 9       |

List prices per Mtok as of Sep 2026: `gpt-6-astra` $10/$50 (cache reads $1, Fast mode
2× on the API and 2.5× in Codex, long-context premium above 272K input) · `opus-5` $5/$25
(batch $2.50/$12.50, Fast mode $10/$50, cache reads $0.50) · `fable-5.1` $10/$50 (batch
$5/$25, cache reads $0.25). Per task the order inverts: on Terminal-Bench 4.0's own
leaderboard Astra resolves 58.2% for $3.3k and 1.5B tokens, Fable 5.1 57.9% for $6.2k and
2.7B, Opus 5 51.8% for $6.0k and 6.5B. On a ChatGPT subscription a codex lane costs
5-hour-window quota rather than dollars, which only widens the gap.

**GPT-6 Astra replaced GPT-5.6 Sol on 2026-09-05** (released 2026-09-03; set
`model = "gpt-6-astra"` in `~/.codex/config.toml`). One GPT row — effort is the dial — and
the separate cheap-codex sweep tier is gone; sweeps are Astra at `low`. What moved:
autonomy — Astra leads the computer-use, terminal and automation boards and does it cheapest (OSWorld 2.0 72.6 vs Opus 5
70.2 at under half the cost per task; Terminal-Bench 4.0 58.2 vs Fable 5.1 57.9 vs Opus 5
51.8 on tbench.ai's leaderboard (OpenAI's own table: 57.7 / 55.8 / 52.3); SRE-Bench 88 vs 12.5; AutomationBench 41.4 vs 31.4; Agents' Last Exam 59.3 vs 55.5
at 65% fewer output tokens than Opus 5; ARC-AGI-3 99.9 on OpenAI's stateful harness, 62.7
on the neutral one, vs Opus 5 30.2). What did not: neutral reasoning — Artificial
Analysis's Intelligence Index is 61, identical to Sol, vs Fable 5.1 at 66; the Coding
Agent Index 67 is level with Opus 5 and behind Fable 5.1 (70); no SWE-bench Pro figure was
published; GDPval-AA (professional work products) dropped ~80 Elo. Steerability went up —
mid-task steering keeps the original job, misaligned outcomes 3.4% vs 18.8%, hallucination
51% vs 92%. Two things to counter in a work order: its reasoning is terser and harder to
audit, so demand evidence rather than claims; and its Codex window is 272K by default
(`~/.codex/models_cache.json`; 872K max under a ChatGPT login via `model_context_window`;
1.05M is the API figure), so raise it for the lane or split orders at ~200K.

**Astra effort is the dial** (`ask-codex --effort LEVEL`): `low` for sweeps with exact
anchors; `medium` the implementation default; `high` when retries, ownership, persisted
state or recovery paths are involved, and for volume writing; `xhigh` for the cross-family
review; `max` for adversarial verification; `ultra` (Codex only) — Astra delegating to its own parallel
subagents — only for a self-contained long-horizon lane whose order caps the fan-out
(Codex subagents inherit the parent's model, so budget Astra-priced workers), never for a
lane the orchestrator is already fanning out.

**Fable 5.1 replaced Fable 5 on 2026-09-01** (`model: "fable"` resolves to it). Same list
price, cache reads at a quarter, and the gains are where lanes run long: hours-long agentic
coding, documents / spreadsheets / decks from a blank page, multistep research, dense-PDF
vision, full-1M-context reasoning, computer use that recovers from failed steps. Anthropic's
own guidance is the routing rule: **start with Opus 5; use Fable 5.1 for demanding reasoning
and long-horizon work, or when Opus 5 at higher effort still falls short.** Counter four 5.1
behaviours in a work order: one tool call per turn where Fable 5 batched (say "issue
independent reads in one turn"); answers from memory at `low` effort (never dispatch it at
`low` for research or verification); whole-file rewrites for small edits (say "targeted
edits only"); denser prose with less formatting (writing orders ask for paragraph breaks).

**Writing is its own routing problem.** Published head-to-heads (Jul–Sep 2026) put Fable
ahead of the GPT family on prose, and 5.1's prose is level with Fable 5's. Nothing yet puts
Astra ahead of Sol on prose. GPT prose is competent, plain, and carries none of Claude's
house tics — the "it's not X, it's Y" reflex, tricolons, the pre-emptive caveat, the closing
flourish. Astra is the better *volume* writer even though Fable is the better *writer*.

**Opus 5's numbers are effort-dependent — effort is the dial, not the model choice.** Read
the reasoning column as ~8.5 at `xhigh`/`max` and ~8 at `medium`.

**Why steerability is a separate axis.** Opus 5 has *not* regressed on capability. It leads
where work is messy and repo-shaped — SWE-bench Pro 79.2% with no Astra figure published,
BenchLM's agentic aggregate 77.4 vs Astra's 70.3 (Fable 5.1 tops it at 78.7) — and is level with Astra on DeepSWE and
FrontierCode. What degraded is obedience, consistently reported: ignores explicit
`CLAUDE.md` constraints; **"done but not done"** — declares fixes complete while leaving
pieces unimplemented; expands scope beyond the ask; delegates to subagents more readily
than prior models. So route away from Opus when a task is *steerability-sensitive*, not
when it is merely hard.

**Cost per task depends on the lane's shape.** Opus 5 and Fable 5.1 both rate 5; read-heavy
lanes (reviews, verification, cached-corpus research) favour Fable (cache reads at a quarter of
Opus's price, about half the tokens per task); output-heavy lanes (long HTML, long documents,
bulk generation) favour Opus (half the output price). Fable reviews, Opus designs.

### How to apply

- These are defaults, not limits. If a cheaper lane's output doesn't meet the bar, rerun
  with a smarter one without asking. Judge the output, not the price tag.
- When axes conflict for anything that ships: **the axis the lane is about (reasoning for
  plans and reviews, autonomy for execution) > steerability > taste > cost per task.**
- **Effort, not tier, is the first knob.** Before escalating opus → fable, re-run the same
  lane at higher effort. Before dropping opus → codex for cost, drop effort first. Never
  run `fable` at `low` for anything that must look something up.
- **Terminal, DevOps, infra, CI, migrations, SRE** → `gpt-6-astra` at `medium` via codex, first choice.
  Terminal-Bench 4.0 58.2 vs 57.9/51.8 at half the cost per task, SRE-Bench 88 vs 12.5.
- **Patterned multi-file refactors** (rename everywhere, apply a contract across modules)
  → `gpt-6-astra` at `medium`. Its patch format survives multi-file edits better than raw
  diffs, at about a third of Sol's tokens.
- **Bulk / mechanical work** → `gpt-6-astra` at `low`/`medium`, one lane per item —
  steerability 9.5 and the cheapest cost per task on those boards. `opus` at `low`
  (`bulk-lane`) only when the idiom is Claude-family (skills, agent definitions, CLAUDE.md
  conventions) or as the quota-overflow lane. Don't reach for `fable` for bulk.
- **Messy repo-level bug hunts, unknown scope** → `opus` at `high`+ stays the default. When
  Opus at `max` has missed, `gpt-6-astra` at `high` is a legitimate cross-family second
  attempt, not a downgrade.
- **Long-horizon lanes** (one lane that runs for hours or spans sessions) → `fable` at
  `high`+ when the lane is repo-shaped or document-shaped (a multi-module feature, a deep
  research brief, a document or deck from nothing, a dense-PDF read), on its 1M window.
  `gpt-6-astra` at `high` when the long lane is browser-, computer-use-, ops- or
  spreadsheet-shaped (automation, runbooks, financial models, data-science tasks in real
  software), with `model_context_window` raised for the lane — or `ultra` when the order
  can cap its own fan-out.
- **User-facing surfaces** (UI, copy-in-a-UI, API design) need taste ≥ 7 → `opus` (default)
  or `fable` when taste *is* the deliverable. Astra has no published taste data.
- **Writing, high stakes** (a counterparty email, a proposal, an investor or board document,
  anything with your name on it) → `fable` at `high`, the bundled `write-lane` agent. Opus 5
  at `xhigh` when the document is long and structured rather than voice-critical.
- **Writing, volume or structured** (prompt packages and generated-video blocks, storyboards,
  shot lists, internal docs, first drafts, routine mail) → `gpt-6-astra` at `high` via
  `ask-codex --effort high --context brief.md --output draft.md`; you hold the brief and
  edit the draft. A slop-and-cost bet, not a quality bet — anything that leaves the building
  still gets a Fable or Opus edit pass. Every writing order states audience, register,
  length ceiling, the reader's one action, banned phrases, and a voice sample.
- **Reviews** → `fable` at `high`/`max` is the Claude-family judgment lane (the bundled
  `verify-lane` agent, Fable 5.1 at `max`): a review is read-heavy, where Fable's cache price and
  token economy beat Opus at the same cost per task, and Fable leads on reasoning and
  steerability. `opus` at `max` is the second Claude opinion on a close call. `gpt-6-astra` at
  `xhigh` via `codex-review` is the co-equal cross-family review — run both on anything that
  ships. Never review at `low`.
- **Runtime verification** → `gpt-6-astra` at `medium` for mechanics, `high` when the next
  step depends on reading the screen — on every run; it costs a fraction of an Opus pass.
  Its ceiling is taste: it confirms the thing *functioned*; the screenshots come back for
  Claude to judge whether it *looks* right.
- **The plan, the work orders and the final review stay with the orchestrator, and the
  orchestrator stays Claude.** Astra's steerability would suit the seat, but the seat needs
  the 1M window, the Claude Code harness, and the reasoning lead, which is where a plan and
  a final review live. Cross-family verification only exists if the lanes are the other
  family from the seat. Give the codex lane more of the dispatched surface, never the
  baton. Fable 5.1 is the best Claude in that seat (steerability 8.5); running it as the
  main loop changes no lane routing.
- **Cross-family routing is also availability insurance.** A setup with every lane on one
  provider has a single point of failure, and provider incidents do happen.
- **Never pay for Fast mode on a dispatched lane** — 2× the price (2.5× for Astra in Codex) for the
  same intelligence, just faster tokens. That is for interactive work where you are watching.
- **Never use Haiku** for judgment work.

### Counter these two Opus 5 behaviours when it orchestrates

1. **It delegates reflexively.** Don't spawn an agent for what a few tool calls would
   finish, and don't split coupled work.
2. **It self-verifies without being told.** Do NOT put "verify your work" or
   "double-check" scaffolding in work orders — that produces over-verification, not more
   rigour.

### What earns an agent — gate this BEFORE sizing anything

**Scouting is the orchestrator's job, not a lane.** Delegated discovery is the most
expensive waste there is: agents burn a full context each, return prose you must
re-verify, and answer worse than the grep you could have run in two seconds.

Four questions before any dispatch:

1. Could a `grep`/`find`/`ls`/`git log`/file read answer this? → **run the command.**
2. What **artifact** does this agent return — a file, a diff, a report at a known path, a
   verdict with citations? No artifact means no dispatch; "investigate X and report back"
   has no completion condition and goes idle.
3. Is this discovery or execution? Discovery is yours. Execution and verification fan out.
4. Is the item bigger than an agent's overhead? If each item is a **single tool call**,
   run them inline however many there are. Independent ≠ worth an agent.

**Fan out over a work-list you already have, never to produce one.** Width belongs
downstream of the cheap grep that enumerates the items.

### Sizing the fan-out

Count follows the work, not a habit. **One agent per independent item** — 20 files to
sweep is 20 agents, not 3; 5 items get 5 agents, not 20. The size guideline is a
**ceiling, not a target**: derive the count from the scouted work-list, then check it
against the ceiling, never the reverse. Never batch items into one agent to keep the count
down — that drops coverage silently. Spend width where agents are cheap; keep
`xhigh`/`max` lanes narrow. If you bound coverage for cost, say what you dropped.

## Reaching the other family

`gpt-6-astra` is reachable only through the Codex CLI. Prefer the dedicated skills —
`codex-review` for an independent diff review, `codex-computer-use` for driving the
running app. For anything else, shell out to `ask-codex` (`--effort LEVEL` per lane,
`--readonly` for pure investigation, `--context FILE` for spec-driven work, `--output FILE`
to skip stdout parsing).

**Read `~/.codex/config.toml` rather than assuming its contents** — `model` and
`model_reasoning_effort` there are independent of the Claude session's effort, and they
drift between releases. A verify lane silently running at `low` is worse than no verify
lane, because it returns a confident pass.

Parallel *write* lanes need isolation: codex has no worktree isolation of its own, so two
codex write-lanes touching the same file collide. Serialize them, or wrap each in an
`Agent`/`Workflow` with `isolation: 'worktree'`.

## Browser automation & UI verification

Judge a browser tool by its real agent interface, not its weakest entry point.

- **Local, driven interactively:** `agent-browser` (`--session <name>` for isolation,
  `snapshot -i` → `@refs`, `screenshot <path>`). **This is the default local lane.**
- **Local, cheap unattended QA:** Codex via the `codex-computer-use` skill. Codex drives
  and screenshots; **Claude then reads the pixels and judges.** Codex confirms mechanics
  only.
- **Cloud / CI / a deployed URL:** a hosted browser service or Playwright. Cloud browsers
  can't reach `localhost`.

Chrome MCP is the **third** choice, after agent-browser and Playwright — it needs a
connected extension. **Never ask anyone to relaunch Chrome with
`--remote-debugging-port`**; that is a symptom of having skipped agent-browser.

**Resolve the dev URL, never assume it.** Most Next apps default to port 3000 and
therefore collide. Start the target app on an explicit free port (`npx next dev -p 3100`)
or identify the real listener with `lsof -nP -iTCP -sTCP:LISTEN | grep node`, and confirm
the page `<title>` matches the app you meant. **Verifying the wrong app is worse than not
verifying.**

**A login wall is a work item, not a blocking question.** Never stop and ask "how should I
handle auth?". Take the first of these that works and keep going:

1. **Named session** — cookies persist across runs, so a login done once keeps working.
2. **Saved auth profile** — check what already exists *first*, before concluding anything
   is missing.
3. **The app's own test-mode path.** On a Clerk *development* instance (`pk_test_`),
   `anything+clerk_test@example.com` with code `424242` signs in with no password and no
   email sent. The trap: Clerk's `<SignIn />` shows a **password** field first, and that
   screen is where agents give up — enter the email → Continue → **"Use another method"**
   → **"Email code to …"** → `424242`. Create test users via the Backend API, not the
   sign-up form (sign-up carries CAPTCHA; sign-in does not).
4. **Unauthenticated surfaces** — capture every public route, empty state and error state
   that doesn't need a session.
5. **Only then**, finish the entire rest of the task, ship it, and close with ONE line
   naming exactly which screens are unverified. Do not open a numbered menu; do not idle
   waiting for an answer.

SPA reliability: after a click on a client-routed link, assert the URL actually changed —
the click can report success without navigating. Use fixed waits, never `networkidle`.

## Recordings are video, not GIF

Any lane that drives a flow records it — scrubbable, full length, no frame-dropping.

- **Web:** `agent-browser --session <lane> record start <dir>/<flow>.webm [url]` *before*
  the flow (it opens a fresh context — start it first, not mid-page), drive, `record
  stop`. Needs a **system** `ffmpeg`. Then
  `ffmpeg -i <flow>.webm -c:v libx264 -pix_fmt yuv420p -crf 23 -movflags +faststart <flow>.mp4`.
- **iOS Simulator:** `xcrun simctl io booted recordVideo --codec h264 <path>.mp4`.
- **Android emulator:** `adb shell screenrecord` (3-min cap; chain files), then `adb pull`.
- **Native macOS app:** `screencapture -v <path>.mp4`.

When recording is genuinely infeasible, a captioned screenshot sequence is the fallback —
say so in the report. **Never present stills as if a recording existed.**

## Headless hosts

On a machine with no display — which is any VM — **never `open` or `xdg-open`**. Publish
the artifact to a served reports directory, or commit it on a pushed branch, and hand back
a **URL, not a disk path**. A disk path on a headless host is a failed handoff.

## Secrets

Never paste a live key into chat, a repo dotfile, or a memory file.

- **macOS:** the login Keychain. Export into the shell from your profile so every CLI
  picks it up: `export FOO_KEY="$(security find-generic-password -s foo-key -w 2>/dev/null)"`.
  Store or rotate interactively so it never enters shell history:
  `security add-generic-password -U -a "$USER" -s foo-key -w`.
- **Linux / VM:** there is no Keychain. Use a `0600` env file (`~/.secrets.env`) sourced
  from **both** `.bashrc` and `.profile`. Any skill that reaches for the Keychain needs an
  env-var-first fallback before it will run on a VM.

**Non-interactive login shells** (`ssh host "cmd"`, `bash -lc`, cron, and every agent
hook) skip `.bashrc` entirely. If Node and the keys load only there, all of those run with
no `npx` and no credentials, and fail in ways that look like broken tooling.
