"""Layer 2 — translate a validated WorkoutSpec into the garminconnect library's
RunningWorkout, ready for `client.upload_running_workout(...)`.

The spec (models/workout.py) is athlete-facing and Garmin-agnostic; this module owns all
Garmin encoding. The library's models give a second, structural validation pass.

Target encoding (verified against Garmin's schema):
- pace     -> targetType pace.zone (id 6); targetValueOne/Two = speed in m/s
             (One = lower speed / slower pace, Two = higher speed / faster pace — ascending)
- hr_zone  -> targetType heart.rate.zone (id 4); zoneNumber = 1..5 (no value fields)
- hr_range -> targetType heart.rate.zone (id 4); targetValueOne/Two = bpm (low, high)

`ExecutableStep` has `model_config = {'extra': 'allow'}`, so targetValueOne/Two and
zoneNumber serialize through `to_dict()` even though they aren't declared fields.
"""

from __future__ import annotations

from garminconnect.workout import (
    BaseWorkout,
    ConditionType,
    ExecutableStep,
    RunningWorkout,
    StepType,
    TargetType,
    WorkoutSegment,
    create_repeat_group,
)

from ..models.workout import (
    HRRangeTarget,
    HRZoneTarget,
    PaceTarget,
    Repeat,
    RestStep,
    Step,
    StrengthSet,
    StrengthStep,
    StrengthWorkoutSpec,
    WorkoutSpec,
)

RUNNING_SPORT = {"sportTypeId": 1, "sportTypeKey": "running"}
STRENGTH_SPORT = {"sportTypeId": 5, "sportTypeKey": "strength_training"}

# step kind -> (stepTypeId, displayOrder)
_STEP_TYPES = {
    "warmup": (StepType.WARMUP, 1),
    "cooldown": (StepType.COOLDOWN, 2),
    "interval": (StepType.INTERVAL, 3),
    "recovery": (StepType.RECOVERY, 4),
    "rest": (StepType.REST, 5),
}

_NO_TARGET = {
    "workoutTargetTypeId": TargetType.NO_TARGET,
    "workoutTargetTypeKey": "no.target",
    "displayOrder": 1,
}
_PACE_TARGET = {
    "workoutTargetTypeId": TargetType.PACE_ZONE,
    "workoutTargetTypeKey": "pace.zone",
    "displayOrder": 6,
}
_HR_TARGET = {
    "workoutTargetTypeId": TargetType.HEART_RATE_ZONE,
    "workoutTargetTypeKey": "heart.rate.zone",
    "displayOrder": 4,
}

# Fallback pace (~6:10/km) for estimating a distance step's duration
_FALLBACK_SPEED_MPS = 2.7


def _speed_mps(sec_per_km: int) -> float:
    return round(1000.0 / sec_per_km, 3)


def _target_fields(target) -> dict:
    """Return the Garmin step fields for a spec target (targetType + values/zone)."""
    if target is None:
        return {"targetType": _NO_TARGET}
    if isinstance(target, PaceTarget):
        return {
            "targetType": _PACE_TARGET,
            "targetValueOne": _speed_mps(target.slow_sec_per_km),  # lower speed
            "targetValueTwo": _speed_mps(target.fast_sec_per_km),  # higher speed
        }
    if isinstance(target, HRZoneTarget):
        return {"targetType": _HR_TARGET, "zoneNumber": target.zone}
    if isinstance(target, HRRangeTarget):
        return {
            "targetType": _HR_TARGET,
            "targetValueOne": target.low_bpm,
            "targetValueTwo": target.high_bpm,
        }
    raise TypeError(f"unsupported target type: {type(target).__name__}")


def _exec_step(step: Step, order: int) -> ExecutableStep:
    step_type_id, display_order = _STEP_TYPES[step.kind]
    if step.minutes is not None:
        end = {"conditionTypeId": ConditionType.TIME, "conditionTypeKey": "time",
               "displayOrder": 2, "displayable": True}
        value = float(step.minutes) * 60.0
    else:
        end = {"conditionTypeId": ConditionType.DISTANCE, "conditionTypeKey": "distance",
               "displayOrder": 2, "displayable": True}
        value = float(step.km) * 1000.0
    return ExecutableStep(
        stepOrder=order,
        stepType={"stepTypeId": step_type_id, "stepTypeKey": step.kind, "displayOrder": display_order},
        endCondition=end,
        endConditionValue=value,
        **_target_fields(step.target),
    )


def _step_seconds(step: Step) -> float:
    """Estimated duration of a step, in seconds (feeds the workout's display estimate)."""
    if step.minutes is not None:
        return step.minutes * 60.0                       # time step: exact
    if isinstance(step.target, PaceTarget):              # distance step w/ pace: derive it
        avg_sec_per_km = (step.target.slow_sec_per_km + step.target.fast_sec_per_km) / 2
        return step.km * avg_sec_per_km
    return (step.km * 1000.0) / _FALLBACK_SPEED_MPS      # distance step, no pace: rough guess


# Shared spec-walking skeleton — running and strength differ only in the group class
# (Repeat / StrengthSet, both `.times` + `.steps`) and the per-step builder / duration fn,
# so the ordering bookkeeping and rollup live here once.

