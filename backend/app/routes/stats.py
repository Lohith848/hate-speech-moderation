from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models_db import ModerationLog

router = APIRouter(prefix="/api/v1", tags=["stats"])


@router.get("/stats")
def stats(range: str = Query("7d", description="e.g. 7d, 30d"), db: Session = Depends(get_db)):
    """FR-6: aggregate counts + a daily timeline, computed on read.
    Fine at practicum scale -- no separate analytics pipeline needed
    (see docs/02_TRD.md section 4)."""
    days = int(range.rstrip("d")) if range.endswith("d") else 7
    since = datetime.utcnow() - timedelta(days=days)

    rows = db.query(ModerationLog).filter(ModerationLog.created_at >= since).all()

    by_label = {"SAFE": 0, "OFFENSIVE": 0, "HATE": 0}
    timeline_map = {}

    for r in rows:
        by_label[r.label] = by_label.get(r.label, 0) + 1
        day = r.created_at.strftime("%Y-%m-%d")
        timeline_map.setdefault(day, {"date": day, "SAFE": 0, "OFFENSIVE": 0, "HATE": 0})
        timeline_map[day][r.label] += 1

    recent = (
        db.query(ModerationLog)
        .order_by(ModerationLog.created_at.desc())
        .limit(20)
        .all()
    )

    return {
        "total": len(rows),
        "by_label": by_label,
        "timeline": sorted(timeline_map.values(), key=lambda x: x["date"]),
        "recent": [
            {
                "id": r.id,
                "text": r.text[:120],
                "label": r.label,
                "confidence": max(r.confidence_safe, r.confidence_offensive, r.confidence_hate),
                "created_at": r.created_at.isoformat(),
            }
            for r in recent
        ],
    }
