# Task 6-1: PyNetBird 测试框架扩展

## 🎯 任务目标
基于 Task 1 已有的测试基础，扩展和完善 PyNetBird 的测试框架，为即将到来的数据模型 (Task 2) 和资源管理器 (Task 3) 准备全面的测试环境。

## 📋 任务清单
- [ ] 扩展现有测试框架配置
- [ ] 创建测试数据工厂和固定装置 (fixtures)
- [ ] 实现 HTTP Mock 服务器用于 API 测试
- [ ] 建立测试数据集 (基于真实 API 响应)
- [ ] 创建测试工具函数
- [ ] 配置持续测试和覆盖率报告

## 🏗️ 技术要求

### 依赖库
- `pytest` - 测试框架 (已有)
- `pytest-asyncio` - 异步测试支持
- `pytest-mock` - Mock 功能增强
- `pytest-cov` - 覆盖率报告
- `httpx` - HTTP 客户端测试 (已有)
- `respx` - HTTP Mock 服务器
- `factory-boy` - 测试数据工厂
- `freezegun` - 时间控制

### 测试策略
- **单元测试**: 测试独立模块功能
- **集成测试**: 测试模块间交互
- **API Mock 测试**: 模拟 NetBird API 响应
- **契约测试**: 验证 API 响应格式兼容性

## 📁 文件结构扩展
```
pynetbird/tests/
├── __init__.py              # 已存在
├── conftest.py             # 新增：pytest 配置和 fixtures
├── fixtures/               # 新增：测试数据目录
│   ├── __init__.py
│   ├── api_responses.py    # 真实 API 响应数据
│   ├── factories.py        # 数据工厂
│   └── mock_server.py      # Mock 服务器配置
├── unit/                   # 新增：单元测试
│   ├── __init__.py
│   ├── test_base.py       # 迁移现有测试
│   ├── test_config.py     # 迁移现有测试
│   ├── test_exceptions.py # 迁移现有测试
│   ├── test_utils.py      # 迁移现有测试
│   └── test_models/       # 为 Task 2 准备
│       ├── __init__.py
│       ├── test_peer.py
│       ├── test_group.py
│       └── test_policy.py
├── integration/            # 新增：集成测试
│   ├── __init__.py
│   ├── test_client.py     # HTTP 客户端集成测试
│   └── test_managers/     # 为 Task 3 准备
│       ├── __init__.py
│       ├── test_peer_manager.py
│       ├── test_group_manager.py
│       └── test_policy_manager.py
├── e2e/                   # 新增：端到端测试
│   ├── __init__.py
│   └── test_real_api.py   # 真实 API 测试 (可选)
└── utils.py               # 新增：测试工具函数
```

## 🔧 详细实现要求

### 1. `conftest.py` - pytest 配置中心

