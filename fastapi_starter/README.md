# FastAPI M-PESA Starter Kit

Production-ready M-PESA STK Push integration for FastAPI.

## What's included

- `/pay` — trigger STK Push on customer's phone
- `/pay/status` — query payment status
- `/mpesa/callback` — handle Safaricom payment results
- Full error handling with typed exceptions
- `.env` based config, sandbox/production toggle

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# fill in your Daraja credentials
```

Get sandbox credentials free at: https://developer.safaricom.co.ke

## Run

```bash
uvicorn main:app --reload
```

## Test with ngrok (local dev)

```bash
# Terminal 1
uvicorn main:app --reload

# Terminal 2
ngrok http 8000
# copy the https URL → paste into MPESA_CALLBACK_URL in .env
```

## Trigger a test payment

```bash
curl -X POST http://localhost:8000/pay \
  -H "Content-Type: application/json" \
  -d '{"phone": "254712345678", "amount": 1, "reference": "TEST-001"}'
```

## API Docs

Visit http://localhost:8000/docs for interactive Swagger UI.
