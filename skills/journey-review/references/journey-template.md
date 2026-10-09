---
id: rep-outlet-visit
persona: Salesperson (rep), Mikono Go on Android, in an outlet
surface: native
features: [go-field-sales, go-van-and-money, delivery-trips]
sources:
  - apps/go-native/src/app/(app)/my-day.tsx
  - apps/go-native/src/app/(app)/trips/**
  - apps/go-native/src/app/(app)/sale.tsx
  - apps/go-native/src/app/(app)/printer.tsx
---

# Rep visits an outlet and sells

A rep on a van route arrives at the next outlet on today's trip, sells from the van, takes payment and
leaves a receipt, then moves on. Twenty to forty times a day; the customer is waiting at the counter.

## Goal and context

- Job: "I'm at Blue Gate Pub. Sell them what they need from my van, take the money, give a receipt."
- Where: standing at the counter, one hand on the phone, often weak network.
- Stakes: cash and stock on the van must reconcile at settlement; a wrong receipt costs trust.

## Steps the user expects

1. See the next outlet on today's route and arrive (check in).
2. See what they usually buy and what is on the van.
3. Add products, change quantities, remove a line.
4. See the total, apply an agreed price if allowed.
5. Take payment: cash, mobile money, part now and the rest on credit.
6. Give a receipt (print or share).
7. Leave (check out) and see the next stop.

## Path in the app

1. My Day → trip → stop row "Visit <outlet>" …
2. …

## Driving it with verify-<app>

Preconditions: …

- **Open My Day.** …

## Gotchas

- …
