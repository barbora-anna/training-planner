"""The spec-walking every discipline reuses.

Disciplines differ only in their group class (both `.times` + `.steps`) and their per-step
builder / duration fn, so the ordering bookkeeping and duration rollup live here once.
"""

from __future__ import annotations

from collections.abc import Callable

from garminconnect.workout import create_repeat_group

__all__ = ["_assemble", "_estimate"]


def _assemble(elements: list, group_cls: type, build_child: Callable) -> list:
    """Walk spec elements into ordered Garmin steps, numbering repeat groups + children."""
    steps: list = []
    order = 1
    for el in elements:
        if isinstance(el, group_cls):
            group_order = order  # the repeat group is numbered before its children
            order += 1
            children = []
            for s in el.steps:
                children.append(build_child(s, order))
                order += 1
            steps.append(create_repeat_group(el.times, children, group_order))
        else:
            steps.append(build_child(el, order))
            order += 1
    return steps


def _estimate(elements: list, group_cls: type, step_seconds: Callable) -> int:
    """Sum estimated durations, expanding repeat groups by their `times`."""
    total = 0.0
    for el in elements:
        if isinstance(el, group_cls):
            total += el.times * sum(step_seconds(s) for s in el.steps)
        else:
            total += step_seconds(el)
    return int(total)
