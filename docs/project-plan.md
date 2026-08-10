# chat-hanbao（hanbao）项目规划

> 文档版本：v0.1 · 日期：2026-08-07 · 状态：进行中（阶段 1 构建跑通原版已完成）
> 上游基线：QwenPaw v2.0.1（Apache-2.0）

---

## 1. 目标与定位

**hanbao** = 基于 QwenPaw v2.0.1（Apache-2.0）fork 改造的个人 AI 聊天软件。

- 面向**飞牛 NAS（fnOS）**用户；
- 以 **FPK 应用包**形式上架飞牛应用中心，用户一键安装即用；
- **单用户、本地数据主权、Web 聊天为主**。

---

## 2. 范围

### MVP（v1.0）
- 核心：Web Console 聊天（8088），单用户
- 模型：**仅云 API**（安装向导填 Key，默认 DashScope / OpenAI）；不做本地模型（飞牛 NAS 无独显）
- 安全：强制管理员认证（`QWENPAW_AUTH_*`）
- 数据：本地持久化（working / working.secret / working.backups 三 volume）
- 交付：飞牛 FPK 包，应用中心一键安装
- 品牌：hanbao 名称 / 图标 / 前端标题

### 后续（v1.x+）
- Skills 市场接入、记忆增强、本地模型引导优化
- 按需裁剪/增强（如保留 Coding Mode）
- 多架构镜像（x86_64 / arm64）

---

## 3. 技术架构

```
飞牛 NAS (fnOS)
└── hanbao.fpk
    ├── cmd/main            # 生命周期 start/stop/status
    ├── manifest            # 应用元数据
    ├── wizard/install      # 端口 / 管理员账号 / 模型 Key
    ├── config/             # 权限 / 资源声明
    ├── ICON.PNG            # 64x64 + 256x256
    └── app/docker/docker-compose.yaml
        └── service: hanbao   # 基于 QwenPaw 2.0.1 的自建镜像
            ├── ports: 8088
            └── volumes:
                ├── hanbao-data     → /app/working
                ├── hanbao-secrets  → /app/working.secret
                └── hanbao-backups  → /app/working.backups
```

> 初期可直接复用官方 `docker-compose.yml`，仅改镜像名 / 卷名 / 品牌标识，快速跑通；后期再做瘦身镜像。

---

## 4. 改造清单

### 4.1 品牌改造清单（必须，按"用户可见优先"）

| 项 | 真实位置（已核实） | 动作 |
| --- | --- | --- |
| 前端标题 / Logo | `console/`（React 源码） | 改为 hanbao |
| CLI 命令别名 | `pyproject.toml` → `[project.scripts]` 的 `qwenpaw` / `copaw` | 增加 `hanbao` 入口（MVP 可保留原命令，加别名） |
| 数据目录名 | File Guard 默认保护 `~/.qwenpaw.secret/`，working 目录 | 改为 `.hanbao.secret/` |
| 遥测上报 | `qwenpaw init` telemetry | 移除或改向自有服务；默认 opt-out |
| 文档 / Help 链接 | `README.md`、内置 help | 指向 hanbao 文档 |
| 镜像名 | `Dockerfile` / compose | `agentscope/qwenpaw` → 自建 `hanbao` |
| Python 包名 `qwenpaw` | `src/qwenpaw/`、`pyproject.toml` name | **MVP 暂保留**（见可行性分析 §9-6），后续彻底改 |

### 4.2 删减清单（按需求，MVP 建议）

- **多渠道 SDK**（钉钉 / 飞书 / Discord / Telegram / iMessage / QQ 等）：MVP 默认禁用，或裁剪以减重；
- **桌面 App（Tauri）**：MVP 不打包；
- **TUI**：可选保留（轻量）；
- **Coding Mode**：可选保留（依赖 `python-lsp-server` / `ast-grep-cli`，体积大）；
- **遥测上报**：移除。

### 4.3 保留 / 增强

- Web Console 聊天核心
- 多模型 provider 抽象（云 API + 本地）
- Skills / MCP 扩展机制
- 安全四层（Sandbox / Tool Guard / File Guard / Skill Scanner）
- 备份 / 恢复

---

## 5. 飞牛 FPK 打包方案

- **工具**：官方 `fnpack` CLI（`fnpack create hanbao --template docker`）
- **结构**：见架构图
- **cmd/main**：`start` → `docker compose up -d`；`stop` → `down`；`status` → 探活 8088
- **wizard/install**：字段（如 `service_port` / `auth_username` / `auth_password` / `default_provider` / `api_key`）→ 映射为环境变量 / compose 变量
- **环境变量映射**：飞牛 `TRIM_PKGVAR` / `TRIM_PKGHOME` → hanbao 数据卷路径
- **ICON**：64×64 与 256×256

---

## 6. 环境要求

- **开发**：Python 3.11–3.13、Node.js（前端构建）、Docker Desktop（已装）、fnpack CLI
- **运行**：飞牛 NAS（x86_64 / arm64），内存 ≥4GB，支持 Docker
- **上游锁定**：QwenPaw v2.0.1（`agentscope==2.0.4.post1`）

---

## 7. 里程碑（阶段）

| 阶段 | 内容 | 产出 | 状态 |
| --- | --- | --- | --- |
| 阶段0 准备 | 源码就位（本地路径）、建 git 仓库、锁定 v2.0.1 | 工程骨架 | ✅ 已完成 |
| 阶段1 构建跑通原版 | 本机 Docker 完整构建并跑通上游原版 QwenPaw | 镜像 `hanbao:0.0.1-upstream`（4.02GB）+ 8088 可访问 | ✅ 已完成 |
| 阶段2 品牌改造 | 改前端/CLI 别名/数据目录/遥测/文档 | 品牌层替换完成 | ⬜ 待开始 |
| 阶段3 删减定制 | 按清单裁剪，跑通测试 | 裁剪后代码可运行 | ⬜ 待开始 |
| 阶段4 容器化 | 自建瘦身镜像（去 XFCE4/Chromium）+ compose 验证 | 本地 Docker 跑通（体积大幅缩小） | ⬜ 待开始 |
| 阶段5 FPK 打包 | fnpack 结构 + wizard + 环境变量映射 | `.fpk` 产出 | ⬜ 待开始 |
| 阶段6 飞牛实测 | 应用中心手动安装，验证聊天/模型/持久化/认证 | 实测报告 | ⬜ 待开始 |
| 阶段7 上架/发布 | 提交飞牛应用中心 | 上架或私有分发 | ⬜ 待开始 |

---

## 8. 待确认

同《可行性分析》§9。
