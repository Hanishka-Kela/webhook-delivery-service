from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from webhook_delivery_service.infrastructure.repositories.user import UserRepository
from webhook_delivery_service.domain.schemas.user import User as DomainUser
from webhook_delivery_service.infrastructure.security.password import hash_password


class AuthService:
    def __init__(self, user_repository: UserRepository, session: Session):
        self.user_repository = user_repository
        self.session = session

    def sign_up(
        self,
        email: str,
        password: str,
        confirm_password: str,
    ) -> DomainUser:

        if password != confirm_password:
            raise ValueError("Passwords don't match")

        if self.user_repository.exists_by_email(email):
            raise ValueError("User already exists")

        hashed_password = hash_password(password)

        user = DomainUser(
            email=email,
            hashed_password=hashed_password,
        )

        try:
            created_user = self.user_repository.create(user)
            self.session.commit()
            return created_user

        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError("User already exists") from exc

        except Exception:
            self.session.rollback()
            raise