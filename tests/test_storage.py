"""The Store layer — round-trips and versioning against a tmp_path (no network)."""

import datetime

from training_planner.models.athlete import FitnessSnapshot, HealthStatus, Profile
from training_planner.models.plan import Block, Target, Week, run_session
from training_planner.models.workout import Step, WorkoutSpec, hr_zone
from training_planner.storage import (
    CampaignStore,
    HealthStatusStore,
    ProfileStore,
    SnapshotStore,
)


class TestProfileStore:
    def test_save_and_load(self, tmp_path):
        store = ProfileStore(base=tmp_path)
        store.save(Profile(name="A", target_preference="pace",
                           updated_on=datetime.date(2026, 1, 1)))
        loaded = store.load()
        assert loaded.name == "A"
        assert loaded.target_preference == "pace"

    def test_load_absent_returns_none(self, tmp_path):
        assert ProfileStore(base=tmp_path).load() is None

    def test_archive_never_clobbers_same_day(self, tmp_path):
        store = ProfileStore(base=tmp_path)
        day = datetime.date(2026, 1, 1)
        store.save(Profile(name="v1", updated_on=day))
        store.save(Profile(name="v2", updated_on=day))  # archives v1 under 2026-01-01
        store.save(Profile(name="v3", updated_on=day))  # must NOT overwrite v1's archive
        archives = list((tmp_path / "profile-history").glob("*.json"))
        assert len(archives) == 2
        assert store.load().name == "v3"


class TestSnapshotStore:
    @staticmethod
    def _snap(date):
        return FitnessSnapshot(date=datetime.date.fromisoformat(date))

    def test_latest_picks_newest_by_date(self, tmp_path):
        store = SnapshotStore(base=tmp_path)
        for d in ["2026-06-01", "2026-06-15", "2026-06-08"]:
            store.save(self._snap(d))
        assert store.latest().date == datetime.date(2026, 6, 15)

    def test_latest_none_when_empty(self, tmp_path):
        assert SnapshotStore(base=tmp_path).latest() is None

    def test_at_specific_date(self, tmp_path):
        store = SnapshotStore(base=tmp_path)
        store.save(self._snap("2026-06-01"))
        assert store.at("2026-06-01").date == datetime.date(2026, 6, 1)
        assert store.at("2026-06-02") is None

    def test_history_is_sorted(self, tmp_path):
        store = SnapshotStore(base=tmp_path)
        for d in ["2026-06-15", "2026-06-01"]:
            store.save(self._snap(d))
        assert [s.date for s in store.history()] == [
            datetime.date(2026, 6, 1), datetime.date(2026, 6, 15),
        ]


class TestHealthStatusStore:
    def test_absent_is_none(self, tmp_path):
        assert HealthStatusStore(base=tmp_path).get() is None

    def test_set_get_clear(self, tmp_path):
        store = HealthStatusStore(base=tmp_path)
        store.set(HealthStatus(date=datetime.date(2026, 1, 1), status="recovering"))
        assert store.get().status == "recovering"
        store.clear()
        assert store.get() is None


class TestCampaignStore:
    @staticmethod
    def _block():
        w = WorkoutSpec(name="w", steps=[Step("interval", minutes=30, target=hr_zone(2))])
        wk = Week(index=1, phase="base", sessions=[
            run_session(date="2026-08-01", title="easy", intent="easy", workout=w)])
        return Block(target=Target(name="Goal", distance_km=10), weeks=[wk])

    def test_target_round_trip(self, tmp_path):
        store = CampaignStore(base=tmp_path)
        store.save_target("goal", Target(name="Goal", distance_km=5))
        assert store.get_target("goal").name == "Goal"

    def test_save_block_writes_md_and_archives_prior(self, tmp_path):
        store = CampaignStore(base=tmp_path)
        store.save_block("goal", self._block())
        assert (tmp_path / "goal" / "block.json").exists()
        assert (tmp_path / "goal" / "block.md").exists()
        store.save_block("goal", self._block())  # second save archives the first
        archives = list((tmp_path / "goal" / "history").glob("*.json"))
        assert len(archives) == 1

    def test_list_returns_sorted_slugs(self, tmp_path):
        store = CampaignStore(base=tmp_path)
        store.save_target("b", Target(name="B"))
        store.save_target("a", Target(name="A"))
        assert store.list() == ["a", "b"]

    def test_get_block_absent_is_none(self, tmp_path):
        assert CampaignStore(base=tmp_path).get_block("nope") is None
