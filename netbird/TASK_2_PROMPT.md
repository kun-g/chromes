# Task 2: PyNetBird Pydantic 数据模型实现

## 🎯 任务目标
基于 Task 1 的基础架构，实现 PyNetBird 的完整数据模型体系。使用 Pydantic v2 创建类型安全、可验证的数据模型，准确映射 NetBird API 的响应结构。

## 📋 任务清单
- [ ] 实现 `models/base.py` - 基础模型类和共享功能
- [ ] 实现 `models/peer.py` - Peer 相关数据模型
- [ ] 实现 `models/group.py` - Group 相关数据模型
- [ ] 实现 `models/policy.py` - Policy 相关数据模型
- [ ] 实现 `models/__init__.py` - 包导出配置
- [ ] 创建模型测试验证功能

## 🏗️ 技术要求

### 依赖库
- `pydantic` v2 - 数据验证和序列化
- `datetime` - 时间处理
- `typing` - 类型提示
- `enum` - 枚举类型
- `uuid` - UUID 验证
- `ipaddress` - IP 地址验证

### 设计原则
- **类型安全**: 使用完整的类型提示
- **数据验证**: 自动验证 API 响应格式
- **向前兼容**: 支持 API 字段的增减
- **性能优化**: 使用 Pydantic v2 的高性能特性

## 📁 文件结构
```
pynetbird/src/pynetbird/models/
├── __init__.py        # 模型导出
├── base.py           # 基础模型类
├── peer.py          # Peer 数据模型
├── group.py         # Group 数据模型
└── policy.py        # Policy 数据模型
```

## 🔧 详细实现要求

### 1. `models/base.py` - 基础模型类

**核心类**: `BaseModel`, `TimestampMixin`, `IDMixin`

**功能要求**:
```python
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict
from pydantic import validator, field_validator

class BaseModel(PydanticBaseModel):
    """PyNetBird 基础数据模型"""
    
    model_config = ConfigDict(
        # 允许额外字段，增强 API 兼容性
        extra='allow',
        # 使用枚举值而不是名称
        use_enum_values=True,
        # 验证赋值
        validate_assignment=True,
        # 序列化时排除未设置的字段
        exclude_unset=True
    )
    
    def to_dict(self, exclude_unset: bool = True, exclude_none: bool = True) -> Dict[str, Any]:
        """转换为字典，便于 API 调用"""
        return self.model_dump(
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
            by_alias=True
        )
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "BaseModel":
        """从 API 响应创建模型实例"""
        return cls.model_validate(data)

class TimestampMixin(BaseModel):
    """时间戳混入类"""
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    
    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        """解析 API 返回的时间格式"""
        if isinstance(v, str):
            # 处理多种时间格式
            import dateutil.parser
            return dateutil.parser.parse(v)
        return v

class IDMixin(BaseModel):
    """ID 混入类"""
    id: str = Field(..., description="Resource unique identifier")
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        """验证 ID 格式"""
        if not v or not isinstance(v, str):
            raise ValueError("ID must be a non-empty string")
        return v

# 引用类型 (用于避免循环引用)
class PeerRef(BaseModel):
    """Peer 引用模型"""
    id: str
    name: Optional[str] = None
    ip: Optional[str] = None

class GroupRef(BaseModel):
    """Group 引用模型"""
    id: str
    name: str
    peers_count: Optional[int] = Field(None, alias="peersCount")

class PolicyRef(BaseModel):
    """Policy 引用模型"""
    id: str
    name: str
    enabled: bool = True
```

### 2. `models/peer.py` - Peer 数据模型

