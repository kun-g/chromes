"""Tests for exception handling."""

import pytest
from pynetbird.exceptions import (
    NetBirdException, AuthenticationError, ResourceNotFoundError,
    ValidationError, RateLimitError, ServerError, NetworkError,
    map_status_code_to_exception, format_api_error
)


class TestNetBirdException:
    """Test cases for NetBirdException base class."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        exc = NetBirdException("Test error")
        
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.status_code is None
        assert exc.response == {}
    
    def test_exception_with_status_code(self):
        """Test exception with status code."""
        exc = NetBirdException("Test error", status_code=400)
        
        assert str(exc) == "[400] Test error"
        assert exc.status_code == 400
    
    def test_exception_with_response(self):
        """Test exception with response data."""
        response_data = {"error": "detailed error"}
        exc = NetBirdException("Test error", response=response_data)
        
        assert exc.response == response_data
    
    def test_exception_repr(self):
        """Test exception representation."""
        exc = NetBirdException("Test", status_code=404, response={"test": True})
        repr_str = repr(exc)
        
        assert "NetBirdException" in repr_str
        assert "Test" in repr_str
        assert "404" in repr_str


class TestSpecificExceptions:
    """Test cases for specific exception types."""
    
    def test_authentication_error(self):
        """Test AuthenticationError."""
        exc = AuthenticationError("Invalid token", status_code=401)
        
        assert isinstance(exc, NetBirdException)
        assert exc.status_code == 401
        assert str(exc) == "[401] Invalid token"
    
    def test_validation_error(self):
        """Test ValidationError."""
        exc = ValidationError("Invalid input", status_code=400)
        
        assert isinstance(exc, NetBirdException)
        assert exc.status_code == 400
    
    def test_rate_limit_error(self):
        """Test RateLimitError with retry_after."""
        exc = RateLimitError("Rate limit exceeded", retry_after=60, status_code=429)
        
        assert isinstance(exc, NetBirdException)
        assert exc.retry_after == 60
        assert exc.status_code == 429


class TestStatusCodeMapping:
    """Test cases for status code to exception mapping."""
    
    def test_map_401_to_authentication_error(self):
        """Test mapping 401 to AuthenticationError."""
        exc = map_status_code_to_exception(401, "Unauthorized")
        
        assert isinstance(exc, AuthenticationError)
        assert exc.status_code == 401
        assert exc.message == "Unauthorized"
    
    def test_map_404_to_not_found_error(self):
        """Test mapping 404 to ResourceNotFoundError."""
        exc = map_status_code_to_exception(404, "Not found")
        
        assert isinstance(exc, ResourceNotFoundError)
        assert exc.status_code == 404
    
    def test_map_400_to_validation_error(self):
        """Test mapping 400 to ValidationError."""
        exc = map_status_code_to_exception(400, "Bad request")
        
        assert isinstance(exc, ValidationError)
        assert exc.status_code == 400
    
    def test_map_429_to_rate_limit_error(self):
        """Test mapping 429 to RateLimitError."""
        exc = map_status_code_to_exception(429, "Too many requests")
        
        assert isinstance(exc, RateLimitError)
        assert exc.status_code == 429
    
    def test_map_500_to_server_error(self):
        """Test mapping 5xx to ServerError."""
        exc = map_status_code_to_exception(500, "Internal server error")
        
        assert isinstance(exc, ServerError)
        assert exc.status_code == 500
    
    def test_map_unknown_to_base_exception(self):
        """Test mapping unknown status code to base exception."""
        exc = map_status_code_to_exception(418, "I'm a teapot")
        
        assert isinstance(exc, NetBirdException)
        assert not isinstance(exc, (AuthenticationError, ValidationError))
        assert exc.status_code == 418


class TestErrorFormatting:
    """Test cases for API error formatting."""
    
    def test_format_error_with_message(self):
        """Test formatting error response with message field."""
        response = {"message": "Invalid API key"}
        formatted = format_api_error(response)
        
        assert formatted == "Invalid API key"
    
    def test_format_error_with_error_field(self):
        """Test formatting error response with error field."""
        response = {"error": "Access denied"}
        formatted = format_api_error(response)
        
        assert formatted == "Access denied"
    
    def test_format_error_with_detail_field(self):
        """Test formatting error response with detail field."""
        response = {"detail": "Resource not found"}
        formatted = format_api_error(response)
        
        assert formatted == "Resource not found"
    
    def test_format_error_with_errors_list(self):
        """Test formatting error response with errors list."""
        response = {"errors": [{"message": "Field is required"}]}
        formatted = format_api_error(response)
        
        assert formatted == "Field is required"
    
    def test_format_error_with_errors_string_list(self):
        """Test formatting error response with string errors list."""
        response = {"errors": ["Field validation failed"]}
        formatted = format_api_error(response)
        
        assert formatted == "Field validation failed"
    
    def test_format_empty_error(self):
        """Test formatting empty error response."""
        formatted = format_api_error({})
        
        assert formatted == "Unknown API error"
    
    def test_format_none_error(self):
        """Test formatting None error response."""
        formatted = format_api_error(None)
        
        assert formatted == "Unknown API error"