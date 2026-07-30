# 🐳 Chat Hanbao - 飞牛 NAS FPK 部署指南

## 📋 前置条件

### 1. Docker Hub 账号（必须）

飞牛 NAS 需要从 Docker Hub 拉取预构建镜像，你需要：

1. 注册 [Docker Hub](https://hub.docker.com/) 账号
2. 创建 4 个公开仓库：
   - `chat-hanbao-postgres`
   - `chat-hanbao-redis`
   - `chat-hanbao-backend`
   - `chat-hanbao-frontend`

### 2. GitHub 账号（必须）

用于 GitHub Actions 自动构建镜像，无需本地 Docker。

### 3. fnpack 工具（必须）

从 [飞牛开发者中心](https://developer.fnnas.com/) 下载 `fnpack` 工具。

---

## 🚀 完整流程（无需本地 Docker）

### 第一步：推送到 GitHub

```bash
# 在 GitHub 上创建新仓库 chat-hanbao
# 然后本地初始化并推送
cd F:\work\chat-hanbao
git init
git add .
git commit -m "init: Chat Hanbao v1.0.0"
git branch -M main
git remote add origin https://github.com/yijiuzero/chat-hanbao.git
git push -u origin main
```

### 第二步：配置 GitHub Secrets

进入 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| 名称 | 说明 |
|------|------|
| `DOCKERHUB_USERNAME` | Docker Hub 用户名（yijiuzero） |
| `DOCKERHUB_TOKEN` | Docker Hub 访问令牌（不是密码） |

**获取 Docker Hub Token：**
Docker Hub → Account Settings → Security → New Access Token

### 第三步：触发自动构建

```bash
# 推送 tag 触发构建
git tag v1.0.0
git push origin v1.0.0
```

或者手动触发：GitHub 仓库 → **Actions** → **Build & Push Docker Images** → **Run workflow**

### 第四步：验证镜像

构建完成后，在 Docker Hub 检查 4 个镜像是否已上传：
- https://hub.docker.com/r/yijiuzero/chat-hanbao-postgres
- https://hub.docker.com/r/yijiuzero/chat-hanbao-redis
- https://hub.docker.com/r/yijiuzero/chat-hanbao-backend
- https://hub.docker.com/r/yijiuzero/chat-hanbao-frontend

### 第五步：打包 FPK

```bash
# 确保 fnpack 在 PATH 中
export PATH=$PATH:/path/to/fpnas-tools

# 运行打包脚本
./scripts/build_fpk.sh 1.0.0
```

产物：`build/chat-hanbao-1.0.0.fpk`

### 第六步：安装到飞牛 NAS

1. 将 `.fpk` 文件上传到飞牛 NAS 任意目录
2. 飞牛桌面 → **应用中心** → 右上角 **设置** → **手动安装应用**
3. 选择 `chat-hanbao-1.0.0.fpk`
4. 安装完成后，桌面会出现 Chat Hanbao 图标
5. 点击图标在浏览器中打开

---

## 📁 FPK 目录结构

```
fpk/
├── manifest                     # 应用元信息
├── app/
│   ├── docker/
│   │   └── docker-compose.yaml  # Docker 编排
│   └── ui/
│       ├── config               # 桌面入口配置
│       └── images/
│           ├── icon.png         # 64x64 图标
│           └── icon_256.png     # 256x256 图标
├── cmd/
│   └── main                     # 生命周期控制脚本
├── config/
│   ├── privilege                # 权限配置（root）
│   └── resource                 # 资源配置（docker-project）
└── wizard/
    └── install                  # 安装向导配置
```

---

## ⚠️ 注意事项

1. **ARM 设备**：飞牛当前仅支持 x86_64 第三方应用，ARM 设备（如 RK3588）暂不支持
2. **镜像标签**：compose 中的镜像 tag 必须与 Docker Hub 推送的完全一致
3. **数据备份**：飞牛托管数据在 `${TRIM_PKGVAR}/data`，升级不会丢数据
4. **端口冲突**：如果默认端口被占用，可在飞牛应用详情中修改端口映射

---

## 🔧 故障排查

| 问题 | 解决方案 |
|------|----------|
| 安装时报 manifest unknown | 检查 compose 中镜像 tag 是否与 Docker Hub 一致 |
| 安装后无法启动 | SSH 进飞牛，运行 `docker logs chat-hanbao-backend` 查看日志 |
| 端口冲突 | 在飞牛应用详情中修改端口映射 |
| 镜像拉取失败 | 检查 Docker Hub 网络连接，或尝试重新推送镜像 |
| GitHub Actions 失败 | 检查 Actions 日志，确认 Secrets 配置正确 |
