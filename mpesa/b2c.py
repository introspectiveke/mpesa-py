import httpx

from .auth import TokenManager
from .exceptions import MpesaRequestError
from .models import B2CResponse

COMMAND_IDS = {"SalaryPayment", "BusinessPayment", "PromotionPayment"}


class B2C:
    def __init__(
        self,
        token_manager: TokenManager,
        shortcode: str,
        initiator_name: str,
        security_credential: str,
        base_url: str,
    ):
        self._tm = token_manager
        self._shortcode = shortcode
        self._initiator_name = initiator_name
        self._security_credential = security_credential
        self._base_url = base_url

    async def pay(
        self,
        phone: str,
        amount: int,
        result_url: str,
        queue_timeout_url: str,
        command_id: str = "BusinessPayment",
        remarks: str = "Payment",
        occasion: str = "",
    ) -> B2CResponse:
        """
        Send money from business to a customer's M-PESA wallet.

        command_id options:
            SalaryPayment   – payroll disbursement
            BusinessPayment – general payout
            PromotionPayment – promotional disbursement
        """
        if command_id not in COMMAND_IDS:
            raise ValueError(f"command_id must be one of {COMMAND_IDS}")

        token = await self._tm.get_token()

        payload = {
            "InitiatorName": self._initiator_name,
            "SecurityCredential": self._security_credential,
            "CommandID": command_id,
            "Amount": amount,
            "PartyA": self._shortcode,
            "PartyB": phone,
            "Remarks": remarks,
            "Occassion": occasion,
            "QueueTimeOutURL": queue_timeout_url,
            "ResultURL": result_url,
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self._base_url}/mpesa/b2c/v1/paymentrequest",
                    json=payload,
                    headers=headers,
                    timeout=15,
                )
                resp.raise_for_status()
                return B2CResponse(**resp.json())
            except httpx.HTTPStatusError as exc:
                raise MpesaRequestError(
                    f"B2C request failed ({exc.response.status_code}): {exc.response.text}",
                    status_code=exc.response.status_code,
                ) from exc
            except httpx.RequestError as exc:
                raise MpesaRequestError(f"Network error: {exc}") from exc
