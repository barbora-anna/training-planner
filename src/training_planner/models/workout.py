"""Validated, library-independent workout spec — Layer 1 of the two-layer design.

These are athlete-friendly pydantic models the agent uses to *describe* a workout.
Everything is validated here, BEFORE translation to Garmin's schema (Layer 2 lives in
`garmin/translate.py`, `spec_to_garmin`). This module knows nothing about Garmin.

A step carries at most ONE target — a pace range, an HR zone, or a custom HR range —
never several at once (it's a single `target` field).

Example:
    WorkoutSpec(
        name="Threshold 5x4",
        steps=[
            Step("warmup", minutes=10, target=hr_zone(2)),
            Repeat(5, [
                Step("interval", minutes=4, target=pace("5:11", "5:32")),
                Step("recovery", minutes=1.5),
            ]),
            Step("cooldown", minutes=10, target=hr_zone(1)),
        ],
    )
"""

from __future__ import annotations

import re
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, model_validator

from .exercises import Exercise

__all__ = [
    "PaceTarget", "HRZoneTarget", "HRRangeTarget",
    "pace", "hr_zone", "hr_range",
    "Step", "Repeat", "WorkoutSpec",
    "StrengthStep", "RestStep", "StrengthSet", "StrengthWorkoutSpec",
]

# --------------------------------------------------------------------------- #
# Pace helpers (min:sec per km <-> seconds per km)
# --------------------------------------------------------------------------- #

_PACE_RE = re.compile(r"^\s*(\d{1,2}):([0-5]\d)\s*$")


def _parse_pace(text: str) -> int:
    """'5:30' -> 330 (seconds per km)."""
    m = _PACE_RE.match(text)
    if not m:
        raise ValueError(f"pace must look like 'm:ss' per km (e.g. '5:30'), got {text!r}")
    total = int(m.group(1)) * 60 + int(m.group(2))
    if total <= 0:
        raise ValueError("pace must be greater than 0")
    return total


def _format_pace(sec_per_km: int) -> str:
    return f"{sec_per_km // 60}:{sec_per_km % 60:02d}"


# --------------------------------------------------------------------------- #
# Targets — each step may carry exactly one (or none)
# --------------------------------------------------------------------------- #

class PaceTarget(BaseModel):
    """A pace band. `fast` is the quicker bound (fewer sec/km) than `slow`."""
    type: Literal["pace"] = "pace"
    fast_sec_per_km: int = Field(gt=0)
    slow_sec_per_km: int = Field(gt=0)

    @model_validator(mode="after")
    def _ordered(self) -> "PaceTarget":
        if self.fast_sec_per_km >= self.slow_sec_per_km:
            raise ValueError("pace 'fast' bound must be quicker (smaller) than the 'slow' bound")
        return self

    def __str__(self) -> str:
        return f"{_format_pace(self.fast_sec_per_km)}–{_format_pace(self.slow_sec_per_km)}/km"


class HRZoneTarget(BaseModel):
    """A heart-rate zone (1–5); the watch uses that zone's configured bpm band."""
    type: Literal["hr_zone"] = "hr_zone"
    zone: int = Field(ge=1, le=5)

    def __str__(self) -> str:
        return f"HR Z{self.zone}"


class HRRangeTarget(BaseModel):
    """A custom heart-rate band in bpm."""
    type: Literal["hr_range"] = "hr_range"
    low_bpm: int = Field(ge=50, le=240)
    high_bpm: int = Field(ge=50, le=240)

    @model_validator(mode="after")
    def _ordered(self) -> "HRRangeTarget":
        if self.low_bpm >= self.high_bpm:
            raise ValueError("HR 'low' must be less than 'high'")
        return self

    def __str__(self) -> str:
        return f"{self.low_bpm}–{self.high_bpm} bpm"


Target = Annotated[
    Union[PaceTarget, HRZoneTarget, HRRangeTarget],
    Field(discriminator="type"),
]

# Friendly factories — what the agent actually calls.

def pace(a: str, b: str) -> PaceTarget:
    """pace('5:11', '5:32') — order-agnostic; faster bound is sorted first."""
    fast, slow = sorted((_parse_pace(a), _parse_pace(b)))
    return PaceTarget(fast_sec_per_km=fast, slow_sec_per_km=slow)


