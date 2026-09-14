# Strength training — theory & science

Reference for the Advisor: research-grounded reasoning behind strength prescriptions, with
sources so claims are checkable, not just plausible-sounding. `generate-plan` and
`adjust-plan` point here for *why*, not just *what* — apply it to the athlete in front of
you, don't recite it at them.

## Split structure & training frequency

- Each muscle group grows best trained **~2–3×/week**; hip-thrust/glute-specific work
  specifically responds well to **1–2×/week** at roughly **5–10+ effective sets/week**
  (Speediance; Bret Contreras; BUBS Naturals).
- For glute priority, an **upper/lower split beats push/pull/legs (PPL)** at the same weekly
  frequency — PPL at 3×/week gives legs only one dedicated session/week; upper/lower gives
  legs two (Outlift; Legacy Muscle; Stronger; Boostcamp).
- **Avoid two heavy lower-body days back-to-back.** When a split repeats lower-body days
  (e.g. Lower A / Lower B), **vary the lead compound** (squat-led vs. hinge-led) so each
  session hits fresh tissue rather than re-stressing the same one (Hevy).
- **48–72h** is the standard window for muscle-damage and CNS recovery after a heavy squat
  session — why this planner spaces heavy lower work rather than repeating it daily (CSEP;
  Optimum Nutrition).

## Periodization

The block's phases (base → build → peak → taper) apply to strength too:

- **Base** — moderate reps (~8–12), movement quality and consistency over load; a novice
  builds the motor patterns everything else layers on.
- **Build** — load/difficulty rises, reps trend down; total weekly stress (run + strength)
  matters more than either discipline alone.
- **Peak** — strength volume drops, intensity/quality holds; the goal is arriving at the
  target session fresh, not chasing gym PRs.
- **Taper** — load drops hard (see `generate-plan/SKILL.md` step 8); short, light sessions
  keep the pattern "on" without adding fatigue.

**Linear vs. undulating isn't a style preference — the evidence is status-dependent.** For
untrained lifters, linear and undulating periodization produce statistically equivalent
strength gains; undulating's edge only shows up in trained-lifter subgroups. For
intermediate/advanced lifters chasing maximal strength, undulating (varying rep
range/intensity session to session) meaningfully outperforms linear — pooled gains around
~24% vs. ~17–18% across studies, a medium effect size. For hypertrophy specifically,
periodization *type* barely matters in volume-equated comparisons — volume and proximity to
failure drive growth, not how it's sequenced (systematic reviews/meta-analyses via PubMed,
Frontiers, PMC). Default to **linear for novices**, switch to **undulating once
`training_status` is intermediate/advanced and progress has plateaued** — not before.

## Warm-up protocol

Heavier warm-up sets outperform a long string of light-volume ones: **2–5 warm-up sets**,
reps tapering down as load rises, stopping once the next jump would be the working set
itself (Stronger by Science; BarBend). This is why a prescription should carry a **ramp**,
not a flat working weight — an athlete's logged ramp (e.g. 20→30→40kg across 3 sets) already
reflects this protocol; flattening it in a plan erases real warm-up structure the data shows
works.

## Equipment reality check

A prescribed load must correspond to equipment that exists, not just a plausible-sounding
number. A standard barbell weighs **~15–20kg empty** — "barbell curl @ 10kg" or "barbell
shoulder press @ 17.5kg" aren't miscalibrated, they're **physically impossible**: you can't
load an empty bar to less than its own weight. Before prescribing any loaded barbell
exercise, check the number is **≥ the bar's own weight** — below that, it needs a
dumbbell/machine/cable variant, not a smaller barbell number. This is a different failure
category from calibration below (equipment feasibility, not wrong magnitude), so the full
pass has to cover both, not just one.

## Rep ranges and the hypertrophy mechanism

Hypertrophy tracks **volume accumulated close to failure**, not peak effort on a single rep:
**5–35 reps produce similar growth** when sets are taken close to failure, because growth
depends on total near-failure time-under-tension across a set, not how heavy any one rep was
(Stronger by Science). So **"hard" and "high-volume-near-failure" are not synonyms** — a
true 1-rep max-effort single can be maximally hard and still contribute almost nothing to
hypertrophy. If a goal includes size (not just moving the 1RM number), a heavy single needs
a **paired back-off set** — e.g. 2×8–10 at ~65–70% of the single, close to failure — to
actually deliver hypertrophy stimulus; the single alone doesn't, no matter the effort behind
it.

