"""The plan domain model — multi-modal, validated, athlete-facing.

The atomic unit is a `Session` (a common envelope + discipline-specific content):
run / strength. Run sessions reuse the existing `WorkoutSpec`, so they translate
straight to Garmin; strength carries guidance (mobility work is folded into strength).

Composition:  Target + Block (base->build->peak->taper) -> Week -> [Session]
A Target is a race OR a performance goal (e.g. a 5k time goal).

This module is Garmin-agnostic (like the workout specs in running.py/strength.py) —
it only describes plans.
"""

from __future__ import annotations

import datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, model_validator

from .running import WorkoutSpec
from .strength import StrengthWorkoutSpec

__all__ = [
    "ExercisePrescription",
    "RunContent", "StrengthContent",
    "Session", "run_session", "strength_session",
    "Week", "Block", "Target", "Milestone",
]

Discipline = Literal["running", "strength"]
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
    discipline: Literal["running"] = "running"
    workout: WorkoutSpec                     # reuses the running spec; syncs to Garmin

    def summary(self) -> str:
        return self.workout.name

    def detail_lines(self) -> list[str]:
        """The structured steps that actually get synced — same detail as Garmin sees."""
        return self.workout.numbered_lines()


class StrengthContent(BaseModel):
    discipline: Literal["strength"] = "strength"
    focus: list[str] = Field(min_length=1)   # ["lower", "posterior-chain"]
    exercises: list[ExercisePrescription] = Field(min_length=1)
    workout: StrengthWorkoutSpec | None = None   # structured + Garmin-syncable; else guidance-only

    def summary(self) -> str:
        return "strength: " + ", ".join(self.focus)

    def detail_lines(self) -> list[str]:
        """Prefer the structured workout (exact sets/reps/weight, what Garmin gets); fall
        back to the free-form prescriptions when there's no structured workout to sync.
        """
        lines = [f"focus: {', '.join(self.focus)}"]
        if self.workout is not None:
            lines += self.workout.numbered_lines()
        else:
            lines += [f"- {ex}" for ex in self.exercises]
        return lines


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

    def preview_lines(self, indent: str = "  ") -> list[str]:
        """The session header plus indented detail lines (steps/exercises), at `indent`.

        All indentation is composed here (not split with the caller) so there's one place
        that decides how a session block looks, however deep it's nested.
        """
        return [f"{indent}{self}"] + [f"{indent}    {line}" for line in self.content.detail_lines()]


# Ergonomic factories (mirror pace()/hr_zone() style in running.py).

def run_session(date, title: str, intent: str, workout: WorkoutSpec,
                *, key: bool = False, notes: str | None = None) -> Session:
    return Session(date=date, title=title, intent=intent, key=key, notes=notes,
                   content=RunContent(workout=workout))


def strength_session(date, title: str, intent: str, focus: list[str],
                     exercises: list[ExercisePrescription],
                     *, workout: StrengthWorkoutSpec | None = None,
                     key: bool = False, notes: str | None = None) -> Session:
    return Session(date=date, title=title, intent=intent, key=key, notes=notes,
                   content=StrengthContent(focus=focus, exercises=exercises, workout=workout))


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


class Milestone(BaseModel):
    """A checkpoint on the way to a Target — a capability to reach en route to the goal.

    Ordered by list position (first = earliest). `achieved_on` is the progress state:
    None = not yet hit, a date = done. Milestones let an open-ended goal (a muscle-up, a
    faster 5k) be tracked as a series of concrete wins rather than one all-or-nothing line.
    """
    label: str = Field(min_length=1)                  # "8–10 strict pull-ups"
    metric: str | None = None                         # optional handle, e.g. "strict_pullups"
    target_date: datetime.date | None = None          # optional soft deadline
    achieved_on: datetime.date | None = None          # None = not yet; a date = done

    @property
    def done(self) -> bool:
        return self.achieved_on is not None

    def __str__(self) -> str:
        mark = "✓" if self.done else "○"
        tail = f"  (by {self.target_date})" if self.target_date else ""
        return f"{mark} {self.label}{tail}"


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
    milestones: list[Milestone] = Field(default_factory=list)   # ordered steps toward the goal


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
        if t.milestones:
            lines.append("\nMilestones")
            for m in t.milestones:
                lines.append(f"  {m}")
        for w in self.weeks:
            vol = f" · {w.target_km:g} km" if w.target_km else ""
            lines.append(f"\nWeek {w.index} · {w.phase}{vol}")
            for s in w.ordered():
                lines.extend(s.preview_lines())
        return "\n".join(lines)
