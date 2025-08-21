"""
Policy data models for PyNetBird.

Represents network access policies and rules.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator

from .base import BaseModel, TimestampMixin, IDMixin, GroupRef


class PolicyAction(str, Enum):
    """Policy action types."""
    ACCEPT = "accept"
    DROP = "drop"


class PolicyProtocol(str, Enum):
    """Network protocols for policy rules."""
    ALL = "all"
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"


class PolicyRuleFlow(str, Enum):
    """Policy rule flow directions."""
    BIDIRECTIONAL = "bidirectional"
    UNIDIRECTIONAL = "unidirectional"


class PolicyRule(IDMixin):
    """
    Policy rule model.
    
    NetBird policies consist of multiple rules.
    """
    
    # Rule basic information
    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    enabled: bool = Field(True, description="Rule enabled status")
    
    # Source and destination
    sources: List[GroupRef] = Field(default_factory=list, description="Source groups")
    destinations: List[GroupRef] = Field(default_factory=list, description="Destination groups")
    
    # Network rules
    protocol: PolicyProtocol = Field(PolicyProtocol.ALL, description="Network protocol")
    ports: List[str] = Field(default_factory=list, description="Port specifications")
    bidirectional: bool = Field(True, description="Bidirectional communication")
    
    # Action
    action: PolicyAction = Field(PolicyAction.ACCEPT, description="Policy action")
    
    # Additional fields
    flow: Optional[PolicyRuleFlow] = Field(None, description="Flow direction")
    
    @field_validator('ports', mode='before')
    @classmethod
    def validate_ports(cls, v):
        """
        Validate and normalize port specifications.
        
        Args:
            v: Port value(s)
            
        Returns:
            List of port strings
        """
        if not v:
            return []
        
        if isinstance(v, str):
            # Single port or range
            return [v.strip()]
        
        if isinstance(v, list):
            # Multiple ports/ranges
            result = []
            for port in v:
                if port:
                    result.append(str(port).strip())
            return result
        
        return []
    
    @field_validator('protocol', mode='before')
    @classmethod
    def parse_protocol(cls, v):
        """
        Parse protocol from string.
        
        Args:
            v: Protocol value
            
        Returns:
            PolicyProtocol enum
        """
        if v is None:
            return PolicyProtocol.ALL
        if isinstance(v, str):
            v_lower = v.lower()
            for proto in PolicyProtocol:
                if proto.value == v_lower:
                    return proto
            return PolicyProtocol.ALL
        return v
    
    @field_validator('action', mode='before')
    @classmethod
    def parse_action(cls, v):
        """
        Parse action from string.
        
        Args:
            v: Action value
            
        Returns:
            PolicyAction enum
        """
        if v is None:
            return PolicyAction.ACCEPT
        if isinstance(v, str):
            v_lower = v.lower()
            for action in PolicyAction:
                if action.value == v_lower:
                    return action
            return PolicyAction.ACCEPT
        return v
    
    @property
    def source_group_names(self) -> List[str]:
        """Get list of source group names."""
        return [group.name for group in self.sources]
    
    @property
    def source_group_ids(self) -> List[str]:
        """Get list of source group IDs."""
        return [group.id for group in self.sources]
    
    @property
    def destination_group_names(self) -> List[str]:
        """Get list of destination group names."""
        return [group.name for group in self.destinations]
    
    @property
    def destination_group_ids(self) -> List[str]:
        """Get list of destination group IDs."""
        return [group.id for group in self.destinations]
    
    def has_source_group(self, group_id: str) -> bool:
        """
        Check if rule has specific source group.
        
        Args:
            group_id: Group ID to check
            
        Returns:
            True if group is in sources
        """
        return group_id in self.source_group_ids
    
    def has_destination_group(self, group_id: str) -> bool:
        """
        Check if rule has specific destination group.
        
        Args:
            group_id: Group ID to check
            
        Returns:
            True if group is in destinations
        """
        return group_id in self.destination_group_ids
    
    @property
    def is_allow_rule(self) -> bool:
        """Check if this is an allow rule."""
        return self.action == PolicyAction.ACCEPT
    
    @property
    def is_deny_rule(self) -> bool:
        """Check if this is a deny rule."""
        return self.action == PolicyAction.DROP
    
    @property
    def port_summary(self) -> str:
        """Get human-readable port summary."""
        if not self.ports:
            return "all ports"
        return ", ".join(self.ports)


class PostureCheck(BaseModel):
    """Posture check model for policies."""
    
    id: str = Field(..., description="Posture check ID")
    name: Optional[str] = Field(None, description="Posture check name")
    checks: Optional[Dict[str, Any]] = Field(None, description="Check definitions")


class Policy(IDMixin, TimestampMixin):
    """
    NetBird Policy model.
    
    Represents network access policy containing multiple rules.
    """
    
    # Policy basic information
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    enabled: bool = Field(True, description="Policy enabled status")
    
    # Policy rules
    rules: List[PolicyRule] = Field(default_factory=list, description="Policy rules")
    
    # Posture checks (if supported)
    source_posture_checks: List[PostureCheck] = Field(
        default_factory=list, 
        alias="sourcePostureChecks",
        description="Source posture checks"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """
        Validate policy name.
        
        Args:
            v: Policy name value
            
        Returns:
            Validated policy name
            
        Raises:
            ValueError: If name is invalid
        """
        if not v or not v.strip():
            raise ValueError("Policy name cannot be empty")
        if len(v) > 100:
            raise ValueError("Policy name too long (max 100 characters)")
        return v.strip()
    
    @property
    def rule_count(self) -> int:
        """Get number of rules in policy."""
        return len(self.rules)
    
    @property
    def enabled_rules(self) -> List[PolicyRule]:
        """Get list of enabled rules."""
        return [rule for rule in self.rules if rule.enabled]
    
    @property
    def disabled_rules(self) -> List[PolicyRule]:
        """Get list of disabled rules."""
        return [rule for rule in self.rules if not rule.enabled]
    
    def get_rule_by_id(self, rule_id: str) -> Optional[PolicyRule]:
        """
        Get rule by ID.
        
        Args:
            rule_id: Rule ID to find
            
        Returns:
            PolicyRule if found, None otherwise
        """
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None
    
    def get_rule_by_name(self, rule_name: str) -> Optional[PolicyRule]:
        """
        Get rule by name.
        
        Args:
            rule_name: Rule name to find
            
        Returns:
            PolicyRule if found, None otherwise
        """
        for rule in self.rules:
            if rule.name == rule_name:
                return rule
        return None
    
    @property
    def all_source_groups(self) -> List[str]:
        """Get all unique source group names across all rules."""
        groups = set()
        for rule in self.rules:
            groups.update(rule.source_group_names)
        return sorted(list(groups))
    
    @property
    def all_destination_groups(self) -> List[str]:
        """Get all unique destination group names across all rules."""
        groups = set()
        for rule in self.rules:
            groups.update(rule.destination_group_names)
        return sorted(list(groups))
    
    @property
    def all_protocols(self) -> List[PolicyProtocol]:
        """Get all unique protocols used in rules."""
        protocols = set()
        for rule in self.rules:
            protocols.add(rule.protocol)
        return list(protocols)
    
    @property
    def has_posture_checks(self) -> bool:
        """Check if policy has posture checks."""
        return len(self.source_posture_checks) > 0
    
    def rules_for_source_group(self, group_id: str) -> List[PolicyRule]:
        """
        Get all rules that have specified group as source.
        
        Args:
            group_id: Group ID to search for
            
        Returns:
            List of matching rules
        """
        return [rule for rule in self.rules if rule.has_source_group(group_id)]
    
    def rules_for_destination_group(self, group_id: str) -> List[PolicyRule]:
        """
        Get all rules that have specified group as destination.
        
        Args:
            group_id: Group ID to search for
            
        Returns:
            List of matching rules
        """
        return [rule for rule in self.rules if rule.has_destination_group(group_id)]


class PolicyCreate(BaseModel):
    """Model for creating a new policy."""
    
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    enabled: bool = Field(True, description="Policy enabled status")
    rules: List[Dict[str, Any]] = Field(..., description="Policy rules configuration")
    source_posture_checks: Optional[List[str]] = Field(
        None,
        alias="sourcePostureChecks",
        description="Source posture check IDs"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate policy name."""
        if not v or not v.strip():
            raise ValueError("Policy name cannot be empty")
        if len(v) > 100:
            raise ValueError("Policy name too long (max 100 characters)")
        return v.strip()
    
    @field_validator('rules')
    @classmethod
    def validate_rules(cls, v):
        """Validate rules list."""
        if not v:
            raise ValueError("Policy must have at least one rule")
        return v


