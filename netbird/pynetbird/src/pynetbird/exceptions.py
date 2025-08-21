"""
NetBird API exceptions and error handling.

This module defines the exception hierarchy for the PyNetBird library,
providing structured error handling for different types of API failures.
"""

from typing import Optional, Dict, Any


class NetBirdException(Exception):
    """Base exception class for all NetBird API errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        response: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize NetBird exception.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code if applicable
            response: Raw API response data if available
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response or {}
    
    def __str__(self) -> str:
        """Return formatted error message."""
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message
    
    def __repr__(self) -> str:
        """Return detailed exception representation."""
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"status_code={self.status_code}, "
            f"response={self.response})"
        )


class AuthenticationError(NetBirdException):
    """Raised when API authentication fails (401)."""
    pass


class AuthorizationError(NetBirdException):
    """Raised when API authorization fails (403)."""
    pass


class ResourceNotFoundError(NetBirdException):
    """Raised when requested resource is not found (404)."""
    pass


class ValidationError(NetBirdException):
    """Raised when request validation fails (400, 422)."""
    pass


class ConflictError(NetBirdException):
    """Raised when request conflicts with current state (409)."""
    pass


class RateLimitError(NetBirdException):
    """Raised when API rate limit is exceeded (429)."""
    
    def __init__(
        self, 
        message: str, 
        retry_after: Optional[int] = None,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize rate limit exception.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            status_code: HTTP status code
            response: API response data
        """
        super().__init__(message, status_code, response)
        self.retry_after = retry_after


class ServerError(NetBirdException):
    """Raised when server encounters an error (5xx)."""
    pass


class NetworkError(NetBirdException):
    """Raised when network connection fails."""
    pass


class TimeoutError(NetBirdException):
    """Raised when request times out."""
    pass


class ConfigurationError(NetBirdException):
    """Raised when client configuration is invalid."""
    pass


def map_status_code_to_exception(
    status_code: int,
    message: str,
    response: Optional[Dict[str, Any]] = None
) -> NetBirdException:
    """
    Map HTTP status code to appropriate exception class.
    
    Args:
        status_code: HTTP status code
        message: Error message
        response: API response data
        
    Returns:
        Appropriate exception instance
    """
    exception_map = {
        400: ValidationError,
        401: AuthenticationError,
        403: AuthorizationError,
        404: ResourceNotFoundError,
        409: ConflictError,
        422: ValidationError,
        429: RateLimitError,
    }
    
    if status_code in exception_map:
        return exception_map[status_code](message, status_code, response)
    elif 500 <= status_code < 600:
        return ServerError(message, status_code, response)
    else:
        return NetBirdException(message, status_code, response)


def format_api_error(response: Dict[str, Any]) -> str:
    """
    Format API error response into readable message.
    
    Args:
        response: API error response
        
    Returns:
        Formatted error message
    """
    if not response:
        return "Unknown API error"
    
    # Try different common error message fields
    for field in ['message', 'error', 'detail', 'description']:
        if field in response and response[field]:
            return str(response[field])
    
    # If no standard field found, try to extract any meaningful info
    if 'errors' in response and isinstance(response['errors'], list):
        errors = response['errors']
        if errors and isinstance(errors[0], dict):
            return str(errors[0].get('message', str(errors[0])))
        elif errors:
            return str(errors[0])
    
    return f"API error: {response}"