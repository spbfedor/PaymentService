from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.payment import (
    OrderCreate,
    OrderRead,
    PaymentCreate,
    PaymentRead
)
from app.models.payment import Order
from app.services import payment_sevice


router = APIRouter()

@router.post("/orders/", response_model=OrderRead)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    return await payment_sevice.process_create_order(
        db,
        order_in.total_amount
    )

@router.get("/", response_model=list[OrderRead])
async def get_orders(db: AsyncSession = Depends(get_db)):
    query = select(Order)
    result = await db.execute(query)
    orders = result.scalars().all()
    return orders

@router.post("/payments/", response_model=PaymentRead)
async def create_payment(
    payment_in: PaymentCreate,
    db: AsyncSession = Depends(get_db)
):
    return await payment_sevice.process_deposit(
        db,
        payment_in.order_id,
        payment_in.amount,
        payment_in.payment_type
    )

@router.post("/payments/{payment_id}/refund", response_model=PaymentRead)
async def refund_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await payment_sevice.process_refund(
        db,
        payment_id
    )
