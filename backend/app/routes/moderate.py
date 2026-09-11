import io
import json

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..db import get_db
from ..model import predict
from ..models_db import ModerationLog
from ..schemas import ModerateRequest, ModerateResponse

router = APIRouter(prefix="/api/v1", tags=["moderate"])


def _run_and_log(text: str, source: str, db: Session) -> ModerateResponse:
    label, confidence, explanation = predict(text)

    log = ModerationLog(
        text=text[:1000],
        label=label,
        confidence_safe=confidence.get("SAFE", 0.0),
        confidence_offensive=confidence.get("OFFENSIVE", 0.0),
        confidence_hate=confidence.get("HATE", 0.0),
        explanation=json.dumps(explanation),
        source=source,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return ModerateResponse(
        id=log.id, label=label, confidence=confidence, explanation=explanation
    )


@router.post("/moderate", response_model=ModerateResponse)
def moderate(payload: ModerateRequest, db: Session = Depends(get_db)):
    """FR-1/FR-2/FR-3/FR-4: single-text prediction with confidence + explanation."""
    return _run_and_log(payload.text, source="web", db=db)


@router.post("/moderate/batch")
def moderate_batch(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """FR-7: CSV upload with a 'text' column -> predictions for every row.
    Useful for your own testing/report generation (implementation plan step 21)."""
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=422, detail="Please upload a .csv file")

    content = file.file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=422, detail="Could not parse CSV")

    if "text" not in df.columns:
        raise HTTPException(status_code=422, detail="CSV must have a 'text' column")

    results = []
    for text in df["text"].astype(str).tolist():
        text = text.strip()
        if not text:
            continue
        resp = _run_and_log(text[:1000], source="batch", db=db)
        row = resp.model_dump()
        row["text"] = text[:1000]
        results.append(row)

    return {"count": len(results), "results": results}
