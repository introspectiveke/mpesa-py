"""
Example: register C2B confirmation and validation URLs.

Run once per shortcode. Use ngrok for local development:
    ngrok http 8000
"""

import asyncio
import os

from dotenv import load_dotenv

from mpesa import MpesaClient
from mpesa.models import C2BRegisterRequest

load_dotenv()

NGROK_URL = "https://your-ngrok-url.ngrok.io"


async def main() -> None:
    client = MpesaClient(
        consumer_key=os.environ["MPESA_CONSUMER_KEY"],
        consumer_secret=os.environ["MPESA_CONSUMER_SECRET"],
        shortcode=os.environ["MPESA_SHORTCODE"],
        passkey=os.environ["MPESA_PASSKEY"],
        sandbox=True,
    )

    response = await client.c2b.register_urls(
        C2BRegisterRequest(
            confirmation_url=f"{NGROK_URL}/mpesa/confirm",
            validation_url=f"{NGROK_URL}/mpesa/validate",
        )
    )

    print(f"ConversationID : {response.conversation_id}")
    print(f"Response       : {response.response_description}")

    # Simulate a payment (sandbox only)
    sim = await client.c2b.simulate(phone="254712345678", amount=100, bill_ref="INV-001")
    print(f"Simulation     : {sim}")


if __name__ == "__main__":
    asyncio.run(main())
