import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Analysis, User
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisHistoryResponse,
    AnalysisResponse,
    AnalysisSummary,
    IndicatorScore,
)
from app.services.gemini_service import generate_explanation
from app.services.market_data import fetch_market_snapshot, normalize_symbol
from app.services.notion_service import sync_analysis_to_notion
from app.services.risk_engine import calculate_risk

router = APIRouter(prefix="/analysis", tags=["analysis"])
logger = logging.getLogger(__name__)


def _to_response(analysis: Analysis) -> AnalysisResponse:
    indicators = [
        IndicatorScore(**item) if isinstance(item, dict) else item
        for item in (analysis.indicators or [])
    ]
    return AnalysisResponse(
        id=analysis.id,
        stock_symbol=analysis.stock_symbol,
        risk_score=analysis.risk_score,
        risk_level=analysis.risk_level,
        explanation=analysis.explanation,
        indicators=indicators,
        created_at=analysis.created_at,
    )


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    payload: AnalysisCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    symbol = normalize_symbol(payload.symbol)

    try:
        snapshot = fetch_market_snapshot(symbol)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Market data fetch failed for %s", symbol)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch market data for '{symbol}'. Please try again shortly.",
        ) from exc

    assessment = calculate_risk(snapshot)
    explanation = generate_explanation(snapshot, assessment)

    indicators_data = [
        {"name": i.name, "score": i.score, "max_score": i.max_score, "detail": i.detail}
        for i in assessment.indicators
    ]

    analysis = Analysis(
        user_id=current_user.id,
        stock_symbol=symbol,
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        explanation=explanation,
        indicators=indicators_data,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    background_tasks.add_task(sync_analysis_to_notion, analysis, current_user)

    return _to_response(analysis)


@router.get("/history", response_model=AnalysisHistoryResponse)
def get_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Analysis).filter(Analysis.user_id == current_user.id)
    total = query.count()
    items = query.order_by(Analysis.created_at.desc()).offset(skip).limit(limit).all()
    return AnalysisHistoryResponse(
        items=[AnalysisSummary.model_validate(a) for a in items],
        total=total,
    )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
        .first()
    )
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return _to_response(analysis)