def _assemble(elements: list, group_cls, build_child) -> list:
    """Walk spec elements into ordered Garmin steps, numbering repeat groups + children."""
    steps: list = []
    order = 1
    for el in elements:
        if isinstance(el, group_cls):
            group_order = order  # the repeat group is numbered before its children
            order += 1
            children = []
            for s in el.steps:
                children.append(build_child(s, order))
                order += 1
            steps.append(create_repeat_group(el.times, children, group_order))
        else:
            steps.append(build_child(el, order))
            order += 1
    return steps


def _estimate(elements: list, group_cls, step_seconds) -> int:
    total = 0.0
    for el in elements:
        if isinstance(el, group_cls):
            total += el.times * sum(step_seconds(s) for s in el.steps)
        else:
            total += step_seconds(el)
    return int(total)


def spec_to_garmin(spec: WorkoutSpec) -> RunningWorkout:
    """Translate a validated WorkoutSpec into a library RunningWorkout."""
    workout_steps = _assemble(spec.steps, Repeat, _exec_step)
    segment = WorkoutSegment(segmentOrder=1, sportType=RUNNING_SPORT, workoutSteps=workout_steps)
    kwargs = {
        "workoutName": spec.name,
        "sportType": RUNNING_SPORT,
        "estimatedDurationInSecs": _estimate(spec.steps, Repeat, _step_seconds),
        "workoutSegments": [segment],
    }
    if spec.description:
        kwargs["description"] = spec.description
    return RunningWorkout(**kwargs)


# --------------------------------------------------------------------------- #
# Strength — there is no library StrengthWorkout class, so we assemble the same
# BaseWorkout structure and inject Garmin's strength fields (category / exerciseName /
# weightValue + weightUnit) via ExecutableStep's `extra: "allow"`, exactly as the running
# path injects pace/HR targets. Weight travels as a value+unit pair (kg + _KG_UNIT) —
# Garmin drops a bare weightValue on save. Result is a dict for upload_workout().
# --------------------------------------------------------------------------- #

_NO_TARGET_FIELDS = {"targetType": _NO_TARGET}
_SECONDS_PER_REP = 3.0            # rough, for the display duration estimate only

# Garmin's weight unit descriptor. `weightValue` is the display value in this unit
# (kilograms); `factor` is how Garmin reaches its internal grams (kg × 1000). Without
# this object Garmin silently drops `weightValue` on save — the weight must travel as a
# value+unit pair, exactly like a pace/HR target carries its targetType.
_KG_UNIT = {"unitId": 8, "unitKey": "kilogram", "factor": 1000.0}


def _reps_condition(reps: int) -> tuple[dict, float]:
    end = {"conditionTypeId": ConditionType.REPS, "conditionTypeKey": "reps",
           "displayOrder": 10, "displayable": True}
    return end, float(reps)


def _time_condition(seconds: float) -> tuple[dict, float]:
    end = {"conditionTypeId": ConditionType.TIME, "conditionTypeKey": "time",
           "displayOrder": 2, "displayable": True}
    return end, float(seconds)


def _strength_exec_step(step: StrengthStep, order: int) -> ExecutableStep:
    end, value = (_reps_condition(step.reps) if step.reps is not None
                  else _time_condition(step.seconds))
    fields = {"category": step.exercise.category, **_NO_TARGET_FIELDS}
    if step.exercise.name is not None:
        fields["exerciseName"] = step.exercise.name
    if step.weight_kg is not None:
        fields["weightValue"] = float(step.weight_kg)            # kg; _KG_UNIT.factor -> grams
        fields["weightUnit"] = _KG_UNIT
    return ExecutableStep(
        stepOrder=order,
        stepType={"stepTypeId": StepType.MAIN, "stepTypeKey": "main", "displayOrder": 8},
        endCondition=end,
        endConditionValue=value,
        **fields,
    )


def _rest_exec_step(step: RestStep, order: int) -> ExecutableStep:
    end, value = _time_condition(step.seconds)
    return ExecutableStep(
        stepOrder=order,
        stepType={"stepTypeId": StepType.REST, "stepTypeKey": "rest", "displayOrder": 5},
        endCondition=end,
        endConditionValue=value,
        **_NO_TARGET_FIELDS,
    )


def _strength_child(step, order: int) -> ExecutableStep:
    return (_rest_exec_step(step, order) if isinstance(step, RestStep)
            else _strength_exec_step(step, order))


def _strength_step_seconds(step) -> float:
    if isinstance(step, RestStep):
        return step.seconds
    if step.seconds is not None:
        return step.seconds
    return step.reps * _SECONDS_PER_REP


def strength_spec_to_garmin(spec: StrengthWorkoutSpec) -> dict:
    """Translate a validated StrengthWorkoutSpec into the dict `upload_workout` wants."""
    workout_steps = _assemble(spec.steps, StrengthSet, _strength_child)
    segment = WorkoutSegment(segmentOrder=1, sportType=STRENGTH_SPORT,
                             workoutSteps=workout_steps)
    kwargs = {
        "workoutName": spec.name,
        "sportType": STRENGTH_SPORT,
        "estimatedDurationInSecs": _estimate(spec.steps, StrengthSet, _strength_step_seconds),
        "workoutSegments": [segment],
    }
    if spec.description:
        kwargs["description"] = spec.description
    return BaseWorkout(**kwargs).to_dict()
