"""reset CLI helpers — the data/README boundary and removal (no real data touched)."""

from training_planner.cli.reset import _deletable, _remove


def test_deletable_keeps_readme_only(tmp_path):
    (tmp_path / "README.md").write_text("keep me")
    (tmp_path / "health-status.json").write_text("{}")
    (tmp_path / "fitness-snapshots").mkdir()
    assert {p.name for p in _deletable(tmp_path)} == {"health-status.json", "fitness-snapshots"}


def test_deletable_absent_root_is_empty(tmp_path):
    assert _deletable(tmp_path / "nope") == []


def test_remove_handles_file_and_dir(tmp_path):
    f = tmp_path / "a.json"; f.write_text("{}")
    d = tmp_path / "camp"; d.mkdir(); (d / "target.json").write_text("{}")
    _remove(f)
    _remove(d)
    assert not f.exists() and not d.exists()
