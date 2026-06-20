from datetime import datetime

from pydantic import BaseModel, Field


class AnalysisCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)


class IndicatorScore(BaseModel):
    name: str
    score: int
    max_score: int
    detail: str


class AnalysisResponse(BaseModel):
    id: int
    stock_symbol: str
    risk_score: int
    risk_level: str
    explanation: str
    indicators: list[IndicatorScore]
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisSummary(BaseModel):
    id: int
    stock_symbol: str
    risk_score: int
    risk_level: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisHistoryResponse(BaseModel):
    items: list[AnalysisSummary]
    total: int
