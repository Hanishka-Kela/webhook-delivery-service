from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from webhook_delivery_service.application.services.auth import AuthService
from webhook_delivery_service.infrastructure.config.settings import get_settings
from webhook_delivery_service.infrastructure.persistence.models.user import (
    User as ORMUser,
)
from webhook_delivery_service.infrastructure.repositories.user import UserRepository
from webhook_delivery_service.infrastructure.security.password import verify_password


@pytest.fixture
def db_session():
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)

    connection = engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


@pytest.fixture
def auth_service(db_session):
    repository = UserRepository(db_session)

    return AuthService(
        user_repository=repository,
        session=db_session,
    )


def test_signup_persists_user(auth_service, db_session):
    email = f"{uuid4()}@example.com"

    user = auth_service.sign_up(
        email=email,
        password="SecurePassword123",
        confirm_password="SecurePassword123",
    )

    saved_user = db_session.scalar(
        select(ORMUser).where(ORMUser.email == email)
    )

    assert saved_user is not None
    assert saved_user.id == user.id
    assert saved_user.email == email
    assert saved_user.is_active is True

    assert verify_password(
        "SecurePassword123",
        saved_user.hashed_password,
    )

    assert saved_user.created_at is not None
    assert saved_user.updated_at is not None


def test_signup_rejects_duplicate_email(auth_service):
    email = f"{uuid4()}@example.com"

    auth_service.sign_up(
        email=email,
        password="SecurePassword123",
        confirm_password="SecurePassword123",
    )

    with pytest.raises(ValueError, match="User already exists"):
        auth_service.sign_up(
            email=email,
            password="AnotherPassword123",
            confirm_password="AnotherPassword123",
        )


def test_signup_repository_lookup(auth_service, db_session):
    email = f"{uuid4()}@example.com"

    created_user = auth_service.sign_up(
        email=email,
        password="SecurePassword123",
        confirm_password="SecurePassword123",
    )

    repository = UserRepository(db_session)

    retrieved_user = repository.get_by_id(created_user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == email
    assert retrieved_user.is_active is True
    assert retrieved_user.created_at is not None