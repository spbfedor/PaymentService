import uuid
from datetime import datetime
from decimal import Decimal


class BankClient:
    @staticmethod
    async def acquiring_start(
        order_id: uuid.UUID,
        amount: Decimal
    ) -> str:
        # await httpx.post(bank.api/acquiring_start) 
        if amount > 1000000:
            raise Exception("Bank: Limit exceeded")
        return f"BANK-ID-{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    async def check_status(bank_transaction_id: str):
        # await httpx.get(bank.api/acquiring_check)
        return {
            "status": "confirmed",
            "bank_id": bank_transaction_id,
            "amount": Decimal("100.00"),
            "payment_at": datetime.now().isoformat()
        }