class PolicyUpdate(BaseModel):
    """Model for updating policy properties."""
    
    name: Optional[str] = Field(None, description="New policy name")
    description: Optional[str] = Field(None, description="New policy description")
    enabled: Optional[bool] = Field(None, description="New enabled status")
    rules: Optional[List[Dict[str, Any]]] = Field(None, description="New rules configuration")
    source_posture_checks: Optional[List[str]] = Field(
        None,
        alias="sourcePostureChecks",
        description="New source posture check IDs"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate policy name if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError("Policy name cannot be empty")
            if len(v) > 100:
                raise ValueError("Policy name too long (max 100 characters)")
            return v.strip()
        return v


class PolicyList(BaseModel):
    """Response model for policy list operations."""
    
    policies: List[Policy] = Field(default_factory=list, description="List of policies")
    total: Optional[int] = Field(None, description="Total number of policies")
    
    def __iter__(self):
        """Iterate over policies."""
        return iter(self.policies)
    
    def __len__(self):
        """Get number of policies."""
        return len(self.policies)
    
    def __getitem__(self, index: int) -> Policy:
        """Get policy by index."""
        return self.policies[index]
    
    def find_by_name(self, name: str) -> Optional[Policy]:
        """
        Find policy by name.
        
        Args:
            name: Policy name to search for
            
        Returns:
            Policy if found, None otherwise
        """
        for policy in self.policies:
            if policy.name == name:
                return policy
        return None
    
    def find_by_id(self, policy_id: str) -> Optional[Policy]:
        """
        Find policy by ID.
        
        Args:
            policy_id: Policy ID to search for
            
        Returns:
            Policy if found, None otherwise
        """
        for policy in self.policies:
            if policy.id == policy_id:
                return policy
        return None
    
    @property
    def enabled_policies(self) -> List[Policy]:
        """Get list of enabled policies."""
        return [policy for policy in self.policies if policy.enabled]
    
    @property
    def disabled_policies(self) -> List[Policy]:
        """Get list of disabled policies."""
        return [policy for policy in self.policies if not policy.enabled]
    
    def policies_using_group(self, group_id: str) -> List[Policy]:
        """
        Find all policies that reference a specific group.
        
        Args:
            group_id: Group ID to search for
            
        Returns:
            List of policies using the group
        """
        result = []
        for policy in self.policies:
            for rule in policy.rules:
                if rule.has_source_group(group_id) or rule.has_destination_group(group_id):
                    result.append(policy)
                    break  # Don't check other rules in same policy
        return result