**功能要求**:
```python
"""
PyNetBird 测试配置中心

提供全局测试 fixtures 和配置
"""
import os
import pytest
import asyncio
from typing import Dict, Any, Generator
from unittest.mock import Mock
import respx
import httpx

from pynetbird.config import NetBirdConfig
from pynetbird.base import BaseClient
from .fixtures.factories import PeerFactory, GroupFactory, PolicyFactory
from .fixtures.api_responses import API_RESPONSES
from .fixtures.mock_server import setup_mock_server

# 测试环境配置
TEST_CONFIG = {
    "api_key": "test_api_key_12345",
    "api_url": "https://api.test.netbird.io",
    "timeout": 10,
    "max_retries": 1,
    "retry_delay": 0.1,
    "enable_logging": False,
}

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_config() -> NetBirdConfig:
    """提供测试配置"""
    return NetBirdConfig(**TEST_CONFIG)

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock 环境变量"""
    monkeypatch.setenv("NETBIRD_API_KEY", TEST_CONFIG["api_key"])
    monkeypatch.setenv("NETBIRD_API_URL", TEST_CONFIG["api_url"])
    yield
    # 清理会在 monkeypatch 自动完成

@pytest.fixture
def sync_client(test_config) -> BaseClient:
    """提供同步测试客户端"""
    return BaseClient(config=test_config)

@pytest.fixture
async def async_client(test_config) -> BaseClient:
    """提供异步测试客户端"""
    client = BaseClient(config=test_config)
    yield client
    await client.aclose()

@pytest.fixture
def mock_http_responses():
    """HTTP 响应 Mock 装置"""
    with respx.mock() as respx_mock:
        yield respx_mock

@pytest.fixture
def netbird_mock_server(mock_http_responses):
    """NetBird API Mock 服务器"""
    return setup_mock_server(mock_http_responses)

# 数据工厂 fixtures
@pytest.fixture
def peer_factory():
    """Peer 数据工厂"""
    return PeerFactory

@pytest.fixture 
def group_factory():
    """Group 数据工厂"""
    return GroupFactory

@pytest.fixture
def policy_factory():
    """Policy 数据工厂"""
    return PolicyFactory

# 测试数据 fixtures
@pytest.fixture
def sample_peer_data():
    """示例 Peer 数据"""
    return API_RESPONSES["peers"]["single"]

@pytest.fixture
def sample_peers_list():
    """示例 Peers 列表"""
    return API_RESPONSES["peers"]["list"]

@pytest.fixture
def sample_group_data():
    """示例 Group 数据"""
    return API_RESPONSES["groups"]["single"]

@pytest.fixture
def sample_policy_data():
    """示例 Policy 数据"""
    return API_RESPONSES["policies"]["single"]

# 辅助 fixtures
@pytest.fixture
def temp_config_file(tmp_path):
    """临时配置文件"""
    config_file = tmp_path / "netbird_config.yaml"
    config_content = f"""
api_key: {TEST_CONFIG['api_key']}
api_url: {TEST_CONFIG['api_url']}
timeout: {TEST_CONFIG['timeout']}
"""
    config_file.write_text(config_content)
    return config_file
```

### 2. `fixtures/api_responses.py` - 真实 API 响应数据

