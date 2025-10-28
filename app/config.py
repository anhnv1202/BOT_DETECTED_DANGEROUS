from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Dangerous Objects AI API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    APP_URL: str = "http://localhost:8000/fe"  # Frontend base URL to receive OAuth codes
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    
    # MoMo Payment
    MOMO_PARTNER_CODE: str = "MOMO"
    MOMO_ACCESS_KEY: str = "F8BBA842ECF85"
    MOMO_SECRET_KEY: str = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    MOMO_ENDPOINT: str = "https://test-payment.momo.vn/v2/gateway/api/create"
    MOMO_REDIRECT_URL: str = "http://localhost:8000/api/payment/success"
    MOMO_IPN_URL: str = "http://localhost:8000/api/payment/momo/ipn"
    
    # ML Model
    MODEL_PATH: str = "mobilenetv2_dangerous_objects.pth"
    MODEL_IMG_SIZE: int = 224

    MODEL_CLASSES: list = ["0", "1", "2", "3"]
    
    # Subscription Plans
    PLAN_FREE_MONTHLY_QUOTA: int = 100
    PLAN_PLUS_MONTHLY_QUOTA: int = 5000
    PLAN_PRO_MONTHLY_QUOTA: int = 999999
    
    PLAN_PLUS_PRICE: int = 99000  # VND
    PLAN_PRO_PRICE: int = 299000  # VND
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()



