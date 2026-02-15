import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, ForeignKey, Numeric, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="new",
        server_default="new"
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id"), 
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=False
    )
    payment_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending"
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    bank_transaction_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    order: Mapped["Order"] = relationship(back_populates="payments")