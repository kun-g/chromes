"""Tests for utility functions."""

import pytest
from datetime import datetime
from pynetbird.utils import (
    format_endpoint, parse_datetime, mask_sensitive_data,
    validate_id, chunk_list, normalize_name, validate_ip_address,
    validate_cidr, is_valid_url, safe_get
)
from pynetbird.exceptions import ValidationError


class TestFormatEndpoint:
    """Test cases for format_endpoint function."""
    
    def test_format_simple_endpoint(self):
        """Test formatting simple endpoint."""
        assert format_endpoint("peers") == "/api/peers"
    
    def test_format_endpoint_with_leading_slash(self):
        """Test formatting endpoint with leading slash."""
        assert format_endpoint("/peers") == "/api/peers"
    
    def test_format_endpoint_with_api_prefix(self):
        """Test formatting endpoint that already has api prefix."""
        assert format_endpoint("api/peers") == "/api/peers"
        assert format_endpoint("/api/peers") == "/api/peers"
    
    def test_format_endpoint_with_whitespace(self):
        """Test formatting endpoint with whitespace."""
        assert format_endpoint("  peers  ") == "/api/peers"
    
    def test_format_endpoint_with_multiple_slashes(self):
        """Test formatting endpoint with multiple slashes."""
        assert format_endpoint("//api//peers//") == "/api/peers"
    
    def test_format_endpoint_with_base_url(self):
        """Test formatting endpoint with base URL."""
        result = format_endpoint("peers", "https://api.example.com")
        assert result == "https://api.example.com/api/peers"


class TestParseDatetime:
    """Test cases for parse_datetime function."""
    
    def test_parse_none(self):
        """Test parsing None value."""
        assert parse_datetime(None) is None
    
    def test_parse_datetime_object(self):
        """Test parsing datetime object."""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        assert parse_datetime(dt) == dt
    
    def test_parse_iso_format(self):
        """Test parsing ISO format datetime string."""
        result = parse_datetime("2023-01-01T12:00:00Z")
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 12
    
    def test_parse_with_microseconds(self):
        """Test parsing datetime with microseconds."""
        result = parse_datetime("2023-01-01T12:00:00.123456Z")
        assert result.microsecond == 123456
    
    def test_parse_invalid_format(self):
        """Test parsing invalid datetime format."""
        with pytest.raises(ValidationError, match="Unable to parse datetime"):
            parse_datetime("invalid-date")
    
    def test_parse_non_string(self):
        """Test parsing non-string input."""
        with pytest.raises(ValidationError, match="Expected string or datetime"):
            parse_datetime(123)


class TestMaskSensitiveData:
    """Test cases for mask_sensitive_data function."""
    
    def test_mask_api_key(self):
        """Test masking API key."""
        data = {"api_key": "secret123456", "name": "test"}
        masked = mask_sensitive_data(data)
        
        assert masked["api_key"] == "********3456"
        assert masked["name"] == "test"  # Non-sensitive unchanged
    
    def test_mask_custom_fields(self):
        """Test masking custom sensitive fields."""
        data = {"custom_secret": "hidden123", "public": "visible"}
        masked = mask_sensitive_data(data, fields=["custom_secret"])
        
        assert masked["custom_secret"] == "*****123"
        assert masked["public"] == "visible"
    
    def test_mask_short_value(self):
        """Test masking very short value."""
        data = {"token": "abc"}
        masked = mask_sensitive_data(data, show_chars=4)
        
        assert masked["token"] == "***"
    
    def test_mask_nested_data(self):
        """Test masking nested dictionary."""
        data = {
            "config": {
                "api_key": "secret123",
                "timeout": 30
            },
            "name": "test"
        }
        masked = mask_sensitive_data(data)
        
        assert masked["config"]["api_key"] == "*****123"
        assert masked["config"]["timeout"] == 30
        assert masked["name"] == "test"
    
    def test_mask_list_data(self):
        """Test masking list data."""
        data = [{"token": "secret123"}, {"name": "test"}]
        masked = mask_sensitive_data(data)
        
        assert masked[0]["token"] == "*****123"
        assert masked[1]["name"] == "test"


class TestValidateId:
    """Test cases for validate_id function."""
    
    def test_validate_valid_id(self):
        """Test validating valid ID."""
        result = validate_id("peer-123", "peer")
        assert result == "peer-123"
    
    def test_validate_id_with_whitespace(self):
        """Test validating ID with whitespace."""
        result = validate_id("  peer-123  ", "peer")
        assert result == "peer-123"
    
    def test_validate_empty_id(self):
        """Test validating empty ID."""
        with pytest.raises(ValidationError, match="peer ID cannot be empty"):
            validate_id("", "peer")
    
    def test_validate_non_string_id(self):
        """Test validating non-string ID."""
        with pytest.raises(ValidationError, match="peer ID must be a string"):
            validate_id(123, "peer")
    
    def test_validate_too_short_id(self):
        """Test validating too short ID."""
        with pytest.raises(ValidationError, match="must be at least"):
            validate_id("a", "test", min_length=2)
    
    def test_validate_too_long_id(self):
        """Test validating too long ID."""
        long_id = "a" * 300
        with pytest.raises(ValidationError, match="must be at most"):
            validate_id(long_id, "test", max_length=255)
    
    def test_validate_invalid_characters(self):
        """Test validating ID with invalid characters."""
        with pytest.raises(ValidationError, match="contains invalid characters"):
            validate_id("peer<>123", "peer")


