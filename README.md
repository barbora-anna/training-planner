# Workout Planner

An agent-driven, trail-running training planner that runs **inside Claude Code**.

- **Live data** — Claude reads your training history directly via the Strava MCP. No OAuth, no snapshots.
- **The plan lives in `plans/`** as version-controlled files: a canonical `plan.json` (the machine contract) plus a readable `plan.md` (for review). Edit them by hand anytime.
- **Garmin sync** — Python scripts in `scripts/` push structured workouts to Garmin Connect and schedule them, via the unofficial [`python-garminconnect`](https://github.com/cyberjunky/python-garminconnect) library.
- **Skills** in `.claude/skills/` drive each step of the workflow.

## Workflow

1. **`assess-fitness`** — analyze Strava → `plans/fitness-snapshot.{json,md}`
2. **`generate-plan`** — race details + fitness snapshot → periodized plan in `plans/<race>/`
3. **review & edit** the plan files
4. **`sync-garmin`** — push workouts to Garmin Connect (review before confirming)
5. **`adjust-plan`** — regenerate / make harder / shorten the block → re-sync

## Setup

- Python ≥ 3.14. Install deps from `pyproject.toml` (`garminconnect`, `python-dotenv`).
- Garmin credentials go in `.env` (gitignored):

  ```
  GARMIN_EMAIL=you@example.com
  GARMIN_PASSWORD=...
  ```