
from collections.abc import Callable
from types import TracebackType

from sqlalchemy.orm import Session

from webhook_delivery_service.application.unit_of_work import UnitOfWork
from webhook_delivery_service.infrastructure.persistence.database import SessionLocal


class SQLAlchemyUnitOfWork(UnitOfWork):

    def __init__(
        self,
        session_factory: Callable[[], Session] = SessionLocal,
    ) -> None:
        self.session_factory = session_factory
        self.session: Session | None = None

    def __enter__(self) -> "SQLAlchemyUnitOfWork":
        self.session = self.session_factory()
        return self

    def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("Unit of Work is not active")

        self.session.commit()

    def rollback(self) -> None:
        if self.session is None:
            raise RuntimeError("Unit of Work is not active")

        self.session.rollback()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            if self.session is not None:
                self.session.rollback()
        finally:
            if self.session is not None:
                self.session.close()
                self.session = None
