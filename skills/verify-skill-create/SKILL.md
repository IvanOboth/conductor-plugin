---
name: verify-skill-create
description: Generate a project-local verification skill (`.claude/skills/verify-<app>/`) that lets any agent drive the real app the way a user does — a small helper CLI (target or launch, doctor, sign-in as a test persona, shot, record, stop) plus a feature map that says where every user-facing feature lives, which persona reaches it, how to drive it and what proves it worked. Use for /verify-skill-create, "make a verification skill for <repo>", "give agents a map of the app", "agents keep getting lost verifying <app>", or when enrolling a project in the bench pipeline. Keep it current with verify-skill-maintain and feature-map-update.
---

# Create a verification skill

An agent that has to verify a change, record a demo or reproduce a bug spends most of its run
working out how to start the app, how to sign in, which persona sees the screen and what the
buttons are called. A verification skill answers those once, in the repository, for every agent and
every developer on the project. It has two parts:

- **The lever: a helper CLI.** One script that targets or launches the app, checks it is the
  instance you mean (`doctor`), signs in as a named test persona, captures evidence and cleans up.
  Agents run commands instead of writing throwaway scripts, so runs are shorter and repeatable.
- **The feature map.** A `features/` directory: a README index plus one file per user-facing
  feature, written from the user's point of view: entry points, the persona for each, exact driving
  commands, the observable proof, and the traps. It is a compact form of the codebase that saves the
  next agent from rediscovering it.

The idea and the feature-map shape come from poteto's pstack (`create-verification-skill`,
`maintain-verification-skill`, MIT; "The Complete Guide to pstack, Part 1: Verification is all you
need"). This version is fitted to our stack: agent-browser, Clerk test identities, shared Convex
deployments, the bench's resource rules and Conductor's evidence contract. Working examples:
`verify-mikono` in IvanOboth/mikono and `verify-animatix` in animatix-lab (written by the Animatix
team on the same pattern).

You write for the next agent, not for a human. It will read the skill cold, mid-task, with no idea
how the app works.

## 1. Interview the repository, not the user

Answer these from the code, `AGENTS.md`/`CLAUDE.md`, existing browser skills, the bench files
(`~/bin/merge-authority.json`, `domains/career-craft/bench/verify-order.<repo>.md`) and a live
probe. Ask the user only what you cannot observe.

- **Surface.** What does a user touch: web app, Mikono-Go-style web sub-app, native app, CLI, API?
  Pick the primary surface; name the others and the skill that covers them (`mobile-app-testing`
  for native).
