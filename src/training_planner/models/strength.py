"""Strength workout spec — the athlete-facing description of a lifting session, validated
here before any translation to Garmin's schema (that's `garmin/translate/strength.py`).
"""

from __future__ import annotations

from typing import Literal, Union

from pydantic import BaseModel, Field, model_validator

from .base import RepeatBase, WorkoutSpecBase
from .exercises import Exercise

__all__ = [
    "StrengthStep", "RestStep", "StrengthSet", "StrengthWorkoutSpec",
]


class StrengthStep(BaseModel):
    """One exercise, ending on reps OR a timed hold (seconds) — exactly one."""
    exercise: Exercise
    reps: int | None = Field(default=None, gt=0)
    seconds: float | None = Field(default=None, gt=0)      # timed holds (planks, carries)
    weight_kg: float | None = Field(default=None, gt=0)    # None = bodyweight

    def __init__(self, exercise: Exercise | None = None, /, **data):
        # Allow positional exercise: StrengthStep(Exercise("SQUAT"), reps=10)
        if exercise is not None:
            data["exercise"] = exercise
        super().__init__(**data)

    @model_validator(mode="after")
    def _exactly_one_effort(self) -> "StrengthStep":
        if (self.reps is None) == (self.seconds is None):
            raise ValueError(f"strength step '{self.exercise}': set exactly one of "
                             "reps= or seconds=")
        return self

    def __str__(self) -> str:
        effort = f"{self.reps} reps" if self.reps is not None else f"{self.seconds:g}s hold"
        load = f" @ {self.weight_kg:g} kg" if self.weight_kg is not None else ""
        return f"{self.exercise} — {effort}{load}"


class RestStep(BaseModel):
    """A rest between sets or exercises, in seconds."""
    seconds: float = Field(gt=0)

    def __init__(self, seconds: float | None = None, /, **data):
        if seconds is not None:
            data["seconds"] = seconds
        super().__init__(**data)

    def __str__(self) -> str:
        return f"rest {self.seconds:g}s"


class StrengthSet(RepeatBase[Union[StrengthStep, RestStep]]):
    """A repeat group of strength/rest steps — e.g. 3× (squat + rest)."""


StrengthElement = Union[StrengthStep, RestStep, StrengthSet]


class StrengthWorkoutSpec(WorkoutSpecBase[StrengthElement]):
    """A complete, validated strength workout."""
    sport: Literal["strength"] = "strength"
