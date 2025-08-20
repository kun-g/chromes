# GitHub Actions Docker 构建配置

本目录包含用于自动构建和推送 Docker 镜像的 GitHub Actions 工作流。

## 包含的工作流

### 1. docker-build.yml (默认)
- **推送到**: GitHub Container Registry (ghcr.io)
- **触发条件**: 
  - 推送到 main/master 分支
  - 创建标签 (v*)
  - Pull Request
  - 手动触发
- **无需额外配置**: 使用 GitHub 自带的 GITHUB_TOKEN

### 2. docker-build-dockerhub.yml.example
- **推送到**: Docker Hub
- **需要配置的 Secrets**:
  - `DOCKERHUB_USERNAME`: Docker Hub 用户名
  - `DOCKERHUB_TOKEN`: Docker Hub Access Token

## 使用说明

### 使用 GitHub Container Registry (推荐)

1. 工作流已默认配置好，无需额外设置
2. 镜像将推送到: `ghcr.io/<你的用户名>/<仓库名>-work-env`
3. 拉取镜像:
   ```bash
   docker pull ghcr.io/<你的用户名>/<仓库名>-work-env:latest
   ```

### 使用 Docker Hub

1. 将 `docker-build-dockerhub.yml.example` 重命名为 `docker-build-dockerhub.yml`
2. 在 GitHub 仓库设置中添加 Secrets:
   - 进入 Settings → Secrets and variables → Actions
   - 添加 `DOCKERHUB_USERNAME` (你的 Docker Hub 用户名)
   - 添加 `DOCKERHUB_TOKEN` (从 Docker Hub 获取的 Access Token)
3. 删除或禁用 `docker-build.yml` 避免重复构建

## 镜像标签策略

- `latest`: 始终指向 main/master 分支的最新构建
- `main` 或 `master`: 对应分支的最新构建
- `v1.0.0`: 版本标签
- `1.0`: 主版本.次版本标签
- `pr-123`: Pull Request 构建

## 支持的平台

两个工作流都配置了多平台构建:
- linux/amd64 (x86_64)
- linux/arm64 (ARM64/Apple Silicon)

## 手动触发构建

可以在 GitHub Actions 页面手动触发工作流:
1. 进入 Actions 标签页
2. 选择对应的工作流
3. 点击 "Run workflow"
4. 选择分支并运行