Muscle cross-sectional area is the single best predictor of raw strength, but 1RM also
depends on neural/coordination adaptations distinct from size (Nature) — part of why a
novice can add weight to the bar for weeks without visibly changing size: most of the early
gain is neural, not hypertrophy.

Practical bands, given the above — loose, not sharp lines:

| Goal | Reps | Rest | Use here |
|---|---|---|---|
| Max strength (1RM-focused) | 1–5 | 2–4 min | Rare here — only advanced athletes with a known 1RM and an explicit strength goal; pair with a back-off set if size matters too |
| Hypertrophy / general strength | 6–12 | 60–120s | Default band for runner-support work — time-efficient and joint-friendly within the wider 5–35 rep window that works |
| Muscular endurance / stability | 12–20+ | 30–60s | Bodyweight/core/stability work — most novice prescriptions land here |

Since `weight_kg` defaults unset, rep range plus RIR/RPE (below) is the real intensity lever
here, not a kg number.

## Autoregulation (RPE / RIR)

RPE/RIR-based prescription is validated, not just a convenient placeholder for an unset
weight: it's **equally effective or superior to percentage-of-1RM** prescription for both
strength and hypertrophy (systematic reviews/meta-analyses via PMC, ScienceDirect).
Reliability is highest in lifters with real training experience working close to failure in
moderate-to-low rep sets — so the base-phase novice default here should sit at **lower RPE
(5–7)**, leaving reps in reserve while movement patterns groove, before build/peak pushes
closer to **RPE 8**.

## Frequency exceptions: skill-loaded compounds

The 1–2×/week default below is right for accessory/hypertrophy work, but **skill-loaded
competition lifts are the exception** — bench press has the cleanest dose-response data: a
6-week study found **22% strength improvement at 2×/week vs. 30% at 3×/week** (BarBend;
PMC), with frequency benefits continuing to scale up to ~3×/week. The mechanism is
**neural/motor-pattern practice**, not extra muscle recovery capacity — the same reason a
novice's early gains are mostly neural (above). Treat competition-style/skill-heavy lifts
(barbell squat, bench, deadlift, when explicitly the target) as their own frequency case,
the way plyometrics already gets its own case below — don't flatten them to the general
default.

## Recovery and the interference effect (for runners)

Strength adaptation happens during recovery, not the session — hence the 48–72h spacing
above. For a runner, strength is layered on top of running as a second stressor, and the
interference is real but **modality- and dose-dependent**, not fixed: resistance training
combined with **running** specifically shows measurable strength/hypertrophy decrements that
combining with **cycling** doesn't, and the size of the effect scales with the **frequency
and duration of the endurance training**, not just its presence (meta-analyses via PubMed,
Sports Medicine/Springer). Separating a hard run and a hard lift by **at least ~6 hours**
measurably reduces the acute interference on running economy (systematic review/
meta-analysis, PMC) — same-day is recoverable if spaced, back-to-back is not. This is why
`generate-plan/SKILL.md` protects the day before a key run (easy or rest, no heavy legs);
total combined load, not either discipline's volume alone, determines recovery.

## Exercise selection for runners

- **Posterior chain** (glutes, hamstrings, calves) — the primary force-producers in running
  gait, commonly under-trained relative to quads in people who mostly run and sit.
- **Unilateral work** — the postural/pelvic-control and injury-prevention case is solid
  (single-leg work trains stabilizers a bilateral lift doesn't touch, exposing side-to-side
  imbalances). The direct-transfer-to-running-economy evidence is thinner and mostly comes
  from sprint research, where unilateral/horizontal-plane work transfers because sprinting
  itself is unilateral and horizontal — don't overstate distance-running transfer beyond the
  stability/imbalance rationale.
- **Plyometrics** — effects on running economy are real but modest and pace-dependent:
  meta-analyses find a *trivial* overall effect but a *small* improvement at speeds
  ≤12km/h, versus heavy resistance training showing a small effect skewed toward *faster*
  paces; either way **at least 8 weeks** of training is needed before an effect shows
  (systematic reviews/meta-analyses, PMC). High-impact and technically demanding — reserve
  for intermediate/advanced athletes with a strength base, introduce gradually, drop first in
  a deload or injury.
- **Core / anti-rotation** (planks, dead bugs, Pallof presses) — low fatigue-cost, safe to
  include often; running posture degrades under fatigue without trunk control.
- **Shoulder/upper accessory health** — e.g. face pulls: **8–20 reps** is the effective band,
  with **3×12–15** specifically called out for shoulder health (RP Strength; StrengthLog) —
  a concrete example that "accessory" doesn't mean "arbitrary rep count."

