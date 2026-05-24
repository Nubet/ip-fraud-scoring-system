from app.domain.interfaces import IPNetworkRepository, VelocityCache
from app.domain.models import IPAnalysis, RiskLevel

DATA_CENTER_SCORE = 40
HIGH_VELOCITY_SCORE = 30
HIGH_RISK_THRESHOLD = 70
MEDIUM_RISK_THRESHOLD = 30


class EvaluateIPUseCase:
    def __init__(
        self,
        network_repo: IPNetworkRepository,
        cache: VelocityCache,
        velocity_high_threshold: int = 10,
    ):
        self.network_repo = network_repo
        self.cache = cache
        self.velocity_high_threshold = velocity_high_threshold

    async def execute(self, ip: str) -> IPAnalysis:
        score = 0
        flags: list[str] = []

        if await self.network_repo.is_data_center(ip):
            score += DATA_CENTER_SCORE
            flags.append("IS_DATA_CENTER")

        request_count = await self.cache.increment_and_get_requests(ip)
        if request_count > self.velocity_high_threshold:
            score += HIGH_VELOCITY_SCORE
            flags.append("HIGH_VELOCITY")

        risk = self._risk_from_score(score)

        return IPAnalysis(ip=ip, fraud_score=min(score, 100), risk_level=risk, flags=flags)

    @staticmethod
    def _risk_from_score(score: int) -> RiskLevel:
        if score >= HIGH_RISK_THRESHOLD:
            return RiskLevel.HIGH
        if score >= MEDIUM_RISK_THRESHOLD:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
