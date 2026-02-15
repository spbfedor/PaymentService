from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
    total_amount: Decimal = Field(gt=0, decimal_places=2)


class OrderRead(OrderCreate):
    id: UUID
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentCreate(BaseModel):
    amount: Decimal = Field(gt=0, decimal_places=2)
    payment_type: Literal["cash", "acquiring"]


class PaymentRead(PaymentCreate):
    id: UUID
    order_id: UUID
    status: str
    created_at: datetime
    bank_transaction_id: str | None = None

    model_config = ConfigDict(from_attributes=True)