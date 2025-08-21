# Task 1: PyNetBird 基础架构实现

## 🎯 任务目标
实现 PyNetBird 包的基础架构层，包括 HTTP 通信、异常处理、配置管理和工具函数。这是整个项目的基础，其他模块都将依赖这些组件。

## 📋 任务清单
- [ ] 实现 `base.py` - HTTP 通信基础类
- [ ] 实现 `exceptions.py` - 自定义异常体系
- [ ] 实现 `config.py` - 配置管理系统
- [ ] 实现 `utils.py` - 工具函数集合
- [ ] 创建基础测试验证功能

## 🏗️ 技术要求

### 依赖库
- `httpx` - HTTP 客户端 (支持同步/异步)
- `pydantic` - 数据验证
- `python-dotenv` - 环境变量加载
- `typing` - 类型提示

### Python 版本
- 兼容 Python 3.8+
- 使用现代 Python 特性 (类型提示、dataclasses 等)

## 📁 文件结构
```
pynetbird/
├── base.py           # HTTP 通信基础类
├── exceptions.py     # 异常定义
├── config.py        # 配置管理
└── utils.py         # 工具函数
```

## 🔧 详细实现要求

### 1. `base.py` - HTTP 通信基础类

**核心类**: `BaseClient`

**功能要求**:
```python
class BaseClient:
    """HTTP 通信基础类，支持同步和异步"""
    
    def __init__(self, api_key: str, api_url: str = "https://api.netbird.io", timeout: int = 30):
        # 初始化 httpx 客户端
        # 设置认证头: "Authorization: Token {api_key}"
        # 设置超时和重试策略
    
    def request(self, method: str, endpoint: str, **kwargs) -> dict:
        """同步请求方法"""
        # 发送 HTTP 请求
        # 处理响应状态码
        # 返回 JSON 数据或抛出异常
    
    async def async_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """异步请求方法"""
        # 异步版本的请求方法
    
    def get(self, endpoint: str, **kwargs) -> dict:
        """GET 请求"""
    
    def post(self, endpoint: str, data: dict = None, **kwargs) -> dict:
        """POST 请求"""
    
    def put(self, endpoint: str, data: dict = None, **kwargs) -> dict:
        """PUT 请求"""
    
    def delete(self, endpoint: str, **kwargs) -> dict:
        """DELETE 请求"""
```

**错误处理**:
- HTTP 状态码映射到自定义异常
- 网络错误处理
- 超时处理
- JSON 解析错误处理

### 2. `exceptions.py` - 异常体系

**异常层次结构**:
```python
class NetBirdException(Exception):
    """基础异常类"""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response

class AuthenticationError(NetBirdException):
    """401 认证失败"""
    pass

class ResourceNotFoundError(NetBirdException):
    """404 资源不存在"""
    pass

class ValidationError(NetBirdException):
    """400 请求参数错误"""
    pass

class RateLimitError(NetBirdException):
    """429 请求频率限制"""
    pass

class ServerError(NetBirdException):
    """5xx 服务器错误"""
    pass

class NetworkError(NetBirdException):
    """网络连接错误"""
    pass
```

**功能要求**:
- 提供状态码到异常的映射函数
- 异常信息格式化
- 支持嵌套异常原因

### 3. `config.py` - 配置管理

**配置类**: `NetBirdConfig`

**功能要求**:
```python
@dataclass
class NetBirdConfig:
    """NetBird 客户端配置"""
    api_key: Optional[str] = None
    api_url: str = "https://api.netbird.io"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    @classmethod
    def from_env(cls) -> 'NetBirdConfig':
        """从环境变量加载配置"""
        # 读取 NETBIRD_API_KEY, NETBIRD_API_URL 等
    
    @classmethod
    def from_file(cls, config_path: str) -> 'NetBirdConfig':
        """从配置文件加载"""
        # 支持 YAML/JSON 格式
    
    def validate(self) -> None:
        """验证配置有效性"""
        # 检查必需字段
        # 验证 URL 格式
```

**配置优先级**:
1. 直接传递的参数
2. 环境变量
3. 配置文件
4. 默认值

### 4. `utils.py` - 工具函数

**功能要求**:
```python
def format_endpoint(endpoint: str) -> str:
    """格式化 API 端点"""
    # 确保以 /api 开头
    # 处理重复的斜杠

def parse_datetime(date_str: str) -> datetime:
    """解析 API 返回的时间字符串"""
    # 支持多种时间格式

def mask_sensitive_data(data: dict, fields: List[str] = None) -> dict:
    """脱敏敏感数据用于日志"""
    # 隐藏 API key、密码等敏感信息

def validate_id(resource_id: str, resource_type: str = "resource") -> str:
    """验证资源 ID 格式"""
    # 检查 ID 格式是否有效

def chunk_list(items: List, chunk_size: int) -> Iterator[List]:
    """将列表分块，用于批量操作"""
    # 生成器模式，节省内存
```

## 🧪 测试要求

创建简单的测试验证基础功能:

```python
# test_base.py
def test_base_client_init():
    """测试客户端初始化"""
    
def test_http_requests():
    """测试 HTTP 请求方法 (使用 mock)"""
    
def test_error_handling():
    """测试错误处理"""

# test_config.py  
def test_config_from_env():
    """测试从环境变量加载配置"""
    
def test_config_validation():
    """测试配置验证"""
```

## 📚 参考资料

### NetBird API 认证格式
```python
headers = {
    "Authorization": f"Token {api_key}",  # 注意是 Token 不是 Bearer
    "Content-Type": "application/json"
}
```

### API 端点格式
- 基础 URL: `https://api.netbird.io`
- 端点格式: `/api/peers`, `/api/groups`, `/api/policies`

### 现有代码参考
查看 `manage_groups.py` 中的实现:
- `_make_request` 方法
- 错误处理逻辑
- API 认证方式

## ✅ 完成标准

1. **代码质量**:
   - 类型提示覆盖率 100%
   - Docstring 完整
   - 遵循 PEP 8 规范

2. **功能测试**:
   - 基础 HTTP 请求正常工作
   - 错误处理正确
   - 配置加载成功

3. **集成测试**:
   - 能够成功连接 NetBird API
   - 认证流程正常
   - 异常映射正确

## 🚀 开始开发

1. **设置环境**:
   ```bash
   cd /Users/kun/Code/chromes/netbird
   # 确保已安装 httpx, pydantic, python-dotenv
   ```

2. **创建文件**:
   ```bash
   touch pynetbird/base.py
   touch pynetbird/exceptions.py  
   touch pynetbird/config.py
   touch pynetbird/utils.py
   ```

3. **实现顺序建议**:
   - 先实现 `exceptions.py` (被其他模块依赖)
   - 再实现 `config.py` (配置管理)
   - 然后 `utils.py` (工具函数)
   - 最后 `base.py` (HTTP 客户端)

4. **测试验证**:
   每完成一个文件就编写简单测试验证功能

## 🤝 交付标准

提交时请包含:
- [ ] 所有 4 个文件的完整实现
- [ ] 简单的测试脚本验证功能
- [ ] 代码中的关键设计决策说明
- [ ] 遇到的问题和解决方案

预计完成时间: 1-2 小时

开始吧！有任何问题随时询问。