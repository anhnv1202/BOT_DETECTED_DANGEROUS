import hashlib
import hmac
import uuid
import httpx
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.config import get_settings
from app.repositories.user_repository import UserRepository
from app.repositories.transaction_repository import TransactionRepository
from app.models.transaction import TransactionType, TransactionStatus

settings = get_settings()


class PaymentService:
    """Service xử lý payment qua MoMo (captureWallet, verify IPN, cộng tiền vào ví)."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.transaction_repo = TransactionRepository(db)

    @staticmethod
    def _sign(secret: str, raw: str) -> str:
        """Tạo chữ ký HMAC SHA256"""
        return hmac.new(secret.encode("utf-8"), raw.encode("utf-8"), hashlib.sha256).hexdigest()

    async def create_topup_payment(self, user_id: int, amount: int) -> Dict[str, Any]:
        """Tạo link thanh toán MoMo QR (captureWallet) để user nạp tiền"""
        if amount < 1000:
            raise ValueError("Minimum topup amount is 1,000 VND")

        # Tạo ID duy nhất
        order_id = f"TOPUP_{user_id}_{uuid.uuid4().hex[:8]}"
        request_id = f"REQ_{uuid.uuid4().hex}"

        # Lưu giao dịch pending
        self.transaction_repo.create(
            user_id=user_id,
            amount=float(amount),
            tx_type=TransactionType.TOPUP,
            status=TransactionStatus.PENDING,
            momo_request_id=request_id,
            description=f"Topup {amount} VND",
        )

        # Chuẩn bị tham số ký
        partner_code = settings.MOMO_PARTNER_CODE
        access_key = settings.MOMO_ACCESS_KEY
        secret_key = settings.MOMO_SECRET_KEY
        redirect_url = settings.MOMO_REDIRECT_URL
        ipn_url = settings.MOMO_IPN_URL
        request_type = "captureWallet"
        order_info = f"Topup {amount} VND"
        extra_data = ""

        # Tạo raw signature (phải đúng thứ tự tham số)
        raw_signature = (
            f"accessKey={access_key}"
            f"&amount={amount}"
            f"&extraData={extra_data}"
            f"&ipnUrl={ipn_url}"
            f"&orderId={order_id}"
            f"&orderInfo={order_info}"
            f"&partnerCode={partner_code}"
            f"&redirectUrl={redirect_url}"
            f"&requestId={request_id}"
            f"&requestType={request_type}"
        )

        signature = self._sign(secret_key, raw_signature)

        # Payload gửi MoMo
        payload = {
            "partnerCode": partner_code,
            "accessKey": access_key,
            "requestId": request_id,
            "amount": str(amount),
            "orderId": order_id,
            "orderInfo": order_info,
            "redirectUrl": redirect_url,
            "ipnUrl": ipn_url,
            "extraData": extra_data,
            "requestType": request_type,
            "signature": signature,
            "lang": "vi",
        }

        # Gửi request
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            resp = await client.post(settings.MOMO_ENDPOINT, json=payload)
            resp.raise_for_status()
            result = resp.json()

        # Check kết quả
        if result.get("resultCode") != 0:
            tx = self.transaction_repo.get_by_momo_request_id(request_id)
            if tx and tx.status == TransactionStatus.PENDING:
                self.transaction_repo.update_status(tx.id, TransactionStatus.FAILED)
            raise RuntimeError(f"MoMo error: {result.get('message')}")

        return {
            "pay_url": result.get("payUrl"),
            "qr_code_url": result.get("qrCodeUrl"),
            "deeplink": result.get("deeplink"),
            "order_id": order_id,
            "request_id": request_id,
            "raw_result": result,
        }

    def verify_ipn_signature(self, ipn_data: Dict[str, Any]) -> bool:
        """Xác thực chữ ký IPN từ MoMo"""
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
        expected_signature = self._sign(settings.MOMO_SECRET_KEY, raw_signature)
        return expected_signature == ipn_data.get("signature")

    def process_ipn(self, ipn_data: Dict[str, Any]) -> bool:
        """Xử lý callback từ MoMo: verify + cập nhật trạng thái"""
        if not self.verify_ipn_signature(ipn_data):
            raise ValueError("Invalid IPN signature")

        request_id = ipn_data.get("requestId")
        tx = self.transaction_repo.get_by_momo_request_id(request_id)
        if not tx:
            raise ValueError(f"Transaction not found: {request_id}")

        if tx.status != TransactionStatus.PENDING:
            return True

        if ipn_data.get("resultCode") == 0:
            self.transaction_repo.update_status(
                tx.id,
                TransactionStatus.SUCCESS,
                momo_transaction_id=str(ipn_data.get("transId")),
            )
            self.user_repo.update_credits(tx.user_id, tx.amount)
            return True
        else:
            self.transaction_repo.update_status(tx.id, TransactionStatus.FAILED)
            return False
