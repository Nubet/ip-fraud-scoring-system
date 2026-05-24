from fastapi.testclient import TestClient

from app.adapters.api.deps import get_auth_usecase, get_evaluate_ip_usecase
from app.domain.models import Client, IPAnalysis, RiskLevel
from app.main import app
from app.usecases.auth import InactiveClientError, InvalidAPIKeyError


class StubAuthUseCase:
    def __init__(self, error: Exception | None = None):
        self.error = error

    async def authenticate(self, api_key: str) -> Client:
        if self.error:
            raise self.error
        return Client(client_id="stub", is_active=True, plan_limit=10)


class StubEvaluateIPUseCase:
    def __init__(self, result: IPAnalysis):
        self.result = result
        self.seen_ip: str | None = None

    async def execute(self, ip: str) -> IPAnalysis:
        self.seen_ip = ip
        return self.result


def _client_with_overrides(auth_stub, evaluate_stub) -> TestClient:
    app.dependency_overrides[get_auth_usecase] = lambda: auth_stub
    app.dependency_overrides[get_evaluate_ip_usecase] = lambda: evaluate_stub
    return TestClient(app)


def _clear_overrides() -> None:
    app.dependency_overrides.clear()


def test_health_endpoint() -> None:
    try:
        client = _client_with_overrides(
            StubAuthUseCase(),
            StubEvaluateIPUseCase(IPAnalysis(ip="8.8.8.8", fraud_score=0, risk_level=RiskLevel.LOW, flags=[])),
        )
        response = client.get("/v1/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    finally:
        _clear_overrides()


def test_score_endpoint_requires_api_key() -> None:
    try:
        client = _client_with_overrides(
            StubAuthUseCase(),
            StubEvaluateIPUseCase(IPAnalysis(ip="8.8.8.8", fraud_score=0, risk_level=RiskLevel.LOW, flags=[])),
        )
        response = client.get("/v1/score", params={"ip": "8.8.8.8"})

        assert response.status_code == 422
    finally:
        _clear_overrides()


def test_score_endpoint_rejects_invalid_api_key() -> None:
    try:
        client = _client_with_overrides(
            StubAuthUseCase(error=InvalidAPIKeyError("Invalid API key")),
            StubEvaluateIPUseCase(IPAnalysis(ip="8.8.8.8", fraud_score=0, risk_level=RiskLevel.LOW, flags=[])),
        )
        response = client.get("/v1/score", params={"ip": "8.8.8.8"}, headers={"X-API-Key": "bad-key"})

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid API key"
    finally:
        _clear_overrides()


def test_score_endpoint_rejects_inactive_client() -> None:
    try:
        client = _client_with_overrides(
            StubAuthUseCase(error=InactiveClientError("Client is inactive")),
            StubEvaluateIPUseCase(IPAnalysis(ip="8.8.8.8", fraud_score=0, risk_level=RiskLevel.LOW, flags=[])),
        )
        response = client.get("/v1/score", params={"ip": "8.8.8.8"}, headers={"X-API-Key": "inactive-key"})

        assert response.status_code == 403
        assert response.json()["detail"] == "Client is inactive"
    finally:
        _clear_overrides()


def test_score_endpoint_rejects_invalid_ip() -> None:
    try:
        client = _client_with_overrides(
            StubAuthUseCase(),
            StubEvaluateIPUseCase(IPAnalysis(ip="8.8.8.8", fraud_score=0, risk_level=RiskLevel.LOW, flags=[])),
        )
        response = client.get("/v1/score", params={"ip": "not-an-ip"}, headers={"X-API-Key": "dev-key"})

        assert response.status_code == 422
    finally:
        _clear_overrides()


def test_score_endpoint_returns_analysis() -> None:
    expected = IPAnalysis(
        ip="8.8.8.8",
        fraud_score=70,
        risk_level=RiskLevel.HIGH,
        flags=["IS_DATA_CENTER", "HIGH_VELOCITY"],
    )
    evaluate_stub = StubEvaluateIPUseCase(expected)

    try:
        client = _client_with_overrides(StubAuthUseCase(), evaluate_stub)
        response = client.get("/v1/score", params={"ip": "8.8.8.8"}, headers={"X-API-Key": "dev-key"})

        assert response.status_code == 200
        assert evaluate_stub.seen_ip == "8.8.8.8"
        assert response.json() == expected.model_dump(mode="json")
    finally:
        _clear_overrides()
