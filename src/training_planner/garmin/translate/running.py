"""Translate a running WorkoutSpec into the garminconnect library's RunningWorkout, ready
for `client.upload_running_workout(...)`.

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
    ConditionType,
    ExecutableStep,
    RunningWorkout,
    StepType,
    TargetType,
    WorkoutSegment,
)

from ...models.running import (
    HRRangeTarget,
    HRZoneTarget,
    PaceTarget,
    Repeat,
    Step,
    WorkoutSpec,
)
from .base import _assemble, _estimate

__all__ = ["RUNNING_SPORT", "spec_to_garmin"]

RUNNING_SPORT = {"sportTypeId": 1, "sportTypeKey": "running"}

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
        return step.minutes * 60.0
    if isinstance(step.target, PaceTarget):
        avg_sec_per_km = (step.target.slow_sec_per_km + step.target.fast_sec_per_km) / 2
        return step.km * avg_sec_per_km
    return (step.km * 1000.0) / _FALLBACK_SPEED_MPS


def spec_to_garmin(spec: WorkoutSpec) -> RunningWorkout:
    """Translate a running spec into a library RunningWorkout."""
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
