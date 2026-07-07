---
name: assess-fitness
description: Analyze the athlete's recent Strava training history to produce a current fitness snapshot — weekly run volume, longest run, elevation, pace and heart-rate ranges, run frequency, strength-session frequency and load, and recent trend. Use when starting a new training plan (run or strength), before generating or adjusting a plan, or when the user asks "how fit am I", "assess my training", or "check my Strava".
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

1. **Profile & zones** — `get_athlete_profile` (name, sex, weight, location, units) and
   `get_athlete_zones` (HR + pace zones). Record the unit system.
   **Then fill in who they are** — the fields Strava can't give that individualize load:
   `age`, `height_cm`, `training_status` (untrained / novice / intermediate / advanced), and
   a `strength_baseline` (current key lifts if they know them, or just "new to lifting" /
   "trains 3×/week"). **Ask the athlete** for whatever's missing — don't assume a beginner is
   an athlete or vice-versa. This is what keeps a small untrained lifter's plan from looking
   like a strong veteran's.
2. **Recent activities** — `list_activities` for ~12 weeks. Keep **runs and strength
   sessions**; note other cross-training (hiking, cycling) as context. Strava tags strength
   as `WeightTraining` / `Workout` — count them, don't discard them.
3. **Detail on key runs** — for the longest and hardest sessions, pull
   `get_activity_performance` / `get_activity_streams` for pace, HR, and elevation.
4. **Compute and record:**
   - **profile.json:** who they are (`sex`, `age`, `height_cm`, `weight_kg`,
     `training_status`, `strength_baseline`), HR zones, pace zones / thresholds, units,
     `target_preference` (**pace** or **hr** — how they want run targets prescribed; ask if
     you don't already know), `updated_on`.
     **Never guess a person-level field.** Each value comes from data (Strava) or the
     athlete's own words — never inferred, averaged, or filled with a plausible number. If
     they give a **range** ("25–32", "around 60 kg"), record the range or ask them to pin it
     down; **don't** write the midpoint as if it were exact. Unknown and can't get it →
     leave it `null` and say so. A wrong value here silently miscalibrates every workout.
   - **snapshot:** weekly volume (distance & time) over 4 / 8 / 12 weeks + trend
     (building / flat / declining); longest run (distance **and** elevation); typical easy
     pace + best estimate of threshold/tempo; run frequency and any consistent long-run day;
     flags (sharp load jumps, gaps suggesting illness/injury, very low recent volume).
   - **snapshot → strength:** a `strength` block — sessions/week over 4 / 8 / 12 weeks +
     trend, typical session duration/effort, and any pattern visible from titles (e.g. a
     lower/upper split, leg day). This is what a strength plan calibrates against, so capture
     it even for a running goal (it's part of their total load). The model is `extra="allow"`,
     so add the block; don't rename existing fields.
5. **Write both files** with today's date and the exact activity date range used.

## Notes

- **Elevation is goal-dependent, not the point.** Capture it either way (it's cheap), but it
  matters for hilly/trail targets and barely for flat road goals — `generate-plan` uses it
  only when the target calls for it.
- **Keep the schemas stable** — they map to `Profile` / `FitnessSnapshot` in
  `src/training_planner/models/athlete.py`. Add fields, don't rename.
- Respect the athlete's measurement preference (km vs miles).
- **Read-only:** this skill summarizes; it does not generate a plan.
