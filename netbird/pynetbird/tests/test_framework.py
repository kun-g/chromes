"""
测试框架验证

验证测试框架各个组件的功能是否正常工作
"""
import pytest
from unittest.mock import Mock

from .fixtures.factories import (
    PeerFactory, GroupFactory, PolicyFactory,
    create_peer_group_relationship, create_test_environment
)
from .fixtures.api_responses import API_RESPONSES
from .utils import MockResponse, assert_dict_subset, TestDataBuilder


class TestFactories:
    """测试数据工厂功能验证"""
    
    def test_peer_factory_creates_valid_data(self):
        """测试 PeerFactory 创建有效数据"""
        peer = PeerFactory.create(name="test-peer")
        
        assert peer["name"] == "test-peer"
        assert "id" in peer
        assert "ip" in peer
        assert peer["ip"].startswith("100.109.")
        assert isinstance(peer["connected"], bool)
        assert peer["sshEnabled"] is False
        assert isinstance(peer["groups"], list)
    
    def test_peer_factory_creates_list(self):
        """测试 PeerFactory 创建列表"""
        peers = PeerFactory.create_list(count=3)
        
        assert len(peers) == 3
        assert all("id" in peer for peer in peers)
        assert all("ip" in peer for peer in peers)
    
    def test_group_factory_creates_valid_data(self):
        """测试 GroupFactory 创建有效数据"""
        group = GroupFactory.create(name="test-group")
        
        assert group["name"] == "test-group"
        assert "id" in group
        assert group["peersCount"] == 0
        assert isinstance(group["peers"], list)
        assert group["resourcesCount"] == 0
    
    def test_policy_factory_creates_valid_data(self):
        """测试 PolicyFactory 创建有效数据"""
        policy = PolicyFactory.create(name="test-policy")
        
        assert policy["name"] == "test-policy"
        assert "id" in policy
        assert isinstance(policy["enabled"], bool)
        assert isinstance(policy["rules"], list)
    
    def test_create_peer_group_relationship(self):
        """测试创建 Peer-Group 关系"""
        relationship = create_peer_group_relationship(peer_count=2, group_name="TestGroup")
        
        assert "group" in relationship
        assert "peers" in relationship
        assert relationship["group"]["name"] == "TestGroup"
        assert len(relationship["peers"]) == 2
        
        # 验证关联关系
        group = relationship["group"]
        peers = relationship["peers"]
        
        assert group["peersCount"] == 2
        assert len(group["peers"]) == 2
        
        # 每个 peer 应该包含 group 引用
        for peer in peers:
            assert len(peer["groups"]) == 1
            assert peer["groups"][0]["name"] == "TestGroup"
    
    def test_create_test_environment(self):
        """测试创建完整测试环境"""
        env = create_test_environment()
        
        assert "groups" in env
        assert "peers" in env
        assert "policies" in env
        assert "routes" in env
        assert "users" in env
        assert "setup_keys" in env
        
        assert len(env["groups"]) == 3
        assert len(env["peers"]) == 6  # 3 groups * 2 peers per group
        assert len(env["policies"]) == 2
        assert len(env["routes"]) == 2
        assert len(env["users"]) == 3
        assert len(env["setup_keys"]) == 2


class TestApiResponses:
    """测试 API 响应数据"""
    
    def test_api_responses_structure(self):
        """测试 API 响应数据结构"""
        assert "peers" in API_RESPONSES
        assert "groups" in API_RESPONSES
        assert "policies" in API_RESPONSES
        assert "errors" in API_RESPONSES
        
        # 验证 peers 响应
        assert "single" in API_RESPONSES["peers"]
        assert "list" in API_RESPONSES["peers"]
        
        peer = API_RESPONSES["peers"]["single"]
        assert "id" in peer
        assert "name" in peer
        assert "ip" in peer
        assert "connected" in peer
    
    def test_error_responses(self):
        """测试错误响应数据"""
        errors = API_RESPONSES["errors"]
        
        assert "401_unauthorized" in errors
        assert "404_not_found" in errors
        assert "400_validation_error" in errors
        
        auth_error = errors["401_unauthorized"]
        assert auth_error["code"] == 401
        assert "message" in auth_error