**基于现有 API 响应结构**:
```python
from enum import Enum
from typing import Optional, List
from ipaddress import IPv4Address
from pydantic import Field, field_validator
from .base import BaseModel, TimestampMixin, IDMixin, GroupRef

class PeerStatus(str, Enum):
    """Peer 连接状态"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    UNKNOWN = "unknown"

class PeerOS(str, Enum):
    """Peer 操作系统类型"""
    LINUX = "linux"
    WINDOWS = "windows"
    DARWIN = "darwin"  # macOS
    ANDROID = "android"
    IOS = "ios"
    UNKNOWN = "unknown"

class Peer(BaseModel, IDMixin, TimestampMixin):
    """
    NetBird Peer 模型
    
    表示网络中的一个设备/节点
    """
    
    # 基础信息
    name: str = Field(..., description="Peer display name")
    ip: IPv4Address = Field(..., description="Assigned IP address in the network")
    
    # 连接状态
    connected: bool = Field(False, description="Current connection status")
    last_seen: Optional[datetime] = Field(None, alias="lastSeen", description="Last activity timestamp")
    
    # 系统信息
    os: PeerOS = Field(PeerOS.UNKNOWN, description="Operating system")
    version: Optional[str] = Field(None, description="NetBird client version")
    kernel_version: Optional[str] = Field(None, alias="kernelVersion")
    os_version: Optional[str] = Field(None, alias="osVersion")
    hostname: Optional[str] = Field(None, description="System hostname")
    
    # 网络配置
    dns_label: Optional[str] = Field(None, alias="dnsLabel")
    ssh_enabled: bool = Field(False, alias="sshEnabled", description="SSH access enabled")
    
    # 关联关系
    groups: List[GroupRef] = Field(default_factory=list, description="Groups this peer belongs to")
    user_id: Optional[str] = Field(None, alias="userId", description="Owner user ID")
    
    # 元数据
    approval_required: bool = Field(False, alias="approvalRequired")
    login_expiration_enabled: bool = Field(False, alias="loginExpirationEnabled")
    login_expiration: Optional[datetime] = Field(None, alias="loginExpiration")
    
    @field_validator('ip', mode='before')
    @classmethod
    def parse_ip(cls, v):
        """解析 IP 地址"""
        if isinstance(v, str):
            return IPv4Address(v)
        return v
    
    @field_validator('connected', mode='before')
    @classmethod
    def parse_connected(cls, v):
        """解析连接状态"""
        if isinstance(v, str):
            return v.lower() in ('true', 'connected', '1', 'yes')
        return bool(v)
    
    @property
    def status(self) -> PeerStatus:
        """获取连接状态枚举"""
        return PeerStatus.CONNECTED if self.connected else PeerStatus.DISCONNECTED
    
    @property
    def group_names(self) -> List[str]:
        """获取所属组名列表"""
        return [group.name for group in self.groups if group.name]
    
    def is_in_group(self, group_name: str) -> bool:
        """检查是否在指定组中"""
        return group_name in self.group_names

class PeerUpdate(BaseModel):
    """Peer 更新模型"""
    name: Optional[str] = None
    ssh_enabled: Optional[bool] = Field(None, alias="sshEnabled")
    login_expiration_enabled: Optional[bool] = Field(None, alias="loginExpirationEnabled")
    approval_required: Optional[bool] = Field(None, alias="approvalRequired")

class PeerList(BaseModel):
    """Peer 列表响应模型"""
    peers: List[Peer] = Field(default_factory=list)
    total: Optional[int] = None
    
    def __iter__(self):
        return iter(self.peers)
    
    def __len__(self):
        return len(self.peers)
```

### 3. `models/group.py` - Group 数据模型

**功能要求**:
```python
from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator
from .base import BaseModel, TimestampMixin, IDMixin, PeerRef

class GroupType(str, Enum):
    """Group 类型"""
    STANDARD = "standard"
    ALL = "all"  # 特殊的全员组
    SYSTEM = "system"  # 系统组

class Group(BaseModel, IDMixin, TimestampMixin):
    """
    NetBird Group 模型
    
    表示设备分组，用于策略管理
    """
    
    # 基础信息
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    
    # 成员信息
    peers_count: int = Field(0, alias="peersCount", description="Number of peers in group")
    peers: Optional[List[PeerRef]] = Field(None, description="Peers in this group")
    
    # 资源信息 (如果支持)
    resources_count: int = Field(0, alias="resourcesCount", description="Number of resources")
    
    # 分组类型
    group_type: GroupType = Field(GroupType.STANDARD, alias="type")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """验证组名"""
        if not v or not v.strip():
            raise ValueError("Group name cannot be empty")
        if len(v) > 100:
            raise ValueError("Group name too long")
        return v.strip()
    
    @property
    def peer_ids(self) -> List[str]:
        """获取成员 Peer ID 列表"""
        if not self.peers:
            return []
        return [peer.id for peer in self.peers]
    
    @property
    def peer_names(self) -> List[str]:
        """获取成员 Peer 名称列表"""
        if not self.peers:
            return []
        return [peer.name for peer in self.peers if peer.name]
    
    def has_peer(self, peer_id: str) -> bool:
        """检查是否包含指定 Peer"""
        return peer_id in self.peer_ids
    
    @property
    def is_all_group(self) -> bool:
        """是否为全员组"""
        return self.name.lower() == "all" or self.group_type == GroupType.ALL

class GroupCreate(BaseModel):
    """创建 Group 请求模型"""
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    peers: Optional[List[str]] = Field(default_factory=list, description="Initial peer IDs")

class GroupUpdate(BaseModel):
    """更新 Group 请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    peers: Optional[List[str]] = None

class GroupList(BaseModel):
    """Group 列表响应模型"""
    groups: List[Group] = Field(default_factory=list)
    total: Optional[int] = None
    
    def __iter__(self):
        return iter(self.groups)
    
    def __len__(self):
        return len(self.groups)
    
    def find_by_name(self, name: str) -> Optional[Group]:
        """按名称查找组"""
        for group in self.groups:
            if group.name == name:
                return group
        return None
```

