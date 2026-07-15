"""Running workout spec — the athlete-facing description of a run, validated here before
any translation to Garmin's schema (that's `garmin/translate/running.py`).

A step carries at most ONE target — a pace range, an HR zone, or a custom HR range.
"""

from __future__ import annotations

import re
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, model_validator

from .base import RepeatBase, WorkoutSpecBase

__all__ = [
    "PaceTarget", "HRZoneTarget", "HRRangeTarget",
    "pace", "hr_zone", "hr_range",
    "Step", "Repeat", "WorkoutSpec",
]

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
    """A custom heart-rate band, in bpm."""
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

def pace(a: str, b: str) -> PaceTarget:
    """pace('5:11', '5:32') — order-agnostic; faster bound is sorted first."""
    fast, slow = sorted((_parse_pace(a), _parse_pace(b)))
    return PaceTarget(fast_sec_per_km=fast, slow_sec_per_km=slow)


def hr_zone(zone: int) -> HRZoneTarget:
    return HRZoneTarget(zone=zone)


def hr_range(low: int, high: int) -> HRRangeTarget:
    return HRRangeTarget(low_bpm=low, high_bpm=high)


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


class Repeat(RepeatBase[Step]):
    """A repeat group of run steps — e.g. Repeat(5, [interval, recovery])."""


Element = Union[Step, Repeat]


class WorkoutSpec(WorkoutSpecBase[Element]):
    """A complete, validated running workout."""
    sport: Literal["running"] = "running"
