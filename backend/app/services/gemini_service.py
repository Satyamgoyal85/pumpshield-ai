import json
import logging

import google.generativeai as genai

from app.config import settings
from app.services.market_data import MarketSnapshot
from app.services.risk_engine import IndicatorResult, RiskAssessment

logger = logging.getLogger(__name__)


def _build_fallback_explanation(assessment: RiskAssessment, snapshot: MarketSnapshot) -> str:
    level_label = "HIGH" if assessment.risk_level == "red" else "LOW"
    reasons = [f"• {i.detail}" for i in assessment.indicators if i.score > 0]
    if not reasons:
        reasons = ["• No significant fraud indicators detected in available market data."]
    return (
        f"Risk Score: {assessment.risk_score} ({level_label} manipulation risk)\n\n"
        f"Analysis for {snapshot.symbol} ({snapshot.company_name}):\n\n"
        + "\n".join(reasons)
    )


def generate_explanation(snapshot: MarketSnapshot, assessment: RiskAssessment) -> str:
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY not set — using fallback explanation")
        return _build_fallback_explanation(assessment, snapshot)

    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)

        indicator_summary = [
            {"name": i.name, "score": i.score, "max": i.max_score, "detail": i.detail}
            for i in assessment.indicators
        ]

        prompt = f"""You are PumpShield AI, a financial fraud analyst. Explain this stock fraud risk assessment
in plain language for beginner investors. Be transparent and educational — do NOT predict stock prices.

Stock: {snapshot.symbol} ({snapshot.company_name})
Current Price: {snapshot.current_price}
Risk Score: {assessment.risk_score}/100
Risk Level: {"RED (High Risk)" if assessment.risk_level == "red" else "GREEN (Low Risk)"}

Indicator Breakdown:
{json.dumps(indicator_summary, indent=2)}

Market Data:
- Volume spike ratio (3d/30d): {snapshot.volume_spike_ratio}
- Daily return volatility: {snapshot.daily_return_std}
- Institutional ownership: {snapshot.institutional_ownership_pct}%
- Recent 3-day price change: {snapshot.recent_price_change_pct}%

Write a clear explanation with:
1. A one-sentence summary of the risk level
2. 3-5 bullet points explaining the key reasons (use • for bullets)
3. A brief disclaimer that this assesses manipulation risk, not investment profitability

Keep it under 200 words. Do not use markdown headers."""

        response = model.generate_content(prompt)
        text = response.text.strip()
        if text:
            return text
    except Exception as exc:
        logger.error("Gemini explanation failed: %s", exc)

    return _build_fallback_explanation(assessment, snapshot)
