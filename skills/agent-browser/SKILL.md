---
name: agent-browser
description: >-
  Browser automation CLI for AI agents. Use when the user needs to interact with websites,
  navigate pages, fill forms, click buttons, take screenshots, extract data, test web apps,
  or automate any browser task. Also trigger when the user says "test this login page",
  "verify the signup form", "check if the dashboard loads", "scrape this page", or any task
  that requires a rendered web page — even if they don't explicitly say "browser". The tool
  manages a persistent background daemon, so commands can be chained without re-launching.
  Do NOT trigger for API-only tasks (curl, fetch) that don't need a rendered page, or when
  the user is already collaborating in their own browser via Chrome MCP.
allowed-tools: Bash(agent-browser:*)
---

# Browser Automation with agent-browser

## When to Use This Tool

**Use agent-browser when** the task requires a rendered web page — filling forms, clicking buttons, reading DOM content, taking screenshots, testing UI flows, scraping rendered content, or verifying that a page works.

**Don't use agent-browser when:**
- The task is API-only (use `curl` or `fetch` instead — no rendering needed)
- The user is actively collaborating in their own browser and Chrome MCP tools are available
- You just need to download a file from a URL (use `curl -O` instead)

## Core Workflow

Every browser automation follows this pattern:

1. **Navigate**: `agent-browser open <url>`
2. **Snapshot**: `agent-browser snapshot -i` (get element refs like `@e1`, `@e2`)
3. **Interact**: Use refs to click, fill, select
4. **Re-snapshot**: After navigation or DOM changes, get fresh refs

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# Output: @e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Submit"

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i  # Check result
```

## Command Chaining

Commands can be chained with `&&` in a single shell invocation. The browser persists between commands via a background daemon, so chaining is safe and more efficient than separate calls.

```bash
# Chain open + wait + snapshot in one call
agent-browser open https://example.com && agent-browser wait --load networkidle && agent-browser snapshot -i

# Chain multiple interactions
agent-browser fill @e1 "user@example.com" && agent-browser fill @e2 "password123" && agent-browser click @e3

# Navigate and capture
agent-browser open https://example.com && agent-browser wait --load networkidle && agent-browser screenshot page.png
```

**When to chain:** Use `&&` when you don't need to read the output of an intermediate command before proceeding (e.g., open + wait + screenshot). Run commands separately when you need to parse the output first (e.g., snapshot to discover refs, then interact using those refs).

## Authentication

Choose the approach that fits your situation:

| Need | Approach | Key command |
|------|----------|-------------|
| One-off task, user already logged in | Auto-connect to their Chrome | `--auto-connect` |
| Recurring automation on same site | Named session (auto-saves cookies) | `--session-name myapp` |
| CI/CD or shared credentials | Auth vault (encrypted) | `auth save` / `auth login` |
| Reuse your real Chrome login (e.g. Google) | Named Chrome profile | `--profile Default` (list via `profiles`) |
| Full browser profile persistence | Persistent profile directory | `--profile ~/.myapp` |
| Manual state snapshot | State file save/load | `state save` / `state load` |

### Auto-connect (borrow user's session)

```bash
agent-browser --auto-connect state save ./auth.json
agent-browser --state ./auth.json open https://app.example.com/dashboard
```

### Named session (recommended for recurring tasks)

```bash
# First run: login and state auto-saves on close
agent-browser --session-name myapp open https://app.example.com/login
# ... fill credentials, submit ...
agent-browser close  # State auto-saved to ~/.agent-browser/sessions/

# Future runs: state auto-restored
agent-browser --session-name myapp open https://app.example.com/dashboard

# Manage saved states
agent-browser state list
agent-browser state clean --older-than 7
```

### Auth vault (encrypted credentials, LLM never sees password)

```bash
# Save once (pipe password via stdin to avoid shell history)
echo "pass" | agent-browser auth save github --url https://github.com/login --username user --password-stdin

# Login by name
agent-browser auth login github

