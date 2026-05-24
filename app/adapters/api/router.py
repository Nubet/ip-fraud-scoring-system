from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import IPvAnyAddress

from app.domain.models import Client, IPAnalysis
from app.usecases.auth import APIKeyAuthUseCase, InactiveClientError, InvalidAPIKeyError
from app.usecases.evaluate_ip import EvaluateIPUseCase

from .deps import get_auth_usecase, get_evaluate_ip_usecase

router = APIRouter(prefix="/v1", tags=["scoring"])


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


async def require_client(
    x_api_key: str = Header(..., alias="X-API-Key"),
    auth_usecase: APIKeyAuthUseCase = Depends(get_auth_usecase),
) -> Client:
    try:
        return await auth_usecase.authenticate(x_api_key)
    except InvalidAPIKeyError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except InactiveClientError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get("/score", response_model=IPAnalysis)
async def get_fraud_score(
    ip: IPvAnyAddress = Query(..., description="IP address to score"),
    _: Client = Depends(require_client),
    use_case: EvaluateIPUseCase = Depends(get_evaluate_ip_usecase),
) -> IPAnalysis:
    return await use_case.execute(str(ip))
