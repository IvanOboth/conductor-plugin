# Project profile and bounded device order

Keep a project's durable facts in `docs/testing/mobile-profile.md` (or its established equivalent). Link existing project authentication/fixture docs instead of copying credentials. Use values discovered for this project, not the examples from a previous run.

## Project profile

- App root, package manager, local instructions and scoped check commands.
- Android package / iOS bundle ID; build system, profiles and artifact lookup.
- Development backend/tenant, how to verify it, test personas and the private source of test authentication details.
- Safe fixture setup, mutation permissions, independent read/assertion methods and intended residual fixture state.
- Required native platforms, screen/text settings, location/camera/service requirements and report delivery surface.
- For Expo: SDK/CLI versions, compatible dev-client lookup, Metro ownership/reachability, QA channel/branch and environment, runtime policy/fingerprint, OTA-capable binary lookup and update-ID observation method.
- Known environment limitations with dated evidence. Treat old APK IDs, device serials and cloud instance IDs as historical, not reusable defaults.

## Work order

```text
Scope: <change, requested flows, source/artifact>
Profile: <path; project instructions also apply>
Execution: gpt-6-astra, effort <medium|high>, reason <task bottleneck>
Routing record: <routing.json with actual model, effort, reason and acceptance criteria>
Review: <active profile; Astra review for Conductor Core, Claude review where required; orchestrator accepts>
Ownership: <one device/session owner; fixture; source files permitted to change>
Checkpoint: <private path known to orchestrator, written before provisioning>
Instance name/tag: <run-unique provider name recorded before the start request>
Environment: <backend, tenant, test accounts by reference; verify before writes>
Platforms: <required devices/OS; unsupported platform handling>
Resources: <authorized provider/capacity and lifetime or budget; build job ownership>
Expo gate: <dated account availability; chosen dev-client/local/cloud/OTA mode; fallback>
Expo provenance: <binary ID/checksum, runtime/fingerprint, channel/branch/environment, running update ID>
Cases: <precondition → actions → expected outcome → independent assertion>
Evidence choice: <video/screenshots/commands; why; output paths>
Artifacts: <report.md, case matrix, sanitized provenance, media; private state elsewhere>
Recovery: <known fallback; missing information that would require user input>
Close: <save evidence, stop owned device/recorders, verify cleanup; review delivery owner>
Limits: <no recursive delegation unless specified; no unapproved production/shipping>
```

Use installed bridge help to choose invocation and sandbox options. Grant the device lane the actual execution/filesystem permissions needed by the task; `read-only` is for source review, not a lane that must install an app or write evidence. Do not treat unrestricted filesystem access as permission for unrelated accounts or production actions.

The lane returns a case matrix with build/platform, expected vs actual result, pass/fail/blocked/not-run, assertion evidence and media paths. Include actual command output and resource cleanup status. The orchestrator reads the artifacts, checks the claims and integrates the final HTML.

## Launch permissions and route availability

Check installed `ask-codex --help`, `codex exec --help`, login status and the relevant sandbox/network settings in Codex's active configuration. Inspect only needed settings; do not copy auth or full configuration into reports. Wrapper versions differ: this checkout’s `bin/ask-codex` explicitly selects workspace-write; the separately installed Bench wrapper observed on 14 September 2026 omits that flag by default and inherits configuration. Inspect the executable actually being launched. Neither its name nor the global config establishes the effective mode or network access. Check available quota/status if the harness exposes it; no artificial model request is needed just to prove the route exists.

If the wrapper cannot express the task's permitted execution mode, use the CLI directly. For a lane whose writes stay inside the workspace, a baseline form is:

```sh
codex exec -m gpt-6-astra -c model_reasoning_effort=high \
  --sandbox workspace-write -o result.md - < order.md
```

Set the host-supported approval policy deliberately for an unattended lane; where the task/harness permits non-interactive execution, `-c approval_policy=never` prevents an unanswered approval prompt and does not grant access denied by the sandbox. Do not override a required approval policy.

Where the host supports and permits it, workspace-write network access can be configured with `-c sandbox_workspace_write.network_access=true`; separately grant the necessary writable paths using the supported harness controls. For an authorized device run that genuinely must act outside the workspace, `codex exec --sandbox danger-full-access ...` is an explicit alternative only when allowed by the host/task permissions. Name the reason and ownership boundaries. These examples do not authorize bypassing a sandbox denial, changing global configuration, or disabling approval controls. If the current harness forbids a required mode, report that concrete block or select another permitted route.

On quota/launch failure, checkpoint the device ID/deadline and build jobs so the orchestrator can resume or stop them. Continue other authorized work. Use a different executor only when the task permits it and record that change; do not silently replace the requested Astra route or claim completion.