# Manage profiles
agent-browser auth list
agent-browser auth show github
agent-browser auth delete github
```

### Chrome profile / persistent profile

`--profile <name|path>` takes either an existing Chrome profile name (reuse your
real logins — Google, etc.) or a directory path for a dedicated persistent profile.

```bash
# Reuse an existing Chrome profile (already logged into Google, GitHub, ...)
agent-browser profiles                                   # List available Chrome profiles
agent-browser --profile Default open https://app.example.com/dashboard

# Dedicated persistent profile (directory path)
agent-browser --profile ~/.myapp open https://app.example.com/login   # First run: login
agent-browser --profile ~/.myapp open https://app.example.com/dashboard  # Already authenticated
```

### State file (manual save/load)

```bash
agent-browser state save ./auth.json     # After logging in
agent-browser state load ./auth.json     # In a future session
```

State files contain session tokens in plaintext — add to `.gitignore` and delete when no longer needed. Set `AGENT_BROWSER_ENCRYPTION_KEY` for encryption at rest.

## Essential Commands

```bash
# Navigation
agent-browser open <url>              # Navigate (aliases: goto, navigate)
agent-browser close                   # Close browser

# Snapshot
agent-browser snapshot -i             # Interactive elements with refs (recommended)
agent-browser snapshot -i -C          # Include cursor-interactive elements (divs with onclick, cursor:pointer)
agent-browser snapshot -s "#selector" # Scope to CSS selector

# Interaction (use @refs from snapshot)
agent-browser click @e1               # Click element
agent-browser click @e1 --new-tab     # Click and open in new tab
agent-browser fill @e2 "text"         # Clear and type text
agent-browser type @e2 "text"         # Type without clearing
agent-browser select @e1 "option"     # Select dropdown option
agent-browser check @e1               # Check checkbox
agent-browser press Enter             # Press key
agent-browser keyboard type "text"    # Type at current focus (no selector)
agent-browser keyboard inserttext "text"  # Insert without key events
agent-browser scroll down 500         # Scroll page
agent-browser scroll down 500 --selector "div.content"  # Scroll within a specific container

# Get information
agent-browser get text @e1            # Get element text
agent-browser get url                 # Get current URL
agent-browser get title               # Get page title

# Wait
agent-browser wait @e1                # Wait for element
agent-browser wait --load networkidle # Wait for network idle
agent-browser wait --url "**/page"    # Wait for URL pattern
agent-browser wait 2000               # Wait milliseconds

# Downloads
agent-browser download @e1 ./file.pdf          # Click element to trigger download
agent-browser wait --download ./output.zip     # Wait for any download to complete
agent-browser --download-path ./downloads open <url>  # Set default download directory

# Viewport & Device Emulation
agent-browser set viewport 1920 1080          # Set viewport size (default: 1280x720)
agent-browser set viewport 1920 1080 2        # 2x retina (same CSS size, higher res screenshots)
agent-browser set device "iPhone 14"          # Emulate device (viewport + user agent)

# Capture
agent-browser screenshot              # Screenshot to temp dir
agent-browser screenshot --full       # Full page screenshot
agent-browser screenshot --annotate   # Annotated screenshot with numbered element labels
agent-browser pdf output.pdf          # Save as PDF
```

## Diffing (Verifying Changes)

Use `diff snapshot` after performing an action to verify it had the intended effect. Compares the current accessibility tree against the last snapshot taken in the session.

```bash
# Typical workflow: snapshot -> action -> diff
agent-browser snapshot -i          # Take baseline snapshot
agent-browser click @e2            # Perform action
agent-browser diff snapshot        # See what changed (auto-compares to last snapshot)

# Compare against a saved baseline
agent-browser diff snapshot --baseline before.txt

# Visual regression testing
agent-browser screenshot baseline.png
# ... changes are made ...
agent-browser diff screenshot --baseline baseline.png

