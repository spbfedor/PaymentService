from fastapi import FastAPI

app = FastAPI(title="PaymentService")

@app.get("/")
async def root():
    return {"status": "ok"}