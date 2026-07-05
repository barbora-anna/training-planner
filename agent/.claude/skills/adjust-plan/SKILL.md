---
name: adjust-plan
description: Modify an existing training block — make it harder/easier, shorter/longer, shift it after missed sessions, or regenerate from a fresh fitness snapshot or new health status. Use when the user says "make it harder", "shorten the plan", "I missed this week", "regenerate", "adjust my plan".
---

# Adjust Plan

Revise a campaign's existing `Block` in place. Each save **archives the prior version** to
`campaigns/<slug>/history/`, so adjustments are reversible.

## Steps

1. **Load the current block** — `uv run plan show <slug>`, and read
   `campaigns/<slug>/block.json` for the full detail.
2. **Understand the ask** and apply the matching change:
   - **Harder / easier** — shift intensity & quality volume (paces toward threshold/VO2 or
     back toward Z2); adjust weekly km. Keep progression sane (see `generate-plan` method).
   - **Shorter / longer** — recompute weeks; re-phase (a shorter block compresses base).
   - **Missed sessions / life** — shift the schedule forward, protect key sessions, don't
     cram lost volume into one week.
   - **Regenerate** — re-read the latest snapshot / health-status and rebuild from current
     state (this is `generate-plan`'s method on fresh inputs).
3. **Respect `health-status`** if present — injury constraints outrank the requested change.
4. **Save + validate** — draft the revised `block.json`, then
   `uv run plan save-block <slug> <draft.json>` (auto-archives prior,
   rewrites `block.md`).
5. **Show what changed** and, since workouts moved, remind the athlete to **re-run
   `/sync-garmin`** so Garmin matches.

## Notes

- Discuss the change with the athlete before committing it.
- Prior versions live in `history/` — you can always describe or restore an earlier block.
- Keep the same `<slug>`; this edits the campaign, it doesn't create a new one.
