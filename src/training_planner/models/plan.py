"""The plan domain model — multi-modal, validated, athlete-facing.

The atomic unit is a `Session` (a common envelope + discipline-specific content):
run / strength. Run sessions reuse the existing `WorkoutSpec`, so they translate
straight to Garmin; strength carries guidance (mobility work is folded into strength).

Composition:  Target + Block (base->build->peak->taper) -> Week -> [Session]
A Target is a race OR a performance goal (e.g. a 5k time goal).

This module is Garmin-agnostic (like workout.py) — it only describes plans.
"""

from __future__ import annotations

import datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, model_validator

from .workout import WorkoutSpec

__all__ = [
    "ExercisePrescription",
    "RunContent", "StrengthContent",
    "Session", "run_session", "strength_session",
    "Week", "Block", "Target",
]

Discipline = Literal["run", "strength"]
Phase = Literal["base", "build", "peak", "taper"]


# --------------------------------------------------------------------------- #
# Discipline-specific content (discriminated union, keyed by `discipline`)
# --------------------------------------------------------------------------- #

class ExercisePrescription(BaseModel):
    """One prescribed strength exercise."""
    name: str = Field(min_length=1)
    sets: int = Field(ge=1)
    reps: str = Field(min_length=1)         # "5", "6-8", "30s" — free-form on purpose
    intensity: str | None = None            # "RPE 7", "@ bodyweight", "3-0-1 tempo"
    rest: str | None = None                 # "2 min"
    purpose: str | None = None              # "unilateral leg strength for descending"

    def __str__(self) -> str:
        bits = [f"{self.name}  {self.sets}×{self.reps}"]
        if self.intensity:
            bits.append(self.intensity)
        if self.rest:
            bits.append(f"rest {self.rest}")
        return "  ".join(bits)


class RunContent(BaseModel):
    discipline: Literal["run"] = "run"
    workout: WorkoutSpec                     # reuses the running spec; syncs to Garmin

    def summary(self) -> str:
        return self.workout.name


class StrengthContent(BaseModel):
    discipline: Literal["strength"] = "strength"
    focus: list[str] = Field(min_length=1)   # ["lower", "posterior-chain"]
    exercises: list[ExercisePrescription] = Field(min_length=1)

    def summary(self) -> str:
        return "strength: " + ", ".join(self.focus)


Content = Annotated[
    Union[RunContent, StrengthContent],
    Field(discriminator="discipline"),
]


# --------------------------------------------------------------------------- #
# Session — the atomic unit
# --------------------------------------------------------------------------- #

class Session(BaseModel):
    date: datetime.date
    title: str = Field(min_length=1)
    intent: str = Field(min_length=1)        # "threshold", "long", "recovery", "strength-support"
    key: bool = False                        # priority session — protect the days around it
    notes: str | None = None
    content: Content

    @property
    def discipline(self) -> Discipline:
        return self.content.discipline

    def __str__(self) -> str:
        star = " ★" if self.key else ""
        weekday = self.date.strftime("%a")
        return f"{weekday}  {self.discipline:<9} {self.title}{star}"


# Ergonomic factories (mirror pace()/hr_zone() style in workout.py).

def run_session(date, title: str, intent: str, workout: WorkoutSpec,
                *, key: bool = False, notes: str | None = None) -> Session:
    return Session(date=date, title=title, intent=intent, key=key, notes=notes,
                   content=RunContent(workout=workout))


def strength_session(date, title: str, intent: str, focus: list[str],
                     exercises: list[ExercisePrescription],
                     *, key: bool = False, notes: str | None = None) -> Session:
    return Session(date=date, title=title, intent=intent, key=key, notes=notes,
                   content=StrengthContent(focus=focus, exercises=exercises))


# --------------------------------------------------------------------------- #
# Week / Block / Race
# --------------------------------------------------------------------------- #

class Week(BaseModel):
    index: int = Field(ge=1)
    phase: Phase
    target_km: float | None = Field(default=None, gt=0)
    notes: str | None = None
    sessions: list[Session] = Field(min_length=1)

    def ordered(self) -> list[Session]:
        return sorted(self.sessions, key=lambda s: s.date)


class Target(BaseModel):
    """What a block trains toward — a race, or a performance goal (e.g. a 5k time goal)."""
    name: str = Field(min_length=1)
    kind: Literal["race", "performance"] = "race"
    date: datetime.date | None = None        # races have a date; open goals may not
    distance_km: float | None = Field(default=None, gt=0)
    elevation_gain_m: int | None = Field(default=None, ge=0)
    terrain: str | None = None
    location: str | None = None
    goal: str | None = None                  # "finish strong", a target time, etc.


class Block(BaseModel):
    """A periodized training block toward a target."""
    target: Target
    generated_from: str | None = None        # provenance: e.g. "fitness-snapshots/2026-06-23.json"
    weeks: list[Week] = Field(min_length=1)

    @model_validator(mode="after")
    def _weeks_sequential(self) -> "Block":
        indices = [w.index for w in self.weeks]
        if indices != list(range(1, len(indices) + 1)):
            raise ValueError(f"week indices must be 1..N in order, got {indices}")
        return self

    def preview(self) -> str:
        t = self.target
        head = t.name + (f" — {t.date}" if t.date else "")
        specs = [s for s in (f"{t.distance_km:g} km" if t.distance_km else None,
                             f"{t.elevation_gain_m} m" if t.elevation_gain_m is not None else None) if s]
        if specs:
            head += "  (" + ", ".join(specs) + ")"
        lines = [head]
        for w in self.weeks:
            vol = f" · {w.target_km:g} km" if w.target_km else ""
            lines.append(f"\nWeek {w.index} · {w.phase}{vol}")
            for s in w.ordered():
                lines.append(f"  {s}")
        return "\n".join(lines)
