"""
Utility functions for the PyNetBird library.

This module provides common utility functions used throughout the library
for data formatting, validation, and processing.
"""

import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Iterator, Optional, Union
from urllib.parse import urljoin, urlparse

from .exceptions import ValidationError


def format_endpoint(endpoint: str, base_url: str = "") -> str:
    """
    Format API endpoint ensuring proper structure.
    
    Args:
        endpoint: API endpoint path
        base_url: Base URL to join with (optional)
        
    Returns:
        Properly formatted endpoint URL
        
    Examples:
        >>> format_endpoint("peers")
        "/api/peers"
        >>> format_endpoint("/peers")
        "/api/peers"
        >>> format_endpoint("api/peers")
        "/api/peers"
        >>> format_endpoint("/api/peers")
        "/api/peers"
    """
    # Remove leading/trailing whitespace
    endpoint = endpoint.strip()
    
    # Remove leading slash
    if endpoint.startswith('/'):
        endpoint = endpoint[1:]
    
    # Add /api prefix if not present
    if not endpoint.startswith('api/'):
        endpoint = f"api/{endpoint}"
    
    # Ensure leading slash
    formatted_endpoint = f"/{endpoint}"
    
    # Remove duplicate slashes
    formatted_endpoint = re.sub(r'/+', '/', formatted_endpoint)
    
    # Join with base URL if provided
    if base_url:
        return urljoin(base_url.rstrip('/') + '/', formatted_endpoint.lstrip('/'))
    
    return formatted_endpoint


def parse_datetime(date_str: Union[str, datetime, None]) -> Optional[datetime]:
    """
    Parse various datetime string formats returned by NetBird API.
    
    Args:
        date_str: DateTime string, datetime object, or None
        
    Returns:
        Parsed datetime object or None
        
    Raises:
        ValidationError: If string cannot be parsed
        
    Examples:
        >>> parse_datetime("2023-01-01T12:00:00Z")
        datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        >>> parse_datetime("2023-01-01T12:00:00.123456Z")
        datetime(2023, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc)
    """
    if date_str is None:
        return None
    
    if isinstance(date_str, datetime):
        return date_str
    
    if not isinstance(date_str, str):
        raise ValidationError(f"Expected string or datetime, got {type(date_str)}")
    
    # Common datetime formats used by NetBird API
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",                    # 2023-01-01T12:00:00Z
        "%Y-%m-%dT%H:%M:%S.%fZ",                 # 2023-01-01T12:00:00.123456Z
        "%Y-%m-%dT%H:%M:%S%z",                   # 2023-01-01T12:00:00+00:00
        "%Y-%m-%dT%H:%M:%S.%f%z",                # 2023-01-01T12:00:00.123456+00:00
        "%Y-%m-%d %H:%M:%S",                     # 2023-01-01 12:00:00
        "%Y-%m-%d %H:%M:%S.%f",                  # 2023-01-01 12:00:00.123456
        "%Y-%m-%d",                              # 2023-01-01
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Try parsing with dateutil if available
    try:
        from dateutil import parser
        return parser.parse(date_str)
    except ImportError:
        pass
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Unable to parse datetime string '{date_str}': {e}")
    
    raise ValidationError(f"Unable to parse datetime string '{date_str}' with any known format")


def mask_sensitive_data(
    data: Any, 
    fields: Optional[List[str]] = None,
    mask_char: str = "*",
    show_chars: int = 4
) -> Any:
    """
    Mask sensitive data for logging purposes.
    
    Args:
        data: Data to mask (dict, list, or any other type)
        fields: List of field names to mask (case-insensitive)
        mask_char: Character to use for masking
        show_chars: Number of characters to show at the end
        
    Returns:
        Data with sensitive fields masked
        
    Examples:
        >>> mask_sensitive_data({"api_key": "secret123", "name": "test"})
        {"api_key": "****et123", "name": "test"}
        >>> mask_sensitive_data({"token": "abcdef123456"}, show_chars=2)
        {"token": "**********56"}
    """
    if fields is None:
        fields = [
            'api_key', 'token', 'password', 'secret', 'key',
            'authorization', 'auth', 'credentials', 'private_key',
            'access_token', 'refresh_token', 'session_id',
        ]
    
    # Convert to lowercase for case-insensitive matching
    fields_lower = [f.lower() for f in fields]
    
    def _mask_value(value: str) -> str:
        """Mask a string value."""
        if not isinstance(value, str) or len(value) <= show_chars:
            return mask_char * len(str(value))
        
        masked_length = len(value) - show_chars
        return mask_char * masked_length + value[-show_chars:]
    
    def _mask_recursive(obj: Any) -> Any:
        """Recursively mask sensitive data."""
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if isinstance(key, str) and key.lower() in fields_lower:
                    result[key] = _mask_value(str(value))
                else:
                    result[key] = _mask_recursive(value)
            return result
        elif isinstance(obj, (list, tuple)):
            return type(obj)(_mask_recursive(item) for item in obj)
        else:
            return obj
    
    return _mask_recursive(data)


