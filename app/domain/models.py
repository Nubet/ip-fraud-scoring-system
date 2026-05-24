from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class IPAnalysis(BaseModel):
    ip: str
    fraud_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    flags: list[str]


class Client(BaseModel):
    client_id: str
    is_active: bool
    plan_limit: int = Field(ge=1)
