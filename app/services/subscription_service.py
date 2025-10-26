from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.config import get_settings
from app.repositories.user_repository import UserRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.transaction_repository import TransactionRepository
from app.models.subscription import Subscription, PlanType, SubscriptionStatus
from app.models.transaction import TransactionType, TransactionStatus

settings = get_settings()


class SubscriptionService:
    """Service quản lý subscription (FREE/PLUS/PRO), check quota, mua gói"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.subscription_repo = SubscriptionRepository(db)
        self.transaction_repo = TransactionRepository(db)
    
    def get_plan_details(self, plan: PlanType) -> dict:
        """Lấy thông tin quota và giá của từng gói"""
        plan_configs = {
            PlanType.FREE: {"quota": settings.PLAN_FREE_MONTHLY_QUOTA, "price": 0},
            PlanType.PLUS: {"quota": settings.PLAN_PLUS_MONTHLY_QUOTA, "price": settings.PLAN_PLUS_PRICE},
            PlanType.PRO: {"quota": settings.PLAN_PRO_MONTHLY_QUOTA, "price": settings.PLAN_PRO_PRICE},
        }
        return plan_configs.get(plan, {"quota": 0, "price": 0})
    
    def get_active_subscription(self, user_id: int) -> Optional[Subscription]:
        """Lấy gói subscription đang active của user (tự động chuyển về FREE nếu hết hạn)"""
        subscription = self.subscription_repo.get_active_by_user(user_id)
        
        # Check if expired
        if subscription and subscription.expires_at:
            if subscription.expires_at < datetime.utcnow():
                self.subscription_repo.update_status(subscription.id, SubscriptionStatus.EXPIRED)
                # Create new free plan
                subscription = self.subscription_repo.create(
                    user_id=user_id,
                    plan=PlanType.FREE,
                    monthly_quota=settings.PLAN_FREE_MONTHLY_QUOTA
                )
        
        return subscription
    
    def purchase_plan(self, user_id: int, plan: str) -> Subscription:
        """Mua gói PLUS/PRO bằng credits trong ví (30 ngày)"""
        if plan not in ["plus", "pro"]:
            raise ValueError("Invalid plan. Choose 'plus' or 'pro'")
        
        plan_type = PlanType.PLUS if plan == "plus" else PlanType.PRO
        plan_details = self.get_plan_details(plan_type)
        price = plan_details["price"]
        quota = plan_details["quota"]
        
        # Check user credits
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.credits < price:
            raise ValueError(f"Insufficient credits. Required: {price}, Available: {user.credits}")
        
        # Deduct credits
        self.user_repo.update_credits(user_id, -price)
        
        # Create transaction
        self.transaction_repo.create(
            user_id=user_id,
            amount=price,
            tx_type=TransactionType.PURCHASE,
            status=TransactionStatus.SUCCESS,
            description=f"Purchase {plan.upper()} plan"
        )
        
        # Expire current subscription if exists
        current_subscription = self.subscription_repo.get_active_by_user(user_id)
        if current_subscription:
            self.subscription_repo.update_status(current_subscription.id, SubscriptionStatus.CANCELLED)
        
        # Create new subscription (30 days)
        expires_at = datetime.utcnow() + timedelta(days=30)
        new_subscription = self.subscription_repo.create(
            user_id=user_id,
            plan=plan_type,
            monthly_quota=quota,
            expires_at=expires_at
        )
        
        return new_subscription
    
    def check_quota(self, user_id: int) -> dict:
        """Kiểm tra user còn quota để gọi API hay không"""
        subscription = self.get_active_subscription(user_id)
        
        if not subscription:
            return {"allowed": False, "reason": "No active subscription", "remaining": 0}
        
        remaining = subscription.monthly_quota - subscription.used_quota
        
        if remaining <= 0:
            return {"allowed": False, "reason": "Quota exceeded", "remaining": 0}
        
        return {"allowed": True, "remaining": remaining, "subscription_id": subscription.id}
    
    def increment_usage(self, subscription_id: int):
        """Tăng số lần đã dùng API (dùng sau mỗi lần predict)"""
        self.subscription_repo.increment_usage(subscription_id, 1)

