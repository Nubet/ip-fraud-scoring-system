from app.domain.interfaces import ClientRepository
from app.domain.models import Client


class InMemoryClientRepository(ClientRepository):
    def __init__(self, api_key_to_client: dict[str, Client]):
        self._api_key_to_client = api_key_to_client

    @classmethod
    def from_csv_api_keys(cls, csv_api_keys: str) -> "InMemoryClientRepository":
        clients: dict[str, Client] = {}
        for idx, raw_key in enumerate(csv_api_keys.split(","), start=1):
            api_key = raw_key.strip()
            if not api_key:
                continue
            clients[api_key] = Client(client_id=f"client-{idx}", is_active=True, plan_limit=10_000)
        return cls(clients)

    async def get_by_api_key(self, api_key: str) -> Client | None:
        return self._api_key_to_client.get(api_key)
