"""
NetBird client configuration management.

This module provides configuration loading and validation for the PyNetBird client,
supporting multiple configuration sources with proper precedence.
"""

import os
import json
from dataclasses import dataclass, field, MISSING
from pathlib import Path
from typing import Optional, Dict, Any, Union
from urllib.parse import urlparse

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from dotenv import load_dotenv

from .exceptions import ConfigurationError


@dataclass
class NetBirdConfig:
    """NetBird client configuration with validation and multiple loading sources."""
    
    api_key: Optional[str] = None
    api_url: str = "https://api.netbird.io"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff_factor: float = 2.0
    verify_ssl: bool = True
    user_agent: str = "PyNetBird/0.1.0"
    
    # Advanced configuration
    connection_pool_size: int = 10
    connection_pool_max_size: int = 20
    enable_logging: bool = False
    log_level: str = "INFO"
    
    # Rate limiting
    rate_limit_requests: Optional[int] = None
    rate_limit_period: Optional[int] = None
    
    # Additional headers
    extra_headers: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls, env_file: Optional[Union[str, Path]] = None) -> 'NetBirdConfig':
        """
        Load configuration from environment variables.
        
        Args:
            env_file: Optional path to .env file to load
            
        Returns:
            NetBirdConfig instance
            
        Environment variables:
            NETBIRD_API_KEY: API authentication key
            NETBIRD_API_URL: API base URL
            NETBIRD_TIMEOUT: Request timeout in seconds
            NETBIRD_MAX_RETRIES: Maximum number of retries
            NETBIRD_RETRY_DELAY: Initial retry delay in seconds
            NETBIRD_VERIFY_SSL: Whether to verify SSL certificates
            NETBIRD_LOG_LEVEL: Logging level
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        return cls(
            api_key=os.getenv('NETBIRD_API_KEY'),
            api_url=os.getenv('NETBIRD_API_URL', cls.api_url),
            timeout=int(os.getenv('NETBIRD_TIMEOUT', cls.timeout)),
            max_retries=int(os.getenv('NETBIRD_MAX_RETRIES', cls.max_retries)),
            retry_delay=float(os.getenv('NETBIRD_RETRY_DELAY', cls.retry_delay)),
            retry_backoff_factor=float(os.getenv('NETBIRD_RETRY_BACKOFF_FACTOR', cls.retry_backoff_factor)),
            verify_ssl=os.getenv('NETBIRD_VERIFY_SSL', 'true').lower() in ('true', '1', 'yes', 'on'),
            user_agent=os.getenv('NETBIRD_USER_AGENT', cls.user_agent),
            connection_pool_size=int(os.getenv('NETBIRD_POOL_SIZE', cls.connection_pool_size)),
            connection_pool_max_size=int(os.getenv('NETBIRD_POOL_MAX_SIZE', cls.connection_pool_max_size)),
            enable_logging=os.getenv('NETBIRD_ENABLE_LOGGING', 'false').lower() in ('true', '1', 'yes', 'on'),
            log_level=os.getenv('NETBIRD_LOG_LEVEL', cls.log_level),
            rate_limit_requests=_get_optional_int_env('NETBIRD_RATE_LIMIT_REQUESTS'),
            rate_limit_period=_get_optional_int_env('NETBIRD_RATE_LIMIT_PERIOD'),
        )
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'NetBirdConfig':
        """
        Load configuration from a file (JSON or YAML).
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            NetBirdConfig instance
            
        Raises:
            ConfigurationError: If file cannot be read or parsed
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ('.yaml', '.yml'):
                    if not YAML_AVAILABLE:
                        raise ConfigurationError(
                            "PyYAML is required to load YAML configuration files. "
                            "Install with: pip install PyYAML"
                        )
                    data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    raise ConfigurationError(
                        f"Unsupported configuration file format: {config_path.suffix}. "
                        "Supported formats: .json, .yaml, .yml"
                    )
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ConfigurationError(f"Failed to parse configuration file: {e}")
        except OSError as e:
            raise ConfigurationError(f"Failed to read configuration file: {e}")
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetBirdConfig':
        """
        Create configuration from dictionary.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            NetBirdConfig instance
        """
        # Filter only known fields to avoid TypeError
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        
        return cls(**filtered_data)
    
    def validate(self) -> None:
        """
        Validate configuration values.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        errors = []
        
        # Validate required fields
        if not self.api_key:
            errors.append("api_key is required")
        
        # Validate API URL
        if not self.api_url:
            errors.append("api_url is required")
        else:
            try:
                parsed = urlparse(self.api_url)
                if not parsed.scheme or not parsed.netloc:
                    errors.append(f"Invalid API URL format: {self.api_url}")
            except Exception:
                errors.append(f"Invalid API URL: {self.api_url}")
        
        # Validate numeric ranges
        if self.timeout <= 0:
            errors.append("timeout must be positive")
        
        if self.max_retries < 0:
            errors.append("max_retries must be non-negative")
        
        if self.retry_delay < 0:
            errors.append("retry_delay must be non-negative")
        
        if self.retry_backoff_factor < 1:
            errors.append("retry_backoff_factor must be >= 1")
        
        if self.connection_pool_size <= 0:
            errors.append("connection_pool_size must be positive")
        
        if self.connection_pool_max_size < self.connection_pool_size:
            errors.append("connection_pool_max_size must be >= connection_pool_size")
        
        # Validate rate limiting
        if self.rate_limit_requests is not None and self.rate_limit_requests <= 0:
            errors.append("rate_limit_requests must be positive if specified")
        
        if self.rate_limit_period is not None and self.rate_limit_period <= 0:
            errors.append("rate_limit_period must be positive if specified")
        
        if ((self.rate_limit_requests is None) != (self.rate_limit_period is None)):
            errors.append("rate_limit_requests and rate_limit_period must both be specified or both be None")
        
        # Validate log level
        valid_log_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"log_level must be one of: {', '.join(valid_log_levels)}")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary
        """
        result = {}
        for field_name, field_def in self.__dataclass_fields__.items():
            value = getattr(self, field_name)
            if field_def.default_factory != MISSING:
                # Handle fields with default_factory (like extra_headers)
                result[field_name] = value
            else:
                result[field_name] = value
        return result
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        
        Returns:
            Dictionary of headers
        """
        headers = {
            'Authorization': f'Token {self.api_key}',
            'User-Agent': self.user_agent,
            'Content-Type': 'application/json',
        }
        headers.update(self.extra_headers)
        return headers


def _get_optional_int_env(key: str) -> Optional[int]:
    """Get optional integer from environment variable."""
    value = os.getenv(key)
    if value is not None:
        try:
            return int(value)
        except ValueError:
            raise ConfigurationError(f"Invalid integer value for {key}: {value}")
    return None


def load_config(
    config_file: Optional[Union[str, Path]] = None,
    env_file: Optional[Union[str, Path]] = None,
    **overrides: Any
) -> NetBirdConfig:
    """
    Load configuration with proper precedence.
    
    Configuration precedence (highest to lowest):
    1. Direct parameter overrides
    2. Environment variables
    3. Configuration file
    4. Default values
    
    Args:
        config_file: Path to configuration file
        env_file: Path to .env file
        **overrides: Direct configuration overrides
        
    Returns:
        NetBirdConfig instance
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    # Start with defaults
    config = NetBirdConfig()
    
    # Load from file if specified
    if config_file:
        file_config = NetBirdConfig.from_file(config_file)
        config = _merge_configs(config, file_config)
    
    # Load from environment (higher precedence)
    env_config = NetBirdConfig.from_env(env_file)
    config = _merge_configs(config, env_config)
    
    # Apply direct overrides (highest precedence)
    if overrides:
        override_config = NetBirdConfig.from_dict(overrides)
        config = _merge_configs(config, override_config)
    
    # Validate final configuration
    config.validate()
    
    return config


def _merge_configs(base: NetBirdConfig, override: NetBirdConfig) -> NetBirdConfig:
    """Merge two configurations, with override taking precedence for non-default values."""
    base_dict = base.to_dict()
    override_dict = override.to_dict()
    
    # Only override non-default values
    defaults = NetBirdConfig().to_dict()
    
    for key, value in override_dict.items():
        if key == 'extra_headers':
            # Merge dictionaries for headers
            base_dict[key].update(value)
        elif value != defaults.get(key):
            # Override non-default values
            base_dict[key] = value
    
    return NetBirdConfig.from_dict(base_dict)