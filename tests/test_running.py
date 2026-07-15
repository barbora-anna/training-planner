"""WorkoutSpec / Step / Repeat and the target factories — validation & ergonomics."""

import pytest
from pydantic import ValidationError

from training_planner.models.running import (
    Repeat,
    Step,
    WorkoutSpec,
    hr_range,
    hr_zone,
    pace,
)


class TestPace:
    def test_sorts_bounds_fast_first(self):
        t = pace("5:32", "5:11")  # given slow-first — factory sorts, and parses m:ss
        assert t.fast_sec_per_km == 311
        assert t.slow_sec_per_km == 332

    def test_rejects_equal_bounds(self):
        with pytest.raises(ValidationError):
            pace("5:00", "5:00")

    @pytest.mark.parametrize("bad", ["5", "5:60"])  # no colon / seconds out of range
    def test_rejects_malformed(self, bad):
        with pytest.raises(ValueError):
            pace(bad, "6:00")

    def test_str(self):
        assert str(pace("5:00", "5:20")) == "5:00–5:20/km"


class TestHrTargets:
    def test_hr_zone(self):
        assert hr_zone(3).zone == 3

    @pytest.mark.parametrize("z", [0, 6])
    def test_hr_zone_out_of_range(self, z):
        with pytest.raises(ValidationError):
            hr_zone(z)

    def test_hr_range(self):
        t = hr_range(140, 155)
        assert (t.low_bpm, t.high_bpm) == (140, 155)

    def test_hr_range_rejects_low_ge_high(self):
        with pytest.raises(ValidationError):
            hr_range(150, 150)


class TestStep:
    def test_positional_kind(self):
        assert Step("interval", minutes=4).kind == "interval"

    def test_requires_exactly_one_duration(self):
        with pytest.raises(ValidationError):
            Step("interval")  # neither minutes nor km
        with pytest.raises(ValidationError):
            Step("interval", minutes=4, km=1)  # both


class TestRepeat:
    def test_positional_args(self):
        r = Repeat(3, [Step("interval", minutes=1)])
        assert r.times == 3 and len(r.steps) == 1

    def test_times_min_two(self):
        with pytest.raises(ValidationError):
            Repeat(1, [Step("interval", minutes=1)])


class TestWorkoutSpec:
    def test_build_and_preview(self):
        spec = WorkoutSpec(name="Threshold", steps=[
            Step("warmup", minutes=10, target=hr_zone(2)),
            Repeat(5, [Step("interval", minutes=4, target=pace("5:11", "5:32")),
                       Step("recovery", minutes=1.5)]),
            Step("cooldown", minutes=10),
        ])
        assert spec.name == "Threshold"
        assert "Threshold" in spec.preview()

    def test_requires_steps(self):
        with pytest.raises(ValidationError):
            WorkoutSpec(name="x", steps=[])

    def test_requires_name(self):
        with pytest.raises(ValidationError):
            WorkoutSpec(name="", steps=[Step("interval", minutes=1)])
