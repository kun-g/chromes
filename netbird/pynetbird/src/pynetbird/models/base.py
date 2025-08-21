"""
Base model classes for PyNetBird.

Provides foundation classes and mixins for all data models.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict
from pydantic import field_validator
import dateutil.parser


class BaseModel(PydanticBaseModel):
    """PyNetBird base data model with common functionality."""
    
    model_config = ConfigDict(
        # Allow extra fields for API compatibility
        extra='allow',
        # Use enum values instead of names
        use_enum_values=True,
        # Validate on assignment
        validate_assignment=True,
        # Exclude unset fields when serializing
        exclude_unset=True,
        # Populate by field name or alias
        populate_by_name=True
    )
    
    def to_dict(self, exclude_unset: bool = True, exclude_none: bool = True) -> Dict[str, Any]:
        """
        Convert model to dictionary for API calls.
        
        Args:
            exclude_unset: Exclude fields that haven't been set
            exclude_none: Exclude fields with None values
            
        Returns:
            Dictionary representation of the model
        """
        return self.model_dump(
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
            by_alias=True
        )
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "BaseModel":
        """
        Create model instance from API response.
        
        Args:
            data: API response data
            
        Returns:
            Model instance
        """
        return cls.model_validate(data)


class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields."""
    
    created_at: Optional[datetime] = Field(None, alias="createdAt", description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt", description="Last update timestamp")
    
    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        """
        Parse datetime from various formats.
        
        Args:
            v: Value to parse (string or datetime)
            
        Returns:
            Parsed datetime object
        """
        if v is None:
            return None
        if isinstance(v, str):
            # Handle multiple datetime formats from API
            return dateutil.parser.parse(v)
        return v


class IDMixin(BaseModel):
    """Mixin for models with ID field."""
    
    id: str = Field(..., description="Resource unique identifier")
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        """
        Validate ID format.
        
        Args:
            v: ID value to validate
            
        Returns:
            Validated ID
            
        Raises:
            ValueError: If ID is invalid
        """
        if not v or not isinstance(v, str):
            raise ValueError("ID must be a non-empty string")
        return v


# Reference models to avoid circular dependencies

class PeerRef(BaseModel):
    """Peer reference model for use in other models."""
    
    id: str = Field(..., description="Peer ID")
    name: Optional[str] = Field(None, description="Peer name")
    ip: Optional[str] = Field(None, description="Peer IP address")


class GroupRef(BaseModel):
    """Group reference model for use in other models."""
    
    id: str = Field(..., description="Group ID")
    name: str = Field(..., description="Group name")
    peers_count: Optional[int] = Field(None, alias="peersCount", description="Number of peers in group")


class PolicyRef(BaseModel):
    """Policy reference model for use in other models."""
    
    id: str = Field(..., description="Policy ID")
    name: str = Field(..., description="Policy name")
    enabled: bool = Field(True, description="Policy enabled status")