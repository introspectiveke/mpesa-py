import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from mpesa import MpesaClient, MpesaRequestError, MpesaValidationError, STKPushRequest

load_dotenv()

# ── Client setup ──────────────────────────────────────────────────────────────

mpesa = MpesaClient(
    consumer_key=os.environ["MPESA_CONSUMER_KEY"],
    consumer_secret=os.environ["MPESA_CONSUMER_SECRET"],
    shortcode=os.environ["MPESA_SHORTCODE"],
    passkey=os.environ["MPESA_PASSKEY"],
    sandbox=os.getenv("MPESA_SANDBOX", "true").lower() == "true",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("M-PESA client ready")
    yield


app = FastAPI(
    title="FastAPI M-PESA Starter",
    description="Production-ready M-PESA STK Push integration",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Schemas ───────────────────────────────────────────────────────────────────

class PaymentRequest(BaseModel):
    phone: str
    amount: int
    reference: str
    description: str = "Payment"


class PaymentResponse(BaseModel):
    success: bool
    checkout_request_id: str
    message: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "ok", "service": "FastAPI M-PESA Starter"}


@app.post("/pay", response_model=PaymentResponse)
async def initiate_payment(body: PaymentRequest):
    """
    Trigger an STK Push on the customer's phone.
    The customer enters their M-PESA PIN to complete payment.
    """
    callback_url = os.environ["MPESA_CALLBACK_URL"]

    try:
        response = await mpesa.stk.push(STKPushRequest(
            phone_number=body.phone,
            amount=body.amount,
            account_reference=body.reference,
            transaction_desc=body.description,
            callback_url=callback_url,
        ))
        return PaymentResponse(
            success=True,
            checkout_request_id=response.checkout_request_id,
            message=response.customer_message,
        )

    except MpesaValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    except MpesaRequestError as e:
        raise HTTPException(status_code=502, detail=f"M-PESA error: {e}")


@app.post("/pay/status")
async def payment_status(checkout_request_id: str):
    """Query the status of a previous STK Push."""
    try:
        result = await mpesa.stk.query(checkout_request_id)
        return {
            "result_code": result.result_code,
            "result_desc": result.result_desc,
            "success": result.result_code == "0",
        }
    except MpesaRequestError as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/mpesa/callback")
async def mpesa_callback(request: Request):
    """
    Safaricom sends payment results here after STK Push.
    Replace the print() with your database write or business logic.
    """
    payload = await request.json()

    try:
        callback = payload["Body"]["stkCallback"]
        result_code = callback["ResultCode"]
        result_desc = callback["ResultDesc"]
        merchant_request_id = callback["MerchantRequestID"]
        checkout_request_id = callback["CheckoutRequestID"]

        if result_code == 0:
            # Payment successful
            items = {
                item["Name"]: item.get("Value")
                for item in callback["CallbackMetadata"]["Item"]
            }
            print(f"✅ Payment received: {items}")
            # TODO: update your database here
            # await db.payments.update(checkout_request_id, status="paid", meta=items)
        else:
            print(f"❌ Payment failed: {result_desc}")
            # TODO: handle failure
            # await db.payments.update(checkout_request_id, status="failed")

    except KeyError as e:
        print(f"Unexpected callback format: {e}")

    # Always return 200 to Safaricom
    return JSONResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
