from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from webhook_delivery_service.application.services.auth import AuthService
from webhook_delivery_service.infrastructure.persistence.database import SessionLocal
from webhook_delivery_service.infrastructure.repositories.user import UserRepository


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_auth_service(db: Annotated[Session, Depends(get_db)]):

    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository, session=db)
    return auth_service
