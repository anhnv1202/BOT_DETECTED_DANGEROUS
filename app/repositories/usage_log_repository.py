from sqlalchemy.orm import Session
from app.models.usage_log import UsageLog
from typing import List
from datetime import datetime, timedelta


class UsageLogRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, endpoint: str, method: str, 
               status_code: int = None, response_time_ms: float = None) -> UsageLog:
        log = UsageLog(
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def get_by_user(self, user_id: int, limit: int = 100) -> List[UsageLog]:
        return self.db.query(UsageLog).filter(
            UsageLog.user_id == user_id
        ).order_by(UsageLog.created_at.desc()).limit(limit).all()
    
    def count_by_user_in_period(self, user_id: int, start_date: datetime) -> int:
        return self.db.query(UsageLog).filter(
            UsageLog.user_id == user_id,
            UsageLog.created_at >= start_date
        ).count()
    
    def count_monthly_usage(self, user_id: int) -> int:
        """Count usage in current month"""
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        return self.count_by_user_in_period(user_id, start_of_month)



