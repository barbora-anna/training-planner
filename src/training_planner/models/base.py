"""Discipline-agnostic workout skeleton — the shared spine every sport reuses."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

__all__ = ["RepeatBase", "WorkoutSpecBase"]

E = TypeVar("E")


class RepeatBase(BaseModel, Generic[E]):
    """A repeat group over `E` — e.g. 5× (interval + recovery), 3× (squat + rest)."""
    times: int = Field(ge=2)
    steps: list[E] = Field(min_length=1)

    def __init__(self, times: int | None = None, steps: list[E] | None = None, /, **data):
        # Allow positional use: Repeat(5, [...]).
        if times is not None:
            data["times"] = times
        if steps is not None:
            data["steps"] = steps
        super().__init__(**data)

    def __str__(self) -> str:
        inner = " + ".join(str(s) for s in self.steps)
        return f"{self.times}x ({inner})"


class WorkoutSpecBase(BaseModel, Generic[E]):
    """A complete, validated workout: a named envelope over an ordered list of elements.

    Subclasses set a concrete `sport` literal and parametrize `E` with their element union.
    """
    name: str = Field(min_length=1)
    sport: str                               # narrowed to a Literal by each discipline
    description: str | None = None
    steps: list[E] = Field(min_length=1)

    def numbered_lines(self) -> list[str]:
        """`steps` rendered as `"1. ..."` lines — the shared building block for previews,
        so every caller (this class's own `preview()`, and anyone else previewing the same
        steps elsewhere) numbers them the same way.
        """
        return [f"{i}. {el}" for i, el in enumerate(self.steps, 1)]

    def preview(self) -> str:
        """Render the workout for review before syncing."""
        lines = [f"{self.name}  ({self.sport})"]
        lines.extend(f"  {line}" for line in self.numbered_lines())
        return "\n".join(lines)
