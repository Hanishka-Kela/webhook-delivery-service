from abc import ABC, abstractmethod
from __future__ import annotations


class UnitOfWork(ABC):
    @abstractmethod
    def commit(self)->None:
        pass

    @abstractmethod
    def rollback(self)->None:
        pass

    @abstractmethod
    def __enter__(self)->UnitOfWork:
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc, tb)->None:
        pass