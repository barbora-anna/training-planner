# athlete/

The athlete's own state. Split by how fast each part changes. Personal data here is
gitignored (this README is the only tracked file); the schemas map to
`../src/training_planner/models/athlete.py`.

- `profile.json` — slow-changing **capacity**: HR/pace zones, thresholds, weight. Drives the
  *targets* in prescribed workouts. Updated deliberately; prior versions are archived to
  `profile-history/` on each change.
- `profile-history/` — dated prior `profile.json` versions (e.g. threshold-pace history).
- `fitness-snapshots/<YYYY-MM-DD>.json` — immutable **weekly training-state** (volume,
  longest run, trend). Append-only — this dated series is the progress history.
- `health-status.json` — **optional** injury/availability. Absent means healthy. When
  present, it shapes the plan (deloads, return-to-run staging, swaps).

Produced/updated by the `assess-fitness` skill; read by `generate-plan` / `adjust-plan`.
