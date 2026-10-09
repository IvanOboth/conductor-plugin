---
name: how
description: Explain how a subsystem, feature or runtime flow works in this codebase, at the level of a senior engineer onboarding onto it — overview, key concepts, the flow step by step with file references, where things live, gotchas — and optionally critique the architecture with independent reviewers from different model families. Use for "how does X work", "walk me through what happens when", "where should this live", "which module owns this", before changing an unfamiliar area, or to give a lane the mental model it needs before a work order. Plain-text answer for agents and engineers; use understand for Ivan's interactive HTML explainer with a quiz.
---

# How

Explore the code to answer a "how does X work?" question and produce an explanation a senior
engineer could build a working mental model from: enough to start changing the area with
confidence, not so much that it reads like annotated source.

Ported from poteto's `how` (github.com/poteto/how, MIT, Copyright (c) 2026 Lauren Tan; licence in
`references/LICENSE-how.txt`). The prompt templates in `references/` are unchanged; the routing
follows Conductor.

Two modes:

1. **Explain** (default): explore, then explain.
2. **Critique**: explain first, then independent critics look for architectural problems.

## Explain

### Step 1. Scope and size

Say what you take the question to cover in one sentence and start; the asker can redirect. Then:

- **Simple** (one module, one function, a narrow question): no explorers. Explore and explain in
  one pass yourself, or with one Opus 5.5 lane at `high`. Go to Step 4.
- **Complex** (a subsystem across many files or services, a cross-cutting flow, an architectural
  overview): explorers first. When in doubt, take the simple path; add explorers if you hit a wall.

### Step 2. Explore (complex only)

Split the question into 2 to 4 angles that do not overlap much, for example data model and state;
rendering or API surface; background jobs and side effects. Launch the explorers in one turn, each
with `references/explorer-prompt.md` filled in (`{QUESTION}`, `{EXPLORATION_ANGLE}`):

- GPT-6.1 Sol at `high`: `ask-codex -m gpt-6.1-sol --effort high --context <filled-prompt>.md --output <scratch>/explorer-N.md "Follow the prompt; your final message is the findings." </dev/null`
  run in the background. Investigation that does not change code is its lane.
- When Codex quota is out, Opus 5.5 at `medium` (`exec-lane`) with the same prompt and an
  instruction not to edit files.

Each returns components, flow, files read, boundaries, non-obvious things and open questions.

### Step 3. Synthesize (complex only)

One Opus 5.5 lane at `high` (or you, if the findings fit comfortably in your context) gets
`references/explainer-prompt.md` with all the explorers' findings and writes the explanation. It may
read code to resolve a contradiction; it does not re-explore.

### Step 4. Present

Give the explanation with light edits. The structure, adapted to the question:

- **Overview**: one or two paragraphs: what it is, what it does, why it exists.
- **Key concepts**: the types, services and abstractions needed to follow the rest.
- **How it works**: the flow, trigger to effect, with files and functions named. Prose, not
  pseudocode. A mermaid or ASCII diagram when several components talk to each other.
- **Where things live**: the files someone needs to start working here.
- **Gotchas**: what surprises people, historical reasons, sharp edges.

### Step 5. Keep what lasts

An explanation is lost when the session ends unless the durable parts go where the next agent will
read them. Before you finish, move anything that would have saved this exploration:

- a trap that breaks verification or a user path: the matching feature file's `Gotchas` in the
  project's verification skill (`.claude/skills/verify-*/features/`), via `feature-map-update`;
- a rule every change in the area must follow: the project's `AGENTS.md`, in one line;
- a rule that a script could enforce: say so, and propose the lint or check instead of the line.

Only promote what you confirmed in the code. Do not copy the whole explanation into the repo.

## Critique

Run when the asker wants problems or improvements, not only understanding.

1. Run Explain first.
2. Launch three critics in one turn, each with `references/critic-prompt.md` filled in (the
   explanation, the relevant file paths, `references/critique-rubric.md`), read-only:

   | Critic | Model |
   |---|---|
   | A | Opus 5.5 at `high` |
   | B | GPT-6.1 Sol at `high` (`ask-codex`) |
   | C | Fable 5.1 at `high` (`verify-lane`) |

   Three models from two families means agreement carries signal and blind spots differ.
3. Judge as a pragmatic lead, not an aggregator. Sort findings into **Act on** (worth fixing now),
   **Consider** (real, unclear cost/benefit), **Noted** (valid, low priority) and **Dismissed**
   (wrong, missing context, or taste). Check every Act-on finding in the code yourself.

Present the explanation first and the critique verdict after it, so someone who only wants to
understand the system does not have to read the critique.