# Compare staging vs production
agent-browser diff url https://staging.example.com https://prod.example.com --screenshot
agent-browser diff url <url1> <url2> --wait-until networkidle  # Custom wait strategy
agent-browser diff url <url1> <url2> --selector "#main"        # Scope to element
```

`diff snapshot` output uses `+` for additions and `-` for removals, similar to git diff. `diff screenshot` produces a diff image with changed pixels highlighted in red, plus a mismatch percentage.

## Common Patterns

### Form Submission

```bash
agent-browser open https://example.com/signup
agent-browser snapshot -i
agent-browser fill @e1 "Jane Doe"
agent-browser fill @e2 "jane@example.com"
agent-browser select @e3 "California"
agent-browser check @e4
agent-browser click @e5
agent-browser wait --load networkidle
```

### Data Extraction

```bash
agent-browser open https://example.com/products
agent-browser snapshot -i
agent-browser get text @e5           # Get specific element text
agent-browser get text body > page.txt  # Get all page text

# JSON output for parsing
agent-browser snapshot -i --json
agent-browser get text @e1 --json
```

### Parallel Sessions

```bash
agent-browser --session site1 open https://site-a.com
agent-browser --session site2 open https://site-b.com

agent-browser --session site1 snapshot -i
agent-browser --session site2 snapshot -i

agent-browser session list
```

### Tab Management

Tabs have stable string IDs (`t1`, `t2`, …) that persist across re-listing. Commands
act on the active tab; switch tabs with `tab <id>` before interacting.

```bash
agent-browser tab list                 # List open tabs with IDs and titles
agent-browser tab new                   # Open a new blank tab
agent-browser tab new --label review    # Open a labeled tab
agent-browser tab t2                    # Switch to tab t2 (then snapshot/click as usual)
agent-browser tab close t2              # Close a specific tab
```

Note: bare integers (e.g. `tab 2`) are rejected — use the `t`-prefixed IDs. A click
that spawns a tab (`click @e1 --new-tab`) shows up in `tab list`; switch to it to act on it.

### Connect to Existing Chrome

```bash
# Auto-discover running Chrome with remote debugging enabled
agent-browser --auto-connect open https://example.com
agent-browser --auto-connect snapshot

# Or with explicit CDP port
agent-browser --cdp 9222 snapshot
```

### Color Scheme (Dark Mode)

```bash
agent-browser --color-scheme dark open https://example.com
# Or via env var: AGENT_BROWSER_COLOR_SCHEME=dark
# Or set during session: agent-browser set media dark
```

### Responsive Testing

```bash
agent-browser set viewport 1920 1080 && agent-browser screenshot desktop.png
agent-browser set viewport 375 812 && agent-browser screenshot mobile.png