- **Targets.** Which instances can be driven? Usually two: a deployed test track (the base
  branch's stable Vercel alias, with its backend URL and any protection bypass) and a local launch
  of the checkout. Name the production host so the helper can refuse it.
- **Backend.** Is the backend shared across checkouts (a Convex dev deployment every session
  pushes to)? What data is on it (real customers, client demo organisations)? This decides the
  write policy.
- **Identity.** Which test accounts exist and what does each see? Clerk dev instances accept
  `<name>+clerk_test@example.com` with code `424242`. Find seeded personas with
  `grep -rhoE '[a-z0-9.]+\+clerk_test@example\.com' <backend> <scripts> | sort -u`, then sign in as
  each and note where it lands. Persona and permission gating is the most common reason an
  agent "cannot find" a feature.
- **Drive.** agent-browser 0.37+ with a named `--session` per run. Prefer semantic locators
  (`find role|label|text`) over refs. Never `--load networkidle` against a Convex app.
- **Observe.** URL, accessibility snapshot, screenshot, MP4 (`record start` keeps the page and
  login on 0.37), plus any read-only backend query for cross-checks.
- **Isolate.** Can two runs share a checkout? Key the browser session and evidence directory on
  `$VERIFY_RUN_ID`. Can two dev servers share a checkout? (Next 16: no.) Say so in the skill.

Walk the sign-in flow by hand once with agent-browser before writing the helper. Write down every
screen, label and redirect you see; the helper encodes exactly that.

## 2. Write the helper

`.claude/skills/verify-<app>/verify-<app>.sh`, executable, usage printed with no arguments.
[`references/helper-contract.md`](references/helper-contract.md) lists the commands, their
behaviour and the bench rules it must follow; `verify-mikono.sh` is a complete example. Minimum:

| Command | Does |
|---|---|
| `target [url]` | record a deployed instance (default: the test-track alias); refuse production |
| `launch [port]` | start this checkout's app on a free port in its own process session |
| `doctor` | read-only: reachable, right title, right backend, right build, listener is ours |
| `sign-in [persona] [as]` | sign the run's browser session in as a named persona |
| `whoami` / `open <path>` | where am I, as whom; open a route and wait for it, fail fast on access denied |
| `shot <name>` | URL + accessibility snapshot + screenshot into `evidence/` |
| `record start <name>` / `record stop` | MP4 of the current page; print codec, frames, duration |
| `features [query]` | list the map, or the feature files matching a word |
| `stop` | close the browser session, kill only what `launch` started, keep evidence |

Test every command against the real app before you write the SKILL.md around it.

## 3. Write the SKILL.md

Front matter `name: verify-<app>` and a description that names the app, the surface, the personas
and the triggers (verify, QA, screenshot, record, "where is", demo click paths). Without front
matter the skill never registers. Then these sections, each from what you found (no placeholders):

- **Find the feature first:** point at `features/README.md` and `$H features <word>`.
- **Launch:** both targets, when to use which, readiness, and what launch does not do (backend
  pushes on a shared deployment).
- **Doctor:** what `OK` means; run it first and after anything surprising.
- **Sign in:** the persona keys, the chooser if there is one, how to switch user.
- **Drive:** locator rules, URL assertions, waits, viewport, the write policy for shared data.
- **Evidence:** where it goes and the proof standards: drive the real user path, capture the action
  and the resulting state, prove writes from a second view, read the PNG yourself, record video
  only when an application change needs demonstrating (Conductor's evidence gate), publish a URL
  rather than a disk path on a headless host.
- **Cleanup:** never kill by process name; evidence survives.
- **Keep the map true:** the checker command (step 5) and the same-PR rule.
- **Helpers:** every script and its invocation.

## 4. Build the feature map

`features/README.md` is the index: baseline preconditions, the persona table, driving conventions,
proof and skip reporting, the entry contract, how the map is kept true, and one line per feature
file. [`references/feature-template.md`](references/feature-template.md) is the file shape.

Each feature file has front matter (`id`, `sources`), an H1, one paragraph, and exactly four H2s:
`Sub-features`, `How to get to it (user POV)`, `Driving it with verify-<app>`, `Gotchas`.
`sources` holds the globs for the routes and code behind the feature. It is the one addition to
poteto's format: it lets a script tell a pull request which feature files its diff touches, so
upkeep is a check rather than a memory exercise. The body stays user-facing.

Enumerate the work-list yourself: list the route files (`git ls-files '<app>/**/page.tsx'` or the
router's equivalent), group them into features (one per module or flow a user would name), and
assign every route to exactly one feature. Then write `features/map.json` (route globs, ignores,
harness name) and copy the checker into the skill:

```bash
cp "${CLAUDE_PLUGIN_ROOT}/skills/verify-skill-create/scripts/feature_map_check.py" .claude/skills/verify-<app>/scripts/
```

Fan out one lane per feature (Opus 5.5 `medium`; at most 6 concurrent browser lanes on the bench),
each with its route list, the entry contract, a read-only rule for shared data, its own
`VERIFY_RUN_ID`, and the instruction to read the source and then drive every entry point live
before writing. A small app can start with the top five features; a product used by clients should
be mapped whole, because the map is only trusted when it is complete.

## 5. Prove it before handing it over

- `python3 .claude/skills/verify-<app>/scripts/feature_map_check.py .claude/skills/verify-<app>/features`
  exits 0 (warnings are acceptable only for routes you deliberately left out, listed in `route_ignore`).
- Run the skill's own instructions end to end once: target or launch, doctor, sign in, drive one
  mapped feature, capture evidence, stop. Confirm the evidence still exists after stop.
- Read every feature file the lanes wrote. Reject a file that guesses: a recipe step must say
  whether it was driven or read from source.
- Run `verify-skill-eval` on two or three real tasks if the project has a baseline worth comparing.

## 6. Wire it in

- `AGENTS.md`: the browser-verification section points at the skill; older browser skills become
  a short pointer to it, so two skills do not give conflicting instructions.
- The bench: the repo's `verify-order.<repo>.md` tells verify lanes to read the map; the
  bench-intake enrollment checklist names the skill.
- The upkeep loop: `feature-map-update` in every PR that changes a user path, and a scheduled
  `verify-skill-maintain` pass.
