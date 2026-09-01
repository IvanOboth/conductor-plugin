# Agent setup runbook

**Give this file to your coding agent.** It is written for the agent, not for you.

> Follow the runbook at
> `https://raw.githubusercontent.com/IvanOboth/conductor-plugin/main/AGENT-SETUP.md`
> — set me up end to end. My VM is `<provider>`, hostname/IP `<x>`, user `<y>`.

You will still have to type passwords and click through three browser logins yourself.
Everything else the agent can do.

---

## Agent: read this part first

You are setting up a two-machine agent-development environment for the person you are
talking to. **You are running on their laptop.** The VM is remote; you reach it over SSH.

### What you are building

| Layer | Where | Holds |
|---|---|---|
| Glass | laptop + phone | nothing — no state, no execution |
| Runtime | their VM | every agent process, worktree, browser |
| Orchestration | both | the `conductor` plugin |

The organising rule: **nothing executes on the laptop.** When it is done, closing the
laptop stops nothing and the same sessions are reachable from a phone.

### Rules that override your defaults

1. **Never run `ufw delete allow OpenSSH` — or any command that closes SSH — until you
   have run `tailscale status` on the VM and seen the node online in the output.** Getting
   this wrong locks your user out of their own machine. Print the `tailscale status`
   output and ask them to confirm before you touch the firewall. This is the single
   highest-consequence step in the runbook.
2. **You cannot do the interactive logins.** `claude`, `codex login`, `gh auth login`
   and `tailscale up` all open a browser and need a human. When you reach one, stop,
   print the exact command, and wait. Do not try to script around them, do not attempt
   to paste tokens, do not look for a headless flag.
3. **Never put an API key into Orca's UI.** Orca stores secrets unencrypted on Linux —
   there is no OS keyring. Keys go in a `0600` env file.
4. **Verify each phase before starting the next.** Every phase below ends with a check
   and its expected output. A silent partial success here surfaces two weeks later as
   "the tooling is flaky". If a check fails, stop and fix it; do not proceed hoping.
5. **Ask before installing anything not in this runbook.**

### Report as you go

After each phase, tell them in one or two lines: what you ran, what the check returned,
and anything you skipped. At the very end produce the summary in the final section.

---

## Phase 0 — Gather, then gate

Ask for, and record:

- VM provider (DigitalOcean, Netcup, Hetzner, other), hostname or IP, SSH user
- Whether they already have Claude and ChatGPT subscriptions, and which tier
- Nothing about tailnets — they get their own (see 2e). Do not ask.

Then check the VM clears these. **If RAM is under 8 GB, stop and say so** — agents will
die mid-run and it will look like broken tooling, not an undersized box.

```bash
ssh <user>@<host> 'lsb_release -d; nproc; free -g | head -2; df -h / | tail -1'
```

| Requirement | Minimum | Note |
|---|---|---|
| OS | Ubuntu 24.04 LTS | Standardise. Several paths below differ on 22.04. |
| RAM | 8 GB, 16 preferred | Orca's headless server alone idles ~1.1 GB. |
| vCPU | 4+ | |
| Disk | 80 GB+ | Worktrees and `node_modules` are the hogs. |

**Gate:** do not continue until the box passes or they explicitly accept the risk.

---

## Phase 1 — Laptop baseline

Do not use a system or Homebrew Node. The agent CLIs are particular about this.

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
# the shell must be reopened before nvm is available
nvm install --lts && nvm alias default node
npm install -g @anthropic-ai/claude-code @openai/codex agent-browser
```

**Then stop.** These three are interactive — print them and wait for the human:

```bash
claude            # sign in with the Claude subscription
codex login       # sign in with the ChatGPT account
gh auth login     # GitHub
```

**Check:**

```bash
node -v && claude --version && codex --version && agent-browser --version && gh auth status
```

Expect a version from each and `Logged in to github.com` from the last.

**Also read `~/.codex/config.toml` and report `model` and `model_reasoning_effort` back
to them.** These are independent of the Claude session's effort and they drift between
releases. A verification lane silently running at `low` is worse than no verification
lane, because it returns a confident pass.

---

## Phase 2 — VM baseline

Everything here runs over SSH on the VM. It is provider-agnostic; Tailscale flattens the
networking differences between DigitalOcean, Netcup and Hetzner.

### 2a. Packages

```bash
sudo apt update && sudo apt install -y \
  ffmpeg git build-essential file libfuse2t64 xvfb curl
```

`ffmpeg` is not optional — `agent-browser record stop` needs a *system* ffmpeg.

### 2b. Node and the CLIs

Same stack as the laptop. Install as their normal user, **not** root.

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
# reopen the shell
nvm install --lts && nvm alias default node
npm install -g @anthropic-ai/claude-code @openai/codex agent-browser
```

