"""Wipe the athlete's data — profile, snapshots, health, and every campaign — to start clean.

Removes everything under `agent/athlete/` and `agent/campaigns/` **except** the tracked
`README.md` in each: the folder structure stays, your personal data goes. Destructive, so it
lists what it will delete and asks you to confirm. Your Garmin login (cached token) is not
touched.

    uv run reset            # list what will go, then confirm
    uv run reset --yes      # skip the prompt (non-interactive)
    uv run reset --dry-run  # show what would be deleted, delete nothing
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from ..storage import CampaignStore, ProfileStore

_KEEP = {"README.md"}          # tracked structure — never delete


def _deletable(root: Path) -> list[Path]:
    """Top-level entries under `root` that count as data (everything but the README)."""
    if not root.exists():
        return []
    return sorted(p for p in root.iterdir() if p.name not in _KEEP)


def _remove(path: Path) -> None:
    shutil.rmtree(path) if path.is_dir() else path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-y", "--yes", action="store_true", help="Skip the confirmation prompt.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be deleted, delete nothing.")
    args = parser.parse_args()

    # athlete/ and campaigns/ roots, via the stores (single source of truth for paths).
    roots = [ProfileStore().base, CampaignStore().base]
    targets = [(root, _deletable(root)) for root in roots]
    total = sum(len(items) for _, items in targets)

    if total == 0:
        print("Already clean — no athlete data or campaigns to remove.")
        return

    print("This will permanently delete:")
    for root, items in targets:
        for p in items:
            kind = "dir " if p.is_dir() else "file"
            print(f"  {kind}  {p.relative_to(root.parent)}")
    print(f"\n({total} item(s); each folder's README.md is kept. Your Garmin login is untouched.)")

    if args.dry_run:
        print("\nDry run — nothing deleted.")
        return

    if not args.yes and input("\nType 'yes' to delete everything above: ").strip().lower() != "yes":
        print("Aborted — nothing deleted.")
        return

    for _, items in targets:
        for p in items:
            _remove(p)
    print(f"Done — removed {total} item(s). You're starting clean.")


if __name__ == "__main__":
    main()
