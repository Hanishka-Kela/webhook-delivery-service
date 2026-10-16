from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from jwt import InvalidTokenError

from webhook_delivery_service.infrastructure.config.settings import get_settings


def create_access_token(user_id: UUID) -> str:
    settings = get_settings()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def verify_access_token(token: str) -> UUID:
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["sub", "exp", "type"]},
        )

        if payload["type"] != "access":
            raise ValueError("Invalid token type")

        subject = payload["sub"]

        if not isinstance(subject, str):
            raise ValueError("Invalid token subject")

        return UUID(subject)

    except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise ValueError("Invalid token") from exc