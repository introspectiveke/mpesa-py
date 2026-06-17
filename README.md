# mpesa-py

**Clean, async-first Python SDK for the Safaricom M-PESA Daraja API.**

Most Python M-PESA libraries are synchronous, poorly typed, and leave token management to you. `mpesa-py` fixes that.

```python
from mpesa import MpesaClient, STKPushRequest

client = MpesaClient(
    consumer_key="...",
    consumer_secret="...",
    shortcode="174379",
    passkey="...",
    sandbox=True,
)

response = await client.stk.push(STKPushRequest(
    phone_number="0712345678",
    amount=100,
    account_reference="ORDER-001",
    transaction_desc="Payment for order",
    callback_url="https://yourapp.com/mpesa/callback",
))
print(response.checkout_request_id)
```

---

## Features

- **Async-first** — built on `httpx`, works with FastAPI, Starlette, and any `asyncio` app
- **Auto token refresh** — OAuth tokens are cached and silently renewed before expiry
- **Pydantic models** — every request and response is fully typed
- **Meaningful errors** — `MpesaAuthError`, `MpesaRequestError`, `MpesaValidationError` instead of raw HTTP errors
- **Phone normalisation** — pass `0712...`, `+2547...`, or `2547...` — the SDK handles it

---

## Installation

```bash
pip install mpesa-py
```

Requires Python 3.10+.

---

## Quick Start

### 1. Get Daraja credentials

Register at [developer.safaricom.co.ke](https://developer.safaricom.co.ke), create an app, and note your:
- Consumer Key & Consumer Secret
- Business Short Code
- Lipa na M-PESA Passkey

### 2. Set environment variables

```bash
cp .env.example .env
# fill in your credentials
```

### 3. Initialise the client

```python
import os
from mpesa import MpesaClient

client = MpesaClient(
    consumer_key=os.environ["MPESA_CONSUMER_KEY"],
    consumer_secret=os.environ["MPESA_CONSUMER_SECRET"],
    shortcode=os.environ["MPESA_SHORTCODE"],
    passkey=os.environ["MPESA_PASSKEY"],
    sandbox=True,   # set False for production
)
```

---

## API Reference

### STK Push

**Initiate payment prompt:**
```python
from mpesa import STKPushRequest

response = await client.stk.push(STKPushRequest(
    phone_number="0712345678",
    amount=500,
    account_reference="INV-001",
    transaction_desc="Invoice payment",
    callback_url="https://yourapp.com/mpesa/callback",
))
# response.checkout_request_id — store this to query status later
```

**Query status:**
```python
status = await client.stk.query(checkout_request_id="ws_CO_...")
print(status.result_code)   # "0" = success
print(status.result_desc)
```

### C2B

**Register URLs:**
```python
from mpesa.models import C2BRegisterRequest

await client.c2b.register_urls(C2BRegisterRequest(
    confirmation_url="https://yourapp.com/mpesa/confirm",
    validation_url="https://yourapp.com/mpesa/validate",
))
```

**Simulate payment (sandbox only):**
```python
await client.c2b.simulate(phone="254712345678", amount=100, bill_ref="INV-001")
```

### B2C

```python
client = MpesaClient(
    ...,
    initiator_name="testapi",
    security_credential="...",
)

response = await client.b2c.pay(
    phone="254712345678",
    amount=200,
    result_url="https://yourapp.com/mpesa/b2c/result",
    queue_timeout_url="https://yourapp.com/mpesa/b2c/timeout",
    command_id="BusinessPayment",
    remarks="Refund",
)
```

---

## Error Handling

```python
from mpesa import MpesaAuthError, MpesaRequestError, MpesaValidationError

try:
    response = await client.stk.push(request)
except MpesaValidationError as e:
    # Bad input — fix before retrying
    print(f"Validation: {e}")
except MpesaAuthError as e:
    # Wrong credentials or network issue on auth
    print(f"Auth error ({e.status_code}): {e}")
except MpesaRequestError as e:
    # Daraja returned a non-2xx response
    print(f"API error ({e.status_code}): {e}")
```

---

## FastAPI Integration

```python
from fastapi import FastAPI
from mpesa import MpesaClient, STKPushRequest

app = FastAPI()
mpesa = MpesaClient(...)

@app.post("/pay")
async def pay(phone: str, amount: int):
    response = await mpesa.stk.push(STKPushRequest(
        phone_number=phone,
        amount=amount,
        account_reference="ORDER",
        transaction_desc="Payment",
        callback_url="https://yourapp.com/mpesa/callback",
    ))
    return {"checkout_request_id": response.checkout_request_id}

@app.post("/mpesa/callback")
async def mpesa_callback(payload: dict):
    # Handle the callback from Safaricom
    result = payload["Body"]["stkCallback"]
    print(result["ResultCode"], result["ResultDesc"])
    return {"ResultCode": 0, "ResultDesc": "Accepted"}
```

---

## Development

```bash
git clone https://github.com/introspectiveke/mpesa-py
cd mpesa-py
pip install -e ".[dev]"
pytest
```

---

## License

MIT
