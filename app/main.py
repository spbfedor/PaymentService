from fastapi import FastAPI

from app.api.v1 import payments

app = FastAPI(title="PaymentService")

@app.get("/")
async def root():
    return {"status": "ok"}

app.include_router(payments.router, prefix="/api/v1", tags=["orders"])