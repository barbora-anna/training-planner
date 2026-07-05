"""Garmin Connect client — resume the cached session (never prompts).

`resume()` / `get_client()` only ever RESUME an already-cached token, so they're safe
for the agent and any non-interactive caller: they never ask for credentials, so none
can flow through the caller. Minting a token is a separate, human-run step — the
interactive login lives in `cli/login.py` (the `garmin-login` command).

Only the token cache is written to disk (0o600 in a 0o700 dir); the sole thing read
from `.env` is an optional `GARMIN_EMAIL`, used by the login command to prefill its prompt.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from garminconnect import Garmin, GarminConnectAuthenticationError

load_dotenv()

DEFAULT_TOKENSTORE = os.path.expanduser(os.getenv("GARMINTOKENS", "~/.garminconnect"))


def resume(tokenstore: str = DEFAULT_TOKENSTORE) -> Garmin | None:
    """Return a client logged in from the cached token, or None if there's no valid session.

    Never prompts — the shared, agent-safe resume primitive. `None` means the token is
    absent/expired and a fresh (human) login is needed; genuine failures (network,
    rate-limit) propagate rather than masquerading as "no session".
    """
    client = Garmin()
    try:
        client.login(tokenstore)
        return client
    except GarminConnectAuthenticationError:
        return None


def get_client(tokenstore: str = DEFAULT_TOKENSTORE) -> Garmin:
    """Return a client resuming the cached Garmin session, or raise if there's none.

    Never prompts — safe for the agent. On a cache miss it raises `SystemExit` telling
    the user to run `garmin-login`; it never asks for credentials.
    """
    client = resume(tokenstore)
    if client is None:
        raise SystemExit(
            "No cached Garmin session. Run `uv run garmin-login` (or `./train`) once to "
            "sign in — interactive and password-free; it caches a token this resumes from."
        )
    return client


if __name__ == "__main__":
    # Quick connectivity check (resume-only).
    c = get_client()
    print(f"Connected to Garmin Connect as: {c.get_full_name()}")
