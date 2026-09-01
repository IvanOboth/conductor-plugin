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

Direct them to install Orca desktop on the laptop and Orca mobile on the phone. Both are
**clients**. The runtime is the VM.

### 3a. Install the AppImage

**Ask them for the Linux AppImage download URL** from Orca's releases page — do not guess
it, and do not install from a URL you inferred. Then:

```bash
sudo mkdir -p /opt/orca
sudo curl -fL -o /opt/orca/orca-linux.AppImage '<URL they gave you>'
sudo chmod +x /opt/orca/orca-linux.AppImage
mkdir -p ~/runs
```

`libfuse2t64`, `file` and `xvfb` came from Phase 2a — the AppImage needs all three.

**Back up the Claude settings file before you ever start the server** (see the traps
below — `orca serve` rewrites it):

```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak-$(date +%Y%m%d)
```

### 3b. The systemd user service

`orca serve` must run as a **user** service with lingering enabled, so it survives logout
and reboot. **The unit does not exist — you have to write it.** Do not run
`systemctl --user enable orca-serve` before this step; it will simply fail.

Derive the values, don't hardcode them — the tailnet IP is what Orca advertises to
clients, and the PATH must contain the nvm node bin directory or the server starts without
node on its PATH:

```bash
TSIP=$(tailscale ip -4 | head -1)
NODEBIN=$(dirname "$(readlink -f "$(command -v node)")")
mkdir -p ~/.config/systemd/user/orca-serve.service.d

cat > ~/.config/systemd/user/orca-serve.service <<EOF
[Unit]
Description=Orca headless server (runtime for laptop + phone clients)
After=network-online.target tailscaled.service

[Service]
Environment=LIBGL_ALWAYS_SOFTWARE=1
Environment=PATH=${NODEBIN}:%h/.local/bin:/usr/local/bin:/usr/bin:/bin
WorkingDirectory=%h/dev
ExecStart=/opt/orca/orca-linux.AppImage serve --port 6768 --pairing-address ${TSIP}
Restart=on-failure
RestartSec=5
StandardOutput=append:%h/runs/orca-serve.log
StandardError=append:%h/runs/orca-serve.log

[Install]
WantedBy=default.target
EOF
```

Add the secrets drop-in. Orca runs hooks and automations **without a login shell**, so
they never see `~/.bashrc` — without this they run with no API keys:

```bash
cat > ~/.config/systemd/user/orca-serve.service.d/secrets.conf <<'EOF'
[Service]
EnvironmentFile=-%h/.secrets.env
EOF
```

Note that a running server only picks up `~/.secrets.env` **at start** — after editing
that file later, restart the service or the new keys are invisible to it.

Start it:

```bash
sudo loginctl enable-linger "$USER"
systemctl --user daemon-reload
systemctl --user enable --now orca-serve
systemctl --user status orca-serve --no-pager
```

**Check:** status shows `active (running)`, and `ss -ltnp | grep 6768` shows it listening.
Because `ufw` was restricted to `tailscale0` in Phase 2e, that port is private by
construction — but verify rather than assume, and tell them you verified it.

### 3c. Fix the CLI — required, not optional

Every registered `orca` / `orca-ide` command fails on Linux with
`bad option: --no-sandbox`. The AppImage's `AppRun` probes `unshare -Ur`, which fails
under the same userns restriction from Phase 2d, so it appends `--no-sandbox` to *every*
launch including the `ELECTRON_RUN_AS_NODE` path the CLI uses — and Node rejects the flag.
Upstream `stablyai/orca#11609`.

```bash
curl -fL -o /tmp/orca-cli-fix.sh \
  https://raw.githubusercontent.com/IvanOboth/conductor-plugin/main/scripts/orca-cli-fix.sh
bash /tmp/orca-cli-fix.sh
```

It extracts the AppImage once to `/opt/orca/squashfs-root` (the supported headless path)
and patches both wrappers to run the CLI bundle from there, keeping the AppImage as a
fallback. `orca serve` itself is untouched.

**Tell them, explicitly, that this must be re-run after every Orca update** and after
Orca's "register CLI" rewrites the wrappers. It is the single most likely thing to break
later and look inexplicable.

**Check:** `orca status --json` returns ready.

### 3d. Pairing

```bash
grep 'Pairing URL' ~/runs/orca-serve.log   # desktop client
orca serve --mobile-pairing                # phone — a separate, mobile-scoped link
```

The mobile flag prints a mobile-scoped link *instead of* the desktop one, so capture the
desktop URL first.

On the desktop client: **Settings → Remote Orca Servers → Add**, then under Advanced set
**Active Server** to their VM. Say this to them in as many words: **if they skip the
Active Server step, everything silently routes through the laptop** and they have rebuilt
the exact problem this setup exists to escape.

### Tell them these five things before you finish the phase

These are not steps — they are things that will bite weeks from now and be baffling
without the context. Say them out loud, don't just do them.

1. **The CLI fix (3c) must be re-run after every Orca update**, and after Orca's
   "register CLI" rewrites the wrappers. This is the most likely future breakage.
2. **`orca serve` rewrites hook config.** It injects its hook into every Claude Code
   event in `~/.claude/settings.json` and into `~/.codex/hooks.json`, and grants itself
   Codex trust. You backed the file up in 3a — tell them to diff it after every upgrade.
3. **Secrets are stored unencrypted** — no OS keyring on Linux. Never enter an API key
   through Orca's UI; it goes in `~/.secrets.env` at `0600`.
4. **"Add Account" is disabled for remote servers**, by design: interactive login needs a
   desktop browser and would authenticate against the wrong device. Adding a second
   Claude or Codex account to the VM is a manual filesystem procedure, not a UI action.
   If they ask, say so rather than letting them hunt for a button that isn't there.
5. **Orca cuts a git worktree per workspace, and there is no setting to stop it.** The
   rule that keeps this sane: *a worktree is a PR in flight; when the PR merges, the
   worktree goes.* Without stating it, boxes accumulate stale worktrees with orphaned
   branches and occasionally unpushed work.

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

Write these two. They decide whether conductor gets used well or cargo-culted.

```bash
curl -fL -o ~/.claude/CLAUDE.md \
  https://raw.githubusercontent.com/IvanOboth/conductor-plugin/main/team-config/CLAUDE.md
mkdir -p ~/.codex && curl -fL -o ~/.codex/AGENTS.md \
  https://raw.githubusercontent.com/IvanOboth/conductor-plugin/main/team-config/AGENTS.md
```

**On both machines — the laptop and the VM.** A codex lane makes its own decisions while
it runs and cannot see the Claude-side file, so skipping `AGENTS.md` leaves half the
orchestration unguided.

**If a `~/.claude/CLAUDE.md` already exists, do NOT overwrite it.** Show them the diff and
merge — their existing project conventions matter. What they need from the team file is
the routing table and the gates.

If the person who sent them here supplied their own versions of these two files, use
**theirs** verbatim instead — do not merge, do not improve, do not reorder. They are a
team standard, and drift between copies is the failure this file exists to prevent.

Tell them what to tune and what not to: the **lane assignments** and the **cost** column
should reflect what they actually pay and work on. The **gates** — "what earns an agent",
the fan-out sizing rules, the Opus counter-behaviours — should be left alone. Those read
as restrictive and are the reason a fan-out costs what they expect.

**Check:** both files exist and are non-empty.

```bash
wc -l ~/.claude/CLAUDE.md ~/.codex/AGENTS.md
```

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
