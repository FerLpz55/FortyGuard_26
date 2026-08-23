class AppException(Exception):
    """
    Base class for application exceptions.
    """
    def __init__(self, detail: str, status_code: int = 500) -> None:
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class NotFoundError(AppException):
    """Exception raised when a resource is not found."""
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(detail=detail, status_code=404)


class AuthenticationError(AppException):
    """Exception raised for authentication failures (e.g., invalid credentials)."""
    def __init__(self, detail: str = "Authentication failed") -> None:
        super().__init__(detail=detail, status_code=401)


class AuthorizationError(AppException):
    """Exception raised when the user is authenticated but lacks necessary permissions."""
    def __init__(self, detail: str = "Not authorized to perform this action") -> None:
        super().__init__(detail=detail, status_code=403)


class ValidationError(AppException):
    """Exception raised for input validation errors."""
    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(detail=detail, status_code=422)


class ConflictError(AppException):
    """Exception raised for resource conflicts (e.g., duplicate email)."""
    def __init__(self, detail: str = "Resource conflict") -> None:
        super().__init__(detail=detail, status_code=409)


class ExternalServiceError(AppException):
    """Exception raised when an external API or service fails."""
    def __init__(self, detail: str = "External service unavailable") -> None:
        super().__init__(detail=detail, status_code=502)