**基于 manage_groups.py 的实际响应**:
```python
"""
NetBird API 真实响应数据

基于实际 API 调用收集的响应格式，确保测试数据的真实性
"""

API_RESPONSES = {
    "peers": {
        "single": {
            "id": "d2itv26kurdc73fqb0cg",
            "name": "ab14ca4f6a9a",
            "ip": "100.109.212.184",
            "connected": True,
            "lastSeen": "2025-08-21T10:30:00Z",
            "os": "linux",
            "version": "0.24.0",
            "hostname": "test-host",
            "sshEnabled": False,
            "groups": [
                {
                    "id": "d1n8evekurdc73cnnpig",
                    "name": "All",
                    "peers_count": 8,
                    "resources_count": 0
                },
                {
                    "id": "d2itruukurdc73fqb0bg", 
                    "name": "Quarantine",
                    "peers_count": 1,
                    "resources_count": 0
                }
            ],
            "userId": "user123",
            "approvalRequired": False,
            "loginExpirationEnabled": False
        },
        
        "list": [
            {
                "id": "d2itv26kurdc73fqb0cg",
                "name": "ab14ca4f6a9a",
                "ip": "100.109.212.184",
                "connected": True,
                "groups": [{"id": "d1n8evekurdc73cnnpig", "name": "All"}]
            },
            {
                "id": "d1n8muukurdc73cnnpkg",
                "name": "dev-container",
                "ip": "100.109.88.220", 
                "connected": True,
                "groups": [{"id": "d1n8evekurdc73cnnpig", "name": "All"}]
            }
        ]
    },
    
    "groups": {
        "single": {
            "id": "d1n8evekurdc73cnnpig",
            "name": "All",
            "peersCount": 8,
            "peers": [
                {"id": "d1n8muukurdc73cnnpkg", "name": "dev-container", "ip": "100.109.88.220"},
                {"id": "d1n8n4ukurdc73cnnpl0", "name": "dev-container-2", "ip": "100.109.134.118"}
            ],
            "resourcesCount": 0
        },
        
        "list": [
            {
                "id": "d1n8evekurdc73cnnpig", 
                "name": "All",
                "peersCount": 8,
                "peers": [
                    {"id": "peer1", "name": "dev-container"},
                    {"id": "peer2", "name": "MacBook-Pro"}
                ]
            },
            {
                "id": "d1n8ohukurdc73cnnplg",
                "name": "PC", 
                "peersCount": 3,
                "peers": [
                    {"id": "peer3", "name": "MacBook-Pro-2.local"},
                    {"id": "peer4", "name": "MBA-m4.local"}
                ]
            }
        ]
    },
    
    "policies": {
        "single": {
            "id": "d1n8evekurdc73cnnpj0",
            "name": "Default",
            "description": "This is a default rule that allows connections between all the resources",
            "enabled": False,
            "rules": [
                {
                    "id": "d1n8evekurdc73cnnpj0",
                    "name": "Default", 
                    "description": "This is a default rule that allows connections between all the resources",
                    "enabled": False,
                    "sources": [
                        {
                            "id": "d1n8evekurdc73cnnpig",
                            "name": "All",
                            "peers_count": 8,
                            "resources_count": 0
                        }
                    ],
                    "destinations": [
                        {
                            "id": "d1n8evekurdc73cnnpig", 
                            "name": "All",
                            "peers_count": 8,
                            "resources_count": 0
                        }
                    ],
                    "bidirectional": True,
                    "protocol": "all",
                    "ports": [],
                    "action": "accept"
                }
            ],
            "sourcePostureChecks": []
        },
        
        "list": [
            {
                "id": "d1n8evekurdc73cnnpj0",
                "name": "Default", 
                "enabled": False,
                "rules": [{"id": "rule1", "name": "Default", "enabled": False}]
            },
            {
                "id": "d2iu28ekurdc73fqb0d0",
                "name": "Super",
                "enabled": True,
                "rules": [{"id": "rule2", "name": "Super", "enabled": True}]
            }
        ]
    },
    
    "errors": {
        "401_unauthorized": {
            "message": "token invalid",
            "code": 401
        },
        "404_not_found": {
            "message": "resource not found", 
            "code": 404
        },
        "400_validation_error": {
            "message": "validation failed",
            "code": 400,
            "details": ["field 'name' is required"]
        }
    }
}

# HTTP 状态码响应映射
HTTP_RESPONSES = {
    200: API_RESPONSES,
    401: API_RESPONSES["errors"]["401_unauthorized"],
    404: API_RESPONSES["errors"]["404_not_found"], 
    400: API_RESPONSES["errors"]["400_validation_error"],
}
```

### 3. `fixtures/factories.py` - 数据工厂