# Retina: same CSS layout at 2x pixel density
agent-browser set viewport 1920 1080 2 && agent-browser screenshot retina.png
```

### Visual Browser (Debugging)

```bash
agent-browser --headed open https://example.com
agent-browser highlight @e1          # Highlight element
agent-browser record start demo.webm # Record session
agent-browser profiler start         # Start Chrome DevTools profiling
agent-browser profiler stop trace.json # Stop and save profile
```

Use `AGENT_BROWSER_HEADED=1` to enable headed mode via environment variable.

### Local Files (PDFs, HTML)

```bash
agent-browser --allow-file-access open file:///path/to/document.pdf
agent-browser screenshot output.png
```

## Security

All security features are opt-in. By default, agent-browser imposes no restrictions.

### Content Boundaries (Recommended for AI Agents)

Enable `--content-boundaries` to wrap page-sourced output in markers that help LLMs distinguish tool output from untrusted page content:

```bash
export AGENT_BROWSER_CONTENT_BOUNDARIES=1
agent-browser snapshot
# Output:
# --- AGENT_BROWSER_PAGE_CONTENT nonce=<hex> origin=https://example.com ---
# [accessibility tree]
# --- END_AGENT_BROWSER_PAGE_CONTENT nonce=<hex> ---
```

### Domain Allowlist

Restrict navigation to trusted domains. Wildcards like `*.example.com` also match the bare domain. Sub-resource requests, WebSocket, and EventSource connections to non-allowed domains are also blocked.

```bash
export AGENT_BROWSER_ALLOWED_DOMAINS="example.com,*.example.com"
```

### Action Policy

Gate destructive actions with a policy file:

```bash
export AGENT_BROWSER_ACTION_POLICY=./policy.json
```

Example `policy.json`:
```json
{"default": "deny", "allow": ["navigate", "snapshot", "click", "scroll", "wait", "get"]}
```

### Output Limits

Prevent context flooding from large pages:

```bash
export AGENT_BROWSER_MAX_OUTPUT=50000
```

## Timeouts and Slow Pages

The default action timeout is 25 seconds. Override with `AGENT_BROWSER_DEFAULT_TIMEOUT` (milliseconds) — all `wait` variants respect it. For slow pages, use explicit waits:

```bash
agent-browser wait --load networkidle       # Wait for network to settle
agent-browser wait "#content"               # Wait for specific element
agent-browser wait --url "**/dashboard"     # Wait for URL pattern
agent-browser wait --fn "document.readyState === 'complete'"  # JS condition
agent-browser wait 5000                     # Fixed duration (last resort)
```

Use `wait --load networkidle` after `open` for slow sites. If a specific element is slow to render, wait for it directly.

## Session Management and Cleanup

When running multiple agents concurrently, always use named sessions to avoid conflicts:

```bash
agent-browser --session agent1 open site-a.com
agent-browser --session agent2 open site-b.com
agent-browser session list
```

Always close your browser session when done to avoid leaked processes:

```bash
agent-browser close                    # Close default session
agent-browser --session agent1 close   # Close specific session
```

## Ref Lifecycle (Important)

Refs (`@e1`, `@e2`, etc.) are invalidated when the page changes. Always re-snapshot after:

- Clicking links or buttons that navigate
- Form submissions
- Dynamic content loading (dropdowns, modals)

```bash
agent-browser click @e5              # Navigates to new page
agent-browser snapshot -i            # MUST re-snapshot
agent-browser click @e1              # Use new refs
```

## Annotated Screenshots (Vision Mode)

Use `--annotate` to take a screenshot with numbered labels overlaid on interactive elements. Each label `[N]` maps to ref `@eN`. This also caches refs, so you can interact immediately without a separate snapshot.

```bash
agent-browser screenshot --annotate
# Output includes the image path and a legend:
#   [1] @e1 button "Submit"
#   [2] @e2 link "Home"
agent-browser click @e2              # Click using ref from annotated screenshot
```

Use annotated screenshots when:
- The page has unlabeled icon buttons or visual-only elements
- You need to verify visual layout or styling
- Canvas or chart elements are present (invisible to text snapshots)

## Semantic Locators (Alternative to Refs)

When refs are unavailable or unreliable, use semantic locators:

```bash
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
agent-browser find role button click --name "Submit"
agent-browser find placeholder "Search" type "query"
agent-browser find testid "submit-btn" click
```

## JavaScript Evaluation (eval)

Use `eval` to run JavaScript in the browser context. **Shell quoting can corrupt complex expressions** — use `--stdin` or `-b` to avoid issues.

```bash
# Simple expressions work with regular quoting
agent-browser eval 'document.title'
agent-browser eval 'document.querySelectorAll("img").length'

# Complex JS: use --stdin with heredoc (RECOMMENDED)
agent-browser eval --stdin <<'EVALEOF'
JSON.stringify(
  Array.from(document.querySelectorAll("img"))
    .filter(i => !i.alt)
    .map(i => ({ src: i.src.split("/").pop(), width: i.width }))
)
EVALEOF

