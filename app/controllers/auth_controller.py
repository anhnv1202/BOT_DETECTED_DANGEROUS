from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import get_settings
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse, GoogleAuthRequest
from app.middleware.auth_middleware import get_current_user_id

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
settings = get_settings()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user with email and password"""
    auth_service = AuthService(db)
    
    try:
        user = auth_service.register(
            email=user_data.email,
            password=user_data.password,
            name=None  # Không còn trường name
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    access_token = auth_service.create_access_token(user.id)
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password"""
    auth_service = AuthService(db)
    
    user = auth_service.login(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = auth_service.create_access_token(user.id)
    return Token(access_token=access_token)


async def _handle_google_auth(code: str, db: Session) -> Token:
    """Helper function to exchange Google auth code for token"""
    auth_service = AuthService(db)
    user = await auth_service.google_login(code)
    access_token = auth_service.create_access_token(user.id)
    return Token(access_token=access_token)


@router.get("/google/callback")
async def google_auth_callback(code: str = Query(...)):
    """Handle Google OAuth callback: redirect code to frontend APP_URL"""
    redirect_to = f"{settings.APP_URL}/auth/callback?code={code}"
    return RedirectResponse(url=redirect_to, status_code=302)


@router.post("/google", response_model=Token)
async def google_auth(auth_request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate with Google OAuth (API client/mobile app)"""
    try:
        return await _handle_google_auth(auth_request.code, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google authentication failed: {str(e)}")


@router.get("/me", response_model=UserResponse)
def get_current_user(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get current user profile (requires authentication)"""
    from app.repositories.user_repository import UserRepository
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user



