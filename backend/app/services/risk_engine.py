from dataclasses import dataclass

from app.services.market_data import MarketSnapshot


@dataclass
class IndicatorResult:
    name: str
    score: int
    max_score: int
    detail: str


@dataclass
class RiskAssessment:
    risk_score: int
    risk_level: str
    indicators: list[IndicatorResult]


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def score_volume_spike(snapshot: MarketSnapshot) -> IndicatorResult:
    max_score = 30
    ratio = snapshot.volume_spike_ratio
    if ratio is None:
        return IndicatorResult("Volume Spike", 0, max_score, "Insufficient volume history available.")
    if ratio >= 3.0:
        score = max_score
        detail = f"Trading volume spiked {ratio:.0%} above the 30-day average over the last 3 days."
    elif ratio >= 2.0:
        score = 22
        detail = f"Trading volume is {ratio:.0%} of the 30-day average — elevated activity detected."
    elif ratio >= 1.5:
        score = 12
        detail = f"Moderate volume increase ({ratio:.0%} of 30-day average)."
    else:
        score = 0
        detail = f"Volume is within normal range ({ratio:.0%} of 30-day average)."
    return IndicatorResult("Volume Spike", score, max_score, detail)


def score_social_hype(snapshot: MarketSnapshot) -> IndicatorResult:
    max_score = 25
    change = snapshot.recent_price_change_pct
    volume_ratio = snapshot.volume_spike_ratio or 1.0
    if change is None:
        return IndicatorResult("Social Media Hype", 0, max_score, "Limited data for hype estimation (MVP stub).")

    hype_signal = _clamp((abs(change) / 30.0) * 0.6 + _clamp(volume_ratio - 1, 0, 2) / 2 * 0.4)
    score = int(hype_signal * max_score)
    if score >= 20:
        detail = "Price and volume patterns suggest coordinated promotional activity may be driving interest."
    elif score >= 10:
        detail = "Some signs of unusual attention, possibly from social media or messaging groups."
    else:
        detail = "No significant hype signals detected based on available market patterns."
    return IndicatorResult("Social Media Hype", score, max_score, detail)


def score_price_volatility(snapshot: MarketSnapshot) -> IndicatorResult:
    max_score = 20
    std = snapshot.daily_return_std
    if std is None:
        return IndicatorResult("Price Volatility", 0, max_score, "Insufficient price history for volatility analysis.")
    if std >= 0.08:
        score = max_score
        detail = f"Extreme daily price swings detected (volatility: {std:.1%})."
    elif std >= 0.05:
        score = 14
        detail = f"High price volatility ({std:.1%} daily std dev) — common in speculative stocks."
    elif std >= 0.03:
        score = 8
        detail = f"Moderate volatility ({std:.1%} daily std dev)."
    else:
        score = 0
        detail = f"Price volatility is within normal range ({std:.1%} daily std dev)."
    return IndicatorResult("Price Volatility", score, max_score, detail)


def score_institutional_ownership(snapshot: MarketSnapshot) -> IndicatorResult:
    max_score = 15
    pct = snapshot.institutional_ownership_pct
    if pct is None:
        return IndicatorResult("Low Institutional Ownership", 5, max_score, "Institutional ownership data unavailable — treated as moderate risk.")
    if pct < 5:
        score = max_score
        detail = f"Very low institutional ownership ({pct:.1f}%) — easier to manipulate."
    elif pct < 15:
        score = 10
        detail = f"Low institutional ownership ({pct:.1f}%)."
    elif pct < 30:
        score = 5
        detail = f"Moderate institutional ownership ({pct:.1f}%)."
    else:
        score = 0
        detail = f"Strong institutional ownership ({pct:.1f}%) — harder to manipulate."
    return IndicatorResult("Low Institutional Ownership", score, max_score, detail)


def score_insider_selling(snapshot: MarketSnapshot) -> IndicatorResult:
    max_score = 10
    change = snapshot.recent_price_change_pct
    volume_ratio = snapshot.volume_spike_ratio or 1.0
    if change is None:
        return IndicatorResult("Insider Selling", 0, max_score, "Insider activity data limited in MVP — no filing data available.")
    if change > 20 and volume_ratio > 2.0:
        score = 8
        detail = "Rapid price rise with high volume may coincide with insider distribution (MVP heuristic)."
    elif change > 10 and volume_ratio > 1.5:
        score = 5
        detail = "Moderate price rise with elevated volume — monitor for insider selling patterns."
    else:
        score = 0
        detail = "No significant insider selling signals detected."
    return IndicatorResult("Insider Selling", score, max_score, detail)


def calculate_risk(snapshot: MarketSnapshot) -> RiskAssessment:
    indicators = [
        score_volume_spike(snapshot),
        score_social_hype(snapshot),
        score_price_volatility(snapshot),
        score_institutional_ownership(snapshot),
        score_insider_selling(snapshot),
    ]
    total = min(100, sum(i.score for i in indicators))
    risk_level = "red" if total >= 80 else "green"
    return RiskAssessment(risk_score=total, risk_level=risk_level, indicators=indicators)
