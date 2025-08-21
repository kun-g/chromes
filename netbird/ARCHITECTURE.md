# PyNetBird 架构设计文档

## 项目概述
PyNetBird 是一个 Python 客户端库，用于与 NetBird API 交互，提供简洁的 API 和 CLI 工具。

## 技术选型
- **HTTP 库**: httpx (支持同步/异步)
- **数据验证**: Pydantic v2
- **CLI**: Click + Rich
- **配置管理**: python-dotenv
- **Python版本**: >=3.8

## 包结构
```
pynetbird/
├── __init__.py
├── client.py           # 同步客户端
├── async_client.py     # 异步客户端
├── base.py            # 基础类和共享逻辑
├── models/
│   ├── __init__.py
│   ├── peer.py        # Peer 数据模型
│   ├── group.py       # Group 数据模型
│   ├── policy.py      # Policy 数据模型
│   └── base.py        # 基础模型类
├── managers/
│   ├── base.py        # 基础管理器
│   ├── peers.py       # Peers 管理器
│   ├── groups.py      # Groups 管理器
│   └── policies.py    # Policies 管理器
├── cli/
│   ├── __init__.py
│   ├── main.py        # CLI 入口
│   ├── commands/      # 各个命令实现
│   └── formatters.py  # 输出格式化
├── exceptions.py      # 自定义异常
├── config.py         # 配置管理
└── utils.py          # 工具函数
```

## API 设计

### 1. 客户端初始化
```python
# 同步客户端
from pynetbird import NetBirdClient

# 方式1: 直接传参
client = NetBirdClient(api_key="xxx", api_url="xxx")

# 方式2: 从环境变量 (NETBIRD_API_KEY, NETBIRD_API_URL)
client = NetBirdClient()

# 方式3: 从配置文件
client = NetBirdClient.from_config("~/.netbird/config.yaml")
```

### 2. 资源管理器 API
```python
# Peers 管理
peers = client.peers.list()                    # 列出所有 peers
peer = client.peers.get("peer_id")            # 获取单个 peer
client.peers.update("peer_id", name="new")    # 更新 peer
client.peers.delete("peer_id")                # 删除 peer

# Groups 管理
groups = client.groups.list()                  # 列出所有 groups
group = client.groups.create(name="dev")      # 创建 group
client.groups.add_peers("group_id", ["p1"])   # 添加 peers 到 group
client.groups.remove_peers("group_id", ["p1"]) # 从 group 移除 peers

# Policies 管理
policies = client.policies.list()              # 列出所有 policies
policy = client.policies.create(...)          # 创建 policy
client.policies.update("policy_id", ...)      # 更新 policy
client.policies.delete("policy_id")           # 删除 policy
```

### 3. 异步 API
```python
from pynetbird import AsyncNetBirdClient

async with AsyncNetBirdClient() as client:
    peers = await client.peers.list()
    # ... 其他异步操作
```

## 数据模型 (Pydantic)

### Peer 模型
```python
class Peer(BaseModel):
    id: str
    name: str
    ip: str
    connected: bool
    last_seen: datetime
    os: str
    version: str
    groups: List[GroupRef]
    ssh_enabled: bool
    user_id: Optional[str]
```

### Group 模型
```python
class Group(BaseModel):
    id: str
    name: str
    peers_count: int
    peers: Optional[List[PeerRef]]
    issued_at: datetime
```

### Policy 模型
```python
class Policy(BaseModel):
    id: str
    name: str
    description: str
    enabled: bool
    rules: List[Rule]
    
class Rule(BaseModel):
    id: str
    name: str
    description: str
    enabled: bool
    sources: List[GroupRef]
    destinations: List[GroupRef]
    bidirectional: bool
    protocol: str
    ports: Optional[List[str]]
    action: str  # "accept" or "drop"
```

## CLI 设计

### 命令结构
```bash
pynetbird [全局选项] <资源> <操作> [选项]
```

### 示例命令
```bash
# Peers 操作
pynetbird peers list
pynetbird peers get <peer-id>
pynetbird peers update <peer-id> --name "new-name"
pynetbird peers delete <peer-id>

# Groups 操作
pynetbird groups list
pynetbird groups create --name "dev-team"
pynetbird groups add-peers <group-id> --peers "peer1,peer2"

# Policies 操作
pynetbird policies list
pynetbird policies create --name "internal" --source "dev" --dest "prod"

# 配置管理
pynetbird config set api_key "xxx"
pynetbird config get api_key
pynetbird config list

# 输出格式
pynetbird peers list --output json
pynetbird peers list --output table
pynetbird peers list --output yaml
```

## 错误处理

### 异常层次结构
```python
NetBirdException
├── AuthenticationError      # 401 认证失败
├── ResourceNotFoundError    # 404 资源不存在
├── ValidationError          # 400 请求参数错误
├── RateLimitError          # 429 请求频率限制
├── ServerError             # 5xx 服务器错误
└── NetworkError            # 网络连接错误
```

## 配置优先级
1. 代码中直接传递的参数
2. 环境变量 (NETBIRD_API_KEY, NETBIRD_API_URL)
3. 配置文件 (~/.netbird/config.yaml)
4. 默认值

## 实现阶段

### Phase 1 - 核心功能 (当前)
- [x] 基础项目结构
- [ ] HTTP 客户端基础类
- [ ] Pydantic 数据模型
- [ ] 同步客户端实现
- [ ] Peers/Groups/Policies 管理器
- [ ] 基本错误处理

### Phase 2 - CLI 和测试
- [ ] Click CLI 框架
- [ ] 基础命令实现
- [ ] 输出格式化 (table/json/yaml)
- [ ] 单元测试
- [ ] 集成测试

### Phase 3 - 异步和高级功能
- [ ] 异步客户端实现
- [ ] 批量操作 API
- [ ] 缓存机制
- [ ] 重试机制
- [ ] WebSocket 支持 (如果 API 支持)

## 并行开发计划

### Session 1: 基础框架
- base.py: HTTP 通信基础类
- exceptions.py: 异常定义
- config.py: 配置管理

### Session 2: 数据模型
- models/base.py: 基础模型
- models/peer.py: Peer 模型
- models/group.py: Group 模型
- models/policy.py: Policy 模型

### Session 3: 管理器实现
- managers/base.py: 基础管理器
- managers/peers.py: Peers 管理
- managers/groups.py: Groups 管理
- managers/policies.py: Policies 管理

### Session 4: 客户端集成
- client.py: 同步客户端
- async_client.py: 异步客户端

### Session 5: CLI 工具
- cli/main.py: CLI 入口
- cli/commands/*: 各命令实现
- cli/formatters.py: 输出格式化

### Session 6: 测试和文档
- tests/*: 单元测试和集成测试
- examples/*: 使用示例
- README.md: 项目文档