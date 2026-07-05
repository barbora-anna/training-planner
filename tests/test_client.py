"""Auth surface — resume() is soft (None on auth-miss, propagates real errors);
get_client() is hard (raises). Neither prompts. All via a fake Garmin, no network."""

import pytest
from garminconnect import (
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
)

from training_planner.garmin import client as clientmod


def _fake_garmin(login_error=None):
    class FakeGarmin:
        def __init__(self, *args, **kwargs):
            pass

        def login(self, tokenstore=None):
            if login_error is not None:
                raise login_error
            return None

    return FakeGarmin


class TestResume:
    def test_none_on_auth_error(self, monkeypatch):
        monkeypatch.setattr(clientmod, "Garmin",
                            _fake_garmin(GarminConnectAuthenticationError("no creds")))
        assert clientmod.resume("/tmp/x") is None

    def test_propagates_connection_error(self, monkeypatch):
        # a real failure must surface, not masquerade as "no session"
        monkeypatch.setattr(clientmod, "Garmin",
                            _fake_garmin(GarminConnectConnectionError("network down")))
        with pytest.raises(GarminConnectConnectionError):
            clientmod.resume("/tmp/x")

    def test_returns_client_on_success(self, monkeypatch):
        monkeypatch.setattr(clientmod, "Garmin", _fake_garmin())
        assert clientmod.resume("/tmp/x") is not None


class TestGetClient:
    def test_raises_systemexit_when_no_session(self, monkeypatch):
        monkeypatch.setattr(clientmod, "resume",
                            lambda tokenstore=clientmod.DEFAULT_TOKENSTORE: None)
        with pytest.raises(SystemExit):
            clientmod.get_client()

    def test_returns_client_when_resumed(self, monkeypatch):
        sentinel = object()
        monkeypatch.setattr(clientmod, "resume",
                            lambda tokenstore=clientmod.DEFAULT_TOKENSTORE: sentinel)
        assert clientmod.get_client() is sentinel
