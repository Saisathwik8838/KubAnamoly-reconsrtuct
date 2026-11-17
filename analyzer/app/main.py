from fastapi import FastAPI
from app.routers.predict import router as predict_router
from app.routers.hardware import router as hardware_router
from app.routers.scheduler import router as scheduler_router
from app.services.model_service import load_models

app = FastAPI(title="KubAnomaly Center", version="0.1-reconstructed")
app.include_router(predict_router)
app.include_router(hardware_router)
app.include_router(scheduler_router)

@app.get("/health")
def health():
    models = load_models()
    return {
        "status": "success",
        "service": "kubanomaly-center",
        "models_available": models,
        "models_count": len(models)
    }
