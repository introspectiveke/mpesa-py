from .auth import TokenManager
from .b2c import B2C
from .c2b import C2B
from .stk import STKPush


class MpesaClient:
    """
    Single entry point for the M-PESA Daraja API.

    Usage::

        client = MpesaClient(
            consumer_key="...",
            consumer_secret="...",
            shortcode="174379",
            passkey="...",
            sandbox=True,
        )

        response = await client.stk.push(STKPushRequest(...))
    """

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        shortcode: str,
        passkey: str,
        sandbox: bool = True,
        # B2C is optional — only needed if sending money out
        initiator_name: str | None = None,
        security_credential: str | None = None,
    ):
        self._sandbox = sandbox
        self._base_url = (
            "https://sandbox.safaricom.co.ke"
            if sandbox
            else "https://api.safaricom.co.ke"
        )

        self._token_manager = TokenManager(consumer_key, consumer_secret, self._base_url)

        self.stk = STKPush(self._token_manager, shortcode, passkey, self._base_url)
        self.c2b = C2B(self._token_manager, shortcode, self._base_url)

        if initiator_name and security_credential:
            self.b2c = B2C(
                self._token_manager,
                shortcode,
                initiator_name,
                security_credential,
                self._base_url,
            )
        else:
            self.b2c = None  # type: ignore[assignment]

    @property
    def is_sandbox(self) -> bool:
        return self._sandbox
