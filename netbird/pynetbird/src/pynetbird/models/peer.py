"""
Peer data models for PyNetBird.

Represents network devices/nodes in the NetBird network.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from ipaddress import IPv4Address
from pydantic import Field, field_validator

from .base import BaseModel, TimestampMixin, IDMixin, GroupRef


class PeerStatus(str, Enum):
    """Peer connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    UNKNOWN = "unknown"


class PeerOS(str, Enum):
    """Peer operating system types."""
    LINUX = "linux"
    WINDOWS = "windows"
    DARWIN = "darwin"  # macOS
    ANDROID = "android"
    IOS = "ios"
    UNKNOWN = "unknown"


class Peer(IDMixin, TimestampMixin):
    """
    NetBird Peer model.
    
    Represents a device/node in the network.
    """
    
    # Basic information
    name: str = Field(..., description="Peer display name")
    ip: IPv4Address = Field(..., description="Assigned IP address in the network")
    
    # Connection status
    connected: bool = Field(False, description="Current connection status")
    last_seen: Optional[datetime] = Field(None, alias="lastSeen", description="Last activity timestamp")
    
    # System information
    os: Optional[PeerOS] = Field(None, description="Operating system")
    version: Optional[str] = Field(None, description="NetBird client version")
    kernel_version: Optional[str] = Field(None, alias="kernelVersion", description="Kernel version")
    os_version: Optional[str] = Field(None, alias="osVersion", description="OS version")
    hostname: Optional[str] = Field(None, description="System hostname")
    ui_version: Optional[str] = Field(None, alias="uiVersion", description="UI version")
    
    # Network configuration
    dns_label: Optional[str] = Field(None, alias="dnsLabel", description="DNS label")
    ssh_enabled: bool = Field(False, alias="sshEnabled", description="SSH access enabled")
    
    # Associations
    groups: List[GroupRef] = Field(default_factory=list, description="Groups this peer belongs to")
    user_id: Optional[str] = Field(None, alias="userId", description="Owner user ID")
    
    # Metadata
    approval_required: bool = Field(False, alias="approvalRequired", description="Approval required flag")
    login_expiration_enabled: bool = Field(False, alias="loginExpirationEnabled", description="Login expiration enabled")
    login_expired: bool = Field(False, alias="loginExpired", description="Login expired flag")
    login_expiration: Optional[datetime] = Field(None, alias="loginExpiration", description="Login expiration time")
    
    # Additional metadata
    serial_number: Optional[str] = Field(None, alias="serialNumber", description="Device serial number")
    city_name: Optional[str] = Field(None, alias="cityName", description="City location")
    country_code: Optional[str] = Field(None, alias="countryCode", description="Country code")
    geo_name_id: Optional[int] = Field(None, alias="geoNameId", description="Geo name ID")
    accessible_peers_count: Optional[int] = Field(None, alias="accessiblePeersCount", description="Number of accessible peers")
    
    @field_validator('ip', mode='before')
    @classmethod
    def parse_ip(cls, v):
        """
        Parse IP address from string.
        
        Args:
            v: IP address value (string or IPv4Address)
            
        Returns:
            IPv4Address object
        """
        if isinstance(v, str):
            return IPv4Address(v)
        return v
    
    @field_validator('connected', mode='before')
    @classmethod
    def parse_connected(cls, v):
        """
        Parse connection status from various formats.
        
        Args:
            v: Connection status value
            
        Returns:
            Boolean connection status
        """
        if isinstance(v, str):
            return v.lower() in ('true', 'connected', '1', 'yes')
        return bool(v)
    
    @field_validator('last_seen', 'login_expiration', mode='before')
    @classmethod
    def parse_optional_datetime(cls, v):
        """
        Parse optional datetime fields.
        
        Args:
            v: Datetime value (string or datetime)
            
        Returns:
            Parsed datetime or None
        """
        if v is None:
            return None
        if isinstance(v, str):
            import dateutil.parser
            return dateutil.parser.parse(v)
        return v
    
    @field_validator('os', mode='before')
    @classmethod
    def parse_os(cls, v):
        """
        Parse operating system from string.
        
        Args:
            v: OS value
            
        Returns:
            PeerOS enum value or None
        """
        if v is None:
            return None
        if isinstance(v, str):
            v_lower = v.lower()
            for os in PeerOS:
                if os.value == v_lower:
                    return os
            return PeerOS.UNKNOWN
        return v
    
    @property
    def status(self) -> PeerStatus:
        """Get connection status as enum."""
        return PeerStatus.CONNECTED if self.connected else PeerStatus.DISCONNECTED
    
    @property
    def group_names(self) -> List[str]:
        """Get list of group names this peer belongs to."""
        return [group.name for group in self.groups if group.name]
    
    @property
    def group_ids(self) -> List[str]:
        """Get list of group IDs this peer belongs to."""
        return [group.id for group in self.groups]
    
    def is_in_group(self, group_name: str) -> bool:
        """
        Check if peer is in specified group.
        
        Args:
            group_name: Name of the group to check
            
        Returns:
            True if peer is in the group
        """
        return group_name in self.group_names


class PeerUpdate(BaseModel):
    """Model for updating peer properties."""
    
    name: Optional[str] = Field(None, description="New peer name")
    ssh_enabled: Optional[bool] = Field(None, alias="sshEnabled", description="SSH enabled status")
    login_expiration_enabled: Optional[bool] = Field(None, alias="loginExpirationEnabled", description="Login expiration enabled")
    approval_required: Optional[bool] = Field(None, alias="approvalRequired", description="Approval required flag")


class PeerList(BaseModel):
    """Response model for peer list operations."""
    
    peers: List[Peer] = Field(default_factory=list, description="List of peers")
    total: Optional[int] = Field(None, description="Total number of peers")
    
    def __iter__(self):
        """Iterate over peers."""
        return iter(self.peers)
    
    def __len__(self):
        """Get number of peers."""
        return len(self.peers)
    
    def __getitem__(self, index: int) -> Peer:
        """Get peer by index."""
        return self.peers[index]
    
    def find_by_name(self, name: str) -> Optional[Peer]:
        """
        Find peer by name.
        
        Args:
            name: Peer name to search for
            
        Returns:
            Peer if found, None otherwise
        """
        for peer in self.peers:
            if peer.name == name:
                return peer
        return None
    
    def find_by_ip(self, ip: str) -> Optional[Peer]:
        """
        Find peer by IP address.
        
        Args:
            ip: IP address to search for
            
        Returns:
            Peer if found, None otherwise
        """
        ip_addr = IPv4Address(ip)
        for peer in self.peers:
            if peer.ip == ip_addr:
                return peer
        return None
    
    @property
    def connected_peers(self) -> List[Peer]:
        """Get list of connected peers."""
        return [peer for peer in self.peers if peer.connected]
    
    @property
    def disconnected_peers(self) -> List[Peer]:
        """Get list of disconnected peers."""
        return [peer for peer in self.peers if not peer.connected]