from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.bank_client import BankClient
from app.models.payment import Order, Payment

async def process_create_order(
        db: AsyncSession,
        total_amount: Decimal
) -> Order:
    new_order = Order(total_amount=total_amount)
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order

async def process_deposit(
        db: AsyncSession,
        order_id: UUID,
        amount: Decimal,
        payment_type: str
) -> Payment:
    result = await db.execute(
        select(Order)
        .where(Order.id==order_id)
        .options(selectinload(Order.payments))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    already_paid = sum(
        p.amount for p in order.payments if p.status == "confirmed"
    )

    if already_paid + amount > order.total_amount:
        remaining = order.total_amount - already_paid
        raise HTTPException(
            status_code=400, 
            detail=f"Overpayment! Limit: {remaining}, sent: {amount}"
        )

    bank_id = None
    if payment_type == "acquiring":
        try:
            bank_transaction_id = await BankClient.acquiring_start(
                order_id,
                amount
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Bank API error {str(e)}")

    new_payment = Payment(
        order_id=order_id,
        amount=amount,
        payment_type=payment_type,
        status="confirmed",
        bank_transaction_id=bank_id
    )

    db.add(new_payment)

    if already_paid + amount >= order.total_amount:
        order.status = "paid"
    else:
        order.status = "partially_paid"

    await db.commit()
    await db.refresh(new_payment)
    return new_payment

async def process_refund(
        db: AsyncSession,
        payment_id: UUID
) -> Payment:
    result = await db.execute(
        select(Payment)
        .where(Payment.id == payment_id)
        .options(
            selectinload(Payment.order)
            .selectinload(Order.payments)
        )
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status == "refunded":
        raise HTTPException(status_code=400, detail="Already refunded")
    payment.status = "refunded"
    order = payment.order

    total_confirmed = sum(
        p.amount for p in order.payments if p.status == "confirmed"
    )
    if total_confirmed >= order.total_amount:
        order.status = "paid"
    elif total_confirmed > 0:
        order.status = "partially_paid"
    else:
        order.status = "new"
    
    await db.commit()
    await db.refresh(payment)
    return payment