**使用 Factory Boy 模式**:
```python
"""
测试数据工厂

使用 Factory Boy 模式生成测试数据，支持灵活的数据创建
"""
import factory
import random
from datetime import datetime, timedelta
from ipaddress import IPv4Address
from typing import List, Dict, Any

class PeerFactory:
    """Peer 数据工厂"""
    
    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """创建 Peer 数据"""
        defaults = {
            "id": f"peer_{factory.Faker('uuid4')}",
            "name": factory.Faker('hostname'),
            "ip": str(IPv4Address(f"100.109.{random.randint(1, 255)}.{random.randint(1, 255)}")),
            "connected": factory.Faker('boolean'),
            "lastSeen": datetime.utcnow().isoformat() + "Z",
            "os": factory.Faker('random_element', elements=['linux', 'windows', 'darwin']),
            "version": "0.24.0",
            "hostname": factory.Faker('hostname'),
            "sshEnabled": False,
            "groups": [],
            "userId": f"user_{factory.Faker('uuid4')}",
            "approvalRequired": False,
            "loginExpirationEnabled": False
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_list(count: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """创建 Peer 列表"""
        return [PeerFactory.create(**kwargs) for _ in range(count)]
    
    @staticmethod
    def create_connected(**kwargs) -> Dict[str, Any]:
        """创建已连接的 Peer"""
        return PeerFactory.create(connected=True, **kwargs)
    
    @staticmethod
    def create_with_groups(group_refs: List[Dict], **kwargs) -> Dict[str, Any]:
        """创建带组的 Peer"""
        return PeerFactory.create(groups=group_refs, **kwargs)

class GroupFactory:
    """Group 数据工厂"""
    
    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """创建 Group 数据"""
        defaults = {
            "id": f"group_{factory.Faker('uuid4')}",
            "name": factory.Faker('company'),
            "peersCount": 0,
            "peers": [],
            "resourcesCount": 0
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_list(count: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """创建 Group 列表"""
        return [GroupFactory.create(**kwargs) for _ in range(count)]
    
    @staticmethod  
    def create_with_peers(peer_refs: List[Dict], **kwargs) -> Dict[str, Any]:
        """创建带成员的 Group"""
        return GroupFactory.create(
            peers=peer_refs,
            peersCount=len(peer_refs),
            **kwargs
        )
    
    @staticmethod
    def create_all_group(**kwargs) -> Dict[str, Any]:
        """创建 'All' 特殊组"""
        return GroupFactory.create(name="All", **kwargs)

class PolicyFactory:
    """Policy 数据工厂"""
    
    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """创建 Policy 数据"""
        defaults = {
            "id": f"policy_{factory.Faker('uuid4')}",
            "name": factory.Faker('company'),
            "description": factory.Faker('sentence'),
            "enabled": True,
            "rules": [],
            "sourcePostureChecks": []
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_rule(**kwargs) -> Dict[str, Any]:
        """创建 Policy Rule 数据"""
        defaults = {
            "id": f"rule_{factory.Faker('uuid4')}",
            "name": factory.Faker('word'),
            "description": factory.Faker('sentence'),
            "enabled": True,
            "sources": [],
            "destinations": [],
            "bidirectional": True,
            "protocol": "all",
            "ports": [],
            "action": "accept"
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_with_rules(rules: List[Dict], **kwargs) -> Dict[str, Any]:
        """创建带规则的 Policy"""
        return PolicyFactory.create(rules=rules, **kwargs)

# 工厂助手函数
def create_peer_group_relationship():
    """创建 Peer 和 Group 的关联关系"""
    group = GroupFactory.create_all_group()
    peers = PeerFactory.create_list(3)
    
    # 为 peers 添加 group 引用
    group_ref = {"id": group["id"], "name": group["name"]}
    for peer in peers:
        peer["groups"] = [group_ref]
    
    # 为 group 添加 peer 引用
    peer_refs = [{"id": p["id"], "name": p["name"], "ip": p["ip"]} for p in peers]
    group["peers"] = peer_refs
    group["peersCount"] = len(peers)
    
    return {"group": group, "peers": peers}

def create_policy_with_groups(source_groups: List[Dict], dest_groups: List[Dict]):
    """创建带组引用的策略"""
    rule = PolicyFactory.create_rule(
        sources=source_groups,
        destinations=dest_groups
    )
    return PolicyFactory.create_with_rules([rule])
```

### 4. `fixtures/mock_server.py` - HTTP Mock 服务器

