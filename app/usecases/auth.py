from app.domain.interfaces import ClientRepository
from app.domain.models import Client


class InvalidAPIKeyError(Exception):
    """Raised when provided API key is unknown."""


class InactiveClientError(Exception):
    """Raised when client exists but is disabled."""


class APIKeyAuthUseCase:
    def __init__(self, client_repo: ClientRepository):
        self.client_repo = client_repo

    async def authenticate(self, api_key: str) -> Client:
        client = await self.client_repo.get_by_api_key(api_key)
        if client is None:
            raise InvalidAPIKeyError("Invalid API key")
        if not client.is_active:
            raise InactiveClientError("Client is inactive")
        return client
