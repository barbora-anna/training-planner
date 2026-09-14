"""Validate and persist targets/blocks through the Store layer.

The Advisor drafts target/block JSON (matching the plan.py models), then runs this to VALIDATE
it against the pydantic models and SAVE it via the stores — so a malformed plan is
caught before it lands, and block.md + history are written automatically.

    uv run plan validate <block.json>
    uv run plan save-target <slug> <target.json>
    uv run plan save-block  <slug> <block.json>
    uv run plan show <slug>
    uv run plan list
    uv run plan delete <slug>          # list what will go, then confirm
    uv run plan delete <slug> --yes    # skip the prompt (non-interactive)
    uv run plan delete <slug> --dry-run  # show what would be deleted, delete nothing
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..models.plan import Block, Target
from ..storage import CampaignStore


def _read(path: str) -> str:
    return Path(path).read_text()


def cmd_validate(args) -> None:
    block = Block.model_validate_json(_read(args.file))
    print(f"OK — valid Block: {len(block.weeks)} weeks, target '{block.target.name}'")
    print(block.preview())


def cmd_save_target(args) -> None:
    target = Target.model_validate_json(_read(args.file))
    CampaignStore().save_target(args.slug, target)
    print(f"Saved target '{target.name}' -> campaigns/{args.slug}/target.json")


def cmd_save_block(args) -> None:
    block = Block.model_validate_json(_read(args.file))          # validates before saving
    CampaignStore().save_block(args.slug, block)
    print(f"Saved block ({len(block.weeks)} weeks) -> campaigns/{args.slug}/block.json (+ block.md)")
    print(block.preview())


def cmd_show(args) -> None:
    block = CampaignStore().get_block(args.slug)
    if block is None:
        sys.exit(f"No block found for '{args.slug}'.")
    print(block.preview())


def cmd_list(args) -> None:
    slugs = CampaignStore().list()
    print("\n".join(slugs) if slugs else "No campaigns yet.")


def cmd_delete(args) -> None:
    store = CampaignStore()
    d = store._dir(args.slug)
    if not d.exists():
        sys.exit(f"No campaign '{args.slug}' found.")

    items = sorted(d.rglob("*"))
    files = [p for p in items if p.is_file()]
    print(f"This will permanently delete campaigns/{args.slug}/ ({len(files)} file(s)):")
    for p in files:
        print(f"  {p.relative_to(store.base)}")

    if args.dry_run:
        print("\nDry run — nothing deleted.")
        return

    if not args.yes and input(f"\nType 'yes' to delete '{args.slug}': ").strip().lower() != "yes":
        print("Aborted — nothing deleted.")
        return

    store.delete(args.slug)
    print(f"Done — removed campaigns/{args.slug}/.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="Validate a block JSON against the model (no save).")
    p.add_argument("file"); p.set_defaults(func=cmd_validate)

    p = sub.add_parser("save-target", help="Validate + save a target.")
    p.add_argument("slug"); p.add_argument("file"); p.set_defaults(func=cmd_save_target)

    p = sub.add_parser("save-block", help="Validate + save a block (writes block.md, archives prior).")
    p.add_argument("slug"); p.add_argument("file"); p.set_defaults(func=cmd_save_block)

    p = sub.add_parser("show", help="Print a saved block's preview.")
    p.add_argument("slug"); p.set_defaults(func=cmd_show)

    p = sub.add_parser("list", help="List campaigns.")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("delete", help="Delete a campaign's whole directory (confirms first).")
    p.add_argument("slug")
    p.add_argument("-y", "--yes", action="store_true", help="Skip the confirmation prompt.")
    p.add_argument("--dry-run", action="store_true",
                    help="Show what would be deleted, delete nothing.")
    p.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
