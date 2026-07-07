"""Athlete state models — the app's own state (not activity history, which lives in Strava).

Split by change-cadence:
- Profile:        capacity/zones — slow-changing; drives PRESCRIPTION targets.
- FitnessSnapshot: weekly training-state — immutable dated history; drives VOLUME/READINESS.
- HealthStatus:   OPTIONAL injury/availability; shapes the plan when present.

All use extra="allow" so we don't drop fields we haven't formalized yet.
"""

from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict, Field


class Profile(BaseModel):
    """Slow-changing capacity + who they are — drives how PRESCRIPTION is calibrated.

    Split between demographics/experience (rarely change) and run zones (change on re-test).
    The person-level fields matter as much for strength as zones do for running: a small
    untrained beginner and a strong experienced lifter get very different loads.
    """
    model_config = ConfigDict(extra="allow")
    name: str | None = None
    units: str = "metric"
    # Who they are — individualizes load, especially for strength.
    sex: str | None = None                   # "female" | "male" | other — for strength norms
    age: int | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    training_status: str | None = None       # "untrained" | "novice" | "intermediate" | "advanced"
    strength_baseline: dict | None = None    # loose: e.g. {"back_squat_kg": 40, "notes": "new to lifting"}
    # Run capacity — from a re-test / assessment.
    hr_zones_bpm: dict | None = None         # {"z1": [0,124], ...} — loose for now
    pace_zones: dict | None = None
    target_preference: str | None = None     # "pace" | "hr" — which target type to prescribe
    updated_on: datetime.date | None = None


class FitnessSnapshot(BaseModel):
    """Weekly training-state at a point in time. Append-only; this is the progress series."""
    model_config = ConfigDict(extra="allow")
    date: datetime.date
    source: str = "Strava"
    weekly_km: dict | None = None            # {"last_4w": 18, ...}
    longest_run_km: float | None = None
    weekly_vert_m: float | None = None
    trend: str | None = None


class HealthStatus(BaseModel):
    """Optional injury/availability. Absent => healthy (the published default)."""
    model_config = ConfigDict(extra="allow")
    date: datetime.date
    status: str = Field(min_length=1)        # "healthy" | "recovering" | "injured"
    limitations: list[str] = Field(default_factory=list)
    return_to_run_stage: str | None = None
    notes: str | None = None
