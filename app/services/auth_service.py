from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import httpx
import hashlib
import bcrypt

from app.config import get_settings
from app.repositories.user_repository import UserRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.models.user import User
from app.models.subscription import PlanType

settings = get_settings()


class AuthService:
    """Service xử lý authentication (đăng ký, đăng nhập, JWT)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.subscription_repo = SubscriptionRepository(db)
    
    def hash_password(self, password: str) -> str:
        """Mã hóa password bằng SHA-256 + bcrypt (hỗ trợ password dài không giới hạn)"""
        # Luôn hash bằng SHA-256 trước để đảm bảo input cho bcrypt là 64 hex chars (32 bytes)
        # Điều này cho phép password bất kỳ độ dài nào
        password_sha256 = hashlib.sha256(password.encode('utf-8')).hexdigest()
        # Bcrypt giới hạn 72 bytes, nhưng SHA256 hexdigest chỉ 64 chars (32 bytes)
        # Hash bằng bcrypt trực tiếp (không dùng passlib)
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_sha256.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Kiểm tra password có khớp với hash không"""
        # Hash password bằng SHA-256 trước khi verify
        password_sha256 = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        # Verify bằng bcrypt
        return bcrypt.checkpw(password_sha256.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, user_id: int) -> str:
        """Tạo JWT token cho user (expire sau 7 ngày)"""
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": str(user_id), "exp": expire}
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[int]:
        """Giải mã JWT token và trả về user_id"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return int(user_id)
        except JWTError:
            return None
    
    def register(self, email: str, password: str, name: Optional[str] = None) -> User:
        """Đăng ký user mới với email/password và tạo gói FREE"""
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        hashed_password = self.hash_password(password)
        user = self.user_repo.create(email=email, name=name, hashed_password=hashed_password)
        
        # Create free subscription
        self.subscription_repo.create(
            user_id=user.id,
            plan=PlanType.FREE,
            monthly_quota=settings.PLAN_FREE_MONTHLY_QUOTA
        )
        
        return user
    
    def login(self, email: str, password: str) -> Optional[User]:
        """Đăng nhập bằng email/password"""
        user = self.user_repo.get_by_email(email)
        if not user or not user.hashed_password:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    async def google_login(self, code: str) -> User:
        """Đăng nhập/đăng ký bằng Google OAuth (tự động link account nếu email đã tồn tại)"""
        # Exchange code for token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
            access_token = tokens.get("access_token")
            
            # Get user info
            user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_info_response = await client.get(user_info_url, headers=headers)
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
        
        google_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name")
        avatar = user_info.get("picture")
        
        # Check if user exists
        user = self.user_repo.get_by_google_id(google_id)
        if not user:
            user = self.user_repo.get_by_email(email)
            if user:
                # Link Google account to existing user
                user.google_id = google_id
                user.avatar = avatar or user.avatar
                user = self.user_repo.update(user)
            else:
                # Create new user
                user = self.user_repo.create(
                    email=email,
                    name=name,
                    google_id=google_id,
                    avatar=avatar
                )
                # Create free subscription
                self.subscription_repo.create(
                    user_id=user.id,
                    plan=PlanType.FREE,
                    monthly_quota=settings.PLAN_FREE_MONTHLY_QUOTA
                )
        
        return user
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Lấy thông tin user từ JWT token"""
        user_id = self.decode_token(token)
        if user_id is None:
            return None
        return self.user_repo.get_by_id(user_id)

