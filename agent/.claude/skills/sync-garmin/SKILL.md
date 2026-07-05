---
name: sync-garmin
description: Push structured running workouts to Garmin Connect and schedule them on the calendar, using the training-planner CLIs (python-garminconnect). Use when the user asks to "sync to Garmin", "push workouts to my watch", "upload the plan to Garmin", or to schedule/unschedule workouts.
disable-model-invocation: true
---

> ⚠️ Explicit-only: this skill has side effects (it pushes to your watch), so the agent
> will not auto-invoke it. Run it deliberately with `/sync-garmin`. Always dry-run first.

# Sync to Garmin Connect

Pushes structured workouts to Garmin Connect and (optionally) schedules them on the
calendar so they appear on the watch. Uses the unofficial `python-garminconnect` library
via the `training-planner` package.

> Run from the advisor's working directory (`agent/`). `uv run <cmd>` finds the repo-root
> project by walking up, so the `plan` / `workouts` / `garmin-login` CLIs work from here.

## Prerequisites

- Dependencies installed: `uv sync` (installs `garminconnect[workout]`, `python-dotenv`).
- **A cached Garmin session, minted by the user — not you.** `get_client()` here is
  **resume-only**; it never prompts. If it raises "No cached Garmin session", **stop and
  tell the user to run `uv run garmin-login` (or `./train`) in their own terminal.**

> 🔒 **Never enter Garmin credentials.** Do not type, request, or route the user's email,
> password, or MFA code through any command you run — logging in is the user's job, done
> outside this session (the `./train` launcher does it before Claude starts). You only ever
> **resume** an already-cached token.

## Building blocks

- `src/training_planner/garmin/client.py` — `get_client()` **resumes** the cached session
  (never prompts; raises if there's none). The user mints the token separately via
  `uv run garmin-login`.
- `src/training_planner/models/workout.py` — the validated, athlete-facing spec the agent builds
  (`WorkoutSpec`, `Step`, `Repeat`, `pace()`, `hr_zone()`, `hr_range()`).
- `src/training_planner/garmin/translate.py` — `spec_to_garmin(spec)` translates a spec into a Garmin
  workout object.
- `src/training_planner/garmin/library.py` — `WorkoutLibrary` (list / find / create / update / delete /
  schedule / upsert) over Garmin's endpoints.

## Workflow

Pushing is programmatic — build the spec for each `run` session, then translate and
upsert. Drive it with a short `uv run python` snippet from `agent/`:

1. **Confirm the user is logged in.** If a push later raises "No cached Garmin session",
   stop and ask them to run `uv run garmin-login` / `./train` themselves — don't attempt it.
2. **Build & dry-run** — for each `run` session, build a `WorkoutSpec` from its
   `content.workout`, translate with `spec_to_garmin()`, and print `.to_dict()` to
   sanity-check the JSON **before** logging in. Never skip the dry-run.
3. **Upload:** `WorkoutLibrary.connect().upsert(workout)` → returns `{"action", "workoutId"}`.
   Re-pushing the same name updates in place (no duplicate).
4. **Schedule:** `lib.schedule(workout_id, "YYYY-MM-DD")` on each session's date.

```python
from training_planner.models.workout import WorkoutSpec, Step, Repeat, pace, hr_zone
from training_planner.garmin.translate import spec_to_garmin
from training_planner.garmin.library import WorkoutLibrary

spec = WorkoutSpec(name="...", steps=[...])   # from the session's content.workout
workout = spec_to_garmin(spec)
print(workout.to_dict())                      # dry-run: inspect before uploading
# lib = WorkoutLibrary.connect(); lib.upsert(workout); lib.schedule(id, "2026-…")
```

## Capabilities & limits (current)

- Supported steps: warmup / interval / recovery / cooldown / rest, time- or distance-based,
  and repeat groups (e.g. `5x (interval + recovery)`).
- Supported targets (one per step): pace range `pace("5:11","5:32")`, HR zone `hr_zone(2)`,
  custom HR range `hr_range(140,155)`.
- `python-garminconnect` is unofficial — review the dry-run JSON before uploading.
- The in-place `update` (PUT) path is built but **not yet exercised live**; if Garmin
  rejects it, use `upsert(..., strategy="replace")`.

## Managing workouts (no duplicates)

`WorkoutLibrary.upsert()` reconciles by name, so re-pushing a workout with the same
name **updates it in place** (keeps its ID + any calendar scheduling) instead of creating a
duplicate. `upsert(workout, strategy="replace")` instead deletes and recreates (new ID,
drops scheduling).

List or clean up the library:

```
uv run workouts list
uv run workouts delete <workoutId>
uv run workouts delete-by-name "✨ TEST — Threshold 5×4 ✨"
```

## Under the hood (raw client methods `WorkoutLibrary` wraps)

`get_workouts()`, `get_workout_by_id(id)`, `delete_workout(id)`,
`get_scheduled_workouts(year, month)`, `schedule_workout(id, date)`, `unschedule_workout(id)`.
Prefer `WorkoutLibrary` for these; drop to the raw client only for what it doesn't cover.
