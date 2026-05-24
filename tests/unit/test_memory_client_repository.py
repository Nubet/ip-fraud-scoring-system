from app.adapters.memory.client_repository import InMemoryClientRepository


async def test_client_repository_reads_csv_keys() -> None:
    repo = InMemoryClientRepository.from_csv_api_keys("k1, k2, ,k3")

    assert (await repo.get_by_api_key("k1")) is not None
    assert (await repo.get_by_api_key("k2")) is not None
    assert (await repo.get_by_api_key("k3")) is not None
    assert (await repo.get_by_api_key("missing")) is None