class TestMockServer:
    """测试 Mock 服务器功能"""
    
    def test_mock_server_setup(self, netbird_mock_server, sync_client):
        """测试 Mock 服务器设置"""
        # Mock 服务器应该已经通过 fixture 设置好
        assert netbird_mock_server is not None
    
    def test_mock_server_responses(self, mock_http_responses):
        """测试 Mock 服务器响应"""
        # 这里我们可以手动设置一些响应
        from .fixtures.mock_server import setup_dynamic_mock_server
        
        custom_responses = {
            "test": {
                "status": 200,
                "json": {"message": "test response"}
            }
        }
        
        server = setup_dynamic_mock_server(mock_http_responses, custom_responses)
        assert server is not None


class TestUtilityFunctions:
    """测试工具函数"""
    
    def test_mock_response(self):
        """测试 MockResponse 类"""
        response_data = {"id": "test123", "name": "test"}
        mock_response = MockResponse(response_data, status_code=200)
        
        assert mock_response.status_code == 200
        assert mock_response.json() == response_data
        assert mock_response.reason_phrase == "OK"
    
    def test_mock_response_error(self):
        """测试 MockResponse 错误处理"""
        mock_response = MockResponse({}, status_code=404)
        
        assert mock_response.status_code == 404
        assert mock_response.reason_phrase == "Not Found"
        
        with pytest.raises(Exception, match="HTTP 404"):
            mock_response.raise_for_status()
    
    def test_assert_dict_subset(self):
        """测试字典子集断言"""
        actual = {
            "name": "test",
            "config": {"timeout": 30, "retries": 3},
            "extra": "value"
        }
        
        expected_subset = {
            "name": "test",
            "config": {"timeout": 30}
        }
        
        # 这应该成功
        assert_dict_subset(actual, expected_subset)
        
        # 这应该失败
        with pytest.raises(AssertionError):
            assert_dict_subset(actual, {"name": "wrong"})
    
    def test_test_data_builder(self):
        """测试数据构建器"""
        builder = TestDataBuilder()
        
        peer_data = {"id": "peer1", "name": "test-peer"}
        group_data = {"id": "group1", "name": "test-group"}
        
        result = (builder
                 .with_peer(peer_data)
                 .with_group(group_data)
                 .build())
        
        assert "peers" in result
        assert "groups" in result
        assert len(result["peers"]) == 1
        assert len(result["groups"]) == 1
        assert result["peers"][0] == peer_data
        assert result["groups"][0] == group_data


class TestFixtures:
    """测试 pytest fixtures"""
    
    def test_test_config_fixture(self, test_config):
        """测试配置 fixture"""
        assert test_config.api_key == "test_api_key_12345"
        assert test_config.api_url == "https://api.test.netbird.io"
        assert test_config.timeout == 10
    
    def test_sample_data_fixtures(self, sample_peer_data, sample_group_data, sample_policy_data):
        """测试示例数据 fixtures"""
        assert "id" in sample_peer_data
        assert "name" in sample_peer_data
        
        assert "id" in sample_group_data
        assert "name" in sample_group_data
        
        assert "id" in sample_policy_data
        assert "name" in sample_policy_data
    
    def test_factory_fixtures(self, peer_factory, group_factory, policy_factory):
        """测试工厂 fixtures"""
        peer = peer_factory.create()
        group = group_factory.create()
        policy = policy_factory.create()
        
        assert "id" in peer
        assert "id" in group
        assert "id" in policy
    
    def test_temp_config_file(self, temp_config_file):
        """测试临时配置文件 fixture"""
        assert temp_config_file.exists()
        content = temp_config_file.read_text()
        assert "api_key: test_api_key_12345" in content


class TestAsyncSupport:
    """测试异步支持"""
    
    @pytest.mark.asyncio
    async def test_async_fixture(self, async_client):
        """测试异步客户端 fixture"""
        assert async_client is not None
        # 在实际测试中，这里会测试异步操作
        await async_client.aclose()  # 确保资源清理
    
    def test_mock_async_method(self):
        """测试异步方法 Mock"""
        from .utils import mock_async_method
        
        mock = mock_async_method(return_value="test_result")
        assert mock is not None
        # 在实际使用中，这个 mock 会被用于模拟异步方法