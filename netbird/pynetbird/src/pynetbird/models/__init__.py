"""
PyNetBird Data Models.

Provides type-safe NetBird API data models with Pydantic v2.
"""

from .base import (
    BaseModel,
    TimestampMixin,
    IDMixin,
    PeerRef,
    GroupRef,
    PolicyRef,
)

from .peer import (
    Peer,
    PeerStatus,
    PeerOS,
    PeerUpdate,
    PeerList,
)

from .group import (
    Group,
    GroupType,
    GroupCreate,
    GroupUpdate,
    GroupList,
)

from .policy import (
    Policy,
    PolicyRule,
    PolicyAction,
    PolicyProtocol,
    PolicyRuleFlow,
    PolicyCreate,
    PolicyUpdate,
    PolicyList,
    PostureCheck,
)

__all__ = [
    # Base classes
    "BaseModel",
    "TimestampMixin", 
    "IDMixin",
    "PeerRef",
    "GroupRef", 
    "PolicyRef",
    
    # Peer models
    "Peer",
    "PeerStatus",
    "PeerOS", 
    "PeerUpdate",
    "PeerList",
    
    # Group models
    "Group",
    "GroupType",
    "GroupCreate",
    "GroupUpdate", 
    "GroupList",
    
    # Policy models
    "Policy",
    "PolicyRule",
    "PolicyAction",
    "PolicyProtocol",
    "PolicyRuleFlow",
    "PolicyCreate",
    "PolicyUpdate",
    "PolicyList",
    "PostureCheck",
]