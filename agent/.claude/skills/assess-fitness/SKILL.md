---
name: assess-fitness
description: Analyze the athlete's recent Strava training history to produce a current fitness snapshot — weekly volume, longest run, elevation, pace and heart-rate ranges, run frequency, and recent load trend. Use when starting a new training plan, before generating or adjusting a plan, or when the user asks "how fit am I", "assess my training", or "check my Strava".
---

# Assess Fitness

Produce a structured snapshot of the athlete's current fitness from their Strava data.
It writes two things (schemas map to `src/training_planner/models/athlete.py`):

- `athlete/profile.json` — slow-changing capacity (HR/pace zones, thresholds, weight).
  Update only when it has actually changed; the prior version is archived automatically.
- `athlete/fitness-snapshots/<YYYY-MM-DD>.json` — today's training-state, append-only.
  This dated series is the progress history.

These are the primary inputs to `generate-plan` and `adjust-plan`.

## Steps

1. **Profile & zones** — `get_athlete_profile` (name, location, weight, units, focus) and
   `get_athlete_zones` (HR + pace zones). Record the unit system.
2. **Recent activities** — `list_activities` for ~12 weeks. Keep runs; note cross-training
   (strength, hiking, cycling) as context.
3. **Detail on key runs** — for the longest and hardest sessions, pull
   `get_activity_performance` / `get_activity_streams` for pace, HR, and elevation.
4. **Compute and record:**
   - **profile.json:** HR zones, pace zones / thresholds, weight, units, `updated_on`.
   - **snapshot:** weekly volume (distance & time) over 4 / 8 / 12 weeks + trend
     (building / flat / declining); longest run (distance **and** elevation); typical easy
     pace + best estimate of threshold/tempo; run frequency and any consistent long-run day;
     flags (sharp load jumps, gaps suggesting illness/injury, very low recent volume).
5. **Write both files** with today's date and the exact activity date range used.

## Notes

- **Elevation is goal-dependent, not the point.** Capture it either way (it's cheap), but it
  matters for hilly/trail targets and barely for flat road goals — `generate-plan` uses it
  only when the target calls for it.
- **Keep the schemas stable** — they map to `Profile` / `FitnessSnapshot` in
  `src/training_planner/models/athlete.py`. Add fields, don't rename.
- Respect the athlete's measurement preference (km vs miles).
- **Read-only:** this skill summarizes; it does not generate a plan.
