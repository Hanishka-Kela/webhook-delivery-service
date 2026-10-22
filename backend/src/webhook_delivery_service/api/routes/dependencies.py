from webhook_delivery_service.infrastructure.persistence.database import SessionLocal
from webhook_delivery_service.infrastructure.repositories.user import UserRepository
from webhook_delivery_service.application.services.auth import AuthService
from sqlalchemy.orm import Session
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_auth_service(db:Session = Depends(get_db)):

    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository, session=db)
    return auth_service