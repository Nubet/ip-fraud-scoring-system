import pytest

from app.domain.interfaces import ClientRepository
from app.domain.models import Client
from app.usecases.auth import APIKeyAuthUseCase, InactiveClientError, InvalidAPIKeyError


class FakeClientRepo(ClientRepository):
    def __init__(self, mapping: dict[str, Client]):
        self.mapping = mapping

    async def get_by_api_key(self, api_key: str) -> Client | None:
        return self.mapping.get(api_key)


async def test_authenticate_valid_key() -> None:
    repo = FakeClientRepo({"ok": Client(client_id="c1", is_active=True, plan_limit=10)})
    use_case = APIKeyAuthUseCase(repo)

    client = await use_case.authenticate("ok")
    assert client.client_id == "c1"


async def test_authenticate_invalid_key() -> None:
    use_case = APIKeyAuthUseCase(FakeClientRepo({}))
    with pytest.raises(InvalidAPIKeyError):
        await use_case.authenticate("missing")


async def test_authenticate_inactive_client() -> None:
    repo = FakeClientRepo({"x": Client(client_id="c1", is_active=False, plan_limit=10)})
    use_case = APIKeyAuthUseCase(repo)

    with pytest.raises(InactiveClientError):
        await use_case.authenticate("x")
