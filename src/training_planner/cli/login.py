"""Sign in to Garmin — the password-free, human-run entry point.

Resumes an existing cached session, or (if there's none) prompts for your email,
password, and MFA code, mints OAuth tokens, and caches them. Your password is typed
hidden and is NEVER written to disk — only the token cache is saved. Afterwards
everything resumes from the cached token, so you don't need the password again unless
it expires or is revoked.

Run this yourself (directly, or via the `./train` launcher) — never inside the agent.

    uv run garmin-login
"""

from __future__ import annotations

import getpass
import os

from garminconnect import Garmin

from ..garmin.client import DEFAULT_TOKENSTORE, resume


def main() -> None:
    client = resume()
    if client is None:                       # no cached session — log in and mint one
        # GARMIN_EMAIL (optional, in .env) just pre-fills the prompt; the password is
        # always typed interactively and never read from the environment.
        email = os.getenv("GARMIN_EMAIL") or input("Garmin email: ").strip()
        password = getpass.getpass("Garmin password (hidden, not stored): ")
        client = Garmin(email, password, prompt_mfa=lambda: input("Garmin MFA code: ").strip())
        client.login(DEFAULT_TOKENSTORE)     # full login + cache the token
    print(f"\n✅ Logged in to Garmin as {client.get_full_name()}.")
    print(f"   Session cached to {DEFAULT_TOKENSTORE} — no password needed from now on.")


if __name__ == "__main__":
    main()