### 4. `models/policy.py` - Policy 数据模型

**基于复杂的策略结构**:
```python
from enum import Enum
from typing import Optional, List, Union
from pydantic import Field, field_validator
from .base import BaseModel, TimestampMixin, IDMixin, GroupRef

class PolicyAction(str, Enum):
    """策略动作"""
    ACCEPT = "accept"
    DROP = "drop"

class PolicyProtocol(str, Enum):
    """网络协议"""
    ALL = "all"
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"

class PolicyRule(BaseModel, IDMixin):
    """
    策略规则模型
    
    NetBird 的策略由多个规则组成
    """
    
    # 规则基础信息
    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    enabled: bool = Field(True, description="Rule enabled status")
    
    # 源和目标
    sources: List[GroupRef] = Field(default_factory=list, description="Source groups")
    destinations: List[GroupRef] = Field(default_factory=list, description="Destination groups")
    
    # 网络规则
    protocol: PolicyProtocol = Field(PolicyProtocol.ALL, description="Network protocol")
    ports: List[str] = Field(default_factory=list, description="Port specifications")
    bidirectional: bool = Field(True, description="Bidirectional communication")
    
    # 动作
    action: PolicyAction = Field(PolicyAction.ACCEPT, description="Policy action")
    
    @field_validator('ports', mode='before')
    @classmethod
    def validate_ports(cls, v):
        """验证端口格式"""
        if not v:
            return []
        
        if isinstance(v, str):
            return [v.strip()]
        
        if isinstance(v, list):
            return [str(port).strip() for port in v if port]
        
        return []
    
    @property
    def source_group_names(self) -> List[str]:
        """获取源组名称列表"""
        return [group.name for group in self.sources]
    
    @property
    def destination_group_names(self) -> List[str]:
        """获取目标组名称列表"""
        return [group.name for group in self.destinations]

class Policy(BaseModel, IDMixin, TimestampMixin):
    """
    NetBird Policy 模型
    
    表示网络访问策略，包含多个规则
    """
    
    # 策略基础信息
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    enabled: bool = Field(True, description="Policy enabled status")
    
    # 策略规则
    rules: List[PolicyRule] = Field(default_factory=list, description="Policy rules")
    
    # 额外的策略检查 (如果支持)
    source_posture_checks: List[Dict] = Field(
        default_factory=list, 
        alias="sourcePostureChecks",
        description="Source posture checks"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """验证策略名称"""
        if not v or not v.strip():
            raise ValueError("Policy name cannot be empty")
        if len(v) > 100:
            raise ValueError("Policy name too long")
        return v.strip()
    
    @property
    def rule_count(self) -> int:
        """获取规则数量"""
        return len(self.rules)
    
    @property
    def enabled_rules(self) -> List[PolicyRule]:
        """获取启用的规则"""
        return [rule for rule in self.rules if rule.enabled]
    
    def get_rule_by_id(self, rule_id: str) -> Optional[PolicyRule]:
        """按 ID 获取规则"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None
    
    @property
    def all_source_groups(self) -> List[str]:
        """获取所有源组名称"""
        groups = set()
        for rule in self.rules:
            groups.update(rule.source_group_names)
        return list(groups)
    
    @property
    def all_destination_groups(self) -> List[str]:
        """获取所有目标组名称"""
        groups = set()
        for rule in self.rules:
            groups.update(rule.destination_group_names)
        return list(groups)

class PolicyCreate(BaseModel):
    """创建 Policy 请求模型"""
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    enabled: bool = Field(True, description="Policy enabled status")
    rules: List[Dict] = Field(..., description="Policy rules configuration")

class PolicyUpdate(BaseModel):
    """更新 Policy 请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    rules: Optional[List[Dict]] = None

class PolicyList(BaseModel):
    """Policy 列表响应模型"""
    policies: List[Policy] = Field(default_factory=list)
    total: Optional[int] = None
    
    def __iter__(self):
        return iter(self.policies)
    
    def __len__(self):
        return len(self.policies)
    
    def find_by_name(self, name: str) -> Optional[Policy]:
        """按名称查找策略"""
        for policy in self.policies:
            if policy.name == name:
                return policy
        return None
```

### 5. `models/__init__.py` - 包导出

