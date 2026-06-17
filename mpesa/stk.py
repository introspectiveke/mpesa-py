import base64
from datetime import datetime

import httpx

from .auth import TokenManager
from .exceptions import MpesaRequestError, MpesaValidationError
from .models import STKPushRequest, STKPushResponse, STKQueryResponse


class STKPush:
    def __init__(
        self,
        token_manager: TokenManager,
        shortcode: str,
        passkey: str,
        base_url: str,
    ):
        self._tm = token_manager
        self._shortcode = shortcode
        self._passkey = passkey
        self._base_url = base_url

    # ── Public ────────────────────────────────────────────────────────────────

    async def push(self, request: STKPushRequest) -> STKPushResponse:
        """Initiate an STK Push prompt on the customer's phone."""
        self._validate(request)

        token = await self._tm.get_token()
        ts = self._timestamp()

        payload = {
            "BusinessShortCode": self._shortcode,
            "Password": self._password(ts),
            "Timestamp": ts,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": request.amount,
            "PartyA": self._fmt_phone(request.phone_number),
            "PartyB": self._shortcode,
            "PhoneNumber": self._fmt_phone(request.phone_number),
            "CallBackURL": request.callback_url,
            "AccountReference": request.account_reference,
            "TransactionDesc": request.transaction_desc,
        }

        data = await self._post("/mpesa/stkpush/v1/processrequest", payload, token)
        return STKPushResponse(**data)

    async def query(self, checkout_request_id: str) -> STKQueryResponse:
        """Check the status of a previous STK Push request."""
        token = await self._tm.get_token()
        ts = self._timestamp()

        payload = {
            "BusinessShortCode": self._shortcode,
            "Password": self._password(ts),
            "Timestamp": ts,
            "CheckoutRequestID": checkout_request_id,
        }

        data = await self._post("/mpesa/stkpush/v1/querystatus", payload, token)
        return STKQueryResponse(**data)

    # ── Private ───────────────────────────────────────────────────────────────

    def _validate(self, req: STKPushRequest) -> None:
        if not req.phone_number:
            raise MpesaValidationError("phone_number is required")
        if req.amount < 1:
            raise MpesaValidationError("amount must be at least 1 KES")
        if not req.callback_url.startswith("https://"):
            raise MpesaValidationError("callback_url must be HTTPS")

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def _password(self, timestamp: str) -> str:
        raw = f"{self._shortcode}{self._passkey}{timestamp}"
        return base64.b64encode(raw.encode()).decode()

    @staticmethod
    def _fmt_phone(phone: str) -> str:
        """Normalise phone to 2547XXXXXXXX format."""
        phone = phone.strip().replace(" ", "").replace("-", "")
        if phone.startswith("0"):
            return f"254{phone[1:]}"
        if phone.startswith("+"):
            return phone[1:]
        return phone

    async def _post(self, path: str, payload: dict, token: str) -> dict:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self._base_url}{path}",
                    json=payload,
                    headers=headers,
                    timeout=15,
                )
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as exc:
                raise MpesaRequestError(
                    f"STK request failed ({exc.response.status_code}): {exc.response.text}",
                    status_code=exc.response.status_code,
                ) from exc
            except httpx.RequestError as exc:
                raise MpesaRequestError(f"Network error: {exc}") from exc
