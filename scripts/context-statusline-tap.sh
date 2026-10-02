#!/bin/bash
# context-statusline-tap.sh — record the real context window size for context-watch.
#
# Hooks are not told the window size; the statusline is. Pipe the statusline's
# stdin JSON here from your statusline command:
#   echo "$input" | ~/dev/conductor-plugin/scripts/context-statusline-tap.sh
# It writes <state>/conductor/context/<session_id>.window only when the value
# changes, so a 5-second refresh costs one jq call and no write.
read -r sid size < <(jq -r '[.session_id // "", (.context_window.context_window_size // 0 | tostring)] | @tsv' 2>/dev/null)
[ -n "$sid" ] && [ "${size:-0}" -gt 0 ] 2>/dev/null || exit 0
dir="${XDG_STATE_HOME:-$HOME/.local/state}/conductor/context"
file="$dir/$sid.window"
[ -f "$file" ] && [ "$(cat "$file")" = "$size" ] && exit 0
mkdir -p "$dir" && printf '%s\n' "$size" > "$file.tmp" && mv "$file.tmp" "$file"
exit 0
