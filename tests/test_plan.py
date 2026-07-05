"""Session / Week / Block / Target — factories, validators, and preview rendering."""

import datetime

import pytest
from pydantic import ValidationError

from training_planner.models.plan import (
    Block,
    ExercisePrescription,
    RunContent,
    StrengthContent,
    Target,
    Week,
    run_session,
    strength_session,
)
from training_planner.models.workout import Step, WorkoutSpec, hr_zone


def _run(date="2026-08-01", title="easy", intent="easy", **kw):
    w = WorkoutSpec(name="w", steps=[Step("interval", minutes=30, target=hr_zone(2))])
    return run_session(date=date, title=title, intent=intent, workout=w, **kw)


class TestSessionFactories:
    def test_run_session_discipline(self):
        s = _run()
        assert s.discipline == "run"
        assert isinstance(s.content, RunContent)

    def test_strength_session_discipline(self):
        s = strength_session(
            date="2026-08-02", title="legs", intent="strength",
            focus=["lower"], exercises=[ExercisePrescription(name="squat", sets=3, reps="5")],
        )
        assert s.discipline == "strength"
        assert isinstance(s.content, StrengthContent)

    def test_key_flag(self):
        assert _run().key is False
        assert _run(title="long", intent="long", key=True).key is True


class TestWeek:
    def test_ordered_by_date(self):
        wk = Week(index=1, phase="base", sessions=[_run("2026-08-03"), _run("2026-08-01")])
        assert [s.date for s in wk.ordered()] == [
            datetime.date(2026, 8, 1), datetime.date(2026, 8, 3),
        ]

    def test_requires_session(self):
        with pytest.raises(ValidationError):
            Week(index=1, phase="base", sessions=[])


class TestBlock:
    def _block(self, indices, **target_kw):
        weeks = [Week(index=i, phase="base", sessions=[_run()]) for i in indices]
        return Block(target=Target(name="Goal", **target_kw), weeks=weeks)

    def test_weeks_must_be_sequential(self):
        with pytest.raises(ValidationError):
            self._block([1, 3])  # gap
        with pytest.raises(ValidationError):
            self._block([2, 1])  # out of order

    def test_valid_sequential(self):
        assert len(self._block([1, 2, 3]).weeks) == 3

    def test_preview_shows_zero_elevation(self):
        # regression: elevation_gain_m=0 must not be dropped by a truthy check
        assert "0 m" in self._block([1], kind="race", distance_km=10, elevation_gain_m=0).preview()

    def test_preview_omits_absent_elevation(self):
        head = self._block([1], kind="race", distance_km=10).preview().splitlines()[0]
        assert head.endswith("(10 km)")


class TestTarget:
    def test_defaults_to_race(self):
        assert Target(name="X").kind == "race"

    def test_performance_goal_needs_no_date(self):
        t = Target(name="sub-40 10k", kind="performance", distance_km=10)
        assert t.date is None
