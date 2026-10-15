
import pytest

from fastapi import status
from fastapi.testclient import TestClient

from webhook_delivery_service.main import create_app


@pytest.fixture
def client():
    app = create_app()

    with TestClient(app) as test_client:
        yield test_client


def test_allowed_origin(client):
    response = client.options(
        "/health/live",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.headers["access-control-allow-origin"]
        == "http://localhost:5173"
    )


def test_disallowed_origin(client):
    response = client.options(
        "/health/live",
        headers={
            "Origin": "http://malicious-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "access-control-allow-origin" not in response.headers


@pytest.mark.parametrize(
    "method",
    ["GET", "POST", "PUT", "PATCH", "DELETE"],
)
def test_allowed_http_methods(client, method):
    response = client.options(
        "/health/live",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": method,
        },
    )

    assert response.status_code == status.HTTP_200_OK


def test_disallowed_http_method(client):
    response = client.options(
        "/health/live",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "TRACE",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "header",
    ["Authorization", "Content-Type"],
)
def test_allowed_request_headers(client, header):
    response = client.options(
        "/health/live",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": header,
        },
    )

    assert response.status_code == status.HTTP_200_OK


def test_disallowed_request_header(client):
    response = client.options(
        "/health/live",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Unauthorized-Header",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_actual_request_from_allowed_origin(client):
    response = client.get(
        "/health/live",
        headers={"Origin": "http://localhost:5173"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}
    assert (
        response.headers["access-control-allow-origin"]
        == "http://localhost:5173"
    )


def test_actual_request_from_disallowed_origin(client):
    response = client.get(
        "/health/live",
        headers={"Origin": "http://malicious-site.com"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access-control-allow-origin" not in response.headers
