"""
Example: trigger an STK Push on a customer's phone.

1. Copy .env.example → .env and fill in your Daraja sandbox credentials.
2. Run:  python examples/stk_push.py
"""

import asyncio
import os

from dotenv import load_dotenv

from mpesa import MpesaClient, STKPushRequest

load_dotenv()


async def main() -> None:
    client = MpesaClient(
        consumer_key=os.environ["MPESA_CONSUMER_KEY"],
        consumer_secret=os.environ["MPESA_CONSUMER_SECRET"],
        shortcode=os.environ["MPESA_SHORTCODE"],
        passkey=os.environ["MPESA_PASSKEY"],
        sandbox=True,
    )

    response = await client.stk.push(
        STKPushRequest(
            phone_number="254712345678",        # replace with your sandbox test number
            amount=1,                           # 1 KES — minimum
            account_reference="ORDER-001",
            transaction_desc="Test payment",
            callback_url="https://your-ngrok-url.ngrok.io/mpesa/callback",
        )
    )

    print(f"MerchantRequestID : {response.merchant_request_id}")
    print(f"CheckoutRequestID : {response.checkout_request_id}")
    print(f"Message           : {response.customer_message}")


if __name__ == "__main__":
    asyncio.run(main())
