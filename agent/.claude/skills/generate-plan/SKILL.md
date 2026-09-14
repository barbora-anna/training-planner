---
name: generate-plan
description: Generate a periodized, multi-modal training block toward a target — run + strength sessions across weeks, calibrated to the athlete's fitness and (if present) health status. Use when the user asks to "generate a plan", "build my training plan", "plan my weeks", after a target is set and fitness assessed.
---

# Generate Plan

Produce a validated `Block` for a campaign: `Target + Profile + latest FitnessSnapshot
(+ optional HealthStatus) → a periodized schedule of run & strength Sessions`, saved to
`campaigns/<slug>/block.json` (+ `block.md` for review).

Models are in `src/training_planner/models/plan.py`; persistence via `uv run plan`.
Strength prescriptions draw on `agent/knowledge/strength-science.md` — the exercise-science
reasoning (progressive overload, periodization, rep ranges, autoregulation, recovery,
runner-specific selection) behind the rules below. Read it before authoring strength
sessions; this skill file stays procedural.

## Inputs (read first)

- `campaigns/<slug>/target.json` — what we're training for (run `plan_cli.py show <slug>`
  won't work before a block exists; just read the file).
- `athlete/profile.json` — zones/thresholds → **calibrates paces & HR** in every run; and
  `sex` / `height_cm` / `weight_kg` / `training_status` / `strength_baseline` → shapes
  **movement selection and difficulty** (a small untrained beginner starts with simple
  bilateral movements and slow steps; a strong, experienced athlete gets advanced variants).
  These fields calibrate *what* to prescribe, not a kg number — see the strength step below
  for when (if ever) a weight gets attached.
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
6. **Sessions per week** — author `running` and `strength` Sessions (`run_session` /
   `strength_session` factories):
   - Runs → a `WorkoutSpec` with targets from `profile.json` zones. **Honor
     `profile.target_preference`:** if `pace`, use `pace(...)` for *every* run target (easy
     from the Z2 pace band, quality at threshold/VO2 paces); if `hr`, use `hr_zone(...)` /
     `hr_range(...)`. If it isn't recorded yet, **ask the athlete before prescribing** — don't
     default silently. Easy stays easy; quality sharpens per phase.
   - Strength → runner-supporting selection per `strength-science.md` (posterior chain,
     unilateral work, eccentric/descending emphasis for hilly targets, core/anti-rotation;
     plyometrics only for intermediate/advanced and healthy), **scaled to `training_status` +
     `strength_baseline`**: untrained/novice → bodyweight, bilateral before unilateral,
     higher reps (12–15+) at low RPE, linear progression; intermediate/advanced → unilateral
     and eccentric work, the 6–12 hypertrophy band, undulating periodization if they've
     plateaued. Match volume/intensity to the block's current phase (base = movement quality
     and moderate reps, build = rising difficulty, peak = volume down/intensity held, taper =
     hard cut). Since `weight_kg` defaults unset, **express intensity as reps + RPE/RIR** in
     the guidance prose (e.g. "3×10, RPE 7") so effort is self-regulated day to day. 1–2×/week,
     reduced in taper. Write the `focus` + `exercises` guidance for `block.md` **always**. If
     the session should sync to the watch, also attach a structured `StrengthWorkoutSpec`
     (`content.workout`) — pick real exercises from the catalog (`Exercise(category[, name])`;
     use `exercises.find("squat")` to discover valid names), sets via `StrengthSet`, `RestStep`
     between them. No `workout` = guidance-only (nothing pushed). For a **strength-primary
     goal**, the block centers on these sessions rather than run periodization.
     - **Default: leave `weight_kg` unset (bodyweight/self-selected) on every exercise.**
       Don't infer or calibrate a kg number from `strength_baseline` or anything else —
       write `focus`/`exercises` as "your working weight" / bodyweight and skip `weight_kg`
       in the synced spec. **Mention the option, don't assume it:** when building a
       strength-relevant plan, tell the athlete they *could* have specific weights
       prescribed instead — that's how progressive-overload tracking works — but it's
       optional and their call. Only attach a real `weight_kg` if the athlete says in this
       conversation that they want it (for that session/block; ask again next time rather
       than assuming it still holds). Never invent a number they haven't given you.
7. **If `health-status` present** — respect `limitations`, stage return-to-run, add deloads,
   swap high-impact work. Injury safety outranks the schedule.
8. **Taper** — cut volume ~40–60% over the final weeks, keep some intensity, drop strength load.

## Output

1. Draft `block.json` matching the `Block` model (weeks 1..N in order; each Session dated).
   Set `generated_from` to the snapshot file used (provenance).
2. Save + validate: `uv run plan save-block <slug> <draft.json>`.
   Fix and re-run on any validation error.
3. Show `block.md` and walk the athlete through the block. Once they approve, **ask how they
   want it delivered** — a visual artifact, `/sync-garmin` (pushes the run sessions and any
   strength sessions that carry a structured `content.workout`), or both — per
   `agent/CLAUDE.md`. Don't default to either silently.

## Notes

- **Discuss before committing.** Talk through the shape with the athlete; don't dump a
  finished block without a look.
- This is guidance-driven periodization, not a rigid template — adapt to the person.
- Both run and strength sessions can sync to Garmin. Strength always gets `focus`/`exercises`
  guidance in `block.md`; attach a structured `content.workout` when it should reach the watch.
