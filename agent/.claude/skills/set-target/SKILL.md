---
name: set-target
description: Capture a race, performance, or strength goal as a training Target for a campaign. Use when the user names something to train for (a race, a distance/time goal, or a strength goal like "first pull-up"), shares a race URL, or says "set a target/goal", "I want to train for X", "let's plan for Y".
---

# Set Target

Turn a race or goal into a validated `target.json` under `campaigns/<slug>/`, which
`generate-plan` then trains toward. A Target is a **race** or a **performance goal**
(`kind: race | performance`) — and a **strength goal** is just a performance goal whose
"performance" is a capability or body part, not a time.

## Steps

1. **Gather the target.** Ask for / infer:
   - `name` (required), `kind` (`race` or `performance`).
   - `date` — races have one; open performance goals may not (leave null).
   - `distance_km` — both usually have one (a 22 km race, a 5 km goal).
   - `elevation_gain_m`, `terrain`, `location` — for races; leave null for flat/road goals.
   - `goal` — the objective in the athlete's words ("finish strong", a target time).
   - `milestones` — the checkpoints on the way to the goal, as a **list of Milestone
     objects** (`label` required; optional `metric`, `target_date`, `achieved_on`). Order
     them earliest-first. This is a real field — **don't cram milestones into `goal` as
     prose**; put each one here so progress can be ticked off (`achieved_on`) and shown in
     `block.md`. Especially useful for open-ended strength goals (e.g. muscle-up →
     "8–10 strict pull-ups" → "chest-to-bar" → "clean transition"). Leave `[]` if there
     aren't any yet.
   - If the user gives a **race URL**, fetch the page (web) to fill in date, distance,
     elevation, terrain, location. If elevation isn't on the page, search for it. Note
     any figure that's provisional (e.g. "2025 course, ~±50 m").
   - **Strength goal** → `kind: "performance"`, `name` the objective ("First unassisted
     pull-up", "Bigger deadlift"), `goal` in the athlete's words, and leave the run fields
     (`date`, `distance_km`, `elevation_gain_m`, `terrain`) **null**. No date unless they
     want a deadline. These goals are open-ended and shift often — capture the current one;
     re-target when it changes (a new focus is a new slug).
2. **Pick a slug** — short kebab-case, e.g. `spring-half`, `city-10k`, or `first-pullup`.
3. **Draft `target.json`** matching the `Target` model (`src/training_planner/models/plan.py`).
4. **Validate + save** — write your draft to a temp file and run:
   `uv run plan save-target <slug> <draft.json>`
   Fix and re-run if it reports a validation error.
5. Confirm what was captured and suggest running `generate-plan` next.

## Notes

- Don't invent numbers. If a race's elevation or distance is unconfirmed, say so and mark
  it provisional rather than guessing precisely.
- One campaign = one target. A new goal is a new slug.
