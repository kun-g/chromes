"""
PyNetBird: Python client library for NetBird API.

This library provides both synchronous and asynchronous clients for interacting
with the NetBird API, including comprehensive error handling, configuration
management, and utility functions.
"""

from .base import BaseClient
from .config import NetBirdConfig, load_config
from .exceptions import (
    NetBirdException,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ValidationError,
    ConflictError,
    RateLimitError,
    ServerError,
    NetworkError,
    TimeoutError,
    ConfigurationError,
)

# Import submodules for easier access
from . import utils
from . import cli
from . import managers
from . import models

__version__ = "0.1.0"
__author__ = "PyNetBird Team"
__license__ = "MIT"

__all__ = [
    # Core classes
    "BaseClient",
    "NetBirdConfig",
    "load_config",
    
    # Exceptions
    "NetBirdException",
    "AuthenticationError", 
    "AuthorizationError",
    "ResourceNotFoundError",
    "ValidationError",
    "ConflictError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    "TimeoutError",
    "ConfigurationError",
    
    # Submodules
    "utils",
    "cli",
    "managers", 
    "models",
    
    # Version info
    "__version__",
]