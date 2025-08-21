"""Tests for configuration management."""

import os
import json
import tempfile
import pytest
from pathlib import Path
from pynetbird.config import NetBirdConfig, load_config
from pynetbird.exceptions import ConfigurationError


class TestNetBirdConfig:
    """Test cases for NetBirdConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = NetBirdConfig()
        
        assert config.api_url == "https://api.netbird.io"
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.verify_ssl is True
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = NetBirdConfig(
            api_key="test-key",
            api_url="https://custom.api.com",
            timeout=60,
            max_retries=5
        )
        
        assert config.api_key == "test-key"
        assert config.api_url == "https://custom.api.com"
        assert config.timeout == 60
        assert config.max_retries == 5
    
    def test_config_validation_success(self):
        """Test successful configuration validation."""
        config = NetBirdConfig(api_key="test-key")
        config.validate()  # Should not raise
    
    def test_config_validation_missing_api_key(self):
        """Test validation failure for missing API key."""
        config = NetBirdConfig()
        
        with pytest.raises(ConfigurationError, match="api_key is required"):
            config.validate()
    
    def test_config_validation_invalid_url(self):
        """Test validation failure for invalid URL."""
        config = NetBirdConfig(api_key="test", api_url="invalid-url")
        
        with pytest.raises(ConfigurationError, match="Invalid API URL"):
            config.validate()
    
    def test_config_validation_invalid_timeout(self):
        """Test validation failure for invalid timeout."""
        config = NetBirdConfig(api_key="test", timeout=-1)
        
        with pytest.raises(ConfigurationError, match="timeout must be positive"):
            config.validate()
    
    def test_config_from_env(self):
        """Test loading configuration from environment variables."""
        # Set environment variables
        os.environ['NETBIRD_API_KEY'] = 'env-test-key'
        os.environ['NETBIRD_API_URL'] = 'https://env.api.com'
        os.environ['NETBIRD_TIMEOUT'] = '45'
        
        try:
            config = NetBirdConfig.from_env()
            
            assert config.api_key == 'env-test-key'
            assert config.api_url == 'https://env.api.com'
            assert config.timeout == 45
        finally:
            # Clean up
            del os.environ['NETBIRD_API_KEY']
            del os.environ['NETBIRD_API_URL']
            del os.environ['NETBIRD_TIMEOUT']
    
    def test_config_from_file_json(self):
        """Test loading configuration from JSON file."""
        config_data = {
            "api_key": "file-test-key",
            "api_url": "https://file.api.com",
            "timeout": 50,
            "max_retries": 4
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            config = NetBirdConfig.from_file(config_file)
            
            assert config.api_key == "file-test-key"
            assert config.api_url == "https://file.api.com"
            assert config.timeout == 50
            assert config.max_retries == 4
        finally:
            os.unlink(config_file)
    
    def test_config_from_file_not_found(self):
        """Test loading configuration from non-existent file."""
        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            NetBirdConfig.from_file("/non/existent/file.json")
    
    def test_config_to_dict(self):
        """Test converting configuration to dictionary."""
        config = NetBirdConfig(api_key="test", timeout=60)
        config_dict = config.to_dict()
        
        assert config_dict["api_key"] == "test"
        assert config_dict["timeout"] == 60
        assert isinstance(config_dict, dict)
    
    def test_auth_headers(self):
        """Test authentication headers generation."""
        config = NetBirdConfig(api_key="test-key")
        headers = config.get_auth_headers()
        
        assert headers["Authorization"] == "Token test-key"
        assert headers["Content-Type"] == "application/json"
        assert "User-Agent" in headers


class TestLoadConfig:
    """Test cases for load_config function."""
    
    def test_load_config_with_overrides(self):
        """Test loading configuration with parameter overrides."""
        config = load_config(api_key="override-key", timeout=90)
        
        assert config.api_key == "override-key"
        assert config.timeout == 90
    
    def test_load_config_precedence(self):
        """Test configuration precedence (overrides > env > file > defaults)."""
        # Set environment variable
        os.environ['NETBIRD_TIMEOUT'] = '60'
        
        try:
            # Override should take precedence over environment
            config = load_config(api_key="test", timeout=120)
            
            assert config.api_key == "test"
            assert config.timeout == 120  # Override wins over env
        finally:
            del os.environ['NETBIRD_TIMEOUT']