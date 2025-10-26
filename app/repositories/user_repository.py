from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional


class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, email: str, name: Optional[str] = None, hashed_password: Optional[str] = None, 
               google_id: Optional[str] = None, avatar: Optional[str] = None) -> User:
        user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,
            google_id=google_id,
            avatar=avatar
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_google_id(self, google_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.google_id == google_id).first()
    
    def update_credits(self, user_id: int, amount: float) -> Optional[User]:
        user = self.get_by_id(user_id)
        if user:
            user.credits += amount
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user



