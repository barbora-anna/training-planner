---
name: set-target
description: Capture a race or performance goal as a training Target for a campaign. Use when the user names something to train for (a race, a distance/time goal), shares a race URL, or says "set a target/goal", "I want to train for X", "let's plan for Y".
---

# Set Target

Turn a race or goal into a validated `target.json` under `campaigns/<slug>/`, which
`generate-plan` then trains toward. A Target is a **race** or a **performance goal**
(`kind: race | performance`).

## Steps

1. **Gather the target.** Ask for / infer:
   - `name` (required), `kind` (`race` or `performance`).
   - `date` — races have one; open performance goals may not (leave null).
   - `distance_km` — both usually have one (a 22 km race, a 5 km goal).
   - `elevation_gain_m`, `terrain`, `location` — for races; leave null for flat/road goals.
   - `goal` — the objective in the athlete's words ("finish strong", a target time).
   - If the user gives a **race URL**, fetch the page (web) to fill in date, distance,
     elevation, terrain, location. If elevation isn't on the page, search for it. Note
     any figure that's provisional (e.g. "2025 course, ~±50 m").
2. **Pick a slug** — short kebab-case, e.g. `spring-half` or `city-10k`.
3. **Draft `target.json`** matching the `Target` model (`src/training_planner/models/plan.py`).
4. **Validate + save** — write your draft to a temp file and run:
   `uv run plan save-target <slug> <draft.json>`
   Fix and re-run if it reports a validation error.
5. Confirm what was captured and suggest running `generate-plan` next.

## Notes

- Don't invent numbers. If a race's elevation or distance is unconfirmed, say so and mark
  it provisional rather than guessing precisely.
- One campaign = one target. A new goal is a new slug.
