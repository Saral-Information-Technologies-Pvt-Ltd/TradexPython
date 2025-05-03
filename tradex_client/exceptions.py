class TradeXAPIError(Exception):
    """Base exception for TradeX API errors."""

    def __init__(self, message: str, response_message: str = None, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
        self.response_message = response_message

    def __str__(self):
        base_message = super().__str__()
        details = []
        if self.status_code is not None:
            details.append(f"Status Code: {self.status_code}")
        if self.response_data:
            details.append(f"Response Data: {self.response_data}")
        if self.response_message:
            details.append(f"Message: {self.response_message}")
        return f"{base_message} ({' | '.join(details)})" if details else base_message


class TradeXAuthenticationError(TradeXAPIError):
    """Raised when authentication fails."""
    pass


class TradeXDataFetchError(TradeXAPIError):
    """Raised when data fetching fails."""
    pass


class TradeXInvalidResponseError(TradeXAPIError):
    """Raised when API returns an invalid or unexpected response."""
    pass
