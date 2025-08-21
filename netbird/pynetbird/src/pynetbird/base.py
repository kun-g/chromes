"""
HTTP communication base class for PyNetBird.

This module provides the foundational HTTP client functionality with support
for both synchronous and asynchronous operations, error handling, and retry logic.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin

import httpx

from .config import NetBirdConfig
from .exceptions import (
    NetBirdException, NetworkError, TimeoutError as NetBirdTimeoutError,
    map_status_code_to_exception, format_api_error
)
from .utils import format_endpoint, mask_sensitive_data, setup_logging


class BaseClient:
    """
    HTTP communication base class with support for sync and async operations.
    
    This class handles all HTTP communication with the NetBird API, including
    authentication, error handling, retries, and request/response processing.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        api_url: str = "https://api.netbird.io",
        timeout: int = 30,
        config: Optional[NetBirdConfig] = None,
        **kwargs
    ):
        """
        Initialize the HTTP client.
        
        Args:
            api_key: NetBird API key
            api_url: NetBird API base URL
            timeout: Request timeout in seconds
            config: Pre-configured NetBirdConfig instance
            **kwargs: Additional configuration overrides
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Use provided config or create from parameters
        if config:
            self.config = config
        else:
            from .config import load_config
            self.config = load_config(
                api_key=api_key,
                api_url=api_url,
                timeout=timeout,
                **kwargs
            )
        
        # Set up logging
        self.logger = setup_logging(
            level=self.config.log_level if self.config.enable_logging else logging.CRITICAL,
            logger_name=f"{__name__}.{self.__class__.__name__}"
        )
        
        # Initialize HTTP clients (lazy initialization)
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None
        
        self.logger.debug(f"Initialized {self.__class__.__name__} with config: {mask_sensitive_data(self.config.to_dict())}")
    
    @property
    def sync_client(self) -> httpx.Client:
        """Get or create synchronous HTTP client."""
        if self._sync_client is None:
            self._sync_client = self._create_sync_client()
        return self._sync_client
    
    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get or create asynchronous HTTP client."""
        if self._async_client is None:
            self._async_client = self._create_async_client()
        return self._async_client
    
    def _create_sync_client(self) -> httpx.Client:
        """Create synchronous HTTP client with configuration."""
        return httpx.Client(
            base_url=self.config.api_url,
            headers=self.config.get_auth_headers(),
            timeout=httpx.Timeout(self.config.timeout),
            verify=self.config.verify_ssl,
            limits=httpx.Limits(
                max_connections=self.config.connection_pool_size,
                max_keepalive_connections=self.config.connection_pool_max_size
            ),
            follow_redirects=True,
        )
    
    def _create_async_client(self) -> httpx.AsyncClient:
        """Create asynchronous HTTP client with configuration."""
        return httpx.AsyncClient(
            base_url=self.config.api_url,
            headers=self.config.get_auth_headers(),
            timeout=httpx.Timeout(self.config.timeout),
            verify=self.config.verify_ssl,
            limits=httpx.Limits(
                max_connections=self.config.connection_pool_size,
                max_keepalive_connections=self.config.connection_pool_max_size
            ),
            follow_redirects=True,
        )
    
    def request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a synchronous HTTP request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Form data
            json: JSON data
            headers: Additional headers
            **kwargs: Additional request parameters
            
        Returns:
            Parsed JSON response
            
        Raises:
            NetBirdException: On API or network errors
        """
        return self._make_request_with_retry(
            self._sync_request, method, endpoint, 
            params=params, data=data, json=json, headers=headers, **kwargs
        )
    
    async def async_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an asynchronous HTTP request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Form data
            json: JSON data
            headers: Additional headers
            **kwargs: Additional request parameters
            
        Returns:
            Parsed JSON response
            
        Raises:
            NetBirdException: On API or network errors
        """
        return await self._make_async_request_with_retry(
            self._async_request, method, endpoint,
            params=params, data=data, json=json, headers=headers, **kwargs
        )
    
    def _sync_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Make a single synchronous HTTP request without retry logic."""
        url = format_endpoint(endpoint)
        
        # Merge additional headers
        request_headers = self.config.get_auth_headers()
        if 'headers' in kwargs and kwargs['headers']:
            request_headers.update(kwargs.pop('headers'))
        
        self.logger.debug(f"Making {method} request to {url}")
        self.logger.debug(f"Request params: {mask_sensitive_data(kwargs)}")
        
        try:
            response = self.sync_client.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                **kwargs
            )
            return self._process_response(response)
            
        except httpx.TimeoutException as e:
            self.logger.error(f"Request timeout: {e}")
            raise NetBirdTimeoutError(f"Request timed out after {self.config.timeout} seconds")
        
        except httpx.NetworkError as e:
            self.logger.error(f"Network error: {e}")
            raise NetworkError(f"Network error: {e}")
        
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            raise NetBirdException(f"HTTP error: {e}")
    
    async def _async_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Make a single asynchronous HTTP request without retry logic."""
        url = format_endpoint(endpoint)
        
        # Merge additional headers
        request_headers = self.config.get_auth_headers()
        if 'headers' in kwargs and kwargs['headers']:
            request_headers.update(kwargs.pop('headers'))
        
        self.logger.debug(f"Making async {method} request to {url}")
        self.logger.debug(f"Request params: {mask_sensitive_data(kwargs)}")
        
        try:
            response = await self.async_client.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                **kwargs
            )
            return self._process_response(response)
            
        except httpx.TimeoutException as e:
            self.logger.error(f"Request timeout: {e}")
            raise NetBirdTimeoutError(f"Request timed out after {self.config.timeout} seconds")
        
        except httpx.NetworkError as e:
            self.logger.error(f"Network error: {e}")
            raise NetworkError(f"Network error: {e}")
        
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            raise NetBirdException(f"HTTP error: {e}")
    
    def _process_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Process HTTP response and handle errors.
        
        Args:
            response: HTTP response object
            
        Returns:
            Parsed JSON response
            
        Raises:
            NetBirdException: On API errors
        """
        self.logger.debug(f"Response status: {response.status_code}")
        self.logger.debug(f"Response headers: {dict(response.headers)}")
        
        # Handle successful responses
        if 200 <= response.status_code < 300:
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    result = response.json()
                    self.logger.debug(f"Response data: {mask_sensitive_data(result)}")
                    return result
                except ValueError as e:
                    self.logger.error(f"Failed to parse JSON response: {e}")
                    raise NetBirdException(f"Invalid JSON response: {e}")
            else:
                # Non-JSON response, return empty dict for successful operations
                return {}
        
        # Handle error responses
        error_data = {}
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
        except ValueError:
            pass
        
        error_message = format_api_error(error_data) or f"HTTP {response.status_code}: {response.reason_phrase}"
        self.logger.error(f"API error {response.status_code}: {error_message}")
        
        # Map status code to appropriate exception
        exception = map_status_code_to_exception(
            response.status_code, 
            error_message, 
            error_data
        )
        raise exception
    
    def _make_request_with_retry(self, request_func, *args, **kwargs) -> Dict[str, Any]:
        """Make request with retry logic (synchronous)."""
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return request_func(*args, **kwargs)
            except (NetworkError, NetBirdTimeoutError) as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    delay = self.config.retry_delay * (self.config.retry_backoff_factor ** attempt)
                    self.logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                    import time
                    time.sleep(delay)
                    continue
                break
            except NetBirdException:
                # Don't retry on API errors (4xx, 5xx)
                raise
        
        # All retries exhausted
        self.logger.error(f"Request failed after {self.config.max_retries + 1} attempts")
        raise last_exception
    
    async def _make_async_request_with_retry(self, request_func, *args, **kwargs) -> Dict[str, Any]:
        """Make request with retry logic (asynchronous)."""
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return await request_func(*args, **kwargs)
            except (NetworkError, NetBirdTimeoutError) as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    delay = self.config.retry_delay * (self.config.retry_backoff_factor ** attempt)
                    self.logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                    continue
                break
            except NetBirdException:
                # Don't retry on API errors (4xx, 5xx)
                raise
        
        # All retries exhausted
        self.logger.error(f"Request failed after {self.config.max_retries + 1} attempts")
        raise last_exception
    
    # Convenience methods for common HTTP verbs
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return self.request('GET', endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return self.request('POST', endpoint, data=data, json=json, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a PUT request."""
        return self.request('PUT', endpoint, data=data, json=json, **kwargs)
    
    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a PATCH request."""
        return self.request('PATCH', endpoint, data=data, json=json, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self.request('DELETE', endpoint, **kwargs)
    
    # Async convenience methods
    
    async def async_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make an async GET request."""
        return await self.async_request('GET', endpoint, params=params, **kwargs)
    
    async def async_post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make an async POST request."""
        return await self.async_request('POST', endpoint, data=data, json=json, **kwargs)
    
    async def async_put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make an async PUT request."""
        return await self.async_request('PUT', endpoint, data=data, json=json, **kwargs)
    
    async def async_patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make an async PATCH request."""
        return await self.async_request('PATCH', endpoint, data=data, json=json, **kwargs)
    
    async def async_delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an async DELETE request."""
        return await self.async_request('DELETE', endpoint, **kwargs)
    
    def close(self) -> None:
        """Close synchronous HTTP client."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
    
    async def aclose(self) -> None:
        """Close asynchronous HTTP client."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()
    
    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, '_sync_client') and self._sync_client:
            try:
                self._sync_client.close()
            except Exception:
                pass