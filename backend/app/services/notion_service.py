import logging
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.models import Analysis, User

logger = logging.getLogger(__name__)

NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"


def _risk_level_label(level: str) -> str:
    return "Red" if level == "red" else "Green"


async def sync_analysis_to_notion(analysis: Analysis, user: User) -> None:
    if not settings.notion_token or not settings.notion_database_id:
        logger.info("Notion credentials not configured — skipping sync for analysis %s", analysis.id)
        return

    payload = {
        "parent": {"database_id": settings.notion_database_id},
        "properties": {
            "Stock": {"title": [{"text": {"content": analysis.stock_symbol}}]},
            "User": {"rich_text": [{"text": {"content": user.email}}]},
            "Risk Score": {"number": analysis.risk_score},
            "Risk Level": {"select": {"name": _risk_level_label(analysis.risk_level)}},
            "Explanation": {
                "rich_text": [{"text": {"content": analysis.explanation[:2000]}}]
            },
            "Timestamp": {
                "date": {"start": analysis.created_at.isoformat() if analysis.created_at else datetime.now(timezone.utc).isoformat()}
            },
            "Analysis ID": {"rich_text": [{"text": {"content": str(analysis.id)}}]},
        },
    }

    headers = {
        "Authorization": f"Bearer {settings.notion_token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(NOTION_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            logger.info("Synced analysis %s to Notion", analysis.id)
    except Exception as exc:
        logger.error("Failed to sync analysis %s to Notion: %s", analysis.id, exc)
