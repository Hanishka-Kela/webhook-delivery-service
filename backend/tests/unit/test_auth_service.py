from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError

from webhook_delivery_service.application.services.auth import AuthService
from webhook_delivery_service.domain.schemas.user import User as DomainUser
from webhook_delivery_service.infrastructure.security.password import verify_password


@pytest.fixture
def auth_setup():
    session = Mock()
    repository = Mock()

    repository.exists_by_email.return_value = False
    repository.create.side_effect = lambda user: user

    service = AuthService(
        user_repository=repository,
        session=session,
    )

    return service, repository, session


def test_signup_success(auth_setup):
    service, repository, session = auth_setup

    user = service.sign_up(
        email="test@example.com",
        password="SecurePassword123",
        confirm_password="SecurePassword123",
    )

    assert isinstance(user, DomainUser)
    assert user.email == "test@example.com"
    assert verify_password("SecurePassword123", user.hashed_password)

    repository.create.assert_called_once()
    session.commit.assert_called_once()
    session.rollback.assert_not_called()


def test_signup_password_mismatch(auth_setup):
    service, repository, session = auth_setup

    with pytest.raises(ValueError, match="Passwords don't match"):
        service.sign_up(
            email="test@example.com",
            password="SecurePassword123",
            confirm_password="DifferentPassword123",
        )

    repository.create.assert_not_called()
    session.commit.assert_not_called()


def test_signup_existing_email(auth_setup):
    service, repository, session = auth_setup

    repository.exists_by_email.return_value = True

    with pytest.raises(ValueError, match="User already exists"):
        service.sign_up(
            email="test@example.com",
            password="SecurePassword123",
            confirm_password="SecurePassword123",
        )

    repository.create.assert_not_called()
    session.commit.assert_not_called()


def test_signup_integrity_error(auth_setup):
    service, repository, session = auth_setup

    repository.create.side_effect = IntegrityError(
        statement="INSERT INTO users",
        params={},
        orig=Exception("unique constraint violation"),
    )

    with pytest.raises(ValueError, match="User already exists"):
        service.sign_up(
            email="test@example.com",
            password="SecurePassword123",
            confirm_password="SecurePassword123",
        )

    session.rollback.assert_called_once()
    session.commit.assert_not_called()


def test_signup_commit_failure(auth_setup):
    service, _, session = auth_setup

    session.commit.side_effect = RuntimeError("Database unavailable")

    with pytest.raises(RuntimeError, match="Database unavailable"):
        service.sign_up(
            email="test@example.com",
            password="SecurePassword123",
            confirm_password="SecurePassword123",
        )

    session.rollback.assert_called_once()


def test_signup_returns_repository_result(auth_setup):
    service, repository, session = auth_setup

    persisted_user = DomainUser(
        email="test@example.com",
        hashed_password="stored-hash",
    )

    repository.create.return_value = persisted_user
    repository.create.side_effect = None

    result = service.sign_up(
        email="test@example.com",
        password="SecurePassword123",
        confirm_password="SecurePassword123",
    )

    assert result is persisted_user
    session.commit.assert_called_once()
