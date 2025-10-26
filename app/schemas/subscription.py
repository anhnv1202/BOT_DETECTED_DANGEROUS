from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubscriptionResponse(BaseModel):
    id: int
    plan: str
    status: str
    monthly_quota: int
    used_quota: int
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PurchasePlanRequest(BaseModel):
    plan: str  # "plus" or "pro"



