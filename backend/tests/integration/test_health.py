from fastapi import status
from fastapi.testclient import TestClient

from webhook_delivery_service.main import create_app


def test_liveness_endpoint():
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}
