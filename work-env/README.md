# Work Environment with OAuth2 Authentication

这是一个带有 OAuth2 认证的 Web 终端环境，基于 ttyd 构建，通过 nginx 和 oauth2-proxy 提供安全访问。

## 快速开始

### 1. 配置 OAuth2 认证

编辑 `.env` 文件，填入你的 OAuth2 配置。以下是常见 OIDC 提供商的配置方法：

#### Google OAuth2

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 进入 "APIs & Services" > "Credentials"
4. 点击 "Create Credentials" > "OAuth client ID"
5. 选择 "Web application"
6. 添加授权重定向 URI: `https://devbox.localhost:8443/oauth2/callback`
7. 获取 Client ID 和 Client Secret

```bash
OAUTH2_PROXY_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
OAUTH2_PROXY_CLIENT_SECRET=your-google-client-secret
OAUTH2_PROXY_OIDC_ISSUER_URL=https://accounts.google.com
```

#### GitHub OAuth2

1. 访问 [GitHub Developer Settings](https://github.com/settings/developers)
2. 点击 "New OAuth App"
3. 填写应用信息：
   - Application name: 你的应用名称
   - Homepage URL: `https://devbox.localhost:8443`
   - Authorization callback URL: `https://devbox.localhost:8443/oauth2/callback`
4. 创建后获取 Client ID 和 Client Secret

```bash
OAUTH2_PROXY_CLIENT_ID=your-github-client-id
OAUTH2_PROXY_CLIENT_SECRET=your-github-client-secret
OAUTH2_PROXY_OIDC_ISSUER_URL=https://github.com/login/oauth
```

#### Azure AD / Microsoft Entra ID

1. 访问 [Azure Portal](https://portal.azure.com/)
2. 进入 "Azure Active Directory" > "App registrations"
3. 点击 "New registration"
4. 填写应用信息：
   - Name: 你的应用名称
   - Redirect URI: `https://devbox.localhost:8443/oauth2/callback`
5. 创建后记录 Application (client) ID
6. 在 "Certificates & secrets" 创建新的 client secret
7. 记录 Directory (tenant) ID

```bash
OAUTH2_PROXY_CLIENT_ID=your-azure-client-id
OAUTH2_PROXY_CLIENT_SECRET=your-azure-client-secret
OAUTH2_PROXY_OIDC_ISSUER_URL=https://login.microsoftonline.com/{your-tenant-id}/v2.0
```

### 2. 生成 Cookie Secret

Cookie Secret 必须是 32 字节的 base64 编码字符串：

```bash
# 生成随机密钥
openssl rand -base64 32

# 或者使用 Python
python -c "import secrets; import base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

将生成的字符串填入 `.env` 文件：
```bash
OAUTH2_PROXY_COOKIE_SECRET=生成的32字节base64字符串
```

### 3. 设置 ttyd 密码

修改 `.env` 文件中的 `TTYD_PASSWORD`，这是作为双重保障的基础认证密码：

```bash
TTYD_PASSWORD=your-secure-password
```

### 4. 配置邮箱域名限制（可选）

如果需要限制只允许特定域名的邮箱访问，编辑 `oauth2-proxy.cfg`，添加：

```ini
email_domains = ["your-domain.com", "another-domain.com"]
```

或者允许所有邮箱（默认）：
```ini
email_domains = ["*"]
```

### 5. 启动服务

```bash
# 拉取或构建镜像
docker pull ghcr.io/kun-g/chromes-work-env:latest

# 或者本地构建
docker build -t ghcr.io/kun-g/chromes-work-env:latest -f dockerfile .

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 6. 访问服务

1. 添加 hosts 记录（如果使用 devbox.localhost）：
   ```bash
   echo "127.0.0.1 devbox.localhost" | sudo tee -a /etc/hosts
   ```

2. 访问 https://devbox.localhost:8443
3. 首次访问会跳转到 OAuth2 提供商进行认证
4. 认证成功后会要求输入 ttyd 密码（双重认证）

## 服务架构

```
用户 → nginx (443/SSL) → oauth2-proxy (认证) → ttyd (Web终端)
```

- **nginx**: 反向代理，处理 SSL 和 WebSocket
- **oauth2-proxy**: OAuth2/OIDC 认证网关
- **ttyd**: Web 终端服务
- **work-env 镜像**: 包含 kubectl、AWS CLI、Amazon Q、NetBird 等开发工具

## NetBird VPN 配置（可选）

NetBird 提供安全的 WireGuard 基础的 VPN 连接，容器启动时会自动连接到 NetBird 网络。

### 配置步骤

1. 从 NetBird 管理界面获取 Setup Key
2. 编辑 `.env` 文件，添加 Setup Key：
   ```bash
   NETBIRD_KEY=your-setup-key-here
   ```
3. 重启容器，NetBird 会自动连接

### NetBird 命令

在容器内可以使用以下命令管理 NetBird：

```bash
# 查看连接状态
netbird status

# 手动连接（如果自动连接失败）
netbird up --setup-key YOUR_KEY

# 断开连接
netbird down

# 查看路由表
netbird routes list
```

## 故障排查

### OAuth2 Proxy 启动失败

检查 `.env` 文件中的必需变量是否都已设置：
- OAUTH2_PROXY_CLIENT_ID
- OAUTH2_PROXY_CLIENT_SECRET
- OAUTH2_PROXY_COOKIE_SECRET
- OAUTH2_PROXY_OIDC_ISSUER_URL

### nginx 无法连接到 oauth2-proxy

确保所有服务都在同一个 Docker 网络中，检查 `docker-compose.yml` 中的网络配置。

### SSL 证书问题

默认使用自签名证书，浏览器会显示警告。生产环境请替换为有效的 SSL 证书：
1. 修改 `nginx.conf` 中的证书路径
2. 挂载证书文件到容器

## 安全建议

1. **生产环境必须使用有效的 SSL 证书**
2. **定期更新 Cookie Secret**
3. **使用强密码作为 ttyd 密码**
4. **限制 OAuth2 邮箱域名**
5. **定期更新镜像以获取安全补丁**

## 自定义配置

### 修改端口

编辑 `docker-compose.yml`：
```yaml
nginx:
  ports:
    - "你的端口:443"
```

### 添加更多工具

编辑 `dockerfile` 添加需要的工具，然后重新构建镜像。

### 持久化数据

默认将 `./data` 目录挂载到容器的 `/home/dev`，你的工作文件会保存在这里。