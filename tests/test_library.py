"""WorkoutLibrary — pagination, name reconciliation, and upsert — via a fake client."""

import pytest

from training_planner.garmin.library import WorkoutLibrary


class FakeWorkout:
    """Stands in for a garminconnect RunningWorkout (only what the library touches)."""

    def __init__(self, name):
        self.workoutName = name

    def to_dict(self):
        return {"workoutName": self.workoutName}


class FakeClient:
    """In-memory stand-in for the Garmin client, with an offset-paged workout list."""

    def __init__(self, workouts=None):
        self._workouts = list(workouts or [])
        self._next_id = 1000
        self.garmin_workouts = "https://example/workout-service"
        self.client = self  # so lib.update() -> self.client.client.put(...) resolves
        self.deleted = []
        self.scheduled = []
        self.put_calls = []

    def get_workouts(self, start=0, limit=100):
        return self._workouts[start:start + limit]

    def upload_running_workout(self, workout):
        wid = self._next_id
        self._next_id += 1
        self._workouts.append({"workoutName": workout.workoutName, "workoutId": wid})
        return {"workoutId": wid}

    def delete_workout(self, wid):
        self.deleted.append(wid)
        self._workouts = [w for w in self._workouts if w.get("workoutId") != wid]

    def schedule_workout(self, wid, date):
        self.scheduled.append((wid, date))
        return {"ok": True}

    def put(self, *args, **kwargs):
        self.put_calls.append((args, kwargs))
        return {"ok": True}


def _named(n, start=0):
    return [{"workoutName": f"w{i}", "workoutId": i} for i in range(start, start + n)]


class TestPagination:
    @pytest.mark.parametrize("total", [0, 100, 305])  # empty / exact page / multi-page remainder
    def test_iterate_yields_every_workout(self, total):
        lib = WorkoutLibrary(FakeClient(_named(total)))
        assert len(list(lib.iterate())) == total

    def test_find_by_name_across_page_boundary(self):
        lib = WorkoutLibrary(FakeClient(_named(305)))
        assert lib.find_by_name("w300")["workoutId"] == 300

    def test_find_by_name_missing(self):
        assert WorkoutLibrary(FakeClient(_named(10))).find_by_name("nope") is None


class TestDeleteByName:
    def test_deletes_all_matches_only(self):
        workouts = ([{"workoutName": "dup", "workoutId": i} for i in range(3)]
                    + [{"workoutName": "keep", "workoutId": 9}])
        client = FakeClient(workouts)
        lib = WorkoutLibrary(client)
        ids = lib.delete_by_name("dup")
        assert sorted(ids) == [0, 1, 2]
        assert sorted(client.deleted) == [0, 1, 2]
        assert lib.find_by_name("keep") is not None


class TestUpsert:
    def test_creates_when_absent(self):
        result = WorkoutLibrary(FakeClient()).upsert(FakeWorkout("A"))
        assert result == {"action": "created", "workoutId": 1000}

    def test_updates_in_place_when_present(self):
        client = FakeClient([{"workoutName": "A", "workoutId": 42}])
        result = WorkoutLibrary(client).upsert(FakeWorkout("A"))
        assert result == {"action": "updated", "workoutId": 42}
        assert client.put_calls          # went through the in-place PUT
        assert client.deleted == []      # nothing deleted

    def test_replace_strategy_deletes_and_recreates(self):
        client = FakeClient([{"workoutName": "A", "workoutId": 42}])
        result = WorkoutLibrary(client).upsert(FakeWorkout("A"), strategy="replace")
        assert result["action"] == "replaced"
        assert 42 in client.deleted
        assert result["workoutId"] != 42

    def test_rejects_unknown_strategy(self):
        with pytest.raises(ValueError):
            WorkoutLibrary(FakeClient()).upsert(FakeWorkout("A"), strategy="bogus")
