"""spec_to_garmin — the pure translation layer: step ordering, target encoding, duration."""

from training_planner.garmin.translate import (
    _estimate,
    _step_seconds,
    spec_to_garmin,
)
from training_planner.models.running import (
    Repeat,
    Step,
    WorkoutSpec,
    hr_range,
    hr_zone,
    pace,
)


def _steps(spec):
    return spec_to_garmin(spec).to_dict()["workoutSegments"][0]["workoutSteps"]


class TestStepOrdering:
    def test_repeat_group_numbered_before_children(self):
        spec = WorkoutSpec(name="t", steps=[
            Step("warmup", minutes=10),
            Repeat(3, [Step("interval", minutes=4), Step("recovery", minutes=2)]),
            Step("cooldown", minutes=10),
        ])
        steps = _steps(spec)
        assert steps[0]["stepOrder"] == 1                     # warmup
        assert steps[1]["stepOrder"] == 2                     # repeat group (before its children)
        assert steps[1]["numberOfIterations"] == 3
        assert [k["stepOrder"] for k in steps[1]["workoutSteps"]] == [3, 4]
        assert steps[2]["stepOrder"] == 5                     # cooldown


class TestTargetEncoding:
    def test_pace_is_ascending_speed_mps(self):
        # pace 5:00–5:20 => fast=300, slow=320 s/km; One=slower speed (<), Two=faster (>)
        step = _steps(WorkoutSpec(name="t", steps=[
            Step("interval", km=1, target=pace("5:00", "5:20"))]))[0]
        assert step["targetType"]["workoutTargetTypeKey"] == "pace.zone"
        assert step["targetValueOne"] < step["targetValueTwo"]
        assert round(step["targetValueOne"], 3) == round(1000 / 320, 3)
        assert round(step["targetValueTwo"], 3) == round(1000 / 300, 3)

    def test_hr_zone_uses_zone_number(self):
        step = _steps(WorkoutSpec(name="t", steps=[
            Step("interval", minutes=5, target=hr_zone(2))]))[0]
        assert step["targetType"]["workoutTargetTypeKey"] == "heart.rate.zone"
        assert step["zoneNumber"] == 2

    def test_hr_range_uses_bpm(self):
        step = _steps(WorkoutSpec(name="t", steps=[
            Step("interval", minutes=5, target=hr_range(140, 155))]))[0]
        assert step["targetType"]["workoutTargetTypeKey"] == "heart.rate.zone"
        assert (step["targetValueOne"], step["targetValueTwo"]) == (140, 155)

    def test_no_target(self):
        step = _steps(WorkoutSpec(name="t", steps=[Step("cooldown", minutes=5)]))[0]
        assert step["targetType"]["workoutTargetTypeKey"] == "no.target"


class TestDurationEstimate:
    def test_time_step_is_exact(self):
        assert _step_seconds(Step("interval", minutes=4)) == 240

    def test_distance_with_pace_is_derived(self):
        # 1 km at 5:00–5:20 -> avg 310 s/km
        assert _step_seconds(Step("interval", km=1, target=pace("5:00", "5:20"))) == 310

    def test_distance_without_pace_uses_fallback(self):
        secs = _step_seconds(Step("interval", km=1, target=hr_zone(2)))
        assert round(secs, 1) == round(1000 / 2.7, 1)

    def test_estimate_sums_including_repeats(self):
        elems = [
            Step("warmup", minutes=10),
            Repeat(2, [Step("interval", minutes=4), Step("recovery", minutes=1)]),
        ]
        assert _estimate(elems, Repeat, _step_seconds) == 600 + 2 * (240 + 60)

    def test_estimated_duration_present_in_payload(self):
        d = spec_to_garmin(WorkoutSpec(name="t", steps=[Step("interval", minutes=5)])).to_dict()
        assert d["estimatedDurationInSecs"] == 300
