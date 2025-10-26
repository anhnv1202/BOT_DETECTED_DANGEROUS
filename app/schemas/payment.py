from pydantic import BaseModel
from typing import Optional


class TopupRequest(BaseModel):
    amount: int  # VND, minimum 10000


class TopupResponse(BaseModel):
    pay_url: str
    request_id: str
    qr_code_url: Optional[str] = None


class MoMoIPNRequest(BaseModel):
    partnerCode: str
    orderId: str
    requestId: str
    amount: int
    orderInfo: str
    orderType: str
    transId: int
    resultCode: int
    message: str
    payType: str
    responseTime: int
    extraData: str
    signature: str



