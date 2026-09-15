---
name: mobile-app-testing
description: Test native mobile apps on Android or iOS devices, diagnose runtime and sign-in failures, fix scoped gaps, and deliver verified evidence. Use for Expo development-client and OTA verification, APK/IPA QA, mobile release checks, or native regression testing.
---

# Mobile app testing

Drive the installed app and prove the requested outcomes. A mobile-sized browser, source review, helper tests, and a successful build provide different evidence; none establishes a native flow by itself. This skill is reusable across projects and works directly or as a Conductor verification lane.

## Ownership and routing

Prefer **GPT-6 Astra (`gpt-6-astra`)** for device setup, native interaction, authentication diagnosis, scoped regression execution, evidence capture, persisted-state checks and cleanup. Use `medium` for an established mechanical replay and `high` when screen interpretation, state, recovery or a sustained device session matters. Record the actual model and effort. A skill cannot change the parent model or grant tools.

- If the current agent is Astra and owns the device, execute here; do not launch a second Astra merely to satisfy routing.
- A Claude orchestrator delegates one bounded device run to Astra. Use the explicit permitted `codex exec` route in the work-order reference for device runs; select the sandbox/network/writable paths that the authorized task needs. Check CLI/bridge help, login/available quota and active permission configuration first. A wrapper is suitable only after confirming it can express those permissions; installed and bundled wrapper versions can differ. A Codex orchestrator uses its available collaboration tools with the same explicit model/effort contract.
- Keep one interaction owner per device, recording session and mutable fixture. Parallelize genuinely independent tests or devices with separate fixtures; serialize shared source edits. No recursive fan-out unless the order grants it.
- Follow the active orchestration profile for review. Conductor Core permits Astra execution and review without a mandatory Claude pass. When the selected profile requires Claude visual/design judgment, retain that requirement and disclose unavailable review. Record the actual reviewer; an Astra review is not cross-family approval. Astra can implement authorized concrete fixes and retest under either profile.
- The orchestrator owns scope, integration and final acceptance. Delegating device execution does not delegate acceptance. If Astra is unavailable, record the limitation and actual execution route; do not relabel another model as Astra.

## Establish the run

Read project instructions and the existing mobile test profile, normally `docs/testing/mobile-profile.md`. Resolve missing facts from the repository/tooling before asking. For a new project, adapt [the profile and work-order template](references/work-order.md); do not import another project's accounts, test codes, URLs or provider assumptions.

Identify the requested flows and independent assertions, app/package identity, source revision and artifact, target backend/tenant, safe fixtures/authentication, platforms, evidence destination, authorized fixes and resource limits. Turn these into a small case matrix before driving. Mark missing platforms or capabilities explicitly; ask only for information/authorization that dependent work actually needs. Installation of a skill is not authorization for production mutations, paid capacity, release publication or personal-device configuration changes. Reuse authorization already given for the task.

For Expo apps, read [Expo iteration and OTA verification](references/expo.md) first. Default to a compatible development client with Metro edit/reload; use official EAS cloud simulators with agent-device when account access and task authorization allow, or an existing suitable local device. Build native code when compatibility changes, a needed compatible binary is missing, or the final candidate requires it. Do not rebuild for every JS edit.

For non-Expo apps and unavailable Expo providers, use [device operations](references/device-operations.md). Inventory installed tools and reachable devices before installing anything or asking for SSH. Mobile Next is an automation driver; Genymotion is a device provider. The established Genymotion/ADB route remains a supported fallback, not the Expo default. Avoid endless software-emulator recovery on a host without usable acceleration.

