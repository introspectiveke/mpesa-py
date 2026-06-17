import base64
import time

import httpx

from .exceptions import MpesaAuthError
from .models import TokenResponse


class TokenManager:
    """
    Manages OAuth 2.0 tokens for the Daraja API.
    Tokens are cached and silently refreshed 60 s before expiry.
    """

    def __init__(self, consumer_key: str, consumer_secret: str, base_url: str):
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._base_url = base_url
        self._token: str | None = None
        self._expires_at: float = 0.0

    # ── Public ────────────────────────────────────────────────────────────────

    async def get_token(self) -> str:
        """Return a valid bearer token, fetching a new one when needed."""
        if self._token and time.monotonic() < self._expires_at - 60:
            return self._token
        return await self._fetch_token()

    # ── Private ───────────────────────────────────────────────────────────────

    def _basic_header(self) -> str:
        raw = f"{self._consumer_key}:{self._consumer_secret}"
        return base64.b64encode(raw.encode()).decode()

    async def _fetch_token(self) -> str:
        url = f"{self._base_url}/oauth/v1/generate?grant_type=client_credentials"
        headers = {"Authorization": f"Basic {self._basic_header()}"}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, headers=headers, timeout=10)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise MpesaAuthError(
                    f"Auth failed ({exc.response.status_code}): {exc.response.text}",
                    status_code=exc.response.status_code,
                ) from exc
            except httpx.RequestError as exc:
                raise MpesaAuthError(f"Auth request error: {exc}") from exc

        data = TokenResponse(**resp.json())
        self._token = data.access_token
        self._expires_at = time.monotonic() + data.expires_in
        return self._token
