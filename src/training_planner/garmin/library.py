"""WorkoutLibrary — a thin repository over Garmin Connect's workout endpoints.

Holds one authenticated client and exposes list / find / create / update / delete /
schedule, plus an `upsert` that reconciles by name so re-pushing the same workout
updates it in place instead of piling up duplicates. The library
(python-garminconnect) has no update helper, so `update` issues the PUT directly.

    lib = WorkoutLibrary.connect()        # logs in (resumes cached token)
    lib.upsert(spec_to_garmin(spec))      # create or update-in-place by name
"""

from __future__ import annotations

from typing import Iterator

from garminconnect import Garmin
from garminconnect.workout import RunningWorkout

from .client import get_client

_PAGE = 100  # Garmin's workout-service page size


class WorkoutLibrary:
    """Repository over Garmin's workout-service endpoints."""

    def __init__(self, client: Garmin):
        self.client = client

    @classmethod
    def connect(cls) -> "WorkoutLibrary":
        """Resume the cached Garmin session and wrap the client."""
        return cls(get_client())

    # --- reads ----------------------------------------------------------------

    def list(self, limit: int = _PAGE) -> list[dict]:
        return self.client.get_workouts(limit=limit)

    def iterate(self) -> Iterator[dict]:
        """Yield every workout, paging through the library `_PAGE` at a time."""
        start = 0
        while True:
            page = self.client.get_workouts(start=start, limit=_PAGE)
            yield from page
            if len(page) < _PAGE:      # short (or empty) page => last one
                return
            start += _PAGE

    def _iter_by_name(self, name: str) -> Iterator[dict]:
        """Yield every workout whose name matches exactly, scanning the whole library."""
        return (w for w in self.iterate() if w.get("workoutName") == name)

    def find_by_name(self, name: str) -> dict | None:
        """First workout with this exact name, or None. Scans the whole library."""
        return next(self._iter_by_name(name), None)

    # --- writes ---------------------------------------------------------------

    def create(self, workout: RunningWorkout) -> dict:
        return self.client.upload_running_workout(workout)

    def update(self, workout_id: int | str, workout: RunningWorkout):
        """Update a workout in place via PUT — preserves its ID and any scheduling."""
        workout_id = int(workout_id)
        payload = workout.to_dict()
        payload["workoutId"] = workout_id
        url = f"{self.client.garmin_workouts}/workout/{workout_id}"
        return self.client.client.put("connectapi", url, json=payload, api=True)

    def delete(self, workout_id: int | str) -> None:
        self.client.delete_workout(workout_id)

    def delete_by_name(self, name: str) -> list:
        """Delete every workout with this exact name; return the deleted IDs."""
        ids = [w.get("workoutId") for w in self._iter_by_name(name)]
        for workout_id in ids:
            self.client.delete_workout(workout_id)
        return ids

    def schedule(self, workout_id: int | str, date_str: str) -> dict:
        return self.client.schedule_workout(workout_id, date_str)

    # --- compound -------------------------------------------------------------

    def upsert(self, workout: RunningWorkout, *, strategy: str = "update") -> dict:
        """Create the workout, or reconcile an existing one with the same name.

        - strategy="update"  (default): in-place PUT — preserves workoutId + schedule.
        - strategy="replace": delete the old one and create fresh — new workoutId.

        Returns {"action": "created"|"updated"|"replaced", "workoutId": <id>}.
        """
        if strategy not in ("update", "replace"):
            raise ValueError(f"strategy must be 'update' or 'replace', got {strategy!r}")

        if not (existing := self.find_by_name(workout.workoutName)):
            result = self.create(workout)
            return {"action": "created", "workoutId": result.get("workoutId")}

        workout_id = existing["workoutId"]
        if strategy == "replace":
            self.delete(workout_id)
            result = self.create(workout)
            return {"action": "replaced", "workoutId": result.get("workoutId")}

        self.update(workout_id, workout)
        return {"action": "updated", "workoutId": workout_id}
