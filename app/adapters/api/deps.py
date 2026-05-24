from functools import lru_cache

from app.adapters.maxmind.asn_reader import MaxMindASNReader
from app.adapters.memory.client_repository import InMemoryClientRepository
from app.adapters.memory.velocity_cache import TTLVelocityCache
from app.config import settings
from app.domain.interfaces import ClientRepository, IPNetworkRepository, VelocityCache
from app.usecases.auth import APIKeyAuthUseCase
from app.usecases.evaluate_ip import EvaluateIPUseCase


@lru_cache
def get_client_repository() -> ClientRepository:
    return InMemoryClientRepository.from_csv_api_keys(settings.valid_api_keys)


@lru_cache
def get_velocity_cache() -> VelocityCache:
    return TTLVelocityCache(ttl_seconds=settings.velocity_ttl_seconds, max_size=settings.velocity_max_size)


@lru_cache
def get_network_repo() -> IPNetworkRepository:
    return MaxMindASNReader(db_path=settings.maxmind_db_path)


def get_auth_usecase() -> APIKeyAuthUseCase:
    return APIKeyAuthUseCase(client_repo=get_client_repository())


def get_evaluate_ip_usecase() -> EvaluateIPUseCase:
    return EvaluateIPUseCase(
        network_repo=get_network_repo(),
        cache=get_velocity_cache(),
        velocity_high_threshold=settings.velocity_high_threshold,
    )