**功能要求**:
```python
"""
PyNetBird Data Models

提供类型安全的 NetBird API 数据模型
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
    PolicyCreate,
    PolicyUpdate,
    PolicyList,
)

__all__ = [
    # 基础类
    "BaseModel",
    "TimestampMixin", 
    "IDMixin",
    "PeerRef",
    "GroupRef", 
    "PolicyRef",
    
    # Peer 模型
    "Peer",
    "PeerStatus",
    "PeerOS", 
    "PeerUpdate",
    "PeerList",
    
    # Group 模型
    "Group",
    "GroupType",
    "GroupCreate",
    "GroupUpdate", 
    "GroupList",
    
    # Policy 模型
    "Policy",
    "PolicyRule",
    "PolicyAction",
    "PolicyProtocol",
    "PolicyCreate",
    "PolicyUpdate",
    "PolicyList",
]
```

## 🧪 测试要求

创建全面的模型测试:

```python
# tests/test_models.py
import pytest
from datetime import datetime
from ipaddress import IPv4Address

from pynetbird.models import Peer, Group, Policy, PolicyRule
from pynetbird.models.base import PeerRef, GroupRef

def test_peer_model():
    """测试 Peer 模型"""
    peer_data = {
        "id": "peer123",
        "name": "test-peer",
        "ip": "192.168.1.100",
        "connected": True,
        "os": "linux",
        "groups": [{"id": "group1", "name": "dev"}]
    }
    
    peer = Peer.model_validate(peer_data)
    assert peer.id == "peer123"
    assert peer.ip == IPv4Address("192.168.1.100")
    assert peer.connected is True
    assert len(peer.groups) == 1

def test_group_model():
    """测试 Group 模型"""
    # 实现完整的组模型测试

def test_policy_model():
    """测试 Policy 模型"""
    # 实现完整的策略模型测试
```

## 📚 参考资料

### 现有 API 响应示例
参考 `manage_groups.py` 中的实际 API 响应:

```python
# Peer API 响应
{
  "id": "d2itv26kurdc73fqb0cg",
  "name": "ab14ca4f6a9a", 
  "ip": "100.109.212.184",
  "connected": true,
  "groups": [
    {"id": "d1n8evekurdc73cnnpig", "name": "All"},
    {"id": "d2itruukurdc73fqb0bg", "name": "Quarantine"}
  ]
}

# Group API 响应
{
  "id": "d1n8evekurdc73cnnpig",
  "name": "All",
  "peers": [
    {"id": "peer1", "name": "dev-container"},
    {"id": "peer2", "name": "MacBook-Pro"}
  ]
}

# Policy API 响应 (复杂结构)
{
  "id": "d1n8evekurdc73cnnpj0",
  "name": "Default",
  "enabled": false,
  "rules": [
    {
      "id": "d1n8evekurdc73cnnpj0",
      "name": "Default",
      "enabled": false,
      "sources": [{"id": "group1", "name": "All"}],
      "destinations": [{"id": "group1", "name": "All"}],
      "bidirectional": true,
      "protocol": "all",
      "action": "accept"
    }
  ]
}
```

## ✅ 完成标准

1. **数据模型完整性**:
   - 覆盖所有主要 API 响应字段
   - 支持嵌套关系 (Peer→Group, Policy→Rule)
   - 正确的类型转换和验证

2. **API 兼容性**:
   - 能解析真实 API 响应
   - 支持字段别名 (camelCase ↔ snake_case)
   - 向前兼容性 (extra='allow')

3. **代码质量**:
   - 完整的类型提示
   - 全面的文档字符串
   - 输入验证和错误处理

4. **测试覆盖**:
   - 所有模型的基础测试
   - 边界情况验证
   - 序列化/反序列化测试

## 🚀 开始开发

1. **环境准备**:
   ```bash
   cd /Users/kun/Code/chromes/netbird/pynetbird
   uv add python-dateutil  # 用于时间解析
   ```

2. **实现顺序**:
   - 先实现 `base.py` (其他模型依赖)
   - 再实现 `peer.py` (最简单)
   - 然后 `group.py` (中等复杂度)  
   - 最后 `policy.py` (最复杂)
   - 完成 `__init__.py` 导出

3. **验证方法**:
   ```python
   # 测试导入
   from pynetbird.models import Peer, Group, Policy
   
   # 测试 API 响应解析
   peer = Peer.model_validate(api_response_data)
   ```

## 🤝 交付标准

提交时请包含:
- [ ] 所有 5 个文件的完整实现
- [ ] 基础功能测试验证
- [ ] 能成功解析真实 API 响应
- [ ] 模型关系验证 (引用完整性)

预计完成时间: 2-3 小时

Task 1 的基础架构已经就绪，现在可以在此基础上构建类型安全的数据模型了！