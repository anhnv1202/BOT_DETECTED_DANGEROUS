from app.controllers.auth_controller import router as auth_router
from app.controllers.payment_controller import router as payment_router
from app.controllers.subscription_controller import router as subscription_router
from app.controllers.prediction_controller import router as prediction_router

__all__ = ["auth_router", "payment_router", "subscription_router", "prediction_router"]