def validate_id(
    resource_id: str, 
    resource_type: str = "resource",
    min_length: int = 1,
    max_length: int = 255
) -> str:
    """
    Validate resource ID format.
    
    Args:
        resource_id: ID to validate
        resource_type: Type of resource for error messages
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        Validated ID (stripped of whitespace)
        
    Raises:
        ValidationError: If ID is invalid
        
    Examples:
        >>> validate_id("peer-123", "peer")
        "peer-123"
        >>> validate_id("", "group")
        ValidationError: group ID cannot be empty
    """
    if not isinstance(resource_id, str):
        raise ValidationError(f"{resource_type} ID must be a string, got {type(resource_id)}")
    
    # Strip whitespace
    resource_id = resource_id.strip()
    
    if not resource_id:
        raise ValidationError(f"{resource_type} ID cannot be empty")
    
    if len(resource_id) < min_length:
        raise ValidationError(f"{resource_type} ID must be at least {min_length} characters long")
    
    if len(resource_id) > max_length:
        raise ValidationError(f"{resource_type} ID must be at most {max_length} characters long")
    
    # Check for invalid characters (basic validation)
    if re.search(r'[<>:"/\\|?*\x00-\x1f]', resource_id):
        raise ValidationError(f"{resource_type} ID contains invalid characters")
    
    return resource_id


def chunk_list(items: List[Any], chunk_size: int) -> Iterator[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
        
    Yields:
        List chunks
        
    Raises:
        ValidationError: If chunk_size is invalid
        
    Examples:
        >>> list(chunk_list([1, 2, 3, 4, 5], 2))
        [[1, 2], [3, 4], [5]]
        >>> list(chunk_list([], 3))
        []
    """
    if chunk_size <= 0:
        raise ValidationError("chunk_size must be positive")
    
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]


def normalize_name(name: str, max_length: int = 100) -> str:
    """
    Normalize resource names for consistency.
    
    Args:
        name: Name to normalize
        max_length: Maximum allowed length
        
    Returns:
        Normalized name
        
    Raises:
        ValidationError: If name is invalid
        
    Examples:
        >>> normalize_name("  My Group  ")
        "My Group"
        >>> normalize_name("test@#$%group")
        "test group"
    """
    if not isinstance(name, str):
        raise ValidationError(f"Name must be a string, got {type(name)}")
    
    # Strip whitespace and normalize spaces
    name = re.sub(r'\s+', ' ', name.strip())
    
    if not name:
        raise ValidationError("Name cannot be empty")
    
    if len(name) > max_length:
        raise ValidationError(f"Name must be at most {max_length} characters long")
    
    # Replace special characters with spaces and clean up
    name = re.sub(r'[^\w\s.-]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def validate_ip_address(ip_address: str) -> str:
    """
    Validate IP address format.
    
    Args:
        ip_address: IP address to validate
        
    Returns:
        Validated IP address
        
    Raises:
        ValidationError: If IP address is invalid
        
    Examples:
        >>> validate_ip_address("192.168.1.1")
        "192.168.1.1"
        >>> validate_ip_address("2001:db8::1")
        "2001:db8::1"
    """
    import ipaddress
    
    try:
        # This will raise ValueError for invalid IPs
        addr = ipaddress.ip_address(ip_address.strip())
        return str(addr)
    except ValueError as e:
        raise ValidationError(f"Invalid IP address '{ip_address}': {e}")


def validate_cidr(cidr: str) -> str:
    """
    Validate CIDR notation.
    
    Args:
        cidr: CIDR to validate
        
    Returns:
        Validated CIDR
        
    Raises:
        ValidationError: If CIDR is invalid
        
    Examples:
        >>> validate_cidr("192.168.1.0/24")
        "192.168.1.0/24"
        >>> validate_cidr("2001:db8::/32")
        "2001:db8::/32"
    """
    import ipaddress
    
    try:
        # This will raise ValueError for invalid networks
        network = ipaddress.ip_network(cidr.strip(), strict=False)
        return str(network)
    except ValueError as e:
        raise ValidationError(f"Invalid CIDR '{cidr}': {e}")


def setup_logging(
    level: Union[str, int] = logging.INFO,
    format_string: Optional[str] = None,
    logger_name: str = "pynetbird"
) -> logging.Logger:
    """
    Set up logging for the PyNetBird library.
    
    Args:
        level: Logging level
        format_string: Custom format string
        logger_name: Logger name
        
    Returns:
        Configured logger
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> is_valid_url("https://api.netbird.io")
        True
        >>> is_valid_url("not-a-url")
        False
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except (ValueError, AttributeError):
        return False


def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary values.
    
    Args:
        data: Dictionary to query
        *keys: Keys to traverse
        default: Default value if key not found
        
    Returns:
        Value at nested key or default
        
    Examples:
        >>> safe_get({"a": {"b": {"c": 123}}}, "a", "b", "c")
        123
        >>> safe_get({"a": {"b": {}}}, "a", "b", "c", default="not found")
        "not found"
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current