---
name: generate-plan
description: Generate a periodized, multi-modal training block toward a target — run + strength sessions across weeks, calibrated to the athlete's fitness and (if present) health status. Use when the user asks to "generate a plan", "build my training plan", "plan my weeks", after a target is set and fitness assessed.
---

# Generate Plan

Produce a validated `Block` for a campaign: `Target + Profile + latest FitnessSnapshot
(+ optional HealthStatus) → a periodized schedule of run & strength Sessions`, saved to
`campaigns/<slug>/block.json` (+ `block.md` for review).

Models are in `src/training_planner/models/plan.py`; persistence via `uv run plan`.

## Inputs (read first)

- `campaigns/<slug>/target.json` — what we're training for (run `plan_cli.py show <slug>`
  won't work before a block exists; just read the file).
- `athlete/profile.json` — zones/thresholds → **calibrates paces & HR** in every workout.
- latest `athlete/fitness-snapshots/<date>.json` — current weekly volume, longest run,
  trend → **sets starting load & progression**.
- `athlete/health-status.json` **if it exists** — injuries/limitations. Absent = healthy.

## Method

1. **Weeks available** = target date − today (for a dated race). For an open performance
   goal, pick a sensible block length (e.g. 8–12 weeks) and say so.
2. **Periodize** into phases: **base → build → peak → taper**. Roughly: base ~25%,
   build ~45%, peak ~15%, taper ~15% (scale to weeks available; short blocks compress base).
3. **Volume progression** — start from the snapshot's current weekly km. Build ~5–10%/week,
   with a **deload every ~4th week** (down ~30%). Never jump the long run > ~2–3 km/week.
4. **Long run** ramps toward (but need not exceed) the target distance; peaks ~2–3 weeks
   before taper. For hilly/trail targets, add vert to long runs; ignore vert for flat goals.
5. **Key sessions** (`key=True`): the long run and the week's main quality session. Protect
   the day before each (easy or rest, no heavy legs).
6. **Sessions per week** — author `run` and `strength` Sessions (`run_session` /
   `strength_session` factories):
   - Runs → a `WorkoutSpec` with targets from `profile.json` zones. **Honor
     `profile.target_preference`:** if `pace`, use `pace(...)` for *every* run target (easy
     from the Z2 pace band, quality at threshold/VO2 paces); if `hr`, use `hr_zone(...)` /
     `hr_range(...)`. If it isn't recorded yet, **ask the athlete before prescribing** — don't
     default silently. Easy stays easy; quality sharpens per phase.
   - Strength → from principles, supporting the goal (unilateral legs, posterior chain,
     core; eccentric/descending work for hilly targets). 1–2×/week, reduced in taper.
7. **If `health-status` present** — respect `limitations`, stage return-to-run, add deloads,
   swap high-impact work. Injury safety outranks the schedule.
8. **Taper** — cut volume ~40–60% over the final weeks, keep some intensity, drop strength load.

## Output

1. Draft `block.json` matching the `Block` model (weeks 1..N in order; each Session dated).
   Set `generated_from` to the snapshot file used (provenance).
2. Save + validate: `uv run plan save-block <slug> <draft.json>`.
   Fix and re-run on any validation error.
3. Show `block.md` and walk the athlete through the block. **The `block.md` is the
   deliverable** — a Garmin watch is optional. If they use one, suggest `/sync-garmin` for
   the run sessions once they approve; if not, they follow `block.md` directly.

## Notes

- **Discuss before committing.** Talk through the shape with the athlete; don't dump a
  finished block without a look.
- This is guidance-driven periodization, not a rigid template — adapt to the person.
- **Garmin is optional.** The plan lives in `block.md` / `block.json` and stands on its own;
  `/sync-garmin` (run sessions) is just an extra convenience for watch owners.