## Nutrition for strength & hypertrophy

- **Protein**: benefit plateaus around **~1.6g/kg/day** for hypertrophy, **1.5–2.0g/kg/day**
  for strength — more doesn't keep helping past that (Examine.com; PMC meta-analysis).
- **Surplus for a lean bulk**: **+200–300 kcal/day** is the evidence-based target for
  already-trained lifters — not the larger surpluses often recommended for novices or common
  online folklore (Micron).
- **Creatine**: dose by bodyweight, **~0.1g/kg/day**, not the flat 5g population default,
  which under- or over-doses depending on the athlete's size; dose doesn't differ by sex
  despite women having lower natural creatine stores (BUBS Naturals; PMC).

## Calibrating weight to logged history, not to a guess

If the athlete has real strength history (Strava sessions, prior plans), a prescribed weight
is a **data lookup, not an estimate**. Before writing a weight into a plan:

- **Do one full pass across every loaded exercise before showing the plan** — not a reactive
  patch after each thing the athlete flags. If one exercise is missing its ramp or fails the
  equipment check above, re-check *every* exercise for the same class of mistake, not just
  the one named.
- **Use the athlete's actual top logged sets**, not a fraction "to be safe" — that's a
  different, legitimate call (e.g. deliberately backing off for a base phase) and should be
  stated as such, not presented as their real number.
- **Prefer the athlete's stated number over a literal Strava read when they conflict.**
  Strava under-logs load for some equipment (cable stacks, plate-loaded machines,
  attachments) — a 0kg or missing weight doesn't mean bodyweight. Ask rather than picking
  either the literal log value or a fresh guess when a number looks implausible.
- **Carry ramping sets** (see warm-up protocol above) instead of flattening to one number.
- **Cross-reference the full recurring exercise list** — an exercise the athlete does
  regularly shouldn't drop from the plan because it wasn't top-of-mind; check history before
  finalizing selection, not just intensity.

## One true max effort per session

A session should carry at most one true near-ceiling effort — "near-ceiling" means any
exercise loaded at or close to the athlete's current top, whether or not it's formally a max
test. Stacking several near-ceiling lifts in one session produces the same accumulated
fatigue as stacking two formal maxes — damage is additive across exercises, not reset by
switching lifts. When multiple exercises in a session are candidates for a ceiling push, pick
**one** to lead and deliberately back the others off (lower volume, a rep or two below
failure, or hold at last known best). When two exercises are both due for a progression test,
spread them across different sessions/days.

## The week is a loop, not a line

A weekly template reads left-to-right, but the schedule repeats — the last day of one week is
immediately followed by the first day of the next, with the same rest-window rules applying
across that seam as mid-week. When checking spacing between heavy lower-body (or any
high-fatigue) sessions, explicitly check the **wrap-around pair** (e.g. Sunday → Monday), not
just sessions adjacent within the printed week — a back-to-back pair hiding across the week
boundary is easy to miss precisely because it doesn't look adjacent on the page. If the
athlete's fixed schedule can't separate that pair with a rest day, the lever is intensity
discipline on both sides of the seam (one true max effort per session, above), not skipping
the check.

## Calibrating to the athlete

`training_status` + `strength_baseline` (from `athlete/profile.json`) decide **where on
these scales** an athlete starts — not whether the theory applies:

- **Untrained/novice** — bilateral before unilateral, bodyweight before loaded, higher reps
  (12–15+) at low RPE, linear progression, no plyometrics yet.
- **Intermediate** — unilateral and eccentric work enters, undulating periodization becomes
  useful (see Periodization above), moderate plyometrics if healthy, reps trend toward the
  6–12 hypertrophy band.
- **Advanced** — heavier relative intensity, more varied periodization, higher training
  density; still capped by the interference effect with running volume.

## Injury & return-to-training

When `health-status.json` is present, physiology still applies but risk tolerance flips:
regress the exercise (fewer joints/less range before less weight), keep reps toward the
higher-rep/lower-RPE end, and reintroduce plyometrics and eccentric loading **last**. This
isn't caution for its own sake: tendon adaptation genuinely lags muscle — strength and muscle
size can shift within weeks of training, while tendon material properties change over
**months**, because tendon tissue turns over slower (research via PMC, Wiley/Scandinavian
Journal of Medicine & Science in Sports). A "feels fine" green light from soft tissue doesn't
mean tendon capacity has caught up yet.
