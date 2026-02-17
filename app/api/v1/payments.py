from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.schemas.payment import (
    OrderCreate,
    OrderRead,
    PaymentCreate,
    PaymentRead
)
from app.models.payment import Order, Payment


router = APIRouter()

@router.post("/orders/", response_model=OrderRead)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    new_order = Order(total_amount=order_in.total_amount)
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    return new_order

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

    result = await db.execute(
        select(Order)
        .where(Order.id==payment_in.order_id)
        .options(selectinload(Order.payments))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    already_paid = sum(
        p.amount for p in order.payments if p.status == "confirmed"
    )
    new_total = already_paid + payment_in.amount
    if new_total > order.total_amount:
        raise HTTPException(status_code=400, detail="Overpayment not allowed")
    
    new_payment = Payment(
        order_id = payment_in.order_id,
        amount = payment_in.amount,
        payment_type = payment_in.payment_type,
        status = "confirmed"
    )
    db.add(new_payment)

    if new_total == order.total_amount:
        order.status = "paid"
    else:
        order.status = "partially_paid"
    
    await db.commit()
    await db.refresh(new_payment)
    return new_payment
