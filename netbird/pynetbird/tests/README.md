# PyNetBird 测试框架

## 📋 概览

这是 PyNetBird 项目的完整测试框架，为 Task 6-1 实现。该框架支持单元测试、集成测试和端到端测试，提供了丰富的测试工具和模拟功能。

## 🏗️ 目录结构

```
pynetbird/tests/
├── __init__.py              # 测试包初始化
├── conftest.py             # pytest 配置和全局 fixtures
├── utils.py                # 测试工具函数
├── test_framework.py       # 框架验证测试
├── README.md              # 本文档
├── 
├── fixtures/               # 测试数据和 Mock
│   ├── __init__.py
│   ├── api_responses.py    # 真实 API 响应数据
│   ├── factories.py        # 数据工厂
│   └── mock_server.py      # Mock 服务器配置
├── 
├── unit/                   # 单元测试
│   ├── __init__.py
│   ├── test_base.py       # BaseClient 测试
│   ├── test_config.py     # 配置测试
│   ├── test_exceptions.py # 异常测试
│   ├── test_utils_module.py # 工具函数测试
│   ├── test_basic_functionality.py # 基础功能测试
│   ├── test_models/       # 模型测试 (Task 2)
│   │   ├── __init__.py
│   │   ├── test_peer.py
│   │   ├── test_group.py
│   │   └── test_policy.py
│   └── test_managers/     # 管理器单元测试 (Task 3)
│       ├── __init__.py
│       ├── test_peer_manager.py
│       ├── test_group_manager.py
│       └── test_policy_manager.py
├── 
├── integration/            # 集成测试
│   ├── __init__.py
│   ├── test_client.py     # HTTP 客户端集成测试
│   └── test_managers/     # 管理器集成测试 (Task 3)
│       ├── __init__.py
│       ├── test_peer_manager.py
│       ├── test_group_manager.py
│       └── test_policy_manager.py
└── 
└── e2e/                   # 端到端测试
    ├── __init__.py
    └── test_real_api.py   # 真实 API 测试 (可选)
```

## 🔧 核心功能

### 1. 测试配置 (conftest.py)

提供全局的 pytest 配置和 fixtures：

- `test_config`: 测试环境配置
- `sync_client`, `async_client`: HTTP 客户端
- `mock_http_responses`: HTTP Mock 装置
- `netbird_mock_server`: NetBird API Mock 服务器
- `peer_factory`, `group_factory`, `policy_factory`: 数据工厂 fixtures
- `sample_*_data`: 示例数据 fixtures

### 2. 数据工厂 (fixtures/factories.py)

提供灵活的测试数据生成：

```python
from pynetbird.tests.fixtures.factories import PeerFactory, GroupFactory

# 创建单个 Peer
peer = PeerFactory.create(name="test-peer")

# 创建 Peer 列表
peers = PeerFactory.create_list(count=3)

# 创建特定类型的 Peer
connected_peer = PeerFactory.create_connected()
linux_peer = PeerFactory.create_linux_peer()

# 创建关联关系
relationship = create_peer_group_relationship(peer_count=3)
```

### 3. API 响应数据 (fixtures/api_responses.py)

基于真实 API 响应的测试数据：

```python
from pynetbird.tests.fixtures.api_responses import API_RESPONSES

# 获取示例数据
peer_data = API_RESPONSES["peers"]["single"]
peers_list = API_RESPONSES["peers"]["list"]
error_response = API_RESPONSES["errors"]["404_not_found"]
```

### 4. Mock 服务器 (fixtures/mock_server.py)

提供多种 Mock 服务器设置：

```python
# 基础 Mock 服务器
setup_mock_server(mock_router)

# 动态 Mock 服务器
setup_dynamic_mock_server(mock_router, custom_responses)

# 有状态 Mock 服务器
state = setup_stateful_mock_server(mock_router)

# Mock 服务器构建器
builder = MockServerBuilder()
builder.add_route("GET", "peers", peer_data)
       .add_error_route("error", 404, "Not Found")
       .build(mock_router)
```

### 5. 测试工具 (utils.py)

提供丰富的测试辅助功能：

```python
from pynetbird.tests.utils import (
    MockResponse, assert_dict_subset, TestDataBuilder,
    mock_async_method, TempEnvVars
)

# Mock HTTP 响应
response = MockResponse({"id": "test"}, status_code=200)

# 断言字典子集
assert_dict_subset(actual_data, expected_subset)

# 测试数据构建器
data = (TestDataBuilder()
        .with_peer(peer_data)
        .with_group(group_data)
        .build())

# 临时环境变量
with TempEnvVars(NETBIRD_API_KEY="test_key"):
    # 测试代码
    pass
```

