from sqlalchemy import select
from sqlalchemy.orm import Session

from uuid import UUID

from webhook_delivery_service.infrastructure.repositories.user import User as ORMUser
from webhook_delivery_service.domain.schemas.user import User as DomainUser


class UserRepository:
    def __init__(self, session: Session):
        self.session = session


    def _to_domain(self, user: ORMUser) -> DomainUser:
        return DomainUser(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash
        )

    def _to_orm(self, user: DomainUser) -> ORMUser:
        return ORMUser(
        id=user.id,
        email=user.email,
        password_hash=user.password_hash
    )

    def get_by_id(self, user_id: UUID) -> DomainUser | None:
        user = self.session.get(ORMUser, user_id)

        if user is None:
            return None

        return self._to_domain(user)

    def get_by_email(self, email: str) -> DomainUser | None:
        user = self.session.scalar(
            select(ORMUser).where(ORMUser.email == email)
        )

        if user is None:
            return None

        return self._to_domain(user)

    def create(self, user: DomainUser) -> DomainUser:
        orm_user = self._to_orm(user)
        self.session.add(orm_user)
        return user

    def exists_by_email(self, email: str) -> bool:
        return self.session.scalar(
            select(ORMUser.user_id).where(ORMUser.email == email)
        ) is not None