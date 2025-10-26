from sqlalchemy.orm import Session
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from typing import Optional, List


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, amount: float, tx_type: TransactionType, 
               status: TransactionStatus = TransactionStatus.PENDING,
               momo_request_id: Optional[str] = None,
               description: Optional[str] = None) -> Transaction:
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type=tx_type,
            status=status,
            momo_request_id=momo_request_id,
            description=description
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    def get_by_momo_request_id(self, request_id: str) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(
            Transaction.momo_request_id == request_id
        ).first()
    
    def get_by_momo_transaction_id(self, transaction_id: str) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(
            Transaction.momo_transaction_id == transaction_id
        ).first()
    
    def get_all_by_user(self, user_id: int) -> List[Transaction]:
        return self.db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(Transaction.created_at.desc()).all()
    
    def update_status(self, transaction_id: int, status: TransactionStatus, 
                     momo_transaction_id: Optional[str] = None) -> Optional[Transaction]:
        transaction = self.get_by_id(transaction_id)
        if transaction:
            transaction.status = status
            if momo_transaction_id:
                transaction.momo_transaction_id = momo_transaction_id
            self.db.commit()
            self.db.refresh(transaction)
        return transaction
    
    def update(self, transaction: Transaction) -> Transaction:
        self.db.commit()
        self.db.refresh(transaction)
        return transaction



