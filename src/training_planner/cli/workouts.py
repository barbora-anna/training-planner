"""List, delete, or bulk-delete Garmin Connect workouts."""

from __future__ import annotations

import argparse

from ..garmin.library import WorkoutLibrary


def _fmt_duration(seconds) -> str:
    return f"{int(seconds) // 60} min" if seconds else "?"


def cmd_list(lib: WorkoutLibrary, args) -> None:
    workouts = list(lib.iterate())
    if not workouts:
        print("No workouts found.")
        return
    print(f"{'workoutId':>12}  {'duration':>8}  name")
    for w in workouts:
        print(f"{w.get('workoutId'):>12}  {_fmt_duration(w.get('estimatedDurationInSecs')):>8}  {w.get('workoutName')}")


def cmd_delete(lib: WorkoutLibrary, args) -> None:
    lib.delete(args.workout_id)
    print(f"Deleted workout {args.workout_id}")


def cmd_delete_by_name(lib: WorkoutLibrary, args) -> None:
    deleted = lib.delete_by_name(args.name)
    if not deleted:
        print(f"No workouts named {args.name!r}.")
        return
    for workout_id in deleted:
        print(f"Deleted {workout_id}  {args.name!r}")
    print(f"Deleted {len(deleted)} workout(s).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="List all workouts (id, duration, name).")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("delete", help="Delete a workout by ID.")
    p.add_argument("workout_id"); p.set_defaults(func=cmd_delete)

    p = sub.add_parser("delete-by-name", help="Delete every workout with an exact name.")
    p.add_argument("name"); p.set_defaults(func=cmd_delete_by_name)

    args = parser.parse_args()
    lib = WorkoutLibrary.connect()
    args.func(lib, args)


if __name__ == "__main__":
    main()
