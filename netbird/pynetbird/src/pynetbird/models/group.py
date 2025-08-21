"""
Group data models for PyNetBird.

Represents device groups used for policy management.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator

from .base import BaseModel, TimestampMixin, IDMixin, PeerRef


class GroupType(str, Enum):
    """Group types."""
    STANDARD = "standard"
    ALL = "all"  # Special all-members group
    SYSTEM = "system"  # System group


class Group(IDMixin, TimestampMixin):
    """
    NetBird Group model.
    
    Represents a group of devices for policy management.
    """
    
    # Basic information
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    
    # Member information
    peers_count: int = Field(0, alias="peersCount", description="Number of peers in group")
    peers: Optional[List[PeerRef]] = Field(None, description="Peers in this group")
    
    # Resource information (if supported)
    resources_count: int = Field(0, alias="resourcesCount", description="Number of resources")
    
    # Group type (optional, defaults to standard)
    group_type: Optional[GroupType] = Field(None, alias="type", description="Group type")
    
    # Additional metadata
    issued: Optional[str] = Field(None, description="Issued by")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """
        Validate group name.
        
        Args:
            v: Group name value
            
        Returns:
            Validated group name
            
        Raises:
            ValueError: If name is invalid
        """
        if not v or not v.strip():
            raise ValueError("Group name cannot be empty")
        if len(v) > 100:
            raise ValueError("Group name too long (max 100 characters)")
        return v.strip()
    
    @field_validator('group_type', mode='before')
    @classmethod
    def parse_group_type(cls, v):
        """
        Parse group type from string.
        
        Args:
            v: Group type value
            
        Returns:
            GroupType enum or None
        """
        if v is None:
            return None
        if isinstance(v, str):
            v_lower = v.lower()
            for gt in GroupType:
                if gt.value == v_lower:
                    return gt
            # Default to standard if unknown type
            return GroupType.STANDARD
        return v
    
    @property
    def peer_ids(self) -> List[str]:
        """Get list of peer IDs in this group."""
        if not self.peers:
            return []
        return [peer.id for peer in self.peers]
    
    @property
    def peer_names(self) -> List[str]:
        """Get list of peer names in this group."""
        if not self.peers:
            return []
        return [peer.name for peer in self.peers if peer.name]
    
    def has_peer(self, peer_id: str) -> bool:
        """
        Check if group contains specified peer.
        
        Args:
            peer_id: ID of the peer to check
            
        Returns:
            True if peer is in the group
        """
        return peer_id in self.peer_ids
    
    def has_peer_by_name(self, peer_name: str) -> bool:
        """
        Check if group contains peer by name.
        
        Args:
            peer_name: Name of the peer to check
            
        Returns:
            True if peer with given name is in the group
        """
        return peer_name in self.peer_names
    
    @property
    def is_all_group(self) -> bool:
        """Check if this is the special 'All' group."""
        return (
            self.name.lower() == "all" or 
            self.group_type == GroupType.ALL
        )
    
    @property
    def is_empty(self) -> bool:
        """Check if group has no members."""
        return self.peers_count == 0
    
    def add_peer(self, peer: PeerRef) -> None:
        """
        Add a peer to the group (local only, not API).
        
        Args:
            peer: Peer reference to add
        """
        if self.peers is None:
            self.peers = []
        if not self.has_peer(peer.id):
            self.peers.append(peer)
            self.peers_count = len(self.peers)
    
    def remove_peer(self, peer_id: str) -> bool:
        """
        Remove a peer from the group (local only, not API).
        
        Args:
            peer_id: ID of peer to remove
            
        Returns:
            True if peer was removed, False if not found
        """
        if self.peers is None:
            return False
        
        initial_count = len(self.peers)
        self.peers = [p for p in self.peers if p.id != peer_id]
        self.peers_count = len(self.peers)
        
        return len(self.peers) < initial_count


class GroupCreate(BaseModel):
    """Model for creating a new group."""
    
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    peers: Optional[List[str]] = Field(default_factory=list, description="Initial peer IDs")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate group name."""
        if not v or not v.strip():
            raise ValueError("Group name cannot be empty")
        if len(v) > 100:
            raise ValueError("Group name too long (max 100 characters)")
        return v.strip()


class GroupUpdate(BaseModel):
    """Model for updating group properties."""
    
    name: Optional[str] = Field(None, description="New group name")
    description: Optional[str] = Field(None, description="New group description")
    peers: Optional[List[str]] = Field(None, description="New peer IDs list")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate group name if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError("Group name cannot be empty")
            if len(v) > 100:
                raise ValueError("Group name too long (max 100 characters)")
            return v.strip()
        return v


class GroupList(BaseModel):
    """Response model for group list operations."""
    
    groups: List[Group] = Field(default_factory=list, description="List of groups")
    total: Optional[int] = Field(None, description="Total number of groups")
    
    def __iter__(self):
        """Iterate over groups."""
        return iter(self.groups)
    
    def __len__(self):
        """Get number of groups."""
        return len(self.groups)
    
    def __getitem__(self, index: int) -> Group:
        """Get group by index."""
        return self.groups[index]
    
    def find_by_name(self, name: str) -> Optional[Group]:
        """
        Find group by name.
        
        Args:
            name: Group name to search for
            
        Returns:
            Group if found, None otherwise
        """
        for group in self.groups:
            if group.name == name:
                return group
        return None
    
    def find_by_id(self, group_id: str) -> Optional[Group]:
        """
        Find group by ID.
        
        Args:
            group_id: Group ID to search for
            
        Returns:
            Group if found, None otherwise
        """
        for group in self.groups:
            if group.id == group_id:
                return group
        return None
    
    @property
    def all_group(self) -> Optional[Group]:
        """Get the special 'All' group if it exists."""
        return self.find_by_name("All")
    
    @property
    def non_empty_groups(self) -> List[Group]:
        """Get list of non-empty groups."""
        return [group for group in self.groups if not group.is_empty]
    
    def groups_containing_peer(self, peer_id: str) -> List[Group]:
        """
        Find all groups containing a specific peer.
        
        Args:
            peer_id: ID of the peer to search for
            
        Returns:
            List of groups containing the peer
        """
        result = []
        for group in self.groups:
            if group.has_peer(peer_id):
                result.append(group)
        return result