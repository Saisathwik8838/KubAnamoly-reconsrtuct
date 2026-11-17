from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any
from app.services.feature_extractor import extract_features, FEATURES
from app.services.model_service import predict
from app.routers.scheduler import append_history

router = APIRouter()

class PredictionRequest(BaseModel):
    records: list[dict[str, Any]]
    container_id: str | None = None
    window_start: str | None = None
    window_seconds: int = 10

class VectorPredictionRequest(BaseModel):
    features: list[float] = Field(..., description="36-element behavioral feature vector")
    container_id: str | None = None
    window_start: str | None = None
    window_seconds: int = 10

@router.post("/predict")
def predict_vector(req: VectorPredictionRequest):
    """
    Accepts a 36-feature vector directly and returns model predictions (Table VI in paper).
    """
    if len(req.features) != len(FEATURES):
        raise HTTPException(
            400,
            f"Feature vector must have exactly {len(FEATURES)} elements, got {len(req.features)}"
        )
    try:
        preds = predict(req.features)
    except Exception as e:
        raise HTTPException(503, str(e))
    
    result = {
        "container_id": req.container_id,
        "window_start": req.window_start,
        "window_seconds": req.window_seconds,
        "predictions": preds,
        "features": req.features
    }
    append_history(result)
    return {"status": "success", "results": [result]}

@router.post("/predict/logs")
def predict_logs(req: PredictionRequest):
    """
    Extracts 36 features from raw Falco JSON records and runs inference.
    """
    if not req.records:
        raise HTTPException(400, "records must not be empty")
    ex = extract_features(req.records, req.container_id)
    try:
        preds = predict(ex["feature_vector"])
    except Exception as e:
        raise HTTPException(503, str(e))
    result = {
        "window_start": req.window_start,
        "window_seconds": req.window_seconds,
        **{k: v for k, v in ex.items() if k != "feature_vector"},
        "predictions": preds
    }
    append_history({"container_id": req.container_id, **result})
    return {"status": "success", "records_received": len(req.records), "windows_processed": 1, "results": [result]}
