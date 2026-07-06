# Training Planner

An agent-driven running training planner that runs **inside Claude Code**.

- **Live data** — Claude reads your training history directly via the Strava MCP.
- **Plans live in `agent/campaigns/<slug>/`** (`block.json` machine contract + `block.md` for review); athlete state lives in `agent/athlete/`. Edit by hand anytime. Your personal data is gitignored.
- **Garmin sync** — the `training-planner` package (`src/training_planner/`) pushes structured workouts to Garmin Connect and schedules them, via the unofficial [`python-garminconnect`](https://github.com/cyberjunky/python-garminconnect) library.
- **Skills** in `agent/.claude/skills/` drive each step. Run `./train` to start the **Fitness Advisor** (it signs you into Garmin first, then launches Claude in `agent/`); run Claude from the repo root for the **Coding Agent** that builds the tool.

## Running

You need [Claude Code](https://claude.com/claude-code) installed (`claude` on your PATH)
and deps synced (`uv sync`, see [Setup](#setup)). Then, from the repo root:

```
./train
```

This signs you into Garmin if needed, then launches Claude Code inside `agent/` as the
**Fitness Advisor**. From there just talk to it — ask it to assess your fitness, set a
goal, or plan a run — and it drives the skills (`/assess-fitness`, `/set-target`,
`/generate-plan`, `/sync-garmin`, `/adjust-plan`). Prefer to launch it yourself?
`cd agent && claude` does the same, minus the Garmin sign-in step.

Any arguments you pass to `./train` are forwarded straight through to `claude`, so you can
use the usual flags — e.g. `./train -c` to continue the last session, or `./train --resume`
to pick one to resume.

You log in at **your own terminal, before Claude starts** — so your Garmin credentials
never pass through the agent. During a session the agent only *resumes* the cached token;
if it ever expires, the agent stops and asks you to re-run `./train`.

> To work on the tool itself instead, run `claude` from the **repo root** — that's the
> Coding Agent (this file's sibling, `CLAUDE.md`).

## Workflow

1. **`assess-fitness`** — analyze Strava → `agent/athlete/` (profile + dated snapshot)
2. **`set-target`** — a race or performance goal → `agent/campaigns/<slug>/target.json`
3. **`generate-plan`** — target + fitness → periodized `block.json` / `block.md`
4. **review & edit** the plan files
5. **`sync-garmin`** — push run workouts to Garmin Connect (explicit; review before confirming)
6. **`review-progress`** — adherence vs Strava actuals + trend reflection (the advisor also does this at the start of each session)
7. **`adjust-plan`** — regenerate / make harder / shorten the block → re-sync

No goal yet? The advisor can also plan a **single run** tailored to your current fitness,
without a campaign.

## Project layout

```
train                     launcher: sign in to Garmin, then start the advisor
CLAUDE.md                 Coding Agent instructions (repo root)

agent/                    the Fitness Advisor — run Claude here
  CLAUDE.md                 advisor persona (discuss & plan; never writes code)
  .claude/skills/           assess-fitness · set-target · generate-plan · review-progress · adjust-plan · sync-garmin
  athlete/                  your state: profile.json, fitness-snapshots/, health-status.json  (gitignored)
  campaigns/<slug>/         per-goal plans: target.json, block.json, block.md                (gitignored)

src/training_planner/     the installable package (the Coding Agent maintains this)
  models/                   domain contracts: workout · plan · athlete
  storage.py                file-backed repositories (swappable behind one interface)
  garmin/                   client (auth) · translate (spec → Garmin) · library (push / schedule)
  cli/                      console scripts: plan · workouts · garmin-login
```

Data flows in one direction: **`models` (contracts) → `storage` (persistence) / `garmin`
(integration) → `cli` (entry points)**. The models know nothing about Garmin or files.

## Setup

- **Python ≥ 3.14**, managed with [`uv`](https://docs.astral.sh/uv/). Install deps:

  ```
  uv sync          # installs garminconnect[workout] + python-dotenv
  ```

- **Garmin auth — password-free.** `./train` signs you in when needed; to do it manually:

  ```
  uv run garmin-login
  ```

  It resumes an existing session, or prompts for your email, password (hidden), and an MFA
  code if needed — **none of which is written to disk**, only a session token cached to
  `~/.garminconnect/`. Everything afterward resumes from that token. Optionally set
  `GARMIN_EMAIL` in `.env` (gitignored) to prefill the prompt; see `.env.example`.

- **Strava** is read live via the Strava MCP — no setup beyond having the MCP connected.

## Tests

The package logic — models, translation, storage, the Garmin library, and auth — is covered
by a fast, fully **offline** test suite (no network, no Garmin/Strava calls):

```
uv run pytest
```

Tests live in `tests/`; `pytest` is a dev dependency, installed by `uv sync`.
