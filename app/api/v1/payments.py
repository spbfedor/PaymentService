from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.payment import OrderCreate, OrderRead
from app.models.payment import Order


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