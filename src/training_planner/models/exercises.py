"""The strength-exercise catalog — every exercise Garmin knows, validated at the source.

Garmin's exercises are a two-level taxonomy: a `category` (e.g. `SQUAT`) and an optional,
more specific `name` within it (e.g. `GOBLET_SQUAT`). The full, authoritative list is the
official **`garmin-fit-sdk`** FIT Profile — 53 categories, ~1,846 named exercises. We load
it live at import (offline, no network) so the catalog is always exactly what the current
SDK version knows; there is no hand-curated subset to drift.

The FIT Profile spells values lowercase (`goblet_squat`); Garmin Connect's workout/activity
API uses UPPERCASE (`GOBLET_SQUAT`). We store and expose UPPERCASE — the form the Connect
API wants — so an `Exercise` translates straight through.

`Exercise` validates against the catalog on construction: an unknown category, or a name
that isn't in its category, raises. So a workout can never carry an exercise Garmin would
reject — the guarantee is enforced here, before anything reaches the wire.
"""

from __future__ import annotations

from garmin_fit_sdk import Profile
from pydantic import BaseModel, model_validator

__all__ = ["Exercise", "categories", "exercises_in", "find"]

# Categories present in the taxonomy but not real prescribable exercises.
_SKIP = {"unknown", "cardio_sensors"}


def _load_catalog() -> dict[str, frozenset[str]]:
    """Build {CATEGORY: frozenset(EXERCISE_NAMES)} from the FIT Profile, UPPERCASE."""
    types = Profile["types"]
    catalog: dict[str, frozenset[str]] = {}
    for cat_key in types["exercise_category"].values():   # {int: 'squat', ...}
        if cat_key in _SKIP:
            continue
        names = types.get(f"{cat_key}_exercise_name", {})  # {int: 'goblet_squat', ...}
        catalog[cat_key.upper()] = frozenset(n.upper() for n in names.values())
    return catalog


# Built once at import — the single source of truth for validation and discovery.
_CATALOG: dict[str, frozenset[str]] = _load_catalog()


class Exercise(BaseModel, frozen=True):
    """A Garmin strength exercise: a category, optionally narrowed to a specific name.

    `Exercise("SQUAT")` is category-only; `Exercise("SQUAT", "GOBLET_SQUAT")` is specific.
    Both category and name are validated against the FIT catalog, case-insensitively —
    the FIT profile's own lowercase spelling (`goblet_squat`) is accepted and stored
    UPPERCASE, the form the Connect API wants.
    """
    category: str
    name: str | None = None

    def __init__(self, category: str | None = None, name: str | None = None, /, **data):
        # Allow positional use: Exercise("SQUAT", "GOBLET_SQUAT")
        if category is not None:
            data["category"] = category
        if name is not None:
            data["name"] = name
        super().__init__(**data)

    @model_validator(mode="before")
    @classmethod
    def _uppercase(cls, data):
        if isinstance(data, dict):
            data = {k: v.upper() if k in ("category", "name") and isinstance(v, str) else v
                    for k, v in data.items()}
        return data

    @model_validator(mode="after")
    def _known_to_garmin(self) -> "Exercise":
        names = _CATALOG.get(self.category)
        if names is None:
            raise ValueError(
                f"unknown exercise category {self.category!r} — see categories()"
            )
        if self.name is not None and self.name not in names:
            raise ValueError(
                f"{self.name!r} is not a known exercise in category {self.category!r} — "
                f"see exercises_in({self.category!r})"
            )
        return self

    def __str__(self) -> str:
        return self.name or self.category


def categories() -> list[str]:
    """All known exercise categories (UPPERCASE), sorted."""
    return sorted(_CATALOG)


def exercises_in(category: str) -> list[str]:
    """Named exercises in a category (UPPERCASE), sorted. Empty if none / unknown."""
    return sorted(_CATALOG.get(category.upper(), ()))


def find(query: str) -> list[Exercise]:
    """Every exercise whose category or name contains `query` (case-insensitive).

    The discovery helper for building strength workouts — e.g. `find("squat")` surfaces
    every squat variant across the whole catalog so the advisor can pick a real one.
    """
    q = query.upper()
    hits: list[Exercise] = []
    for cat, names in _CATALOG.items():
        if q in cat:
            hits.append(Exercise(cat))
        hits.extend(Exercise(cat, name) for name in names if q in name)
    return sorted(hits, key=str)
