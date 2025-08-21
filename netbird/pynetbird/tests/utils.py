"""
测试工具函数

提供通用的测试辅助功能
"""
import json
import asyncio
from typing import Dict, Any, Callable, Optional, List
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import yaml

def load_test_data(filename: str) -> Dict[str, Any]:
    """加载测试数据文件"""
    data_dir = Path(__file__).parent / "fixtures" / "data"
    file_path = data_dir / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Test data file not found: {filename}")
    
    with open(file_path) as f:
        if filename.endswith('.json'):
            return json.load(f)
        elif filename.endswith(('.yaml', '.yml')):
            return yaml.safe_load(f)
    
    raise ValueError(f"Unsupported file format: {filename}")

def assert_model_fields(
    model_instance,
    expected_data: Dict[str, Any],
    exclude_fields: Optional[List[str]] = None
):
    """断言模型字段值"""
    exclude_fields = exclude_fields or []
    
    for field, expected_value in expected_data.items():
        if field in exclude_fields:
            continue
            
        actual_value = getattr(model_instance, field, None)
        assert actual_value == expected_value, (
            f"Field {field}: expected {expected_value}, got {actual_value}"
        )

def assert_dict_subset(
    actual: Dict[str, Any],
    expected_subset: Dict[str, Any],
    path: str = ""
) -> None:
    """断言字典包含指定的子集"""
    for key, expected_value in expected_subset.items():
        current_path = f"{path}.{key}" if path else key
        
        assert key in actual, f"Missing key: {current_path}"
        
        actual_value = actual[key]
        
        if isinstance(expected_value, dict) and isinstance(actual_value, dict):
            assert_dict_subset(actual_value, expected_value, current_path)
        else:
            assert actual_value == expected_value, (
                f"At {current_path}: expected {expected_value}, got {actual_value}"
            )

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
    
    def __init__(
        self,
        json_data: Dict[str, Any],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None
    ):
        self.json_data = json_data
        self.status_code = status_code
        self.headers = headers or {"content-type": "application/json"}
        self.reason_phrase = self._get_reason_phrase(status_code)
    
    def json(self):
        """返回 JSON 数据"""
        return self.json_data
    
    def raise_for_status(self):
        """检查 HTTP 状态"""
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}: {self.reason_phrase}")
    
    @property
    def text(self):
        """返回文本响应"""
        return json.dumps(self.json_data)
    
    @property
    def content(self):
        """返回字节内容"""
        return self.text.encode('utf-8')
    
    @staticmethod
    def _get_reason_phrase(status_code: int) -> str:
        """获取状态码对应的说明"""
        status_codes = {
            200: "OK",
            201: "Created",
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            409: "Conflict",
            429: "Too Many Requests",
            500: "Internal Server Error",
            503: "Service Unavailable"
        }
        return status_codes.get(status_code, "Unknown")

def create_mock_client(responses: Dict[str, MockResponse]) -> Mock:
    """创建 Mock HTTP 客户端"""
    mock_client = Mock()
    
    # 创建方法映射
    method_responses = {}
    
    for endpoint, response in responses.items():
        # 支持格式：'GET:/peers', '/peers' (默认GET)
        if ':' in endpoint:
            method, path = endpoint.split(':', 1)
        else:
            method, path = 'GET', endpoint
        
        method = method.upper()
        
        # 为每个方法创建 Mock
        if method not in method_responses:
            method_responses[method] = {}
        
        method_responses[method][path] = response
    
    # 设置客户端方法
    def create_method_mock(method: str):
        def method_func(url, **kwargs):
            # 从 URL 中提取路径
            path = url.split('/api')[-1] if '/api' in url else url
            if path in method_responses.get(method, {}):
                return method_responses[method][path]
            # 默认返回 404
            return MockResponse({"message": "Not Found"}, 404)
        return Mock(side_effect=method_func)
    
    mock_client.get = create_method_mock('GET')
    mock_client.post = create_method_mock('POST')
    mock_client.put = create_method_mock('PUT')
    mock_client.delete = create_method_mock('DELETE')
    mock_client.patch = create_method_mock('PATCH')
    
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

def time_test(test_func: Callable) -> Callable:
    """测试执行时间装饰器"""
    import time
    import functools
    
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = test_func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"\nTest {test_func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"\nTest {test_func.__name__} failed after {execution_time:.3f}s")
            raise
    
    return wrapper

class TestDataBuilder:
    """测试数据构建器"""
    
    def __init__(self):
        self.data = {}
    
    def with_peer(self, peer_data: Dict[str, Any]) -> "TestDataBuilder":
        """添加 peer 数据"""
        if "peers" not in self.data:
            self.data["peers"] = []
        self.data["peers"].append(peer_data)
        return self
    
    def with_group(self, group_data: Dict[str, Any]) -> "TestDataBuilder":
        """添加 group 数据"""
        if "groups" not in self.data:
            self.data["groups"] = []
        self.data["groups"].append(group_data)
        return self
    
    def with_policy(self, policy_data: Dict[str, Any]) -> "TestDataBuilder":
        """添加 policy 数据"""
        if "policies" not in self.data:
            self.data["policies"] = []
        self.data["policies"].append(policy_data)
        return self
    
    def build(self) -> Dict[str, Any]:
        """构建测试数据"""
        return self.data.copy()

def cleanup_test_data(test_data: Dict[str, Any]) -> None:
    """清理测试数据"""
    # 这里可以添加清理逻辑，例如删除临时文件等
    pass

def compare_api_responses(
    actual: Dict[str, Any],
    expected: Dict[str, Any],
    ignore_fields: Optional[List[str]] = None
) -> List[str]:
    """比较 API 响应，返回差异列表"""
    ignore_fields = ignore_fields or ['timestamp', 'lastSeen', 'id']
    differences = []
    
    def _compare_recursive(actual_val, expected_val, path=""):
        if isinstance(expected_val, dict) and isinstance(actual_val, dict):
            for key, value in expected_val.items():
                if key in ignore_fields:
                    continue
                    
                current_path = f"{path}.{key}" if path else key
                
                if key not in actual_val:
                    differences.append(f"Missing field: {current_path}")
                else:
                    _compare_recursive(actual_val[key], value, current_path)
        
        elif isinstance(expected_val, list) and isinstance(actual_val, list):
            if len(actual_val) != len(expected_val):
                differences.append(f"List length mismatch at {path}: {len(actual_val)} vs {len(expected_val)}")
            else:
                for i, (a_item, e_item) in enumerate(zip(actual_val, expected_val)):
                    _compare_recursive(a_item, e_item, f"{path}[{i}]")
        
        elif actual_val != expected_val:
            differences.append(f"Value mismatch at {path}: {actual_val} vs {expected_val}")
    
    _compare_recursive(actual, expected)
    return differences

def setup_test_logging():
    """设置测试日志"""
    import logging
    
    # 为测试设置日志级别
    logging.getLogger('pynetbird').setLevel(logging.DEBUG)
    
    # 创建测试日志处理器
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger('pynetbird')
    logger.addHandler(handler)
    
    return logger

# Context manager for temporary environment variables
class TempEnvVars:
    """临时环境变量上下文管理器"""
    
    def __init__(self, **env_vars):
        self.env_vars = env_vars
        self.original_values = {}
    
    def __enter__(self):
        import os
        
        for key, value in self.env_vars.items():
            self.original_values[key] = os.environ.get(key)
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = str(value)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import os
        
        for key, original_value in self.original_values.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value