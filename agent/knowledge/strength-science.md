# Strength training — theory & science

Reference for the Advisor: research-grounded reasoning behind strength prescriptions, with
sources so claims are checkable, not just plausible-sounding. `generate-plan` and
`adjust-plan` point here for *why*, not just *what* — apply it to the athlete in front of
you, don't recite it at them.

## Split structure & training frequency

- Each muscle group grows best trained **~2–3×/week**. Popular glute-training sources put
  hip-thrust-specific work at **1–2×/week, ~5–10+ effective sets/week** (Speediance; Bret
  Contreras; BUBS Naturals) — treat that as a *floor*, not a target. The dose-response
  meta-regression data (see *The hypertrophy hierarchy*) supports **10–20 hard sets per
  muscle per week** for a priority muscle, counting every exercise that trains it, not just
  the signature lift. Frequency mostly matters as a way to *fit* that volume in with enough
  rest between sets; it is not an independent lever of its own.
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
**5–35 reps produce similar growth** when sets are taken close to failure (Schoenfeld et al.
2017, 21-study meta-analysis: 8.3% vs 7.0% gains for high- vs low-load, not significantly
different), because growth depends on near-failure effort across the set, not how heavy any
one rep was. So **"hard" and "high-volume-near-failure" are not synonyms** — a true 1-rep
max-effort single can be maximally hard and still contribute almost nothing to hypertrophy.
If a goal includes size (not just moving the 1RM number), a heavy single needs **paired
back-off sets** to deliver the stimulus; the single alone doesn't, no matter the effort
behind it.

**Prescribe back-offs by proximity to failure, not by a percentage of the top set.** Because
load is close to irrelevant within 5–35 reps, the percentage is the *wrong* control variable
— the thing that must be true is that the set finishes at **1–2 RIR**. Pick the load that
lands there in a rep count the athlete will actually complete (commonly ~70–80% of 1RM for
8–12 reps), then progress by **double progression**: hold the load, add reps across sessions
until the top of the range is hit at 2 RIR on every set, then add load and drop back down.

⚠️ **Check that the prescribed load and the prescribed RIR are compatible.** Writing
"10 reps @ 100kg, RPE 9" for an athlete whose 1RM is ~154kg is self-contradictory: 100kg is
65% of max, which is a ~15–20-rep load, so ten reps lands nowhere near RPE 9 — the athlete
obeys the number and gets the wrong stimulus. Whenever a prescription carries **both** a load
and an RIR/RPE target, sanity-check them against the athlete's estimated rep-max at that
load before writing it down. A mismatch here is silent: the session looks completed, the
adherence looks perfect, and the stimulus was never delivered.

Muscle cross-sectional area is the single best predictor of raw strength, but 1RM also
depends on neural/coordination adaptations distinct from size (Nature) — part of why a
novice can add weight to the bar for weeks without visibly changing size: most of the early
gain is neural, not hypertrophy.

Practical bands, given the above — loose, not sharp lines:

| Goal | Reps | Rest | Use here |
|---|---|---|---|
| Max strength (1RM-focused) | 1–5 | 3–5 min | Rare here — only advanced athletes with a known 1RM and an explicit strength goal; pair with back-off sets if size matters too |
| Hypertrophy / general strength | 6–12 | **2–3 min** | Default band for runner-support work. Note the rest figure — see *Rest intervals* below; the old "60–90s for hypertrophy" advice is wrong |
| Muscular endurance / stability | 12–20+ | 60–90s | Bodyweight/core/stability work — most novice prescriptions land here |

Since `weight_kg` defaults unset, rep range plus RIR/RPE (below) is the real intensity lever
here, not a kg number.

## The hypertrophy hierarchy — what actually drives growth

When an athlete asks "how do I grow this muscle fastest", the
levers are **not** equally weighted. Ranked by strength of evidence and size of effect:

**1. Weekly volume — hard sets per muscle. The strongest, most reliable lever.**
The Pelland et al. dose-response meta-regression (67 studies, 2,058 participants) found a
clear monotonic relationship: more weekly sets → more growth, with a **posterior probability
of ~100%** that the effect exceeds zero. Around the average weekly volume of ~12 sets, each
additional set was worth roughly **+0.24% hypertrophy**. Returns diminish as volume climbs
**but never reverse** within the studied range. Practical band: **10–20 hard sets per muscle
per week**, biased to the upper end for a priority muscle.

**2. Proximity to failure — real, but it plateaus early and cheaply.**
Refalo et al. (2022), 15 studies: training to set failure beat non-failure by an effect size
of **0.19 (95% CI 0.00–0.37)** — formally "trivial", with the confidence interval touching
zero. For *momentary* muscular failure specifically there was **no** advantage at all. The
2024 meta-regressions confirm hypertrophy rises as RIR falls, but the curve flattens: **1–2
RIR is indistinguishable from true failure**, while costing far less fatigue.

