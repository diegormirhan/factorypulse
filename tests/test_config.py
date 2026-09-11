import pytest

from factorypulse.config import load_settings


def test_config_file_supplies_the_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("FACTORYPULSE_PREDICTIONS_LOG", raising=False)

    settings = load_settings()

    assert settings.api.port == 8000
    assert settings.api.host == "0.0.0.0"
    assert settings.paths.predictions_log == settings.root / "artifacts/predictions.jsonl"


def test_port_environment_variable_overrides_the_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PORT", "10000")

    assert load_settings().api.port == 10000


def test_host_environment_variable_overrides_the_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOST", "127.0.0.1")

    assert load_settings().api.host == "127.0.0.1"


@pytest.mark.parametrize("value", ["", "http", "0", "70000", "-1"])
def test_unusable_port_fails_at_load_time(value: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PORT", value)

    if value == "":
        assert load_settings().api.port == 8000
        return
    with pytest.raises(ValueError, match="PORT"):
        load_settings()


def test_empty_prediction_log_override_disables_logging(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FACTORYPULSE_PREDICTIONS_LOG", "")

    assert load_settings().paths.predictions_log is None


def test_prediction_log_override_redirects_the_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FACTORYPULSE_PREDICTIONS_LOG", "/tmp/predictions.jsonl")

    log_path = load_settings().paths.predictions_log

    assert log_path is not None
    assert log_path.as_posix().endswith("/tmp/predictions.jsonl")
