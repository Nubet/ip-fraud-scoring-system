from app.domain.interfaces import IPNetworkRepository, VelocityCache
from app.domain.models import RiskLevel
from app.usecases.evaluate_ip import EvaluateIPUseCase


class FakeNetworkRepo(IPNetworkRepository):
    def __init__(self, is_dc: bool):
        self.is_dc = is_dc

    async def is_data_center(self, ip: str) -> bool:
        return self.is_dc


class FakeVelocityCache(VelocityCache):
    def __init__(self, count: int):
        self.count = count

    async def increment_and_get_requests(self, ip: str) -> int:
        return self.count


async def test_evaluate_ip_no_flags_low_risk() -> None:
    use_case = EvaluateIPUseCase(FakeNetworkRepo(False), FakeVelocityCache(1), velocity_high_threshold=10)
    result = await use_case.execute("8.8.8.8")

    assert result.fraud_score == 0
    assert result.risk_level == RiskLevel.LOW
    assert result.flags == []


async def test_evaluate_ip_data_center_medium_risk() -> None:
    use_case = EvaluateIPUseCase(FakeNetworkRepo(True), FakeVelocityCache(1), velocity_high_threshold=10)
    result = await use_case.execute("8.8.8.8")

    assert result.fraud_score == 40
    assert result.risk_level == RiskLevel.MEDIUM
    assert "IS_DATA_CENTER" in result.flags


async def test_evaluate_ip_high_velocity_medium_risk() -> None:
    use_case = EvaluateIPUseCase(FakeNetworkRepo(False), FakeVelocityCache(11), velocity_high_threshold=10)
    result = await use_case.execute("8.8.8.8")

    assert result.fraud_score == 30
    assert result.risk_level == RiskLevel.MEDIUM
    assert "HIGH_VELOCITY" in result.flags


async def test_evaluate_ip_threshold_boundary_does_not_trigger_velocity_flag() -> None:
    use_case = EvaluateIPUseCase(FakeNetworkRepo(False), FakeVelocityCache(10), velocity_high_threshold=10)
    result = await use_case.execute("8.8.8.8")

    assert result.fraud_score == 0
    assert result.risk_level == RiskLevel.LOW
    assert "HIGH_VELOCITY" not in result.flags


async def test_evaluate_ip_both_flags_high_risk() -> None:
    use_case = EvaluateIPUseCase(FakeNetworkRepo(True), FakeVelocityCache(20), velocity_high_threshold=10)
    result = await use_case.execute("8.8.8.8")

    assert result.fraud_score == 70
    assert result.risk_level == RiskLevel.HIGH
    assert set(result.flags) == {"IS_DATA_CENTER", "HIGH_VELOCITY"}
