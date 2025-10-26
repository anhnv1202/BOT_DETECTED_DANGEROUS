from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)  # For email/password auth
    google_id = Column(String, unique=True, nullable=True, index=True)  # For OAuth
    credits = Column(Float, default=0.0)  # Wallet balance in VND
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    usage_logs = relationship("UsageLog", back_populates="user")



