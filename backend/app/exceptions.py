"""Custom exception classes for the Todo application."""


class TodoException(Exception):
    """Base exception for Todo application."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(TodoException):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class AuthenticationError(TodoException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, status_code=401)


class AuthorizationError(TodoException):
    """Raised when user lacks permission."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403)


class NotFoundError(TodoException):
    """Raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ConflictError(TodoException):
    """Raised when there's a conflict (e.g., duplicate email)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=409)
