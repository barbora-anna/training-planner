"""Session / Week / Block / Target — factories, validators, and preview rendering."""

import datetime

import pytest
from pydantic import ValidationError

from training_planner.models.exercises import Exercise
from training_planner.models.plan import (
    Block,
    ExercisePrescription,
    Milestone,
    RunContent,
    StrengthContent,
    Target,
    Week,
    run_session,
    strength_session,
)
from training_planner.models.running import Step, WorkoutSpec, hr_zone
from training_planner.models.strength import StrengthStep, StrengthWorkoutSpec


def _run(date="2026-08-01", title="easy", intent="easy", **kw):
    w = WorkoutSpec(name="w", steps=[Step("interval", minutes=30, target=hr_zone(2))])
    return run_session(date=date, title=title, intent=intent, workout=w, **kw)


def _strength(**kw):
    return strength_session(
        date="2026-08-02", title="legs", intent="strength",
        focus=["lower"], exercises=[ExercisePrescription(name="squat", sets=3, reps="5")],
        **kw,
    )


class TestSessionFactories:
    def test_run_session_discipline(self):
        s = _run()
        assert s.discipline == "running"
        assert isinstance(s.content, RunContent)

    def test_strength_session_discipline(self):
        s = _strength()
        assert s.discipline == "strength"
        assert isinstance(s.content, StrengthContent)

    def test_strength_workout_is_optional_and_round_trips(self):
        assert _strength().content.workout is None    # guidance-only by default
        spec = StrengthWorkoutSpec(name="Lower A", steps=[
            StrengthStep(Exercise("SQUAT", "GOBLET_SQUAT"), reps=10, weight_kg=20),
        ])
        content = _strength(workout=spec).content
        loaded = StrengthContent.model_validate_json(content.model_dump_json())
        assert loaded.workout.steps[0].exercise.name == "GOBLET_SQUAT"

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

    def test_preview_includes_session_detail(self):
        # regression: block.md should render step detail, not just the session title
        assert "interval 30 min" in self._block([1], kind="race", distance_km=10).preview()


class TestTarget:
    def test_defaults_to_race(self):
        assert Target(name="X").kind == "race"

    def test_performance_goal_needs_no_date(self):
        t = Target(name="sub-40 10k", kind="performance", distance_km=10)
        assert t.date is None

    def test_milestones_default_empty(self):
        assert Target(name="X").milestones == []

    def test_milestone_done_state(self):
        pending = Milestone(label="8–10 strict pull-ups")
        hit = Milestone(label="chest-to-bar", achieved_on=datetime.date(2026, 8, 1))
        assert pending.done is False and str(pending).startswith("○")
        assert hit.done is True and str(hit).startswith("✓")

    def test_milestones_round_trip(self):
        t = Target(name="First muscle-up", kind="performance",
                   milestones=[Milestone(label="8–10 strict pull-ups"),
                               Milestone(label="chest-to-bar",
                                         target_date=datetime.date(2026, 9, 1))])
        loaded = Target.model_validate_json(t.model_dump_json())
        assert [m.label for m in loaded.milestones] == ["8–10 strict pull-ups", "chest-to-bar"]
        assert loaded.milestones[1].target_date == datetime.date(2026, 9, 1)


class TestSessionPreview:
    def test_run_detail_shows_steps(self):
        s = _run()
        assert "interval 30 min" in "\n".join(s.preview_lines())

    def test_strength_detail_prefers_structured_workout(self):
        spec = StrengthWorkoutSpec(name="Lower A", steps=[
            StrengthStep(Exercise("SQUAT", "GOBLET_SQUAT"), reps=10, weight_kg=20),
        ])
        s = _strength(workout=spec)
        detail = "\n".join(s.preview_lines())
        assert "GOBLET_SQUAT" in detail and "20 kg" in detail
        assert "squat  3×5" not in detail    # structured wins over the free-form prescription

    def test_strength_detail_falls_back_to_prescriptions_without_workout(self):
        s = _strength()
        detail = "\n".join(s.preview_lines())
        assert "squat  3×5" in detail

    def test_strength_detail_shows_focus(self):
        s = _strength()
        assert "focus: lower" in "\n".join(s.preview_lines())


class TestMilestonePreview:
    def test_preview_lists_milestones_with_marks(self):
        block = Block(
            target=Target(name="First muscle-up", kind="performance",
                          milestones=[Milestone(label="8–10 strict pull-ups",
                                                achieved_on=datetime.date(2026, 8, 1)),
                                      Milestone(label="clean transition")]),
            weeks=[Week(index=1, phase="base", sessions=[_run()])],
        )
        out = block.preview()
        assert "Milestones" in out
        assert "✓ 8–10 strict pull-ups" in out
        assert "○ clean transition" in out