def hr_zone(zone: int) -> HRZoneTarget:
    return HRZoneTarget(zone=zone)


def hr_range(low: int, high: int) -> HRRangeTarget:
    return HRRangeTarget(low_bpm=low, high_bpm=high)


# --------------------------------------------------------------------------- #
# Steps & structure
# --------------------------------------------------------------------------- #

StepKind = Literal["warmup", "interval", "recovery", "cooldown", "rest"]


class Step(BaseModel):
    """One workout step, ending on time (minutes) OR distance (km) — exactly one."""
    kind: StepKind
    minutes: float | None = Field(default=None, gt=0)
    km: float | None = Field(default=None, gt=0)
    target: Target | None = None

    def __init__(self, kind: StepKind | None = None, /, **data):
        # Allow positional kind: Step("interval", minutes=4, ...)
        if kind is not None:
            data["kind"] = kind
        super().__init__(**data)

    @model_validator(mode="after")
    def _exactly_one_duration(self) -> "Step":
        if (self.minutes is None) == (self.km is None):
            raise ValueError(f"step '{self.kind}': set exactly one of minutes= or km=")
        return self

    def __str__(self) -> str:
        dur = f"{self.minutes:g} min" if self.minutes is not None else f"{self.km:g} km"
        tgt = f" @ {self.target}" if self.target is not None else ""
        return f"{self.kind} {dur}{tgt}"


class Repeat(BaseModel):
    """A repeat group, e.g. Repeat(5, [interval, recovery])."""
    times: int = Field(ge=2)
    steps: list[Step] = Field(min_length=1)

    def __init__(self, times: int | None = None, steps: list[Step] | None = None, /, **data):
        if times is not None:
            data["times"] = times
        if steps is not None:
            data["steps"] = steps
        super().__init__(**data)

    def __str__(self) -> str:
        inner = " + ".join(str(s) for s in self.steps)
        return f"{self.times}x ({inner})"


Element = Union[Step, Repeat]


class WorkoutSpec(BaseModel):
    """A complete, validated workout description."""
    name: str = Field(min_length=1)
    sport: Literal["running"] = "running"
    description: str | None = None
    steps: list[Element] = Field(min_length=1)

    def preview(self) -> str:
        """A readable rendering for review before syncing."""
        lines = [f"{self.name}  ({self.sport})"]
        for i, el in enumerate(self.steps, 1):
            lines.append(f"  {i}. {el}")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Strength — a parallel spec (running steps/targets don't apply to lifting)
#
# An exercise ends on reps OR a time hold (seconds); optional weight (kg, None =
# bodyweight). Sets are a `StrengthSet` repeat group — the strength counterpart to
# `Repeat`, typed to strength steps rather than running `Step`.
# --------------------------------------------------------------------------- #

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
    """A rest between sets/exercises, in seconds."""
    seconds: float = Field(gt=0)

    def __init__(self, seconds: float | None = None, /, **data):
        if seconds is not None:
            data["seconds"] = seconds
        super().__init__(**data)

    def __str__(self) -> str:
        return f"rest {self.seconds:g}s"


class StrengthSet(BaseModel):
    """A repeat group of strength/rest steps — e.g. 3× (squat + rest)."""
    times: int = Field(ge=2)
    steps: list[StrengthStep | RestStep] = Field(min_length=1)

    def __init__(self, times: int | None = None,
                 steps: list[StrengthStep | RestStep] | None = None, /, **data):
        if times is not None:
            data["times"] = times
        if steps is not None:
            data["steps"] = steps
        super().__init__(**data)

    def __str__(self) -> str:
        inner = " + ".join(str(s) for s in self.steps)
        return f"{self.times}x ({inner})"


StrengthElement = Union[StrengthStep, RestStep, StrengthSet]


class StrengthWorkoutSpec(BaseModel):
    """A complete, validated strength workout description."""
    name: str = Field(min_length=1)
    sport: Literal["strength"] = "strength"
    description: str | None = None
    steps: list[StrengthElement] = Field(min_length=1)

    def preview(self) -> str:
        """A readable rendering for review before syncing."""
        lines = [f"{self.name}  (strength)"]
        for i, el in enumerate(self.steps, 1):
            lines.append(f"  {i}. {el}")
        return "\n".join(lines)
