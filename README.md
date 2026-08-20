# hanbao（函包）

> **hanbao 基于 [Hanbao](https://github.com/agentscope-ai/QwenPaw) v2.0.1（Apache-2.0）修改而来。**
> 原始版权归 **The Hanbao Authors** 所有。
> 修改内容详见 [CHANGES-FROM-UPSTREAM.md](docs/CHANGES-FROM-UPSTREAM.md)。

一个轻量的个人 AI 聊天应用，专为**飞牛 NAS** 打造。

---

## 这是什么

hanbao 是一个运行在你自己的 NAS 上的 AI 助手。打开浏览器就能聊天，数据完全本地化，不需要第三方云服务。

## 特性

- 🏠 **本地数据主权** — 聊天记录、配置、技能全部存在你的 NAS 上
- 🌐 **Web 聊天** — 浏览器打开就能用，无需安装客户端
- ☁️ **云模型支持** — 兼容 OpenAI API 格式（DeepSeek / Kimi / 智谱 / 硅基流动等）
- 🇨🇳 **中英双语** — 默认中文，支持中英文界面切换
- 📦 **FPK 应用包** — 目标是一键安装到飞牛 NAS 应用中心

## 快速开始

### 飞牛 NAS 一键安装（推荐）
1. 从飞牛应用中心安装 `hanbao` 应用（`.fpk` 包，镜像已内置离线分发，无需外部仓库）
2. 安装向导设置管理员账号密码（默认开启登录认证，消除局域网抢注窗口）
3. 浏览器打开 `http://<飞牛IP>:8088` 即可聊天

### 手动 Docker 部署（开发者）
镜像需自行构建，不提供外部 registry：
```bash
docker build -t hanbao:latest .
docker run -d --name hanbao -p 8088:8088 -v hanbao-working:/app/working hanbao:latest
```

> 💡 **Web Console 默认开启登录认证**：首次打开页面会进入注册页，请设置管理员密码
> （环境变量 `HANBAO_AUTH_ENABLED=false` 可显式关闭，不推荐）。

## 项目状态

| 阶段 | 状态 |
|---|---|
| 品牌改造 & 中英双语 | ✅ |
| 删减定制 | ✅ |
| 镜像瘦身 | ✅（1.78GB） |
| 界面品牌化 | ✅（水墨古典基调 + 全站去 qwenpaw 味：token 全量化/空态/欢迎语 hanbao 化，2026-08-20） |
| FPK 打包 | ✅（脚手架已按官方规范建，待 fnOS 实测） |
| 飞牛上架 | ⬜ |

## 许可

hanbao 基于 QwenPaw v2.0.1（fork）并移植 v2.1.0 安全修复，遵循 [Apache License 2.0](LICENSE)。

原始项目：[QwenPaw](https://github.com/agentscope-ai/QwenPaw) — Copyright 2025 The QwenPaw Authors
