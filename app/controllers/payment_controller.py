from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx
import json

from app.database import get_db
from app.services.payment_service import PaymentService
from app.config import get_settings
from app.schemas.payment import TopupRequest, TopupResponse
from app.middleware.auth_middleware import get_current_user_id

router = APIRouter(prefix="/api/payment", tags=["Payment"])
settings = get_settings()


@router.post("/topup", response_model=TopupResponse)
async def create_topup(
    topup_data: TopupRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Create MoMo payment for topup (requires authentication)"""
    payment_service = PaymentService(db)
    
    try:
        result = await payment_service.create_topup_payment(user_id, topup_data.amount)
        return TopupResponse(
            pay_url=result["pay_url"],
            request_id=result["request_id"],
            qr_code_url=result.get("qr_code_url")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPStatusError as e:
        # Enhanced error for MoMo API errors
        error_detail = f"MoMo API error: {e.response.status_code} - {e.response.text}"
        raise HTTPException(status_code=500, detail=error_detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment creation failed: {str(e)}")


@router.post("/momo/ipn")
async def momo_ipn(request: Request, db: Session = Depends(get_db)):
    """MoMo IPN callback endpoint (webhook)"""
    payment_service = PaymentService(db)
    
    try:
        raw_body = await request.body()
        raw_body_str = raw_body.decode('utf-8')
        
        # Handle empty body (health check)
        if not raw_body_str.strip():
            return {"resultCode": 0, "message": "IPN endpoint is ready"}
        
        ipn_data = json.loads(raw_body_str)
        success = payment_service.process_ipn(ipn_data)
        
        return {
            "partnerCode": ipn_data.get("partnerCode"),
            "requestId": ipn_data.get("requestId"),
            "orderId": ipn_data.get("orderId"),
            "resultCode": 0 if success else 1,
            "message": "Success" if success else "Failed"
        }
        
    except json.JSONDecodeError:
        return {"resultCode": 1, "message": "Invalid JSON"}
    except ValueError as e:
        return {"resultCode": 1, "message": f"Validation failed: {str(e)}"}
    except Exception as e:
        return {"resultCode": 1, "message": "Processing failed"}


@router.get("/success")
async def payment_success_redirect(
    orderId: str,
    requestId: str,
    resultCode: int,
    amount: int = None,
    transId: int = None,
    message: str = None
):
    """Redirect URL sau khi user thanh toán trên MoMo → redirect sang FE"""
    # Build frontend redirect URL with all useful params
    query = {
        "orderId": orderId,
        "requestId": requestId,
        "resultCode": resultCode,
        "amount": amount,
        "transId": transId,
        "message": message,
    }
    # Remove None values
    query_str = "&".join([
        f"{k}={v}" for k, v in query.items() if v is not None
    ])
    fe_url = f"{settings.APP_URL}/payment/success"
    redirect_to = f"{fe_url}?{query_str}" if query_str else fe_url
    return RedirectResponse(url=redirect_to, status_code=302)