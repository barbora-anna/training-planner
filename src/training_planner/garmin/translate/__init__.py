"""Translate validated, Garmin-agnostic workout specs into garminconnect payloads.

One module per discipline, over a shared spec-walking skeleton (`base.py`). Adding a
discipline = add its module plus one entry in the registry below.
"""

from __future__ import annotations

from .base import _assemble, _estimate
from .running import RUNNING_SPORT, _step_seconds, spec_to_garmin
from .strength import STRENGTH_SPORT, strength_spec_to_garmin

__all__ = [
    "to_garmin",
    "spec_to_garmin", "strength_spec_to_garmin",
    "RUNNING_SPORT", "STRENGTH_SPORT",
]

_TRANSLATORS = {
    "running": spec_to_garmin,
    "strength": strength_spec_to_garmin,
}


def to_garmin(spec):
    """Route a spec to its discipline translator by `spec.sport`.

    Returns a RunningWorkout object for running and a dict for strength — both feed the
    same Garmin upsert flow.
    """
    try:
        translate = _TRANSLATORS[spec.sport]
    except KeyError:
        raise ValueError(f"no Garmin translator for sport {spec.sport!r}") from None
    return translate(spec)
