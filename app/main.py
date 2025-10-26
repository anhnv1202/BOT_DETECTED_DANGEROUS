from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db
from app.controllers import auth_router, payment_router, subscription_router, prediction_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(payment_router)
app.include_router(subscription_router)
app.include_router(prediction_router)


@app.get("/")
def root():
    """API root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "ok",
        "endpoints": {
            "auth": "/api/auth",
            "payment": "/api/payment",
            "subscription": "/api/subscription",
            "prediction": "/api/v1",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"}
