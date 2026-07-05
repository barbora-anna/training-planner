# campaigns/

One directory per **target** — a race or a performance goal you're training toward.
Personal data here is gitignored (this README is the only tracked file); the schemas map
to `../src/training_planner/models/plan.py`.

```
campaigns/<slug>/
  target.json    # the goal — a race OR a performance goal (kind: race | performance)
  block.json     # the periodized, multi-modal training block (machine contract)
  block.md       # readable rendering of the block, regenerated on every save
  history/       # prior block.json versions, archived on each adjust
```

- `target.json` is written by `set-target`; `block.json` by `generate-plan` / `adjust-plan`.
- `block.json` is the source of truth the Garmin sync reads; `block.md` is for you.
- Run sessions in a block sync to Garmin; strength sessions are guidance in `block.md`.
