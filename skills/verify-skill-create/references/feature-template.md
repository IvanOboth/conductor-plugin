---
id: delivery-trips
sources:
  - apps/web/app/**/dashboard/delivery/trips/**
  - apps/web/app/**/dashboard/delivery/[tripId]/**        # brackets are literal; only * ** ? are wildcards
  - packages/backend/convex/trips*.ts
---

# Delivery trips and settlement

A back-office user plans a truck's journey, loads it, follows it during the day and settles cash
and stock when it returns. Managers see the same trips read-only.

## Sub-features

- `trips-list` lists today's trips with status (planned, loaded, in transit, back, settled).
- `trip-detail` shows one trip's stops, load sheet and collections.
- `trip-settle` counts cash and returned stock and closes the trip.

## How to get to it (user POV)

- Back Office: sidebar **Daily operations › Trips**.
- Back Office: Depot today › **Trips out** tile.
- Manager: ⌘K, type `trips`.
- Not on Mikono Go for back office; reps see their own trip under Go › Trips.

## Driving it with verify-<app>

Preconditions:

- `$H doctor` prints `OK`; signed in with `$H sign-in kbd.backoffice`.
- The demo day is seeded for today (Depot today shows at least one trip out), or the list is empty
  and only `trips-list` can be proven.

- **Open the list.** `$H open /dashboard/delivery/trips`. The heading reads `Trips`; rows show a
  status badge.
- **Open a trip.** `$B find role link click --name "<trip number>"`, then `$B wait --url "**/delivery/*"`.
  The heading shows the trip number and the `Load sheet` tab.
- **Settle (Writes, not safe to repeat in a demo org).** `$B find role button click --name "Settle trip"`
  opens the settlement form; stop before `Confirm settlement`. From source: confirming sets the
  status to `Settled` and posts the cash to the till.
- **Proof.** `$H shot trips-detail`. The PNG shows the trip number, its status and the load sheet.

## Gotchas

- Without a seeded demo day the list is empty; that is not a bug.
- The old route `/dashboard/delivery/[tripId]` still works and shows the same screen.
- The settlement print view opens in a new tab; use `$B tab` to switch.
