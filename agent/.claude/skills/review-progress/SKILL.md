---
name: review-progress
description: Check adherence and progress against the active training plan — compare the prescribed sessions to what the athlete actually did (from Strava), summarize what's on track vs slipping, reflect on the trend, and recommend. Use at the START of a session whenever a plan exists, or when the user asks "how am I doing", "am I on track", "did I hit the plan", "review my progress".
---

# Review Progress

Answer **"am I on track?"** by comparing the prescribed `block` (what we planned) against
what actually happened (Strava, live via MCP) — then reflect and recommend. The point is
that the athlete shouldn't have to dig through old sessions to know how they're doing: you
open with it.

Only runnable when a plan exists (`campaigns/<slug>/block.json`). No plan → nothing to
review; do `/assess-fitness` and `/generate-plan` first.

## Inputs (read first)

- `campaigns/<slug>/block.json` — the prescription: weeks → sessions (dates, targets, `key`).
- **Strava actuals** — `list_activities` over the plan window (since it started, or since your
  last review); pull `get_activity_performance` on key sessions for pace/HR vs target.
- `athlete/profile.json` (zones) + latest `fitness-snapshots/<date>.json` (recent state).
- `athlete/health-status.json` if present.

## Method

1. **Locate where we are** — today's date against the block's week/session schedule.
2. **Match prescribed → actual.** For each planned session up to today, find the Strava
   activity that fulfills it (date / type / duration / distance). Tag each: **done · partial ·
   missed · swapped · extra** (unplanned work counts too).
3. **Score adherence** — per week and overall: session completion, volume (planned vs actual
   km), long-run hit-rate, and whether **key** sessions landed. On key runs, compare pace/HR
   to the prescribed target.
4. **Reflect on the trend** — building as planned, or flat/declining? Fresh or fatigued?
   Consistent, or gaps that suggest illness/life? Cross-check the latest snapshot; if it's
   stale (>~1–2 weeks), write a new dated one so the series stays current.
5. **Recommend** — one of: on track (carry on) · drifting (a specific fix) · over/under-doing
   it (adjust load). If changes are warranted, hand off to `/adjust-plan`.

## Output

A short, honest progress read — where you are in the block, what landed vs slipped (call out
**key** sessions specifically), the trend, and a clear recommendation. **Talk it through**,
don't just dump a table. Be honest but encouraging: missed sessions happen; judge the trend,
not one rough week.

## Notes

- **Strava is the source of truth for actuals** — the app never stored them.
- **Read-only on the plan** — this reviews and recommends; actual changes go through
  `/adjust-plan`.
- Respect `health-status` — a missed week during a flare-up isn't "bad adherence".
