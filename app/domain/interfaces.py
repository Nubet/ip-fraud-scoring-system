from abc import ABC, abstractmethod

from app.domain.models import Client


class IPNetworkRepository(ABC):
    @abstractmethod
    async def is_data_center(self, ip: str) -> bool:
        ...


class VelocityCache(ABC):
    @abstractmethod
    async def increment_and_get_requests(self, ip: str) -> int:
        ...


class ClientRepository(ABC):
    @abstractmethod
    async def get_by_api_key(self, api_key: str) -> Client | None:
        ...
