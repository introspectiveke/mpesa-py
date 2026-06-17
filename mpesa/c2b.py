import httpx

from .auth import TokenManager
from .exceptions import MpesaRequestError
from .models import C2BRegisterRequest, C2BRegisterResponse


class C2B:
    def __init__(self, token_manager: TokenManager, shortcode: str, base_url: str):
        self._tm = token_manager
        self._shortcode = shortcode
        self._base_url = base_url

    async def register_urls(self, request: C2BRegisterRequest) -> C2BRegisterResponse:
        """Register confirmation and validation URLs for C2B payments."""
        token = await self._tm.get_token()

        payload = {
            "ShortCode": request.shortcode or self._shortcode,
            "ResponseType": request.response_type,
            "ConfirmationURL": request.confirmation_url,
            "ValidationURL": request.validation_url,
        }

        data = await self._post("/mpesa/c2b/v1/registerurl", payload, token)
        return C2BRegisterResponse(**data)

    async def simulate(
        self,
        phone: str,
        amount: int,
        bill_ref: str = "test",
    ) -> dict:
        """
        Simulate a C2B payment (sandbox only).
        Use this to trigger test callbacks without a real phone.
        """
        token = await self._tm.get_token()

        payload = {
            "ShortCode": self._shortcode,
            "CommandID": "CustomerPayBillOnline",
            "Amount": amount,
            "Msisdn": phone,
            "BillRefNumber": bill_ref,
        }

        return await self._post("/mpesa/c2b/v1/simulate", payload, token)

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
                    f"C2B request failed ({exc.response.status_code}): {exc.response.text}",
                    status_code=exc.response.status_code,
                ) from exc
            except httpx.RequestError as exc:
                raise MpesaRequestError(f"Network error: {exc}") from exc
