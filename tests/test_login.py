"""garmin-login CLI — the non-blocking `--resume-only` path (no network, no prompts)."""

import training_planner.cli.login as login


def _no_prompt(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("resume-only must never prompt")
    monkeypatch.setattr("builtins.input", boom)
    monkeypatch.setattr("getpass.getpass", boom)


def test_resume_only_without_session_continues_silently(monkeypatch, capsys):
    monkeypatch.setattr(login, "resume", lambda: None)   # no cached token
    _no_prompt(monkeypatch)
    login.main(["--resume-only"])                        # must not raise / prompt
    assert "Strava-only" in capsys.readouterr().out


def test_resume_only_with_session_reports_login(monkeypatch, capsys):
    class FakeClient:
        def get_full_name(self):
            return "Test Athlete"
    monkeypatch.setattr(login, "resume", lambda: FakeClient())
    _no_prompt(monkeypatch)
    login.main(["--resume-only"])
    assert "Test Athlete" in capsys.readouterr().out
