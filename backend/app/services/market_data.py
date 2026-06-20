import logging
import time
from dataclasses import dataclass

import yfinance as yf

logger = logging.getLogger(__name__)

_cache: dict[str, tuple[float, dict]] = {}
CACHE_TTL_SECONDS = 900

# Fallback snapshots for well-known symbols when Yahoo Finance is unavailable
_DEMO_SNAPSHOTS: dict[str, dict] = {
    "AAPL": {
        "company_name": "Apple Inc.",
        "current_price": 190.0,
        "avg_volume_3d": 55_000_000,
        "avg_volume_30d": 52_000_000,
        "volume_spike_ratio": 1.06,
        "daily_return_std": 0.015,
        "institutional_ownership_pct": 62.0,
        "recent_price_change_pct": 1.2,
        "market_cap": 2_900_000_000_000,
    },
    "MSFT": {
        "company_name": "Microsoft Corporation",
        "current_price": 420.0,
        "avg_volume_3d": 22_000_000,
        "avg_volume_30d": 21_000_000,
        "volume_spike_ratio": 1.05,
        "daily_return_std": 0.014,
        "institutional_ownership_pct": 72.0,
        "recent_price_change_pct": 0.8,
        "market_cap": 3_100_000_000_000,
    },
    "TSLA": {
        "company_name": "Tesla, Inc.",
        "current_price": 250.0,
        "avg_volume_3d": 120_000_000,
        "avg_volume_30d": 80_000_000,
        "volume_spike_ratio": 1.5,
        "daily_return_std": 0.045,
        "institutional_ownership_pct": 44.0,
        "recent_price_change_pct": 8.5,
        "market_cap": 800_000_000_000,
    },
    "GME": {
        "company_name": "GameStop Corp.",
        "current_price": 25.0,
        "avg_volume_3d": 15_000_000,
        "avg_volume_30d": 4_000_000,
        "volume_spike_ratio": 3.75,
        "daily_return_std": 0.09,
        "institutional_ownership_pct": 28.0,
        "recent_price_change_pct": 35.0,
        "market_cap": 7_500_000_000,
    },
}


@dataclass
class MarketSnapshot:
    symbol: str
    company_name: str
    current_price: float | None
    avg_volume_3d: float | None
    avg_volume_30d: float | None
    volume_spike_ratio: float | None
    daily_return_std: float | None
    institutional_ownership_pct: float | None
    recent_price_change_pct: float | None
    market_cap: float | None


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def _get_cached(symbol: str) -> MarketSnapshot | None:
    entry = _cache.get(symbol)
    if entry is None:
        return None
    ts, data = entry
    if time.time() - ts > CACHE_TTL_SECONDS:
        del _cache[symbol]
        return None
    return MarketSnapshot(**data)


def _set_cache(symbol: str, snapshot: MarketSnapshot) -> None:
    _cache[symbol] = (time.time(), snapshot.__dict__)


def _demo_snapshot(symbol: str) -> MarketSnapshot | None:
    demo = _DEMO_SNAPSHOTS.get(symbol)
    if not demo:
        return None
    logger.info("Using demo market data for %s (live data unavailable)", symbol)
    return MarketSnapshot(symbol=symbol, **demo)


def _fetch_history(symbol: str):
    try:
        data = yf.download(symbol, period="3mo", progress=False, auto_adjust=True)
        if data is not None and not data.empty:
            return data
    except Exception as exc:
        logger.warning("yf.download failed for %s: %s", symbol, exc)

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo")
        if hist is not None and not hist.empty:
            return hist
    except Exception as exc:
        logger.warning("Ticker.history failed for %s: %s", symbol, exc)

    return None


def _fetch_info(symbol: str) -> dict:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info if isinstance(info, dict) else {}
    except Exception as exc:
        logger.warning("ticker.info failed for %s: %s", symbol, exc)
        return {}


def fetch_market_snapshot(symbol: str) -> MarketSnapshot:
    symbol = normalize_symbol(symbol)
    cached = _get_cached(symbol)
    if cached:
        return cached

    hist = _fetch_history(symbol)
    info = _fetch_info(symbol)

    if hist is None or hist.empty:
        demo = _demo_snapshot(symbol)
        if demo:
            _set_cache(symbol, demo)
            return demo
        if not info.get("shortName") and not info.get("longName"):
            raise ValueError(f"Could not find market data for symbol '{symbol}'")

    avg_volume_3d = None
    avg_volume_30d = None
    volume_spike_ratio = None
    daily_return_std = None
    recent_price_change_pct = None
    current_price = None

    if hist is not None and not hist.empty:
        if hasattr(hist.columns, "levels") and hist.columns.nlevels > 1:
            try:
                hist = hist.xs(symbol, axis=1, level=1)
            except (KeyError, ValueError):
                pass

        vol_col = "Volume" if "Volume" in hist.columns else None
        close_col = "Close" if "Close" in hist.columns else None

        if vol_col:
            volumes = hist[vol_col].dropna()
            if len(volumes) >= 3:
                avg_volume_3d = float(volumes.tail(3).mean())
            if len(volumes) >= 30:
                avg_volume_30d = float(volumes.tail(30).mean())
            elif len(volumes) > 0:
                avg_volume_30d = float(volumes.mean())
            if avg_volume_3d and avg_volume_30d and avg_volume_30d > 0:
                volume_spike_ratio = avg_volume_3d / avg_volume_30d

        if close_col:
            closes = hist[close_col].dropna()
            if len(closes) >= 1:
                current_price = float(closes.iloc[-1])
            if len(closes) >= 2:
                returns = closes.pct_change().dropna()
                daily_return_std = float(returns.std()) if len(returns) > 0 else None
                if len(closes) >= 4:
                    recent_price_change_pct = float(
                        (closes.iloc[-1] - closes.iloc[-4]) / closes.iloc[-4] * 100
                    )

    institutional = info.get("heldPercentInstitutions")
    institutional_pct = float(institutional * 100) if institutional is not None else None

    snapshot = MarketSnapshot(
        symbol=symbol,
        company_name=info.get("longName") or info.get("shortName") or symbol,
        current_price=info.get("currentPrice") or info.get("regularMarketPrice") or current_price,
        avg_volume_3d=avg_volume_3d,
        avg_volume_30d=avg_volume_30d,
        volume_spike_ratio=volume_spike_ratio,
        daily_return_std=daily_return_std,
        institutional_ownership_pct=institutional_pct,
        recent_price_change_pct=recent_price_change_pct,
        market_cap=info.get("marketCap"),
    )

    _set_cache(symbol, snapshot)
    return snapshot
