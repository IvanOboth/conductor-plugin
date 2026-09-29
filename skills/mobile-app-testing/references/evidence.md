# Native evidence and delivery

Use the installed Conductor evidence gate when applicable: record testing of changed native interactions, not static documents, skills or report browsing. Capture representative flows and reproduced failures; do not impose a recording for every unit test or every edit.

## Recording ownership

Use the driver's supported start/stop recording API when it manages recorder lifetime. Otherwise launch the platform recorder in a durable task-owned shell/session. A short-lived lane shell can kill a background recorder and leave a single-frame file. The owner must survive until recording stops; it can be the GPT-6.1 Sol lane or the orchestrator.

- Android: `adb -s <serial> shell screenrecord /sdcard/<unique-flow>.mp4`, then stop that owned recorder with SIGINT and `adb pull`. The usual three-minute cap needs separate labelled clips for longer flows. Track the recorder PID/session; never kill every `screenrecord` process on a shared device.
- iOS simulator: `xcrun simctl io <device-udid> recordVideo --codec h264 <flow>.mp4`, then SIGINT the owned process. Prefer a specific device over an ambiguous `booted` target.
- For physical iOS/other drivers, use their supported recording route. If capture is infeasible, preserve the actual failure and use captioned screenshots plus assertions as a declared fallback.

Start before the actions that establish the claim. Stop on success and failure, verify nonempty file/duration/codec (for example with `ffprobe`) and actual playback. On a headless host, an owned browser can load the served video, seek, call `play()` and assert advancing playback/current frame and no media error; no desktop display is required. A decode/frame-extraction check is useful where browser playback is unavailable, with that limitation stated. Metadata alone does not establish playback or visual quality. Native MP4 does not need transcoding simply to match a previous workflow. On Bench, necessary conversions use `bench-heavy-run` with bounded threads.

## Run artifacts

Keep a small sanitized provenance record containing source revision, build ID/profile/version, artifact checksum, installed app ID/version, device/provider/OS/ABI, screen and text settings, timezone, backend/tenant, fixture IDs, actual executor model/effort, test timestamps and cleanup status. For Expo, also record the dev-client/Metro or OTA execution mode, native runtime/fingerprint, channel/branch and environment, and the running platform update ID (or embedded/Metro state). An EAS upload receipt is not proof the device loaded that update. Keep raw auth/deployment/viewer state and private configuration outside report roots; include only sanitized evidence needed for the claim.

Per case, retain expected/actual result, pass/fail/blocked/not-run, tested build/platform, assertion command/output and media references. Compare before/after with matching steps and conditions when feasible; explain mismatches. Identify the final artifact retests and earlier-build coverage separately. An assertion over an exported snapshot proves that snapshot, not a new live transaction. Unit tests, SDK/interpreter probes, native interaction, independent state checks and visual review are separate evidence classes. Distinguish warm offline behavior from cold startup and reconnect; preserve timed download-state/connectivity observations for interruption claims. Pending native acceptance remains pending even when SDK probes pass.

For hosted native runs, retain both workflow and job identities plus downloaded artifacts; confirm screenshots, video and actual assertion results survived artifact upload. Preserve failed evidence alongside passing retests, including a flow that failed before login. Report static flow validation, expression-interpreter checks and native execution separately. For an OTA retest, tie the assertion to the verified running update UUID and installed binary identity, not merely the latest publication or a fresh-state launch. See [Expo iteration and OTA verification](expo.md) for job-log lookup, monorepo artifact paths and runtime identity checks.

For mutations, verify the specific records tied to the UI action, including intended idempotency/notification counts. Global fixture totals can change during another run. Do not mask a real duplicate by counting only one selected record. Preserve the first failing run and the corrected retest. A mock or seeded signature does not establish native drawing/upload.

## Report and verification

Update the issue's existing report when this is the same issue. Include outcome and scope, what changed and why, case matrix, version-specific captions/media, commands and actual output, material failures, unresolved findings, missing platforms and cleanup. Embed native video with `<video controls playsinline preload="metadata" src="assets/<run>/<flow>.mp4"></video>`. Explain the workflow in plain language; keep raw logs/reviews in supporting links or disclosures. Follow Conductor's current report design rather than copying an old report's styling.

Deliver through the project's configured surface and access boundary. On Ivan's Bench, follow the local REPORTS.md, run `~/bin/report-link.py <report>`, confirm HTTP 200 and intended bytes, inspect the served page at desktop and phone widths, and check required images/media load and play. Label its URL **private — Tailscale access required**. Account for navigation links/logs that the helper does not copy automatically. A VM path or printed URL is not delivery. Other hosts use their configured artifact surface; do not require Ivan's private host names.

No public publication, issue comments, release or merge is authorized merely by this skill. Report missing visual judgment or runtime access as a gap, never as a pass. Skill authoring/validation needs source, command and static report evidence; it does not require renting a device or recording the report.
