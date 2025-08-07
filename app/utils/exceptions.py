"""
Custom exceptions for the application.
"""


class KEFError(Exception):
    """Base exception for KEF application."""
    pass


class ValidationError(KEFError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: str = None, errors: dict = None):
        super().__init__(message)
        self.message = message
        self.field = field
        self.errors = errors or {}


class LayoutNotFoundError(KEFError):
    """Raised when a layout is not found."""
    pass


class DatabaseError(KEFError):
    """Raised when database operations fail."""
    pass


class ConfigurationError(KEFError):
    """Raised when configuration is invalid."""
    pass


class AuthenticationError(KEFError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(KEFError):
    """Raised when authorization fails."""
    pass
