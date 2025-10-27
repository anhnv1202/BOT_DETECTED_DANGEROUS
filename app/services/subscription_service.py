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
    
    PLAN_HIERARCHY = {PlanType.FREE: 0, PlanType.PLUS: 1, PlanType.PRO: 2}
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.subscription_repo = SubscriptionRepository(db)
        self.transaction_repo = TransactionRepository(db)
    
    def get_plan_details(self, plan: PlanType) -> dict:
        """Lấy thông tin quota và giá của từng gói"""
        configs = {
            PlanType.FREE: {"quota": settings.PLAN_FREE_MONTHLY_QUOTA, "price": 0},
            PlanType.PLUS: {"quota": settings.PLAN_PLUS_MONTHLY_QUOTA, "price": settings.PLAN_PLUS_PRICE},
            PlanType.PRO: {"quota": settings.PLAN_PRO_MONTHLY_QUOTA, "price": settings.PLAN_PRO_PRICE},
        }
        return configs.get(plan, {"quota": 0, "price": 0})
    
    def get_active_subscription(self, user_id: int) -> Optional[Subscription]:
        """
        Lấy gói subscription đang active của user
        - CANCELLED subscription: User vẫn dùng đến hết hạn
        - EXPIRED: Tự động chuyển về FREE
        """
        subscription = self.subscription_repo.get_active_by_user(user_id)
        now = datetime.utcnow()
        
        # Handle expired subscriptions
        if subscription and subscription.expires_at and subscription.expires_at < now:
            # Auto-downgrade to FREE if was ACTIVE or CANCELLED
            if subscription.status in (SubscriptionStatus.ACTIVE, SubscriptionStatus.CANCELLED):
                self.subscription_repo.update_status(subscription.id, SubscriptionStatus.EXPIRED)
                return self.subscription_repo.create(
                    user_id=user_id, plan=PlanType.FREE,
                    monthly_quota=settings.PLAN_FREE_MONTHLY_QUOTA
                )
        
        return subscription
    
    def purchase_plan(self, user_id: int, plan: str) -> Subscription:
        """Mua gói PLUS/PRO bằng credits trong ví (30 ngày)"""
        if plan not in ("plus", "pro"):
            raise ValueError("Invalid plan. Choose 'plus' or 'pro'")
        
        plan_type = PlanType.PLUS if plan == "plus" else PlanType.PRO
        plan_details = self.get_plan_details(plan_type)
        price = plan_details["price"]
        
        # Validate user and credits
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if user.credits < price:
            raise ValueError(f"Insufficient credits. Required: {price}, Available: {user.credits}")
        
        # Check current subscription
        current_subscription = self.subscription_repo.get_active_by_user(user_id)
        
        # Prevent duplicate purchase
        if current_subscription and current_subscription.plan == plan_type:
            msg = (f"You cancelled your {plan.upper()} subscription, but you can still use it until it expires. "
                   if current_subscription.status == SubscriptionStatus.CANCELLED
                   else f"You are already on the {plan.upper()} plan.")
            raise ValueError(msg + " No need to purchase again.")
        
        # Prevent downgrade
        if current_subscription:
            current_level = self.PLAN_HIERARCHY.get(current_subscription.plan, 0)
            if self.PLAN_HIERARCHY.get(plan_type, 0) < current_level:
                raise ValueError(
                    f"Cannot downgrade from {current_subscription.plan.upper()} to {plan.upper()}. "
                    "You can only upgrade or cancel your current subscription."
                )
        
        # Process payment
        self.user_repo.update_credits(user_id, -price)
        self.transaction_repo.create(
            user_id=user_id, amount=price,
            tx_type=TransactionType.PURCHASE, status=TransactionStatus.SUCCESS,
            description=f"Purchase {plan.upper()} plan"
        )
        
        # Cancel current and create new subscription
        if current_subscription:
            self.subscription_repo.update_status(current_subscription.id, SubscriptionStatus.CANCELLED)
        
        return self.subscription_repo.create(
            user_id=user_id, plan=plan_type, monthly_quota=plan_details["quota"],
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
    
    def cancel_subscription(self, user_id: int) -> Subscription:
        """
        Cancel current subscription - user can still use until expires
        Will auto-downgrade to FREE when expires_at reached
        """
        current_subscription = self.subscription_repo.get_active_by_user(user_id)
        
        if not current_subscription:
            raise ValueError("No active subscription to cancel")
        
        if current_subscription.plan == PlanType.FREE:
            raise ValueError("Cannot cancel FREE plan")
        
        # Mark as cancelled - user can still use until expires_at
        self.subscription_repo.update_status(current_subscription.id, SubscriptionStatus.CANCELLED)
        
        return current_subscription  # Return cancelled subscription
    
    def check_and_renew(self, user_id: int):
        """Check if subscription expired and auto-renew (called periodically)"""
        subscription = self.subscription_repo.get_active_by_user(user_id)
        if subscription and subscription.expires_at and subscription.status == SubscriptionStatus.ACTIVE:
            if subscription.expires_at < datetime.utcnow():
                self.subscription_repo.update_status(subscription.id, SubscriptionStatus.EXPIRED)
    
    def check_quota(self, user_id: int) -> dict:
        """Kiểm tra user còn quota để gọi API hay không"""
        subscription = self.get_active_subscription(user_id)
        
        if not subscription:
            return {"allowed": False, "reason": "No active subscription", "remaining": 0}
        
        remaining = subscription.monthly_quota - subscription.used_quota
        
        return {
            "allowed": remaining > 0,
            "remaining": max(remaining, 0),
            "subscription_id": subscription.id,
            **({"reason": "Quota exceeded"} if remaining <= 0 else {})
        }
    
    def increment_usage(self, subscription_id: int):
        """Tăng số lần đã dùng API (dùng sau mỗi lần predict)"""
        self.subscription_repo.increment_usage(subscription_id, 1)