**功能要求**:
```python
"""
NetBird API Mock 服务器

使用 respx 模拟 NetBird API 响应
"""
import re
from typing import Dict, Any
import respx
from httpx import Response

from .api_responses import API_RESPONSES, HTTP_RESPONSES

def setup_mock_server(mock: respx.MockRouter) -> respx.MockRouter:
    """设置 NetBird API Mock 服务器"""
    
    base_url = "https://api.test.netbird.io/api"
    
    # Peers endpoints
    mock.get(f"{base_url}/peers").mock(
        return_value=Response(200, json=API_RESPONSES["peers"]["list"])
    )
    
    mock.get(re.compile(f"{base_url}/peers/.*")).mock(
        return_value=Response(200, json=API_RESPONSES["peers"]["single"])
    )
    
    mock.post(f"{base_url}/peers").mock(
        return_value=Response(201, json=API_RESPONSES["peers"]["single"])
    )
    
    mock.put(re.compile(f"{base_url}/peers/.*")).mock(
        return_value=Response(200, json=API_RESPONSES["peers"]["single"])
    )
    
    mock.delete(re.compile(f"{base_url}/peers/.*")).mock(
        return_value=Response(204)
    )
    
    # Groups endpoints
    mock.get(f"{base_url}/groups").mock(
        return_value=Response(200, json=API_RESPONSES["groups"]["list"])
    )
    
    mock.get(re.compile(f"{base_url}/groups/.*")).mock(
        return_value=Response(200, json=API_RESPONSES["groups"]["single"])
    )
    
    mock.post(f"{base_url}/groups").mock(
        return_value=Response(201, json=API_RESPONSES["groups"]["single"])
    )
    
    mock.put(re.compile(f"{base_url}/groups/.*")).mock(
        return_value=Response(200, json=API_RESPONSES["groups"]["single"])
    )
    
    mock.delete(re.compile(f"{base_url}/groups/.*")).mock(
        return_value=Response(204)
    )
    
    # Policies endpoints  
    mock.get(f"{base_url}/policies").mock(
        return_value=Response(200, json=API_RESPONSES["policies"]["list"])
    )
    
    mock.get(re.compile(f"{base_url}/policies/.*")).mock(
        return_value=Response(200, json=API_RESPONSES["policies"]["single"])
    )
    
    mock.post(f"{base_url}/policies").mock(
        return_value=Response(201, json=API_RESPONSES["policies"]["single"])
    )
    
    mock.put(re.compile(f"{base_url}/policies/.*")).mock(
        return_value=Response(200, json=API_RESPONSES["policies"]["single"])
    )
    
    mock.delete(re.compile(f"{base_url}/policies/.*")).mock(
        return_value=Response(204)
    )
    
    # Error scenarios
    setup_error_scenarios(mock, base_url)
    
    return mock

def setup_error_scenarios(mock: respx.MockRouter, base_url: str):
    """设置错误场景模拟"""
    
    # 401 Unauthorized
    mock.get(f"{base_url}/unauthorized").mock(
        return_value=Response(401, json=HTTP_RESPONSES[401])
    )
    
    # 404 Not Found
    mock.get(f"{base_url}/not-found").mock(
        return_value=Response(404, json=HTTP_RESPONSES[404])
    )
    
    # 400 Validation Error
    mock.post(f"{base_url}/validation-error").mock(
        return_value=Response(400, json=HTTP_RESPONSES[400])
    )
    
    # 500 Server Error
    mock.get(f"{base_url}/server-error").mock(
        return_value=Response(500, json={"message": "Internal server error", "code": 500})
    )
    
    # Network timeout simulation
    mock.get(f"{base_url}/timeout").mock(
        side_effect=Exception("Timeout")
    )

def setup_dynamic_mock_server(mock: respx.MockRouter, responses: Dict[str, Any]) -> respx.MockRouter:
    """设置动态 Mock 服务器，支持自定义响应"""
    
    base_url = "https://api.test.netbird.io/api"
    
    for endpoint, response_data in responses.items():
        status_code = response_data.get("status", 200)
        json_data = response_data.get("json", {})
        
        mock.get(f"{base_url}/{endpoint}").mock(
            return_value=Response(status_code, json=json_data)
        )
    
    return mock
```

### 5. `tests/utils.py` - 测试工具函数