> **Corollary that matters when someone says "every set must go to failure":** failure is
> not the lever they think it is. Trading *sets* (lever 1, large and certain) for *failure*
> (lever 2, trivial and uncertain) moves an athlete backwards. Doing a second hard set is
> never evidence that the first one was too easy — recovering between sets is the design.

**3. Load / rep range — close to irrelevant, given equal effort.**
See the section above. **5–35 reps grow muscle equally** when sets are near failure. Load is
the lever for **strength and neural skill**, not for size. This is what lets a hypertrophy
back-off be prescribed by RIR instead of by percentage.

**4. Rest intervals — small but free.** See below.

**5. Exercise selection — matters less than the internet claims.** See below.

**6. Periodization scheme — negligible for hypertrophy specifically.** Already covered under
*Periodization*: in volume-equated comparisons, scheme type barely moves size. It matters for
*strength*, in trained lifters.

**When an athlete's growth stalls, audit in that order.** The near-universal real answer is
lever 1 or 2 — not enough hard sets, or sets ending far from failure — not exercise choice,
which is where most gym advice starts.

## Rest intervals

Counterintuitive and worth stating explicitly, because the folklore is backwards: **short
rests cost you growth.** Schoenfeld et al. (2016), trained men, identical sets and reps
across 8 weeks — **3-minute rests produced significantly more strength *and* more muscle
thickness than 1-minute rests.** A 2024 Bayesian meta-analysis confirms a hypertrophic
benefit for rests longer than 60s.

The mechanism is not mysterious and it points straight back to lever 1: with longer rest you
hold more reps and more load on later sets, so you accumulate **more effective volume** from
the same number of sets. Short rests generate more burn and less muscle.

Practical: **2–3 minutes between hypertrophy sets**, 3–5 before a genuine near-ceiling
attempt. The only good reasons to compress rest are time constraints and conditioning goals
— neither is a hypertrophy reason, and both should be named as the trade-off they are.

## Muscle length, ROM, and exercise selection for hypertrophy

**EMG does not predict growth.** This is the single most-abused number in glute training.
The barbell hip thrust produces roughly **double** the gluteus maximus EMG of a back squat
(mean 69.5% vs 29.4% upper glute; 86.8% vs 45.4% lower glute). And yet Plotkin et al. (2023)
trained the two head-to-head and measured by MRI: **hip thrust and back squat produced
equivalent glute hypertrophy** — upper, middle, lower and total — and transferred equally to
the deadlift. There were **no consistent correlations** between EMG and actual growth.
Activation tells you a muscle is working; it does not tell you it will grow more.

**Training at long muscle lengths is the selection variable that does hold up.** The Wolf et
al. meta-analysis found full ROM superior to partial ROM overall, but the effect is mediated
by *where* in the range the work happens: **long-muscle-length training beats short-muscle-
length training**, and lengthened partials perform comparably to full ROM. Emphasising the
**stretched position** is the thing that matters — whether via full ROM or lengthened
partials is a detail.

**This has a sharp consequence for hip-thrust-centric glute training.** The hip thrust loads
the glute hardest at **peak contraction** (hips locked out, glute shortest) and unloads it in
the stretched position at the bottom — it is a **short-position-biased** exercise. It is an
excellent strength and peak-contraction lift, and a *one-sided* hypertrophy stimulus. A glute
programme built only on hip thrusts trains half the length curve.

So for a glute-hypertrophy goal, deliberately pair the two:

| Position bias | Exercises | Role |
|---|---|---|
| **Shortened / peak contraction** | Barbell hip thrust, glute bridge, cable kickback, hip abduction | Peak tension, heavy loadable, the 1RM-specific lift |
| **Lengthened / stretch** | Romanian deadlift, deep squat, 45° back extension, split squat, good morning | Stretch-mediated growth — the half the hip thrust misses |

Programme **both**, and count both toward weekly glute volume. Adding a third hip-thrust
variation is a worse use of a set than adding the first real lengthened-position movement.

## Autoregulation (RPE / RIR)

**RIR = Reps In Reserve: how many more reps the athlete could have done when they racked the
set.** 0 RIR is momentary failure; 2 RIR means two left in the tank. RPE is the same scale
inverted, and the two are used interchangeably here:

| RIR | RPE | Meaning |
|---|---|---|
| 0 | 10 | Failure — could not complete another rep |
| 1 | 9 | One more, and it would have been a grind |
| 2 | 8 | Two more — the working target for most hypertrophy sets |
| 3–4 | 6–7 | Comfortably short; fine for technique/base work, thin stimulus for growth |
| 5+ | ≤5 | Warm-up territory — not a working set |

