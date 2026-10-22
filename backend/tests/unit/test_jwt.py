from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from webhook_delivery_service.infrastructure.config.settings import get_settings
from webhook_delivery_service.infrastructure.security.jwt import (
    create_access_token,
    verify_access_token,
)


@pytest.fixture
def jwt_settings():
    return get_settings()


def test_create_access_token(jwt_settings):
    user_id = uuid4()

    token = create_access_token(user_id)

    payload = jwt.decode(
        token,
        jwt_settings.JWT_SECRET_KEY.get_secret_value(),
        algorithms=[jwt_settings.JWT_ALGORITHM],
    )

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"
    assert "exp" in payload


def test_verify_valid_access_token():
    user_id = uuid4()
    token = create_access_token(user_id)

    assert verify_access_token(token) == user_id


def test_reject_expired_token(jwt_settings):
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "type": "access",
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        jwt_settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=jwt_settings.JWT_ALGORITHM,
    )

    with pytest.raises(ValueError, match="Invalid token"):
        verify_access_token(token)


def test_reject_invalid_signature(jwt_settings):
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        },
        "different-test-secret-key-at-least-32-bytes",
        algorithm=jwt_settings.JWT_ALGORITHM,
    )

    with pytest.raises(ValueError, match="Invalid token"):
        verify_access_token(token)


def test_reject_wrong_token_type(jwt_settings):
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "type": "refresh",
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        },
        jwt_settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=jwt_settings.JWT_ALGORITHM,
    )

    with pytest.raises(ValueError, match="Invalid token"):
        verify_access_token(token)


def test_reject_missing_subject(jwt_settings):
    token = jwt.encode(
        {
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        },
        jwt_settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=jwt_settings.JWT_ALGORITHM,
    )

    with pytest.raises(ValueError, match="Invalid token"):
        verify_access_token(token)


def test_reject_invalid_subject(jwt_settings):
    token = jwt.encode(
        {
            "sub": "not-a-uuid",
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        },
        jwt_settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=jwt_settings.JWT_ALGORITHM,
    )

    with pytest.raises(ValueError, match="Invalid token"):
        verify_access_token(token)


def test_reject_malformed_token():
    with pytest.raises(ValueError, match="Invalid token"):
        verify_access_token("invalid.jwt.token")
