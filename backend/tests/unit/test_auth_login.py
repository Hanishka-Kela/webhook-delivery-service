from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from webhook_delivery_service.application.services.auth import AuthService
from webhook_delivery_service.domain.schemas.user import User as DomainUser
from webhook_delivery_service.infrastructure.security.password import hash_password


@pytest.fixture
def auth_setup():
    session = Mock()
    repository = Mock()

    user = DomainUser(
        id=uuid4(),
        email="test@example.com",
        hashed_password=hash_password("SecurePassword123"),
        is_active=True,
    )

    repository.get_by_email.return_value = user

    service = AuthService(
        user_repository=repository,
        session=session,
    )

    return service, repository, session, user


def test_login_success(auth_setup):
    service, repository, session, user = auth_setup

    with patch(
        "webhook_delivery_service.application.services.auth.create_access_token",
        return_value="test-access-token",
    ) as create_token:
        token = service.login(
            email="test@example.com",
            password="SecurePassword123",
        )

    assert token == "test-access-token"
    repository.get_by_email.assert_called_once_with("test@example.com")
    create_token.assert_called_once_with(user.id)
    session.commit.assert_not_called()


def test_login_nonexistent_user(auth_setup):
    service, repository, session, _ = auth_setup

    repository.get_by_email.return_value = None

    with pytest.raises(ValueError, match="Invalid credentials"):
        service.login(
            email="missing@example.com",
            password="SecurePassword123",
        )

    session.commit.assert_not_called()


def test_login_wrong_password(auth_setup):
    service, _, session, _ = auth_setup

    with pytest.raises(ValueError, match="Invalid credentials"):
        service.login(
            email="test@example.com",
            password="WrongPassword123",
        )

    session.commit.assert_not_called()


def test_login_inactive_user(auth_setup):
    service, _, session, user = auth_setup

    user.is_active = False

    with pytest.raises(ValueError, match="Account is inactive"):
        service.login(
            email="test@example.com",
            password="SecurePassword123",
        )

    session.commit.assert_not_called()


def test_login_does_not_modify_database(auth_setup):
    service, repository, session, _ = auth_setup

    with patch(
        "webhook_delivery_service.application.services.auth.create_access_token",
        return_value="test-access-token",
    ):
        service.login(
            email="test@example.com",
            password="SecurePassword123",
        )

    repository.create.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_not_called()
