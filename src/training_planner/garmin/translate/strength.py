"""Translate a StrengthWorkoutSpec into the dict `upload_workout()` wants.

There is no library StrengthWorkout class, so we assemble the same BaseWorkout structure
as the running path and inject Garmin's strength fields (category / exerciseName /
weightValue + weightUnit) via ExecutableStep's `extra: "allow"`, exactly as the running
path injects pace/HR targets.
"""

from __future__ import annotations

from garminconnect.workout import (
    BaseWorkout,
    ConditionType,
    ExecutableStep,
    StepType,
    WorkoutSegment,
)

from ...models.strength import (
    RestStep,
    StrengthSet,
    StrengthStep,
    StrengthWorkoutSpec,
)
from .base import _assemble, _estimate
from .running import _NO_TARGET

__all__ = ["STRENGTH_SPORT", "strength_spec_to_garmin"]

STRENGTH_SPORT = {"sportTypeId": 5, "sportTypeKey": "strength_training"}

_NO_TARGET_FIELDS = {"targetType": _NO_TARGET}
_SECONDS_PER_REP = 3.0            # rough, for the display duration estimate only

# Garmin's weight unit descriptor.
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
        fields["weightValue"] = float(step.weight_kg)
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
    """Translate a strength spec into the dict `upload_workout()` wants."""
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
