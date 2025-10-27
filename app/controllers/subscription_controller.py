from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.subscription_service import SubscriptionService
from app.schemas.subscription import SubscriptionResponse, PurchasePlanRequest
from app.middleware.auth_middleware import get_current_user_id

router = APIRouter(prefix="/api/subscription", tags=["Subscription"])


@router.get("/current", response_model=SubscriptionResponse)
def get_current_subscription(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get current active subscription (requires authentication)"""
    subscription_service = SubscriptionService(db)
    
    subscription = subscription_service.get_active_subscription(user_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    return subscription


@router.post("/purchase", response_model=SubscriptionResponse)
def purchase_plan(
    plan_data: PurchasePlanRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Purchase a subscription plan (requires authentication)"""
    subscription_service = SubscriptionService(db)
    
    try:
        subscription = subscription_service.purchase_plan(user_id, plan_data.plan)
        return subscription
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cancel", response_model=SubscriptionResponse)
def cancel_subscription(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Cancel current subscription and downgrade to FREE (requires authentication)"""
    subscription_service = SubscriptionService(db)
    
    try:
        subscription = subscription_service.cancel_subscription(user_id)
        return subscription
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



