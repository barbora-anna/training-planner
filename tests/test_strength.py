"""Strength spec + translation — validation and the Garmin dict shape (offline)."""

import pytest
from pydantic import ValidationError

from training_planner.garmin.translate import STRENGTH_SPORT, strength_spec_to_garmin
from training_planner.models.exercises import Exercise
from training_planner.models.workout import (
    RestStep,
    StrengthSet,
    StrengthStep,
    StrengthWorkoutSpec,
)


def _squat(**kw):
    return StrengthStep(Exercise("SQUAT", "GOBLET_SQUAT"), **kw)


class TestStrengthStep:
    def test_requires_exactly_one_effort(self):
        with pytest.raises(ValidationError):
            _squat()                       # neither reps nor seconds
        with pytest.raises(ValidationError):
            _squat(reps=10, seconds=30)    # both


class TestStrengthWorkoutSpec:
    def test_build_and_preview(self):
        spec = StrengthWorkoutSpec(name="Lower A", steps=[
            StrengthSet(3, [_squat(reps=10, weight_kg=20), RestStep(90)]),
            StrengthSet(2, [StrengthStep(Exercise("PLANK"), seconds=45)]),
        ])
        assert spec.sport == "strength"
        assert "Lower A" in spec.preview()

    def test_requires_steps(self):
        with pytest.raises(ValidationError):
            StrengthWorkoutSpec(name="x", steps=[])

    def test_set_needs_min_two(self):
        with pytest.raises(ValidationError):
            StrengthSet(1, [_squat(reps=5)])


class TestStrengthTranslation:
    def _payload(self):
        spec = StrengthWorkoutSpec(name="Lower A", steps=[
            StrengthSet(3, [_squat(reps=10, weight_kg=20), RestStep(90)]),
            StrengthStep(Exercise("PLANK"), seconds=45),
        ])
        return strength_spec_to_garmin(spec)

    def test_is_dict_tagged_strength(self):
        d = self._payload()
        assert isinstance(d, dict)
        assert d["sportType"] == STRENGTH_SPORT

    def test_squat_step_fields(self):
        d = self._payload()
        squat = d["workoutSegments"][0]["workoutSteps"][0]["workoutSteps"][0]
        assert squat["endCondition"]["conditionTypeKey"] == "reps"
        assert squat["endConditionValue"] == 10.0
        assert squat["category"] == "SQUAT"
        assert squat["exerciseName"] == "GOBLET_SQUAT"
        assert squat["weightValue"] == 20.0           # kg, as Garmin's display unit wants
        # weight must carry its unit or Garmin drops it on save (kg × factor 1000 = grams)
        assert squat["weightUnit"] == {"unitId": 8, "unitKey": "kilogram", "factor": 1000.0}

    def test_bodyweight_hold_has_no_weight_or_name(self):
        d = self._payload()
        plank = d["workoutSegments"][0]["workoutSteps"][1]
        assert plank["endCondition"]["conditionTypeKey"] == "time"
        assert plank["endConditionValue"] == 45.0
        assert plank["category"] == "PLANK"
        assert plank.get("exerciseName") is None      # category-only
        assert plank.get("weightValue") is None        # bodyweight
        assert plank.get("weightUnit") is None         # no weight -> no unit
