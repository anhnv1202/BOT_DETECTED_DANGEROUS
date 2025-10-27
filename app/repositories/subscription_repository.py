from sqlalchemy.orm import Session
from app.models.subscription import Subscription, PlanType, SubscriptionStatus
from typing import Optional, List
from datetime import datetime


class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, plan: PlanType, monthly_quota: int, 
               expires_at: Optional[datetime] = None) -> Subscription:
        subscription = Subscription(
            user_id=user_id,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            monthly_quota=monthly_quota,
            expires_at=expires_at
        )
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
    
    def get_by_id(self, subscription_id: int) -> Optional[Subscription]:
        return self.db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    def get_active_by_user(self, user_id: int) -> Optional[Subscription]:
        """
        Get current active subscription for user
        Includes CANCELLED subscriptions that haven't expired yet
        """
        from sqlalchemy import or_
        return self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            or_(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.status == SubscriptionStatus.CANCELLED
            )
        ).order_by(Subscription.created_at.desc()).first()
    
    def get_all_by_user(self, user_id: int) -> List[Subscription]:
        return self.db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).order_by(Subscription.created_at.desc()).all()
    
    def increment_usage(self, subscription_id: int, count: int = 1) -> Optional[Subscription]:
        subscription = self.get_by_id(subscription_id)
        if subscription:
            subscription.used_quota += count
            self.db.commit()
            self.db.refresh(subscription)
        return subscription
    
    def reset_usage(self, subscription_id: int) -> Optional[Subscription]:
        subscription = self.get_by_id(subscription_id)
        if subscription:
            subscription.used_quota = 0
            self.db.commit()
            self.db.refresh(subscription)
        return subscription
    
    def update_status(self, subscription_id: int, status: SubscriptionStatus) -> Optional[Subscription]:
        subscription = self.get_by_id(subscription_id)
        if subscription:
            subscription.status = status
            self.db.commit()
            self.db.refresh(subscription)
        return subscription
    
    def bulk_update_status(self, subscription_ids: List[int], status: SubscriptionStatus) -> int:
        """Bulk update status for multiple subscriptions"""
        result = self.db.query(Subscription).filter(Subscription.id.in_(subscription_ids)).update(
            {"status": status}, synchronize_session=False
        )
        self.db.commit()
        return result
    
    def update(self, subscription: Subscription) -> Subscription:
        self.db.commit()
        self.db.refresh(subscription)
        return subscription



