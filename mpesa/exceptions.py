class MpesaError(Exception):
    """Base exception for all M-PESA errors."""
    pass


class MpesaAuthError(MpesaError):
    """Raised when OAuth authentication fails."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class MpesaRequestError(MpesaError):
    """Raised when an API request returns a non-2xx response."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_code: str | None = None,
    ):
        self.status_code = status_code
        self.response_code = response_code
        super().__init__(message)


class MpesaValidationError(MpesaError):
    """Raised when request parameters fail local validation."""
    pass
