"""Tests for base HTTP client functionality."""

import pytest
from unittest.mock import Mock, patch
from pynetbird.base import BaseClient
from pynetbird.config import NetBirdConfig
from pynetbird.exceptions import NetBirdException, AuthenticationError


class TestBaseClient:
    """Test cases for BaseClient class."""
    
    def test_client_initialization(self):
        """Test BaseClient initialization."""
        config = NetBirdConfig(api_key="test-key", api_url="https://api.test.com")
        client = BaseClient(config=config)
        
        assert client.config.api_key == "test-key"
        assert client.config.api_url == "https://api.test.com"
    
    def test_sync_client_creation(self):
        """Test synchronous client creation."""
        config = NetBirdConfig(api_key="test-key")
        client = BaseClient(config=config)
        
        sync_client = client.sync_client
        assert sync_client is not None
        
        # Should reuse the same client
        assert client.sync_client is sync_client
    
    def test_async_client_creation(self):
        """Test asynchronous client creation."""
        config = NetBirdConfig(api_key="test-key")
        client = BaseClient(config=config)
        
        async_client = client.async_client
        assert async_client is not None
        
        # Should reuse the same client
        assert client.async_client is async_client
    
    def test_client_cleanup(self):
        """Test client cleanup."""
        config = NetBirdConfig(api_key="test-key")
        client = BaseClient(config=config)
        
        # Access clients to create them
        _ = client.sync_client
        _ = client.async_client
        
        # Test cleanup
        client.close()
        assert client._sync_client is None
    
    @patch('httpx.Client.request')
    def test_successful_request(self, mock_request):
        """Test successful HTTP request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'data': 'test'}
        mock_request.return_value = mock_response
        
        config = NetBirdConfig(api_key="test-key")
        client = BaseClient(config=config)
        
        result = client.get('/api/test')
        assert result == {'data': 'test'}
    
    @patch('httpx.Client.request')
    def test_error_request(self, mock_request):
        """Test HTTP request with error response."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.reason_phrase = "Unauthorized"
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'message': 'Invalid token'}
        mock_request.return_value = mock_response
        
        config = NetBirdConfig(api_key="test-key")
        client = BaseClient(config=config)
        
        with pytest.raises(AuthenticationError):
            client.get('/api/test')
    
    def test_context_manager(self):
        """Test BaseClient as context manager."""
        config = NetBirdConfig(api_key="test-key")
        
        with BaseClient(config=config) as client:
            assert client is not None
            _ = client.sync_client  # Create client
        
        # Client should be cleaned up
        assert client._sync_client is None