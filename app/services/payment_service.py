import hashlib
import hmac
import uuid
import httpx
from typing import Dict
from sqlalchemy.orm import Session

from app.config import get_settings
from app.repositories.user_repository import UserRepository
from app.repositories.transaction_repository import TransactionRepository
from app.models.transaction import TransactionType, TransactionStatus

settings = get_settings()


class PaymentService:
    """Service xử lý payment qua MoMo (tạo QR, verify IPN, cộng tiền vào ví)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.transaction_repo = TransactionRepository(db)
    
    def generate_signature(self, data: str) -> str:
        """Tạo chữ ký HMAC SHA256 để bảo mật với MoMo"""
        return hmac.new(
            settings.MOMO_SECRET_KEY.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def create_topup_payment(self, user_id: int, amount: int) -> Dict:
        """Tạo link thanh toán MoMo QR để user nạp tiền (tối thiểu 10,000 VNĐ)"""
        if amount < 10000:
            raise ValueError("Minimum topup amount is 10,000 VND")
        
        # Generate unique IDs
        order_id = f"TOPUP_{user_id}_{uuid.uuid4().hex[:8]}"
        request_id = f"REQ_{uuid.uuid4().hex}"
        
        # Create pending transaction
        transaction = self.transaction_repo.create(
            user_id=user_id,
            amount=float(amount),
            tx_type=TransactionType.TOPUP,
            status=TransactionStatus.PENDING,
            momo_request_id=request_id,
            description=f"Topup {amount} VND"
        )
        
        # Build MoMo request
        raw_signature = (
            f"accessKey={settings.MOMO_ACCESS_KEY}"
            f"&amount={amount}"
            f"&extraData="
            f"&ipnUrl={settings.MOMO_IPN_URL}"
            f"&orderId={order_id}"
            f"&orderInfo=Topup {amount} VND"
            f"&partnerCode={settings.MOMO_PARTNER_CODE}"
            f"&redirectUrl={settings.MOMO_REDIRECT_URL}"
            f"&requestId={request_id}"
            f"&requestType=captureWallet"
        )
        
        signature = self.generate_signature(raw_signature)
        
        payload = {
            "partnerCode": settings.MOMO_PARTNER_CODE,
            "accessKey": settings.MOMO_ACCESS_KEY,
            "requestId": request_id,
            "amount": amount,
            "orderId": order_id,
            "orderInfo": f"Topup {amount} VND",
            "redirectUrl": settings.MOMO_REDIRECT_URL,
            "ipnUrl": settings.MOMO_IPN_URL,
            "extraData": "",
            "requestType": "captureWallet",
            "signature": signature,
            "lang": "vi"
        }
        
        # Call MoMo API
        async with httpx.AsyncClient() as client:
            response = await client.post(settings.MOMO_ENDPOINT, json=payload, timeout=30.0)
            response.raise_for_status()
            result = response.json()
        
        if result.get("resultCode") != 0:
            raise Exception(f"MoMo error: {result.get('message')}")
        
        return {
            "pay_url": result.get("payUrl"),
            "qr_code_url": result.get("qrCodeUrl"),
            "request_id": request_id
        }
    
    def verify_ipn_signature(self, ipn_data: Dict) -> bool:
        """Kiểm tra chữ ký IPN từ MoMo để đảm bảo request hợp lệ"""
        raw_signature = (
            f"accessKey={settings.MOMO_ACCESS_KEY}"
            f"&amount={ipn_data['amount']}"
            f"&extraData={ipn_data['extraData']}"
            f"&message={ipn_data['message']}"
            f"&orderId={ipn_data['orderId']}"
            f"&orderInfo={ipn_data['orderInfo']}"
            f"&orderType={ipn_data['orderType']}"
            f"&partnerCode={ipn_data['partnerCode']}"
            f"&payType={ipn_data['payType']}"
            f"&requestId={ipn_data['requestId']}"
            f"&responseTime={ipn_data['responseTime']}"
            f"&resultCode={ipn_data['resultCode']}"
            f"&transId={ipn_data['transId']}"
        )
        expected_signature = self.generate_signature(raw_signature)
        return expected_signature == ipn_data.get("signature")
    
    def process_ipn(self, ipn_data: Dict) -> bool:
        """Xử lý callback từ MoMo sau khi user thanh toán (cộng tiền vào ví user)"""
        if not self.verify_ipn_signature(ipn_data):
            raise ValueError("Invalid IPN signature")
        
        request_id = ipn_data.get("requestId")
        transaction = self.transaction_repo.get_by_momo_request_id(request_id)
        
        if not transaction:
            raise ValueError(f"Transaction not found for request_id: {request_id}")
        
        # Check if already processed
        if transaction.status != TransactionStatus.PENDING:
            return True
        
        result_code = ipn_data.get("resultCode")
        
        if result_code == 0:  # Success
            # Update transaction
            self.transaction_repo.update_status(
                transaction.id,
                TransactionStatus.SUCCESS,
                momo_transaction_id=str(ipn_data.get("transId"))
            )
            
            # Add credits to user
            self.user_repo.update_credits(transaction.user_id, transaction.amount)
            return True
        else:
            # Payment failed
            self.transaction_repo.update_status(transaction.id, TransactionStatus.FAILED)
            return False

