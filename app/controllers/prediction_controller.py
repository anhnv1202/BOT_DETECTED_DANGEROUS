from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import time

from app.database import get_db
from app.services.subscription_service import SubscriptionService
from app.services.ml_inference_service import MLInferenceService
from app.repositories.usage_log_repository import UsageLogRepository
from app.schemas.prediction import PredictionResponse
from app.middleware.auth_middleware import get_current_user_id

router = APIRouter(prefix="/api/v1", tags=["Prediction"])

# Initialize ML service (singleton)
ml_service = MLInferenceService()


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    file: UploadFile = File(...),
    threshold: float = 0.5,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Predict dangerous objects in image (requires authentication and quota)"""
    
    # Check quota
    subscription_service = SubscriptionService(db)
    quota_check = subscription_service.check_quota(user_id)
    
    if not quota_check["allowed"]:
        raise HTTPException(status_code=403, detail=quota_check["reason"])
    
    # Validate threshold
    if threshold <= 0.0 or threshold >= 1.0:
        raise HTTPException(status_code=400, detail="Threshold must be in (0, 1)")
    
    # Read image
    try:
        image_bytes = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read image")
    
    # Perform inference
    start_time = time.time()
    try:
        result = ml_service.predict(image_bytes, threshold)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")
    
    response_time = (time.time() - start_time) * 1000  # ms
    
    # Increment usage
    subscription_service.increment_usage(quota_check["subscription_id"])
    
    # Log usage
    usage_log_repo = UsageLogRepository(db)
    usage_log_repo.create(
        user_id=user_id,
        endpoint="/api/v1/predict",
        method="POST",
        status_code=200,
        response_time_ms=response_time
    )
    
    # Return result with remaining quota
    return PredictionResponse(
        classes=result["classes"],
        probabilities=result["probabilities"],
        active=result["active"],
        quota_remaining=quota_check["remaining"] - 1
    )



