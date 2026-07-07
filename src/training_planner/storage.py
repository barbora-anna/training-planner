"""The Store layer — repositories over the file layout under `agent/`.

All persistence goes through these classes, so the backend is swappable: a future
db backend reimplements the same method surface without touching callers.

    ProfileStore()       # athlete/profile.json  (+ profile-history/ on update)
    SnapshotStore()      # athlete/fitness-snapshots/<date>.json
    HealthStatusStore()  # athlete/health-status.json  (optional)
    CampaignStore()      # campaigns/<slug>/target.json + block.json (+ block.md, history/)
"""

from __future__ import annotations

import datetime
import shutil
from pathlib import Path

from .models.athlete import FitnessSnapshot, HealthStatus, Profile
from .models.plan import Block, Target

# src/training_planner/ -> repo root -> agent/
_AGENT = Path(__file__).resolve().parents[2] / "agent"


class JsonStore:
    """Shared file backend: read/write pydantic models as JSON under a base dir."""

    def __init__(self, base: Path | str):
        self.base = Path(base)

    def _load(self, path: Path, model):
        return model.model_validate_json(path.read_text()) if path.exists() else None

    def _load_all(self, directory: Path, model) -> list:
        """Every *.json in `directory`, name-sorted, parsed into `model` instances."""
        if not directory.exists():
            return []
        return [model.model_validate_json(p.read_text())
                for p in sorted(directory.glob("*.json"))]

    def _dump(self, path: Path, obj) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(obj.model_dump_json(indent=2))
        return path

    def _archive(self, current: Path, history_dir: Path, stamp: str) -> None:
        """Copy `current` into `history_dir/{stamp}.json`, never clobbering an existing archive."""
        if not current.exists():
            return
        history_dir.mkdir(parents=True, exist_ok=True)
        dest = history_dir / f"{stamp}.json"
        if dest.exists():  # keep the earlier archive for this stamp — disambiguate by time
            dest = history_dir / f"{stamp}-{datetime.datetime.now():%H%M%S%f}.json"
        shutil.copyfile(current, dest)


class ProfileStore(JsonStore):
    """Current profile, versioned: the prior version is archived on each save."""

    def __init__(self, base: Path | str = _AGENT / "athlete"):
        super().__init__(base)
        self.current = self.base / "profile.json"
        self.history_dir = self.base / "profile-history"

    def load(self) -> Profile | None:
        return self._load(self.current, Profile)

    def save(self, profile: Profile) -> None:
        prev = self.load()
        if prev is not None:
            stamp = (prev.updated_on or datetime.date.today()).isoformat()
            self._archive(self.current, self.history_dir, stamp)
        self._dump(self.current, profile)

    def history(self) -> list[Profile]:
        return self._load_all(self.history_dir, Profile)


class SnapshotStore(JsonStore):
    """Append-only dated fitness snapshots — the progress time-series."""

    def __init__(self, base: Path | str = _AGENT / "athlete" / "fitness-snapshots"):
        super().__init__(base)

    def save(self, snapshot: FitnessSnapshot) -> None:
        self._dump(self.base / f"{snapshot.date.isoformat()}.json", snapshot)

    def history(self) -> list[FitnessSnapshot]:
        return self._load_all(self.base, FitnessSnapshot)

    def latest(self) -> FitnessSnapshot | None:
        files = sorted(self.base.glob("*.json"))  # dated names => newest sorts last
        return self._load(files[-1], FitnessSnapshot) if files else None

    def at(self, date: datetime.date | str) -> FitnessSnapshot | None:
        d = date if isinstance(date, datetime.date) else datetime.date.fromisoformat(date)
        return self._load(self.base / f"{d.isoformat()}.json", FitnessSnapshot)


class HealthStatusStore(JsonStore):
    """Optional health status. `get()` returns None when absent (== healthy)."""

    def __init__(self, base: Path | str = _AGENT / "athlete"):
        super().__init__(base)
        self.file = self.base / "health-status.json"

    def get(self) -> HealthStatus | None:
        return self._load(self.file, HealthStatus)

    def set(self, status: HealthStatus) -> None:
        self._dump(self.file, status)

    def clear(self) -> None:
        self.file.unlink(missing_ok=True)


class CampaignStore(JsonStore):
    """One directory per target: target.json + block.json (+ block.md, history/)."""

    def __init__(self, base: Path | str = _AGENT / "campaigns"):
        super().__init__(base)

    def _dir(self, slug: str) -> Path:
        return self.base / slug

    def save_target(self, slug: str, target: Target) -> None:
        self._dump(self._dir(slug) / "target.json", target)

    def get_target(self, slug: str) -> Target | None:
        return self._load(self._dir(slug) / "target.json", Target)

    def save_block(self, slug: str, block: Block) -> None:
        d = self._dir(slug)
        current = d / "block.json"
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self._archive(current, d / "history", stamp)          # archive the prior version, if any
        self._dump(current, block)
        (d / "block.md").write_text(block.preview() + "\n")   # human-review rendering

    def get_block(self, slug: str) -> Block | None:
        return self._load(self._dir(slug) / "block.json", Block)

    def list(self) -> list[str]:
        if not self.base.exists():
            return []
        return sorted(p.name for p in self.base.iterdir() if p.is_dir())