**Stop again** for `claude`, `codex login`, `gh auth login` on the VM. These are separate
logins from the laptop's — the VM is a different machine.

### 2c. Non-interactive login shells — do not skip this

Non-interactive login shells (`ssh host "cmd"`, `bash -lc`, cron, and every agent hook)
skip `.bashrc` entirely. If Node and the keys load only there, all of those run with no
`npx` and no credentials, and fail in ways that look like broken skills.

Ensure `~/.profile` loads both nvm and the secrets file:

```bash
# ~/.profile
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
[ -f "$HOME/.secrets.env" ] && set -a && . "$HOME/.secrets.env" && set +a
```

Create the secrets file with the right permissions:

```bash
touch ~/.secrets.env && chmod 600 ~/.secrets.env
```

**Check — this must pass:**

```bash
ssh <user>@<host> 'which node npx claude codex'
```

All four must resolve. If they don't, `.profile` is not being read and every hook on this
box will fail later.

### 2d. Browser verification

Two independent failure modes here; both present as "the browser lane hangs forever".

```bash
agent-browser install --with-deps
```

Without this, agent-browser falls back to `which chromium-browser`, which on Ubuntu is
the **snap** — AppArmor-confined, no `xdg-settings`, hangs with `<defunct>` children.

Then the userns restriction. Ubuntu 24.04 ships
`kernel.apparmor_restrict_unprivileged_userns=1`, which kills Chrome's sandbox with
`FATAL: No usable sandbox!` for a non-root user on a bare VM.

**Do not "fix" this with `--no-sandbox` and do not flip the sysctl.** Both drop a real
security boundary. Use Chromium's documented option 2 — a named AppArmor profile granting
`userns` to the agent Chrome binaries only:

```bash
sudo tee /etc/apparmor.d/agent-chrome >/dev/null <<'PROFILE'
abi <abi/4.0>,
include <tunables/global>

profile agent-chrome
  /home/*/.agent-browser/browsers/**/chrome flags=(unconfined) {
  userns,
}

profile playwright-chrome
  /home/*/.cache/ms-playwright/**/chrome{,-linux/chrome} flags=(unconfined) {
  userns,
}
PROFILE
sudo apparmor_parser -r /etc/apparmor.d/agent-chrome
```

**Check:**

```bash
agent-browser --session smoke open https://example.com
agent-browser --session smoke screenshot /tmp/smoke.png
ls -l /tmp/smoke.png
```

A non-zero PNG means both failure modes are cleared. If it hangs, kill it with
`kill $(pgrep -f 'bin/agent-browser-linu[x]')` — note that a plain `pkill -f agent-browser`
matches its own command line and kills the calling shell too.

### 2e. Tailscale — VM, laptop AND phone

Tailscale is a private network, and a network with one member does nothing. It goes on
all three. After this the VM is reachable by a stable name from anywhere, with no public
port open.

Each person runs their **own** tailnet — their VM, their laptop, their phone, nobody
else's. There is no shared account and no org to join, so do not ask them which tailnet
to use. They sign in with their own Tailscale account and approve their own machines.

On the VM:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up      # prints a URL — the human approves it in a browser
```

**Stop.** Wait for them to approve. Then:

```bash
tailscale status
```

**Print that output and ask them to confirm the node is online before you go further.**

Only now, and only after that confirmation:

```bash
sudo ufw allow in on tailscale0
sudo ufw delete allow OpenSSH
sudo ufw enable
```

Tell them to keep their provider's web console open in a tab while you do this —
DigitalOcean has a Recovery Console and Netcup a VNC console, so a lockout is
recoverable, but it is a twenty-minute detour.

Then remind them to install the Tailscale app on their **laptop** and **phone**, signed
into the same tailnet. Without the phone's VPN toggle on, no tailnet URL will resolve
from it — this is the most common "it's broken" report and it is almost always this.

**Check:** from the laptop, `ssh <user>@<tailnet-hostname>` connects.

---

## Phase 3 — Orca

Orca is a client on the laptop and phone, and a headless server on the VM. The desktop
app is a **client only** — it never becomes the runtime.

Direct them to install Orca desktop on the laptop and Orca mobile on the phone. Then on
the VM, install the AppImage to `/opt/orca`, and run it as a **systemd user service** with
linger enabled so it survives logout and reboot:

```bash
sudo loginctl enable-linger "$USER"
systemctl --user enable --now orca-serve
systemctl --user status orca-serve
```

Pairing links:

```bash
grep 'Pairing URL' ~/runs/orca-serve.log   # desktop
orca serve --mobile-pairing                # phone — a separate, mobile-scoped link
```

On the desktop client: **Settings → Remote Orca Servers → Add**, then under Advanced set
**Active Server** to their VM. Tell them explicitly that if they skip that last step,
everything silently routes through the laptop and they have rebuilt the problem this
setup exists to escape.

### Four Orca traps — handle these proactively

**The CLI is broken on Linux out of the box.** Every `orca` command fails with
`bad option: --no-sandbox`. The AppImage's `AppRun` probes `unshare -Ur`, which fails
under the same userns restriction from 2d, so it appends `--no-sandbox` to *every* launch
including the Node CLI path, and Node rejects the flag. Upstream `stablyai/orca#11609`.
Fix by extracting the AppImage once to `/opt/orca/squashfs-root` and patching both
wrappers to run the CLI bundle from there. **Re-run that fix after every Orca update** and
after Orca's "register CLI" rewrites the wrappers.