**功能要求**:
```python
"""
测试工具函数

提供通用的测试辅助功能
"""
import json
import asyncio
from typing import Dict, Any, Callable, Optional
from pathlib import Path
from unittest.mock import Mock, AsyncMock

def load_test_data(filename: str) -> Dict[str, Any]:
    """加载测试数据文件"""
    data_dir = Path(__file__).parent / "fixtures" / "data"
    file_path = data_dir / filename
    
    with open(file_path) as f:
        if filename.endswith('.json'):
            return json.load(f)
        elif filename.endswith('.yaml'):
            import yaml
            return yaml.safe_load(f)
    
    raise ValueError(f"Unsupported file format: {filename}")

def assert_model_fields(model_instance, expected_data: Dict[str, Any], exclude_fields: Optional[List[str]] = None):
    """断言模型字段值"""
    exclude_fields = exclude_fields or []
    
    for field, expected_value in expected_data.items():
        if field in exclude_fields:
            continue
            
        actual_value = getattr(model_instance, field, None)
        assert actual_value == expected_value, f"Field {field}: expected {expected_value}, got {actual_value}"

def mock_async_method(return_value: Any = None, side_effect: Any = None) -> AsyncMock:
    """创建异步方法 Mock"""
    mock = AsyncMock()
    
    if return_value is not None:
        mock.return_value = return_value
    
    if side_effect is not None:
        mock.side_effect = side_effect
    
    return mock

def run_async_test(coro):
    """运行异步测试函数"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

class MockResponse:
    """Mock HTTP 响应"""
    
    def __init__(self, json_data: Dict[str, Any], status_code: int = 200):
        self.json_data = json_data
        self.status_code = status_code
        self.headers = {"content-type": "application/json"}
        self.reason_phrase = "OK" if status_code == 200 else "Error"
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

def create_mock_client(responses: Dict[str, MockResponse]) -> Mock:
    """创建 Mock HTTP 客户端"""
    mock_client = Mock()
    
    for endpoint, response in responses.items():
        method_name = f"get_{endpoint.replace('/', '_')}"
        setattr(mock_client, method_name, Mock(return_value=response))
    
    return mock_client

# 测试装饰器
def skip_if_no_api_key(test_func: Callable) -> Callable:
    """如果没有 API key 则跳过测试"""
    import os
    import pytest
    
    def wrapper(*args, **kwargs):
        if not os.getenv('NETBIRD_API_KEY'):
            pytest.skip("No NETBIRD_API_KEY provided for live API tests")
        return test_func(*args, **kwargs)
    
    return wrapper

def parametrize_with_factories(factories: Dict[str, Callable]) -> Callable:
    """使用工厂进行参数化测试的装饰器"""
    import pytest
    
    def decorator(test_func: Callable) -> Callable:
        factory_names = list(factories.keys())
        factory_funcs = list(factories.values())
        
        return pytest.mark.parametrize(
            "factory_name,factory_func", 
            zip(factory_names, factory_funcs),
            ids=factory_names
        )(test_func)
    
    return decorator
```

## 📦 依赖安装

在开始之前需要安装额外的测试依赖：

```bash
cd /Users/kun/Code/chromes/netbird/pynetbird
uv add --dev pytest-asyncio pytest-mock pytest-cov respx factory-boy freezegun python-dateutil pyyaml
```

## 🧪 测试用例示例

创建一些示例测试验证框架功能：

```python
# tests/unit/test_factories.py
def test_peer_factory(peer_factory):
    """测试 Peer 工厂"""
    peer = peer_factory.create(name="test-peer")
    assert peer["name"] == "test-peer"
    assert "id" in peer
    assert "ip" in peer

def test_mock_server(netbird_mock_server, sync_client):
    """测试 Mock 服务器"""
    response = sync_client.get("/peers")
    assert len(response) > 0
```

## ✅ 完成标准

1. **框架完整性**:
   - 所有测试工具正常工作
   - Mock 服务器响应真实 API 格式
   - 数据工厂能生成有效测试数据

2. **可扩展性**:
   - 为 Task 2 (模型测试) 做好准备
   - 为 Task 3 (管理器测试) 预留结构
   - 支持集成测试和端到端测试

3. **测试覆盖**:
   - 验证现有 Task 1 代码的测试覆盖率
   - 所有 fixture 和工厂正常工作
   - Mock 服务器正确模拟 API 行为

## 🚀 开始开发

1. **安装依赖**: 使用上面的 `uv add` 命令
2. **实现顺序**: 按文件依赖顺序实现
3. **验证方法**: 运行测试确保框架工作正常

## 🤝 交付标准

- [ ] 所有测试框架文件实现完毕
- [ ] 基础测试通过，覆盖率报告正常
- [ ] Mock 服务器能正确响应 API 调用
- [ ] 数据工厂和 fixture 正常工作
- [ ] 为后续任务预留的测试结构就绪

**预计完成时间**: 2-3 小时  
**并行级别**: 可与 Task 2 同时进行

这个测试框架将为整个项目的质量保障奠定坚实基础！