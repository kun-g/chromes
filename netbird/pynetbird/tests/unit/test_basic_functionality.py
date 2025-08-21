#!/usr/bin/env python3
"""
Basic functionality tests for PyNetBird base infrastructure.

This script tests the core components without requiring a real NetBird API connection.
Run this to verify that the base infrastructure is working correctly.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / ".." / "src"))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        from pynetbird import (
            BaseClient, NetBirdConfig, load_config,
            NetBirdException, AuthenticationError, ValidationError
        )
        from pynetbird.utils import (
            format_endpoint, parse_datetime, mask_sensitive_data,
            validate_id, chunk_list, normalize_name
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_exceptions():
    """Test exception hierarchy and functionality."""
    print("Testing exceptions...")
    
    from pynetbird.exceptions import (
        NetBirdException, AuthenticationError, map_status_code_to_exception,
        format_api_error
    )
    
    # Test basic exception
    try:
        raise NetBirdException("Test error", status_code=400, response={"error": "test"})
    except NetBirdException as e:
        assert e.status_code == 400
        assert "Test error" in str(e)
        assert e.response["error"] == "test"
    
    # Test status code mapping
    auth_error = map_status_code_to_exception(401, "Unauthorized")
    assert isinstance(auth_error, AuthenticationError)
    
    # Test error formatting
    error_msg = format_api_error({"message": "Invalid request"})
    assert error_msg == "Invalid request"
    
    print("✓ Exception tests passed")
    return True


def test_config():
    """Test configuration management."""
    print("Testing configuration...")
    
    from pynetbird.config import NetBirdConfig, load_config
    from pynetbird.exceptions import ConfigurationError
    
    # Test basic config
    config = NetBirdConfig(api_key="test-key", api_url="https://test.api.com")
    assert config.api_key == "test-key"
    assert config.api_url == "https://test.api.com"
    
    # Test config validation
    try:
        config.validate()
        print("✓ Config validation passed")
    except ConfigurationError as e:
        print(f"✓ Config validation correctly failed: {e}")
    
    # Test environment config
    os.environ['NETBIRD_API_KEY'] = 'env-test-key'
    os.environ['NETBIRD_TIMEOUT'] = '60'
    
    env_config = NetBirdConfig.from_env()
    assert env_config.api_key == 'env-test-key'
    assert env_config.timeout == 60
    
    # Test file config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "api_key": "file-test-key",
            "timeout": 45,
            "max_retries": 5
        }, f)
        config_file = f.name
    
    try:
        file_config = NetBirdConfig.from_file(config_file)
        assert file_config.api_key == "file-test-key"
        assert file_config.timeout == 45
        assert file_config.max_retries == 5
    finally:
        os.unlink(config_file)
    
    # Clean up environment
    del os.environ['NETBIRD_API_KEY']
    del os.environ['NETBIRD_TIMEOUT']
    
    print("✓ Configuration tests passed")
    return True


def test_utils():
    """Test utility functions."""
    print("Testing utilities...")
    
    from pynetbird.utils import (
        format_endpoint, mask_sensitive_data, validate_id,
        chunk_list, normalize_name, validate_ip_address, validate_cidr
    )
    from pynetbird.exceptions import ValidationError
    
    # Test endpoint formatting
    assert format_endpoint("peers") == "/api/peers"
    assert format_endpoint("/peers") == "/api/peers"
    assert format_endpoint("api/peers") == "/api/peers"
    assert format_endpoint("/api/peers") == "/api/peers"
    
    # Test data masking
    sensitive_data = {"api_key": "secret123", "name": "test", "password": "hidden"}
    masked = mask_sensitive_data(sensitive_data)
    assert "secret123" not in str(masked)
    assert masked["name"] == "test"  # Non-sensitive field unchanged
    
    # Test ID validation
    valid_id = validate_id("peer-123", "peer")
    assert valid_id == "peer-123"
    
    try:
        validate_id("", "test")
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected
    
    # Test list chunking
    items = list(range(10))
    chunks = list(chunk_list(items, 3))
    assert len(chunks) == 4
    assert chunks[0] == [0, 1, 2]
    assert chunks[-1] == [9]
    
    # Test name normalization
    name = normalize_name("  Test@Group#Name  ")
    assert name == "Test Group Name"
    
    # Test IP validation
    assert validate_ip_address("192.168.1.1") == "192.168.1.1"
    assert validate_ip_address("2001:db8::1") == "2001:db8::1"
    
    # Test CIDR validation
    assert validate_cidr("192.168.1.0/24") == "192.168.1.0/24"
    
    print("✓ Utility tests passed")
    return True


def test_base_client_init():
    """Test BaseClient initialization without making actual requests."""
    print("Testing BaseClient initialization...")
    
    from pynetbird.base import BaseClient
    from pynetbird.config import NetBirdConfig
    
    # Save and clear environment variables to ensure clean test
    old_api_url = os.environ.pop('NETBIRD_API_URL', None)
    old_api_key = os.environ.pop('NETBIRD_API_KEY', None)
    
    try:
        # Test basic initialization with explicit config
        config = NetBirdConfig(api_key="test-key", api_url="https://api.netbird.io")
        client = BaseClient(config=config)
        assert client.config.api_key == "test-key"
        assert client.config.api_url == "https://api.netbird.io"
        
        # Test with custom config
        config = NetBirdConfig(api_key="custom-key", timeout=60)
        client = BaseClient(config=config)
        assert client.config.api_key == "custom-key"
        assert client.config.timeout == 60
        
        # Test client creation
        sync_client = client.sync_client
        assert sync_client is not None
        
        async_client = client.async_client  
        assert async_client is not None
        
        # Test cleanup
        client.close()
        
        print("✓ BaseClient initialization tests passed")
        return True
        
    finally:
        # Restore environment variables
        if old_api_url is not None:
            os.environ['NETBIRD_API_URL'] = old_api_url
        if old_api_key is not None:
            os.environ['NETBIRD_API_KEY'] = old_api_key


def run_all_tests():
    """Run all basic functionality tests."""
    print("=" * 60)
    print("PyNetBird Basic Functionality Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_exceptions,
        test_config,
        test_utils,
        test_base_client_init,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            import traceback
            print(f"✗ {test.__name__} failed with exception: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All basic functionality tests passed!")
        print("\nThe PyNetBird base infrastructure is working correctly.")
        print("You can now proceed to implement higher-level managers and models.")
    else:
        print(f"❌ {failed} test(s) failed. Please review the errors above.")
        return False
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)