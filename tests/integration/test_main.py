from __future__ import annotations

from typing import cast

import pytest
from fastapi.testclient import TestClient

from app.config import Environment, Settings
from app.main import create_app


@pytest.mark.parametrize("environment", ["local", "dev"])
def test_health_endpoint_and_docs_are_available(environment: str) -> None:
    app = create_app(Settings(environment=cast(Environment, environment), debug=True))

    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok", "environment": environment}
        assert client.get("/docs").status_code == 200
        assert client.get("/openapi.json").status_code == 200


def test_docs_are_disabled_in_production() -> None:
    app = create_app(Settings(environment="prod", debug=False))

    with TestClient(app) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/redoc").status_code == 404
        assert client.get("/openapi.json").status_code == 404


def test_lifespan_runs_successfully() -> None:
    app = create_app(Settings(environment="test", debug=True))

    with TestClient(app):
        pass