RPE/RIR-based prescription is validated, not just a convenient placeholder for an unset
weight: it's **equally effective or superior to percentage-of-1RM** prescription for both
strength and hypertrophy (systematic reviews/meta-analyses via PMC, ScienceDirect). It is
also the *right* control variable for hypertrophy specifically, because load is nearly
irrelevant across 5–35 reps (see *The hypertrophy hierarchy*) while proximity to failure is
not. Base-phase novices sit at **RPE 5–7** while patterns groove; build/peak pushes to
**RPE 8**.

### Self-reported RIR is biased, and the bias is one-directional

Athletes **under**-predict how many reps they have left — they think they are closer to
failure than they are. Magnitude depends on experience: **experienced lifters under-predict
by ~1–2 reps; inexperienced lifters by ~4–5** (Steele et al.). Newer work in
resistance-trained individuals finds accuracy is decent *near* failure (mean error ~0.65
reps) and that it improves with practice — so don't overstate the problem for a trained
athlete. Two things stay reliably true:

- **The error grows the further from failure the set ends.** An estimate at 1 RIR is roughly
  trustworthy; an estimate at 5 RIR is close to a guess.
- **It always errs the same way.** A set logged as "hard" is, more often than not, easier
  than it felt.

**Practical consequence for prescriptions:** when an athlete reports hitting a target rep
count comfortably, treat that as evidence the load was too light, not as evidence they are
strong. And expect a prescription of "1–2 RIR" to be *executed* nearer 2–3 RIR.

### Calibrating an athlete's RIR sense

The fix is cheap and worth doing once per lift, then occasionally: **take one back-off set
to genuine momentary failure and count the reps past the point they'd normally stop.** That
single data point recalibrates their internal scale for months and converts RIR from a vibe
into a measurement. Do it on a back-off/accessory set — never on a near-ceiling compound,
where failure carries real technique and injury cost, and never on a day that precedes a
key session (the fatigue is genuine). This is the one legitimate use of training to failure
in a programme built on 1–2 RIR: **as a measuring instrument, not as a stimulus.**

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

## Sources — hypertrophy evidence base

Checkable references for *The hypertrophy hierarchy*, *Rest intervals*, *Muscle length, ROM,
and exercise selection*, and the back-off guidance under *Rep ranges*.

| Claim | Source |
|---|---|
| Volume dose-response; ~+0.24%/set at ~12 sets/wk; diminishing but non-reversing returns | Pelland et al., *The Resistance Training Dose Response* — <https://pubmed.ncbi.nlm.nih.gov/41343037/> |
| Earlier volume dose-response (10+ sets/wk > 5–9 > <5) | Schoenfeld et al. 2016 — <https://pubmed.ncbi.nlm.nih.gov/27433992/> |
| Failure vs non-failure: ES 0.19 (95% CI 0.00–0.37); no advantage for momentary failure | Refalo et al. 2022 — <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9935748/> |
| Proximity-to-failure dose-response meta-regressions; hypertrophy rises as RIR falls, strength does not | Robinson et al. 2024 — <https://pubmed.ncbi.nlm.nih.gov/38970765/> |
| 5–35 reps equivalent for growth when near failure (8.3% vs 7.0%) | Schoenfeld et al. 2017 — <https://journals.lww.com/nsca-jscr/fulltext/2017/12000/strength_and_hypertrophy_adaptations_between_low_.31.aspx> |
| Repetition continuum re-examined | Schoenfeld, Grgic et al. — <https://pmc.ncbi.nlm.nih.gov/articles/PMC7927075/> |
| 3-min rest > 1-min rest for strength and hypertrophy in trained men | Schoenfeld et al. 2016 — <https://brookbushinstitute.com/articles/longer-interset-rest-periods-enhance-muscle-strength-hypertrophy-resistance-trained-men> |
| Hip thrust vs back squat: equal glute hypertrophy by MRI despite EMG gap; EMG does not predict growth | Plotkin et al. 2023 — <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10593473/> |
| Hip thrust vs squat glute EMG magnitudes | Contreras et al. — <https://bretcontreras.com/squats-versus-hip-thrusts-emg-activity/> |
| RIR under-prediction: ~1–2 reps (experienced), ~4–5 (inexperienced); error grows with distance from failure | Steele et al. — <https://www.researchgate.net/publication/321395253_Ability_to_predict_repetitions_to_momentary_failure_is_not_perfectly_accurate_though_improves_with_resistance_training_experience> |
| RIR estimation accuracy in resistance-trained individuals (mean error ~0.65 reps), improves with training | Refalo et al. — <https://onlinelibrary.wiley.com/doi/full/10.1002/ejsc.12266> |
| Full ROM ≥ partial ROM; long-muscle-length training superior; lengthened partials ≈ full ROM | Wolf et al. meta-analysis; Kassiano et al. 2025 — <https://pubmed.ncbi.nlm.nih.gov/39959841/>, <https://www.strongerbyscience.com/stretch-mediated-hypertrophy/> |