# Alternative: base64 encoding (avoids all shell escaping issues)
agent-browser eval -b "$(echo -n 'Array.from(document.querySelectorAll("a")).map(a => a.href)' | base64)"
```

**Rules of thumb:**
- Single-line, no nested quotes -> regular `eval 'expression'` with single quotes
- Nested quotes, arrow functions, multiline -> use `eval --stdin <<'EVALEOF'`
- Programmatic/generated scripts -> use `eval -b` with base64

## Configuration File

Create `agent-browser.json` in the project root for persistent settings:

```json
{
  "headed": true,
  "proxy": "http://localhost:8080",
  "profile": "./browser-data"
}
```

Priority (lowest to highest): `~/.agent-browser/config.json` < `./agent-browser.json` < env vars < CLI flags. Use `--config <path>` or `AGENT_BROWSER_CONFIG` env var for a custom config file. All CLI options map to camelCase keys (e.g., `--executable-path` -> `"executablePath"`). Boolean flags accept `true`/`false` values.

## Troubleshooting

### First step: run doctor
`doctor` diagnoses the install (CLI version, Chrome, daemons, state dir, providers) and
auto-cleans stale daemon files. Use `--fix` to also resolve fixable issues.
```bash
agent-browser doctor              # Full diagnostics
agent-browser doctor --quick      # Fast checks only
agent-browser doctor --fix        # Auto-clean stale files / fix issues
```
A "version mismatch" warning on a session means the daemon predates a CLI upgrade —
close that session (`agent-browser --session <name> close`) and reopen.

### Daemon stuck or zombie process
```bash
agent-browser close                         # Try graceful close first
pkill -f "agent-browser" 2>/dev/null        # Force kill if close hangs
agent-browser open https://example.com      # Start fresh
```

### Snapshot returns empty or incomplete
The page hasn't fully loaded. Add explicit waits before snapshotting:
```bash
agent-browser wait --load networkidle && agent-browser snapshot -i
# For SPAs that hydrate after network idle:
agent-browser wait --fn "document.querySelector('#app')?.children.length > 0"
```

### Click fails silently (element covered by overlay)
A modal, toast, or cookie banner may be covering the target element. Dismiss it first:
```bash
agent-browser snapshot -i  # Look for overlays/modals
agent-browser click @eN    # Click dismiss/close on the overlay
agent-browser snapshot -i  # Re-snapshot, then retry your action
```

### SPA hydration — networkidle fires too early
Single-page apps often show a shell before JS hydration completes. Wait for a specific element that only appears after hydration:
```bash
agent-browser wait "#main-content"
# or wait for a JS condition:
agent-browser wait --fn "window.__APP_READY === true"
```

### "os error 35" or "Browser not launched"
```bash
agent-browser close          # Clean up stale daemon
agent-browser open <url>     # Retry
```

### Refs stop working after page change
Refs are invalidated on navigation or DOM mutation. Always `snapshot -i` again after clicking links, submitting forms, or triggering client-side routing.

### Clerk/OAuth sign-in stuck or not loading
- Wait longer for auth JS to load: `agent-browser wait --load networkidle && agent-browser wait 3000`
- Take a debug screenshot: `agent-browser screenshot /tmp/debug.png`
- If CAPTCHA appears, switch to headed mode: `agent-browser --headed open <url>`

## Performance & Framework Introspection

```bash
# Core Web Vitals (LCP / CLS / TTFB / FCP / INP) + React hydration summary
agent-browser vitals https://example.com
agent-browser vitals --json              # Full data for parsing

# SPA client-side navigation (auto-detects Next.js router; triggers RSC fetch)
agent-browser pushstate /dashboard

# React component introspection (requires devtools enabled at open time)
agent-browser open https://example.com --enable react-devtools
agent-browser react tree                 # Full component tree
agent-browser react inspect <id>         # Props, hooks, state, source for one fiber
agent-browser react renders start        # Record re-renders...
agent-browser react renders stop --json  # ...then print the render profile
agent-browser react suspense --only-dynamic --json   # Suspense boundary report
```

## Self-Updating Reference

The CLI ships version-matched skill docs — prefer these over guessing flags:

```bash
agent-browser skills                     # List bundled skills
agent-browser skills get core            # Core usage guide (overview + patterns)
agent-browser skills get core --full     # Full command reference + templates
agent-browser skills get <name>          # Specialized: electron, slack, dogfood, vercel-sandbox, agentcore
```

## Advanced Features

For iOS Simulator testing, native Rust daemon mode, and alternative browser engines (Lightpanda), see `references/advanced.md`.
