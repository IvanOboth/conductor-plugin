#!/usr/bin/env bash
# orca-cli-fix.sh — make the registered `orca` / `orca-ide` CLI work on a userns-restricted Linux host.
#
# Upstream bug stablyai/orca#11609 (open since 30 Jul 2026): the AppImage's AppRun probes `unshare -Ur`,
# which fails under Ubuntu 24.04's kernel.apparmor_restrict_unprivileged_userns=1, so it appends
# --no-sandbox to EVERY launch — including the ELECTRON_RUN_AS_NODE one the CLI wrapper uses, and Node
# rejects it: "bad option: --no-sandbox". Fix = bypass AppRun for the CLI: extract the AppImage once
# (the headless guide's supported path) and run the CLI bundle straight from squashfs-root/orca-ide.
# `orca serve` (systemd) keeps using the AppImage; nothing about the server changes.
# Re-run after every AppImage update (Orca's "register CLI" may also rewrite the wrappers).
set -euo pipefail
APPIMAGE=/opt/orca/orca-linux.AppImage
ROOT=/opt/orca/squashfs-root
[ -f "$APPIMAGE" ] || { echo "no $APPIMAGE" >&2; exit 1; }

# 1. (Re)extract when missing or older than the AppImage.
if [ ! -x "$ROOT/orca-ide" ] || [ "$APPIMAGE" -nt "$ROOT/orca-ide" ]; then
  tmp=$(mktemp -d /opt/orca/.extract.XXXXXX 2>/dev/null || sudo mktemp -d /opt/orca/.extract.XXXXXX)
  ( cd "$tmp" && "$APPIMAGE" --appimage-extract >/dev/null )
  sudo rm -rf "$ROOT"; sudo mv "$tmp/squashfs-root" "$ROOT"; sudo rm -rf "$tmp"
  sudo chmod -R a+rX "$ROOT"
  echo "extracted → $ROOT"
fi

# 2. Patch the registered wrappers to run the CLI from the extracted tree (no AppRun, no --no-sandbox).
for w in "$HOME/.local/bin/orca" "$HOME/.local/bin/orca-ide"; do
  [ -f "$w" ] || continue
  grep -q "squashfs-root" "$w" && { echo "$w already patched"; continue; }
  python3 - "$w" "$ROOT" <<'PY'
import re, sys
p, root = sys.argv[1], sys.argv[2]
s = open(p).read()
old = 'ELECTRON_RUN_AS_NODE=1 exec "$APPIMAGE" -e '
new = ('# orca-cli-fix.sh: run the CLI from the extracted tree; AppRun would inject --no-sandbox (orca#11609).\n'
       'if [ -x "%s/orca-ide" ]; then APPDIR="%s" ELECTRON_RUN_AS_NODE=1 exec "%s/orca-ide" -e ' % (root, root, root))
assert old in s, "wrapper anchor not found in " + p
# keep the original AppImage line as the fallback branch
s = s.replace(old, new, 1)
open(p, 'w').write(s)
PY
  # append the fallback branch (original AppImage invocation) after the patched exec line
  python3 - "$w" <<'PY'
import sys
p = sys.argv[1]; lines = open(p).read().split('\n')
out = []
for i, l in enumerate(lines):
    out.append(l)
    if l.startswith('if [ -x ') and 'ELECTRON_RUN_AS_NODE=1 exec' in l:
        fallback = l.split('exec ', 1)[1]           # "<root>/orca-ide" -e '...' -- "$@"
        script = fallback.split(' -e ', 1)[1]
        out.append('fi')
        out.append('ELECTRON_RUN_AS_NODE=1 exec "$APPIMAGE" -e ' + script)
open(p, 'w').write('\n'.join(out))
PY
  bash -n "$w" && echo "patched $w"
done

# 3. Prove it.
"$HOME/.local/bin/orca" status --json | head -c 300; echo
