#!/usr/bin/env bash
#
# install.sh — plain-copy install for people who'd rather not use the plugin system.
#
# The plugin route is better and takes two commands:
#   /plugin marketplace add IvanOboth/conductor-plugin
#   /plugin install conductor@agent-ops
#
# Use this script instead if you want the files in your own ~/.claude tree.
# It copies the skills and agents into place, drops ask-codex on your PATH, and
# rewrites ${CLAUDE_PLUGIN_ROOT} — which only resolves inside a real plugin — to
# the absolute install path.
#
# Usage:  ./install.sh [--prefix DIR] [--bin DIR] [--dry-run] [--uninstall]

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFIX="${HOME}/.claude"
BINDIR="${HOME}/.local/bin"
DATADIR=""   # derived from PREFIX after arg parsing
DRY_RUN=false
UNINSTALL=false

SKILLS=(conductor codex-review codex-computer-use agent-browser run-report)
AGENTS=(design-lane bulk-lane verify-lane)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prefix)    PREFIX="$2"; shift 2 ;;
    --bin)       BINDIR="$2"; shift 2 ;;
    --dry-run)   DRY_RUN=true; shift ;;
    --uninstall) UNINSTALL=true; shift ;;
    -h|--help)
      sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
done

DATADIR="${PREFIX}/conductor"

run() {
  if $DRY_RUN; then echo "  [dry-run] $*"; else "$@"; fi
}

if $UNINSTALL; then
  echo "Removing conductor from ${PREFIX}…"
  for s in "${SKILLS[@]}"; do run rm -rf "${PREFIX}/skills/${s}"; done
  for a in "${AGENTS[@]}"; do run rm -f "${PREFIX}/agents/${a}.md"; done
  run rm -rf "${DATADIR}"
  run rm -f "${BINDIR}/ask-codex"
  echo "Done. (Your own ask-codex, if you had one, was overwritten on install — restore it from your dotfiles if needed.)"
  exit 0
fi

echo "Installing conductor"
echo "  from:    ${SRC}"
echo "  skills:  ${PREFIX}/skills/"
echo "  agents:  ${PREFIX}/agents/"
echo "  scripts: ${DATADIR}/"
echo "  bin:     ${BINDIR}/"
$DRY_RUN && echo "  (dry run — nothing will be written)"
echo

# Warn before clobbering anything that's already there.
CLOBBER=()
for s in "${SKILLS[@]}"; do [[ -e "${PREFIX}/skills/${s}" ]] && CLOBBER+=("skills/${s}"); done
for a in "${AGENTS[@]}"; do [[ -e "${PREFIX}/agents/${a}.md" ]] && CLOBBER+=("agents/${a}.md"); done
[[ -e "${BINDIR}/ask-codex" ]] && CLOBBER+=("$(basename "${BINDIR}")/ask-codex")

if [[ ${#CLOBBER[@]} -gt 0 ]] && ! $DRY_RUN; then
  echo "These already exist and will be OVERWRITTEN:"
  printf '  %s\n' "${CLOBBER[@]}"
  read -r -p "Continue? [y/N] " reply
  [[ "$reply" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 1; }
  echo
fi

run mkdir -p "${PREFIX}/skills" "${PREFIX}/agents" "${DATADIR}" "${BINDIR}"

for s in "${SKILLS[@]}"; do
  run rm -rf "${PREFIX}/skills/${s}"
  run cp -R "${SRC}/skills/${s}" "${PREFIX}/skills/${s}"
  echo "  skill    ${s}"
done

for a in "${AGENTS[@]}"; do
  run cp "${SRC}/agents/${a}.md" "${PREFIX}/agents/${a}.md"
  echo "  agent    ${a}"
done

run cp "${SRC}/scripts/conductor-report.py" "${DATADIR}/conductor-report.py"
run cp "${SRC}/bin/ask-codex" "${BINDIR}/ask-codex"
run chmod +x "${BINDIR}/ask-codex"
echo "  script   conductor-report.py"
echo "  bin      ask-codex"

# ${CLAUDE_PLUGIN_ROOT} only resolves inside a real plugin. Point the copies at
# the absolute paths we just installed to, or the telemetry step silently no-ops.
if ! $DRY_RUN; then
  for f in "${PREFIX}/skills/conductor/SKILL.md" "${PREFIX}/skills/run-report/SKILL.md"; do
    [[ -f "$f" ]] || continue
    perl -pi -e "s{\\\$\\{CLAUDE_PLUGIN_ROOT\\}/scripts}{${DATADIR}}g; \
                 s{\\\$\\{CLAUDE_PLUGIN_ROOT\\}/bin/ask-codex}{ask-codex}g" "$f"
  done
  echo "  rewrote  \${CLAUDE_PLUGIN_ROOT} -> ${DATADIR}"
fi

echo
if [[ ":${PATH}:" != *":${BINDIR}:"* ]]; then
  echo "⚠  ${BINDIR} is not on your PATH — ask-codex won't be callable."
  echo "   Add to your shell profile:  export PATH=\"${BINDIR}:\$PATH\""
  echo
fi

echo "Installed. Restart Claude Code, then try /conductor."
echo
echo "Prerequisites (each missing one disables that lane, nothing breaks):"
command -v codex          >/dev/null 2>&1 && echo "  ✓ codex"         || echo "  ✗ codex          — npm i -g @openai/codex && codex login   (codex lanes)"
command -v agent-browser  >/dev/null 2>&1 && echo "  ✓ agent-browser" || echo "  ✗ agent-browser  — npm i -g agent-browser                   (browser verification)"
command -v gh             >/dev/null 2>&1 && echo "  ✓ gh"            || echo "  ✗ gh             — optional, for run-report's GitHub steps"
command -v python3        >/dev/null 2>&1 && echo "  ✓ python3"       || echo "  ✗ python3        — optional, for the telemetry ledger"
