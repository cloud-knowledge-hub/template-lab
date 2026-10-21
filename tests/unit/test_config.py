from __future__ import annotations

from typing import Any, cast

import pytest
from pydantic import ValidationError

from app.config import Environment, LogLevel, Settings


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [(" debug ", "DEBUG"), ("info", "INFO"), ("WARNING", "WARNING")],
)
def test_log_level_is_normalized(raw_value: str, expected: LogLevel) -> None:
    settings = Settings(log_level=cast(Any, raw_value))

    assert settings.log_level == expected


def test_invalid_log_level_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(log_level=cast(Any, "verbose"))


@pytest.mark.parametrize(
    ("app_name", "host", "expected_app_name", "expected_host"),
    [
        ("  sample-app  ", "localhost", "sample-app", "localhost"),
        ("sample-app", "  localhost  ", "sample-app", "localhost"),
    ],
)
def test_text_fields_are_trimmed(
    app_name: str, host: str, expected_app_name: str, expected_host: str
) -> None:
    settings = Settings(app_name=app_name, host=host)

    assert settings.app_name == expected_app_name
    assert settings.host == expected_host


@pytest.mark.parametrize("blank_field", ["app_name", "host"])
def test_blank_text_fields_are_rejected(blank_field: str) -> None:
    with pytest.raises(ValidationError):
        if blank_field == "app_name":
            Settings(app_name="   ")
        else:
            Settings(host="   ")


def test_debug_is_rejected_in_production() -> None:
    with pytest.raises(ValidationError, match="DEBUG=true is forbidden"):
        Settings(environment="prod", debug=True)


def test_debug_is_allowed_in_production_when_disabled() -> None:
    settings = Settings(environment="prod", debug=False)

    assert settings.environment == "prod"
    assert settings.debug is False


@pytest.mark.parametrize(
    ("environment", "expected"),
    [("local", True), ("dev", True), ("test", False), ("staging", False), ("prod", False)],
)
def test_docs_enabled_depends_on_environment(environment: str, expected: bool) -> None:
    settings = Settings(environment=cast(Environment, environment), debug=False)

    assert settings.docs_enabled is expected