**It rewrites hooks.** `orca serve` injects its hook into every Claude Code event in
`~/.claude/settings.json` and into `~/.codex/hooks.json`, and grants itself Codex trust.
**Back up `~/.claude/settings.json` before the first `orca serve`** and diff it after
every upgrade.

**Secrets are unencrypted.** Covered above — never enter a key through the UI.

**"Add Account" is disabled for remote servers**, by design: interactive login needs a
desktop browser and would authenticate against the wrong device. A second Claude or Codex
account on the VM is a manual filesystem procedure. If they ask for one, say so rather
than letting them hunt for a button that isn't there.

**Check:** `orca status --json` returns ready, and the desktop client lists the VM as
Active Server.

---

## Phase 4 — Conductor

On **both** the laptop and the VM, in Claude Code:

```
/plugin marketplace add IvanOboth/conductor-plugin
/plugin install conductor@agent-ops
```

**Check that all four prerequisites resolve**, on both machines:

```bash
command -v codex && command -v agent-browser && command -v gh && command -v python3
```

This check matters more than it looks. Conductor degrades **silently**: no Codex CLI and
cross-family verification quietly becomes Claude reviewing Claude; no Opus access and the
design lane falls back to the session model. Nothing errors — they just stop getting the
thing they installed. Say this to them in as many words.

---

## Phase 5 — Config files

Write these two. They are what decide whether conductor gets used well or cargo-culted.

- `~/.claude/CLAUDE.md` — the Claude-side brain: model routing, lane assignments, the
  gates on what earns an agent, fan-out sizing, browser lane order, headless-host
  handling.
- `~/.codex/AGENTS.md` — the Codex-side mirror. Needed because when a codex lane runs,
  *it* is making the decisions and it cannot see the Claude-side file.

**If the person who sent you here supplied their own versions of these two files, use
theirs verbatim — do not merge, do not improve, do not reorder.** They are a team
standard, and drift between copies is the failure this file exists to prevent.

If they did not, ask for them before writing anything. Do not invent a routing table.

One thing to flag if you do write them: leave the *gates* alone — "what earns an agent",
the fan-out sizing rules, and the counter-instructions for reflexive delegation. Those
are the parts that keep the bill predictable, and they are the parts a new user is most
tempted to delete because they read as restrictive.

---

## Phase 6 — Acceptance run

Do not report success until this passes. A checklist of installed things proves nothing —
every failure mode above is silent.

Have them pick a small, real, already-scoped issue in a repo they know. Not a toy. Run
`/conductor` on it from the VM. Then verify all six:

- [ ] **It scouted before dispatching** — grep and file reads in the main loop, not an
      agent sent to "investigate and report back"
- [ ] **Lane count matches the work** — one per independent item, not three out of habit
- [ ] **A codex lane actually ran** — check the transcript. If the whole run was Claude,
      cross-family verification did not happen and the run is worth less than it looks.
- [ ] **A video exists** — any lane that drove a flow produced a `.webm`/`.mp4`, not a
      screenshot with a claim attached
- [ ] **An HTML review was handed over as a URL** — on a headless VM a disk path is a
      failed handoff
- [ ] **The work was committed and pushed** — otherwise it exists on one VM and nowhere
      else

---

## Final report

Close with:

**Done** — phases completed, one line each.

**Verification** — the actual output of each phase's check. Not a claim that it passed;
paste what the command returned.

**Skipped or deferred** — anything you could not complete, and why.

**Needs them** — any interactive step still outstanding, as an exact command to run.

**Flagged** — anything you noticed that is not broken but will bite later: the codex
effort setting, an undersized box they accepted, a missing subscription tier.

"Not verified" is a valid and useful entry. A confident false pass is the most expensive
thing you can return.