class TestChunkList:
    """Test cases for chunk_list function."""
    
    def test_chunk_even_division(self):
        """Test chunking list with even division."""
        items = [1, 2, 3, 4, 5, 6]
        chunks = list(chunk_list(items, 2))
        
        assert chunks == [[1, 2], [3, 4], [5, 6]]
    
    def test_chunk_uneven_division(self):
        """Test chunking list with uneven division."""
        items = [1, 2, 3, 4, 5]
        chunks = list(chunk_list(items, 2))
        
        assert chunks == [[1, 2], [3, 4], [5]]
    
    def test_chunk_empty_list(self):
        """Test chunking empty list."""
        chunks = list(chunk_list([], 3))
        assert chunks == []
    
    def test_chunk_invalid_size(self):
        """Test chunking with invalid chunk size."""
        with pytest.raises(ValidationError, match="chunk_size must be positive"):
            list(chunk_list([1, 2, 3], 0))


class TestNormalizeName:
    """Test cases for normalize_name function."""
    
    def test_normalize_basic_name(self):
        """Test normalizing basic name."""
        result = normalize_name("Test Group")
        assert result == "Test Group"
    
    def test_normalize_name_with_whitespace(self):
        """Test normalizing name with extra whitespace."""
        result = normalize_name("  Test   Group  ")
        assert result == "Test Group"
    
    def test_normalize_name_with_special_chars(self):
        """Test normalizing name with special characters."""
        result = normalize_name("Test@#$Group")
        assert result == "Test Group"
    
    def test_normalize_empty_name(self):
        """Test normalizing empty name."""
        with pytest.raises(ValidationError, match="Name cannot be empty"):
            normalize_name("")
    
    def test_normalize_non_string_name(self):
        """Test normalizing non-string name."""
        with pytest.raises(ValidationError, match="Name must be a string"):
            normalize_name(123)
    
    def test_normalize_too_long_name(self):
        """Test normalizing too long name."""
        long_name = "a" * 150
        with pytest.raises(ValidationError, match="must be at most"):
            normalize_name(long_name, max_length=100)


class TestValidateIpAddress:
    """Test cases for validate_ip_address function."""
    
    def test_validate_ipv4(self):
        """Test validating IPv4 address."""
        result = validate_ip_address("192.168.1.1")
        assert result == "192.168.1.1"
    
    def test_validate_ipv6(self):
        """Test validating IPv6 address."""
        result = validate_ip_address("2001:db8::1")
        assert result == "2001:db8::1"
    
    def test_validate_invalid_ip(self):
        """Test validating invalid IP address."""
        with pytest.raises(ValidationError, match="Invalid IP address"):
            validate_ip_address("999.999.999.999")


class TestValidateCidr:
    """Test cases for validate_cidr function."""
    
    def test_validate_ipv4_cidr(self):
        """Test validating IPv4 CIDR."""
        result = validate_cidr("192.168.1.0/24")
        assert result == "192.168.1.0/24"
    
    def test_validate_ipv6_cidr(self):
        """Test validating IPv6 CIDR."""
        result = validate_cidr("2001:db8::/32")
        assert result == "2001:db8::/32"
    
    def test_validate_invalid_cidr(self):
        """Test validating invalid CIDR."""
        with pytest.raises(ValidationError, match="Invalid CIDR"):
            validate_cidr("192.168.1.0/33")


class TestIsValidUrl:
    """Test cases for is_valid_url function."""
    
    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        assert is_valid_url("https://api.example.com") is True
    
    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        assert is_valid_url("http://api.example.com") is True
    
    def test_invalid_url(self):
        """Test invalid URL."""
        assert is_valid_url("not-a-url") is False
    
    def test_url_without_scheme(self):
        """Test URL without scheme."""
        assert is_valid_url("example.com") is False


class TestSafeGet:
    """Test cases for safe_get function."""
    
    def test_safe_get_existing_key(self):
        """Test getting existing nested key."""
        data = {"a": {"b": {"c": 123}}}
        result = safe_get(data, "a", "b", "c")
        assert result == 123
    
    def test_safe_get_missing_key(self):
        """Test getting missing nested key."""
        data = {"a": {"b": {}}}
        result = safe_get(data, "a", "b", "c", default="not found")
        assert result == "not found"
    
    def test_safe_get_none_default(self):
        """Test getting missing key with None default."""
        data = {"a": {}}
        result = safe_get(data, "a", "missing")
        assert result is None
    
    def test_safe_get_non_dict_intermediate(self):
        """Test getting from non-dict intermediate value."""
        data = {"a": "not-a-dict"}
        result = safe_get(data, "a", "b", default="fallback")
        assert result == "fallback"