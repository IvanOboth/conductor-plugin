# Device selection and recovery

These are routes and diagnostic anchors, not instructions to install every tool. Read installed help/tool schemas before executing version-sensitive commands. Discover actual executables, configured providers and available devices without dumping credentials.

For Expo apps, start with [Expo iteration and OTA verification](expo.md). The routes below support non-Expo apps and Expo fallback when official cloud access is unavailable or a local device better fits the task. Preserve an already working Genymotion route as a fallback; do not make it the Expo default.

## Android

- Check `adb devices -l`, emulator availability, architecture/ABI and acceleration. On Linux, check accessible `/dev/kvm`; a successful boot animation does not prove system services can survive sign-in. On a capable Mac or Linux host, a compatible accelerated emulator is suitable. Prefer authorized cloud hardware when acceleration is absent or repeated system-server/watchdog failures prevent testing.
- Genymotion SaaS can expose a virtual device over ADB. Check the installed `gmsaas` or project wrapper help, list existing instances, start only authorized capacity with a bounded lifetime (provider-enforced where supported), record the expiry and fallback cleanup owner, then connect the exact instance. A checkpoint survives a worker restart; a background shell alone is not a shutdown guarantee. Commands observed on Bench in September 2026 included `gmsaas instances adbconnect <uuid> --adb-serial-port <free-port>` and `gmsaas instances stop <uuid>`; recheck the installed contract. An API-token login may work even if a user-identity subcommand does not. The installed Bench CLI supports `gmsaas instances start --max-run-duration <minutes> <recipe-uuid> <run-unique-name>`: pass an explicit nonzero duration within the authorized limit, never rely on the organization default. The timeout counts from boot; separately track the provisioning deadline. Persist the unique name and creation intent before calling start, then reconcile by that exact name after an interrupted response. Recheck current help on other versions and use the equivalent enforced timeout when available.
- Mobile Next/mobile-mcp can drive an ADB-visible virtual device as well as a physical phone. Enumerate its actual tools; prefer its install, element listing, input, screenshot and recording operations when available. Maestro/Appium or direct ADB are valid existing alternatives. No project requires a particular driver merely because it was used once.
- Verify installation succeeded and check package/version (`adb -s <serial> shell dumpsys package <package>`). Record checksum of the installed artifact and source/build metadata. SDK/package mismatches are environmental failures, not auth fixes.
- On an owned disposable device, exercise the real IME: `settings put secure show_ime_with_hard_keyboard 1` may be needed. `wm size`, `wm density` and `settings ... font_scale` allow small-screen/enlarged-text checks. Record physical pixels, density, logical size, IME, font scale, locale and timezone. Preserve/restore borrowed-device settings; disposable instances can be destroyed after capture.
- UI tree dumps can transiently fail while an app changes screens. Observe the current screenshot and retry the read when settled. Input tools may append instead of replace, or expose bounds outside the visible scroll viewport. Do not reuse stale coordinates or blindly repeat credential typing.
- For a native drawing pad, use real touch gestures long enough to produce the application's minimum valid stroke. A fast gesture with too few points may correctly leave Sign disabled. Check enabled state, Clear, cancellation, the uploaded image and saved reference; never inject an image and call it a native signing test.

### Auth versus system services

If the process/system disappears on sign-in, inspect app process state, crash/logcat evidence and system-service health before blaming Clerk or another auth provider. If the app remains alive with an auth error, inspect the supported factor, environment configuration and session activation without exposing secrets. Verify the selected tenant/persona after login.

A cloud Android image may lack Google Play Services. When location fails with service-unavailable/invalid evidence, check packages and provider capabilities. Where appropriate, use the provider's supported Google Apps installer on an authorized disposable guest, then reboot/reconnect and retest. Do not assume every Genymotion image supports the same installer, install an arbitrary APK mirror, or treat Play Services as mandatory for apps that do not need them.

Set simulated GPS through the provider's supported controls when testing simulation. Capture permission-denied and granted behavior if relevant. Report simulated coordinates accurately; it proves the software path, not real sensor reception. Keep authenticated viewer pages/configuration private and stop their owned browser contexts afterward.

### Artifact iteration

For Expo/EAS, follow [the dev-client and OTA decision](expo.md) before submitting a build. Use the project's package manager and exact profile/environment. Read existing job status before retrying. Download the selected artifact, verify it, install it and assert its identity. For Gradle/Xcode/other build systems, use the project's existing incremental workflow and final-artifact checks. A successful build alone is not a device test.

## iOS and physical devices

Use an available Mac's Xcode simulator for compatible simulator builds. An IPA for a physical device is not interchangeable with a simulator app. Inspect `xcrun simctl list devices` and the app's architecture/signing requirements; record the exact device and artifact. Mobile Next can drive supported connected targets; verify the installed tool's capabilities rather than assuming Android commands work on iOS.

Physical phones may require pairing, trust, provisioning or user interaction. Ask only for the concrete missing step when necessary, and continue independent work. Existing authorization to test does not authorize changing unrelated personal-device settings.

### Mac access bootstrap

For unattended recurring runs, prefer an authorized managed cloud route when the Mac may be asleep or off; a reachable Mac remains useful for interactive local testing. If Mac setup is requested through computer use, discover the actual connected desktop-control tool/session and confirm which host it controls before claiming you can operate the Mac. Browser automation or SSH on another host is not Mac desktop control.

Remote Login enables the SSH service; it does not establish the Mac's short account name, allowed users or authorized key. Inspect existing host configuration, known account and exact connection error first. Check the intended public-key fingerprint and explicitly select the existing identity with supported SSH options such as `-i <identity-path>` and `IdentitiesOnly=yes`; nondefault key filenames may not be offered automatically. Never display or request a private key or password, and do not guess many usernames or rotate keys to mask an authentication failure.

If neither desktop control nor authenticated transport is available, explain that concrete limit, request the short Mac username only if unknown, and provide one additive local public-key setup step for that user to run. Prepare it from the intended public key: preserve existing `authorized_keys` entries, add the key only if absent, preserve ownership and secure `.ssh`/`authorized_keys` permissions, and constrain the entry to the intended source tailnet host/address when appropriate. Do not overwrite the file, loosen existing permissions or add another account's key. Keep host/account/key details in private task state, not this reusable skill. A pending local setup is not a completed remote action; continue independent authorized work while waiting.

After access succeeds, verify `id` and `uname` on the intended host, then inspect actual Xcode/simulator/device tools and available targets before claiming native capability. SSH success is transport evidence; only a subsequent installed-app run establishes a simulator test. Do not pursue Mac SSH when another authorized runtime already satisfies the task. If iOS is required and no iOS runtime is reachable, keep that case blocked rather than substituting Android/web evidence.
