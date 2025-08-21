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
    with respx.mock(assert_all_called=False) as respx_mock:
        yield respx_mock

@pytest.fixture
def netbird_mock_server(mock_http_responses):
    """NetBird API Mock 服务器"""
    from .fixtures.mock_server import setup_mock_server
    return setup_mock_server(mock_http_responses)

# 数据工厂 fixtures
@pytest.fixture
def peer_factory():
    """Peer 数据工厂"""
    from .fixtures.factories import PeerFactory
    return PeerFactory

@pytest.fixture 
def group_factory():
    """Group 数据工厂"""
    from .fixtures.factories import GroupFactory
    return GroupFactory

@pytest.fixture
def policy_factory():
    """Policy 数据工厂"""
    from .fixtures.factories import PolicyFactory
    return PolicyFactory

# 测试数据 fixtures
@pytest.fixture
def sample_peer_data():
    """示例 Peer 数据"""
    from .fixtures.api_responses import API_RESPONSES
    return API_RESPONSES["peers"]["single"]

@pytest.fixture
def sample_peers_list():
    """示例 Peers 列表"""
    from .fixtures.api_responses import API_RESPONSES
    return API_RESPONSES["peers"]["list"]

@pytest.fixture
def sample_group_data():
    """示例 Group 数据"""
    from .fixtures.api_responses import API_RESPONSES
    return API_RESPONSES["groups"]["single"]

@pytest.fixture
def sample_policy_data():
    """示例 Policy 数据"""
    from .fixtures.api_responses import API_RESPONSES
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

# Mock HTTP 客户端 fixture
@pytest.fixture
def mock_httpx_client(monkeypatch):
    """Mock httpx 客户端"""
    mock_client = Mock(spec=httpx.Client)
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "success"}
    mock_response.raise_for_status = Mock()
    mock_client.request.return_value = mock_response
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    mock_client.put.return_value = mock_response
    mock_client.delete.return_value = mock_response
    
    monkeypatch.setattr("httpx.Client", Mock(return_value=mock_client))
    return mock_client

# 异步 Mock HTTP 客户端 fixture
@pytest.fixture
def mock_async_httpx_client(monkeypatch):
    """Mock 异步 httpx 客户端"""
    from unittest.mock import AsyncMock
    
    mock_client = Mock(spec=httpx.AsyncClient)
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "success"}
    mock_response.raise_for_status = Mock()
    
    mock_client.request = AsyncMock(return_value=mock_response)
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.put = AsyncMock(return_value=mock_response)
    mock_client.delete = AsyncMock(return_value=mock_response)
    mock_client.aclose = AsyncMock()
    
    monkeypatch.setattr("httpx.AsyncClient", Mock(return_value=mock_client))
    return mock_client