## 🚀 使用方法

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest pynetbird/tests/test_framework.py

# 运行特定测试类
uv run pytest pynetbird/tests/test_framework.py::TestFactories

# 运行单元测试
uv run pytest pynetbird/tests/unit/

# 运行集成测试
uv run pytest pynetbird/tests/integration/

# 带覆盖率报告
uv run pytest --cov=pynetbird --cov-report=html

# 详细输出
uv run pytest -v
```

### 编写测试

#### 单元测试示例

```python
import pytest
from pynetbird.tests.fixtures.factories import PeerFactory

def test_peer_creation(peer_factory):
    """测试 Peer 创建"""
    peer = peer_factory.create(name="test-peer")
    assert peer["name"] == "test-peer"
    assert "id" in peer

def test_with_mock_server(netbird_mock_server, sync_client):
    """使用 Mock 服务器的测试"""
    response = sync_client.get("/api/peers")
    assert response.status_code == 200
```

#### 集成测试示例

```python
import pytest
from unittest.mock import Mock

@pytest.mark.integration
def test_peer_manager_integration(peer_factory, mock_http_responses):
    """测试 PeerManager 集成"""
    # 设置 Mock 响应
    peer_data = peer_factory.create()
    # ... 测试逻辑
```

#### 异步测试示例

```python
import pytest

@pytest.mark.asyncio
async def test_async_operation(async_client):
    """测试异步操作"""
    result = await async_client.some_async_method()
    assert result is not None
```

## 🎯 测试标记

项目使用以下测试标记：

- `@pytest.mark.slow`: 标记慢速测试
- `@pytest.mark.integration`: 标记集成测试
- `@pytest.mark.e2e`: 标记端到端测试
- `@pytest.mark.real_api`: 标记需要真实 API 的测试

```bash
# 跳过慢速测试
uv run pytest -m "not slow"

# 只运行集成测试
uv run pytest -m "integration"

# 跳过真实 API 测试
uv run pytest -m "not real_api"
```

## 📊 覆盖率报告

测试框架配置了全面的覆盖率报告：

- **终端报告**: 显示缺失的行
- **HTML 报告**: 生成到 `htmlcov/` 目录
- **XML 报告**: 生成 `coverage.xml` 文件

```bash
# 查看 HTML 覆盖率报告
open htmlcov/index.html
```

## 🔮 为未来任务准备

### Task 2: 数据模型测试

框架已为模型测试准备了结构：

- `tests/unit/test_models/test_peer.py`
- `tests/unit/test_models/test_group.py`
- `tests/unit/test_models/test_policy.py`

### Task 3: 资源管理器测试

框架已为管理器测试准备了结构：

- 单元测试: `tests/unit/test_managers/`
- 集成测试: `tests/integration/test_managers/`

## 📈 当前状态

- ✅ **测试依赖**: 已安装所有必要的测试库
- ✅ **框架结构**: 完整的目录结构已建立
- ✅ **配置文件**: pytest 配置完成
- ✅ **数据工厂**: 可生成各种测试数据
- ✅ **Mock 服务器**: 支持多种 Mock 场景
- ✅ **工具函数**: 丰富的测试辅助功能
- ✅ **验证测试**: 框架功能已验证
- ✅ **覆盖率报告**: 配置完成

## 🤝 贡献指南

1. **新增测试**: 在适当的目录下创建测试文件
2. **使用工厂**: 优先使用数据工厂生成测试数据
3. **Mock 外部依赖**: 使用提供的 Mock 工具
4. **标记测试**: 为测试添加适当的标记
5. **覆盖率**: 确保新代码有适当的测试覆盖

## 🎉 总结

该测试框架为 PyNetBird 项目提供了：

- **完整的测试结构**: 单元、集成、端到端测试
- **强大的Mock功能**: HTTP Mock 和数据 Mock
- **灵活的数据生成**: 基于工厂模式的测试数据
- **真实的响应数据**: 基于实际 API 响应
- **丰富的工具函数**: 简化测试编写
- **为未来准备**: Task 2 和 Task 3 的测试结构已就绪

框架已经过验证，可以立即支持后续的开发和测试工作。