Before provisioning, give the orchestrator the private checkpoint path and a run-unique provider instance name/tag. Persist that ownership name and creation intent before the start request, then update the record with device ID, recording owner, build job ID, source revision, tested cases and cleanup commands. On interrupted creation, the orchestrator can reconcile that exact owned name/tag against provider state without guessing from a list of all devices. For cloud capacity, use a provider-enforced maximum lifetime within the authorized limit when supported; record its deadline and the orchestrator responsible for cleanup if the worker is interrupted. If only manual shutdown is available, checkpoint that limitation and keep an explicit deadline check; do not claim automatic release. Keep credentials, raw environment captures and authenticated device-viewer state outside report roots. Record the installed version/build and downloaded artifact checksum; when a tool fails, inspect its result before starting dependent work.

## Execute and fix

1. **Establish authentication first.** Verify launch and the intended account/tenant/persona; reuse a suitable authorized session. When sign-in or session behavior is in scope, test the supported factor, wrong/invalid input recovery, correct sign-in and relevant restart behavior. Use the real app SDK and authorized test identity. A development OTP proves session activation, not email/SMS delivery. Never bypass authentication or mark backend-only access as native login.
2. **Drive the changed path.** Include the happy path and the failure/recovery states implied by the change: empty/invalid input, cancel/Back, permissions, repeats, interrupted operations or concurrent answers where relevant. A test plan is not a pass. Do not expand a small fix into every feature in the app.
3. **Exercise actual geometry.** For changed forms/signatures, test a small supported screen, enlarged text and the real software keyboard. Check input, caret and action visibility; scroll reachability; focus while the keyboard is already open; dismissal and draft retention. Verify signature draw/Clear/cancel and long content when relevant. Accessibility bounds can include views behind a keyboard—use screenshots plus interaction to settle visibility.
4. **Assert independently.** Confirm navigation/UI outcome and, for a business mutation, inspect the specific saved record, uploaded object, stock movement or notification through an authorized independent read. Record IDs and expected/actual values. Do not use an API write to manufacture the result of a supposedly native action. Distinguish a modeled race from simultaneous live-device execution, simulated GPS from physical sensing, and a restart online from offline operation.
5. **Diagnose before retrying.** Separate app/SDK failures from device services, provider transport and build failures. Preserve the failing state/logs. After a repeated identical environment failure with no new diagnosis, stop that retry loop and choose another suitable authorized runtime or report the specific block. Do not weaken app authentication or host protections to make a test pass.
6. **Fix within ownership, then retest.** Batch understood related fixes before another expensive build. For Expo JS/assets, use the compatible dev client/Metro loop by default and the isolated QA OTA route when updates are in scope; retain the artifact/release configuration needed for the claim. Check an existing remote job before retrying it; do not duplicate builds after a tool interruption. Run relevant project checks and the failing native case on the resulting artifact, plus regressions justified by the change. If another gap appears, continue this loop rather than reporting the earlier build as the final pass.

Use fresh accessibility/UI observations before actions. Inspect tool errors and transient loading states before retrying; never blindly append a code or credential into an unknown focused field. Preserve failed recordings alongside successful retests with accurate captions.

## Evidence and completion

Apply Conductor's current evidence gate when available. Native interaction changes normally warrant native video; static skill/report changes do not. Follow [evidence and delivery](references/evidence.md) for recording ownership, provenance, assertions and the report contract.

Track **pass / fail / blocked / not run** per case and tested build/platform. Preserve results from earlier APKs as earlier results, and explicitly identify final-artifact retests. A passing helper suite does not fill a missing device result. Resolve or visibly retain every material finding; do not call a broad release fully verified because the requested slice passed.

On completion, cancellation or failure: stop and save owned recordings, stop billable owned devices, close owned automation contexts and temporary services, and verify release. The orchestrator also checks provider/device state after the worker returns or fails, so cleanup does not depend solely on the worker staying alive. Preserve evidence and diagnostic state needed for review. Do not close another person's app/device or delete shared fixtures as cleanup. If a resource cannot be stopped, identify its ID, current state and required cleanup immediately.

Deliver the checked report URL and concise outcome: what changed; commands and actual output; native assertions/evidence; what was not run and why; residual risks. A draft PR or skill does not authorize a merge or deployment.
