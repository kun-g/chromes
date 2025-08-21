# NetBird Groups Management

管理 NetBird Peers 和 Groups 的 Python 脚本，支持将指定的两个 peer 放到一个 Group，并按情况创建 Policy 让 Group 内部互通。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

设置环境变量：

```bash
export NETBIRD_API_KEY="your-api-key-here"
export NETBIRD_API_URL="https://api.netbird.io"  # 可选，默认为 https://api.netbird.io
```

获取 API Key: https://app.netbird.io/settings/personal-access-token

## 使用方法

### 列出所有 peers
```bash
python manage_groups.py list-peers
```

### 列出所有 groups
```bash
python manage_groups.py list-groups
```

### 列出所有 policies
```bash
python manage_groups.py list-policies
```

### 创建新的 group
```bash
python manage_groups.py create-group -n "dev-team" -d "Development team group"
```

### 将两个 peers 添加到 group
```bash
python manage_groups.py add-peers-to-group -p "peer-id-1,peer-id-2" -g "dev-team" -c
```

参数说明：
- `-p, --peer-ids`: Peer IDs (逗号分隔)
- `-g, --group-name`: Group 名称
- `-c, --create-group`: 如果 group 不存在则自动创建

### 创建 policy 让 group 内部互通
```bash
python manage_groups.py create-policy -g "dev-team" -n "dev-team-policy" -d "Allow dev team internal communication"
```

参数说明：
- `-g, --group-name`: Group 名称
- `-n, --policy-name`: Policy 名称
- `-d, --description`: Policy 描述
- `-b, --bidirectional`: 双向通信 (默认: True)

## 完整示例

1. 创建一个名为 "test-group" 的组，并将两个 peers 添加到该组：

```bash
python manage_groups.py add-peers-to-group -p "peer-abc123,peer-def456" -g "test-group" -c
```

2. 为该组创建允许内部通信的策略：

```bash
python manage_groups.py create-policy -g "test-group" -n "test-group-internal" -d "Allow internal communication for test group"
```

3. 检查结果：

```bash
python manage_groups.py list-groups
python manage_groups.py list-policies
```

## 功能特性

- ✅ 列出所有 peers、groups 和 policies
- ✅ 创建新的 group
- ✅ 将多个 peers 添加到 group（自动去重）
- ✅ 自动创建不存在的 group
- ✅ 创建或更新 policy 以允许 group 内部互通
- ✅ 支持双向通信配置
- ✅ 错误处理和友好的中文提示

## API 权限要求

确保你的 NetBird API Key 具有以下权限：
- 读取 peers
- 管理 groups
- 管理 policies