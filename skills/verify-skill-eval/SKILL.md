---
name: verify-skill-eval
description: Measure whether a change to agent guidance (a verification skill, a feature map, an AGENTS.md section, a rewritten skill) makes agents better at real tasks — paired headless Claude trials in two checkouts, same organic prompts, neutral labels, metrics from the transcripts (time, turns, tool calls, cost, whether the guidance was actually read), and a blind judgement of each result against its acceptance check. Use for "does the map help", "test agents with and without", "A/B this skill", or before promoting a guidance change across projects.
disable-model-invocation: true
---

# Evaluate a guidance change

A skill or map that reads well can still leave agents no faster or no more correct. This skill
answers the question with trials, not opinion: the same real tasks, run by the same model and
effort, once in a checkout without the change (arm `a`) and once with it (arm `b`).

Built on poteto's eval playbook (pstack): candidates never see that they are being tested, results
are judged blind, and the chain is read from transcripts rather than from what the agent says it
did.

## 1. Frame

Write down, for yourself only:

- the variant under test, as a git diff between the two checkouts;
- 3 to 6 tasks that the guidance is meant to help, drawn from real work (verify a merged fix,
  record a flow for a demo, find a screen as a given persona, reproduce a reported bug);
- for each task an acceptance check a judge can apply to the output: the screenshot shows X, the
  answer names value Y, the recording is longer than N frames and shows Z;
- what you will compare: success first, then time, turns, tool calls and cost.

Prefer read-only tasks on shared environments. A task that must write needs a scratch tenant or a
reset fixture, or it will leave rows behind twice per rep.

## 2. Set up the arms

Two checkouts of the same base, one with the change and one without, with project-shaped names
(not `eval`, `test`, `baseline`, `with-map`). `git worktree add` both from the base; apply the
change to one. Nothing else differs: same user settings, same global skills, same target.

## 3. Write organic prompts

What a person would type. Name the goal and the target environment; never mention the guidance,
the comparison, skills, files to read or how you will judge. Ask for the deliverable you will
check ("send me the screenshot path and the balance shown"). The same prompt goes to both arms.

## 4. Run

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/verify-skill-eval/scripts/run_trials.py" run plan.json
```

`plan.json` (format in the script's docstring) names the arms, the tasks, reps (2 or more; one run
per arm is an anecdote), the model and effort (Opus 5.5 at `medium` matches a build or verify
lane), concurrency (4 browser-driving trials at once on the bench), a timeout, and `probe` strings
that show the guidance was used (the helper's name, `features/`), and `deny`: permission rules every
trial runs under. Trials run unattended with permissions bypassed, and the arm without the guidance
follows whatever setup the repo documents, so deny anything that writes to shared state: backend
pushes and watchers (`Bash(npx convex:*)`, `Bash(pnpm convex:*)`, `Bash(pnpm dev:*)`), deploys,
`git push`. Run it in the background with stdin closed; it resumes, skipping finished trials. Each trial gets a neutral label and its own
`VERIFY_RUN_ID`.

## 5. Judge blind

First read each unfinished trial's `<label>.err` and stream tail: a trial killed by a usage limit or
a timeout is a lost trial, not a failure of its arm; re-run it. Then, for each trial, read its final
message and the evidence it names, against the task's acceptance
check, without looking at its arm (`summary.md` lists labels; hide the arm column while judging).
Record pass, partial or fail with one line of reason. For a second opinion, give a judge from the
other model family (GPT-6.1 Sol at `high`) the labels, the outputs and the checks, never the arms.
Disagreement between you and the judge means the check is ambiguous: tighten it and re-judge.

## 6. Read the chain

From each stream (`<label>.jsonl`): did the `b` agent open the guidance (`probe` hits, the files it
read)? Did an `a` agent find the same knowledge some other way, and at what cost? A `b` run that
ignored the guidance is a discoverability problem (description, trigger words, AGENTS.md pointer),
not proof the guidance is useless.

## 7. Report

Variant, tasks and checks, the per-trial table, success per arm, median time, turns and tool calls
per arm, total cost, what the transcripts show about how the guidance was used, and a
recommendation: promote, revise (and what), or drop. On the bench, publish it as a report page.
Say plainly how many trials stand behind each number.
