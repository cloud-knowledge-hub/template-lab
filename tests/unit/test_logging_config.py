from __future__ import annotations

import json
import logging
import sys
from typing import Any

from app.logging_config import JsonFormatter


def test_json_formatter_serializes_standard_log_fields() -> None:
    record = logging.LogRecord(
        name="app.example",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Hello %s",
        args=("world",),
        exc_info=None,
    )

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "app.example"
    assert payload["message"] == "Hello world"
    assert payload["timestamp"].endswith("Z")


def test_json_formatter_includes_optional_fields_and_exception() -> None:
    try:
        raise ValueError("sample failure")
    except ValueError:
        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="app.example",
        level=logging.ERROR,
        pathname=__file__,
        lineno=30,
        msg="Request failed",
        args=(),
        exc_info=exc_info,
    )
    extras: dict[str, Any] = {"request_id": "request-123", "status_code": 500}
    record.__dict__.update(extras)

    payload = json.loads(JsonFormatter().format(record))

    assert payload["request_id"] == "request-123"
    assert payload["status_code"] == 500
    assert "ValueError: sample failure" in payload["exception"]
