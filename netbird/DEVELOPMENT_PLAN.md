# PyNetBird 开发计划

## 开发策略
基于现有 manage_groups.py 的实现经验，将其重构为完整的 Python 包。采用模块化设计，便于并行开发。

## 当前状态
- ✅ 已有工作的 NetBird API 集成代码
- ✅ 了解了正确的 API 认证方式 (Token vs Bearer)
- ✅ 修复了 API 响应结构解析问题
- ✅ 配置了 uv 依赖管理

## 并行开发任务分解

### Task 1: 基础架构 🏗️
**预估时间**: 1-2 小时
**文件清单**:
```
pynetbird/
├── base.py           # HTTP 通信基础类
├── exceptions.py     # 异常定义
├── config.py        # 配置管理
└── utils.py         # 工具函数
```

**核心功能**:
- HTTP 客户端封装 (基于 httpx)
- 统一错误处理
- 配置加载 (环境变量/文件/参数)
- 响应数据预处理

### Task 2: 数据模型 📋
**预估时间**: 2-3 小时
**文件清单**:
```
models/
├── __init__.py
├── base.py          # 基础模型类
├── peer.py         # Peer 数据模型
├── group.py        # Group 数据模型
└── policy.py       # Policy 数据模型
```

**核心功能**:
- Pydantic 模型定义
- 数据验证和类型检查
- 序列化/反序列化
- 模型之间的关系处理

### Task 3: 资源管理器 🔧
**预估时间**: 3-4 小时
**文件清单**:
```
managers/
├── base.py         # 基础管理器
├── peers.py        # Peers 管理
├── groups.py       # Groups 管理
└── policies.py     # Policies 管理
```

**核心功能**:
- CRUD 操作实现
- 批量操作支持
- 参数验证
- 错误处理

### Task 4: 客户端封装 🎯
**预估时间**: 1-2 小时
**文件清单**:
```
├── client.py           # 同步客户端
├── async_client.py     # 异步客户端
└── __init__.py        # 包入口
```

**核心功能**:
- 客户端初始化
- 管理器集成
- 同步/异步接口统一

### Task 5: CLI 工具 💻
**预估时间**: 3-4 小时
**文件清单**:
```
cli/
├── __init__.py
├── main.py            # CLI 入口
├── commands/
│   ├── peers.py      # peers 命令
│   ├── groups.py     # groups 命令
│   ├── policies.py   # policies 命令
│   └── config.py     # config 命令
└── formatters.py     # 输出格式化
```

**核心功能**:
- Click 命令行框架
- 多种输出格式 (table/json/yaml)
- 配置管理命令
- 帮助文档

### Task 6: 测试和文档 🧪
**预估时间**: 2-3 小时
**文件清单**:
```
tests/
├── test_models.py
├── test_managers.py
├── test_client.py
└── test_cli.py
examples/
├── basic_usage.py
├── async_usage.py
└── cli_examples.md
```

**核心功能**:
- 单元测试 (pytest)
- Mock API 响应
- 使用示例
- API 文档

## 开发优先级

### 🚀 Phase 1: MVP (最小可用版本)
1. **Task 1**: 基础架构
2. **Task 2**: 数据模型
3. **Task 3**: 资源管理器
4. **Task 4**: 同步客户端

**目标**: 替换现有 manage_groups.py，提供更好的 API

### 📈 Phase 2: 功能完善
5. **Task 5**: CLI 工具
6. **Task 6**: 测试和文档

**目标**: 提供完整的用户体验

### ⚡ Phase 3: 高级特性
- 异步客户端
- 缓存机制
- 重试策略
- WebSocket 支持

## 代码迁移策略

### 从 manage_groups.py 迁移的代码
```python
# 现有代码中可重用的部分:
1. API 端点定义
2. 认证逻辑 (Token 格式)
3. 错误处理逻辑
4. 数据解析代码
5. CLI 参数定义
```

### 重构要点
```python
# Before (manage_groups.py)
class NetBirdManager:
    def list_peers(self):
        response = self._make_request("GET", "/peers")
        # 直接打印，难以复用

# After (pynetbird)
class PeersManager:
    def list(self) -> List[Peer]:
        response = self._client.get("/peers")
        return [Peer.model_validate(peer) for peer in response]
        # 返回结构化数据，便于复用
```

## 质量保证

### 代码标准
- Type hints 覆盖率 > 90%
- Docstring 覆盖率 100%
- 测试覆盖率 > 85%
- Black 代码格式化
- isort 导入排序

### 测试策略
```python
# 1. 单元测试 - Mock API 响应
@pytest.fixture
def mock_netbird_api():
    with responses.RequestsMock() as rsps:
        yield rsps

# 2. 集成测试 - 真实 API (可选)
@pytest.mark.integration
def test_real_api():
    pass

# 3. CLI 测试 - Click testing
def test_cli_command():
    result = runner.invoke(cli, ['peers', 'list'])
    assert result.exit_code == 0
```

## Session 分工建议

### Session A: 核心基础 (推荐先做)
- Task 1: 基础架构
- Task 2: 数据模型

### Session B: 业务逻辑
- Task 3: 资源管理器
- Task 4: 客户端封装

### Session C: 用户界面
- Task 5: CLI 工具
- Task 6: 测试文档

## 下一步行动
1. **选择一个 Task 开始** (建议从 Task 1 开始)
2. **创建对应的文件结构**
3. **实现核心功能**
4. **编写简单测试验证**
5. **提交代码并记录进度**

你想从哪个 Task 开始？我建议从 Task 1 (基础架构) 开始，因为其他模块都会依赖它。