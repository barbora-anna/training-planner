"""The exercise catalog — loads from garmin-fit-sdk and validates against it (offline)."""

import pytest
from pydantic import ValidationError

from training_planner.models.exercises import (
    Exercise,
    categories,
    exercises_in,
    find,
)


class TestCatalog:
    def test_loads_uppercase_catalog(self):
        cats = categories()
        assert len(cats) > 40                     # ~51 real categories
        assert "SQUAT" in cats
        assert all(c == c.upper() for c in cats)  # stored UPPERCASE (Connect's form)

    def test_exercises_in_is_case_insensitive_and_safe(self):
        assert exercises_in("squat") == exercises_in("SQUAT")
        assert "GOBLET_SQUAT" in exercises_in("SQUAT")
        assert exercises_in("NOPE") == []         # unknown → empty, no raise


class TestExerciseValidation:
    def test_category_only(self):
        assert Exercise("PLANK").name is None

    def test_rejects_unknown_category(self):
        with pytest.raises(ValidationError):
            Exercise("NOT_A_CATEGORY")

    def test_rejects_name_not_in_category(self):
        with pytest.raises(ValidationError):
            Exercise("SQUAT", "BENCH_PRESS")      # real name, wrong category

    def test_normalizes_case(self):
        # the FIT profile spells names lowercase — accept that, store Connect's UPPERCASE
        assert Exercise("squat", "goblet_squat") == Exercise("SQUAT", "GOBLET_SQUAT")
        assert Exercise(category="squat").category == "SQUAT"


class TestFind:
    def test_finds_across_catalog(self):
        assert Exercise("SQUAT", "GOBLET_SQUAT") in find("goblet")
