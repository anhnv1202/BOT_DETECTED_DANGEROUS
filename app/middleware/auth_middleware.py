from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.auth_service import AuthService

security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> int:
    """Extract and validate JWT token, return user_id"""
    token = credentials.credentials
    
    auth_service = AuthService(db)
    user_id = auth_service.decode_token(token)
    
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_id


def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[int]:
    """Extract user_id if token provided, otherwise return None"""
    if not credentials:
        return None
    
    token = credentials.credentials
    auth_service = AuthService(db)
    return auth_service.decode_token(token)



