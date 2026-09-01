# hanbao（函包）

> **hanbao 基于 [QwenPaw](https://github.com/agentscope-ai/QwenPaw) v2.0.1（Apache-2.0）修改而来。**
> 原始版权归 **The QwenPaw Authors** 所有。
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
- 🧠 **记忆 & 档案面板** — 控制台可视化浏览 / 单条删除 / 纠正 agent 记忆，展示来源标签 `[user_stated]` / `[AI_inferred]`，改口冲突旧版标 `[已废弃]`，不破坏记忆写路径
- 📡 **渠道健康监控** — 微信 / QQ / 钉钉 / 飞书 / Telegram 的在线状态、最后心跳、重连次数一览；断线主动自动重连（不止收消息重试），凭据脱敏不外泄
- 📚 **家庭本地知识库（RAG）** — 索引本地文档 / 相册 / 账单，对话中可检索并引用；纯本地 BM25、数据不出 NAS、零新第三方依赖
- 🔗 **飞牛生态联动** — 影视库 / 文件 / 下载联动（仅本地调 fnOS API），失败优雅降级

## 快速开始

### 飞牛 NAS 一键安装（推荐）
1. 从飞牛应用中心安装 `hanbao` 应用（`.fpk` 包，镜像已内置离线分发，无需外部仓库）
2. 安装向导设置管理员账号密码（默认开启登录认证，消除局域网抢注窗口）
3. 浏览器打开 `http://<飞牛IP>:8088` 即可聊天

### 手动 Docker 部署（开发者）
镜像需自行构建，不提供外部 registry：
```bash
docker build -t hanbao:latest .
docker run -d --name hanbao -p 8088:8088 -v hanbao-data:/app/working -v hanbao-secrets:/app/working.secret -v hanbao-backups:/app/working.backups hanbao:latest
```

> 💡 **Web Console 默认开启登录认证**：首次打开页面会进入注册页，请设置管理员密码
> （环境变量 `HANBAO_AUTH_ENABLED=false` 可显式关闭，不推荐）。

## 项目状态

| 阶段 | 状态 |
|---|---|
| 品牌改造 & 中英双语 | ✅ |
| 删减定制 | ✅ |
| 镜像瘦身 | ✅（1.23GB） |
| 界面品牌化 | ✅（水墨古典基调 + 全站去 qwenpaw 味 + 两轮实质美化：登录页意境/聊天气泡/会话项/页眉，2026-08-24 已重建验收） |
| 频道精简 | ✅（砍 10 留 8：微信/钉钉/飞书/QQ/企微/小忆/iMessage/Console） |
| 桌面端 | ✅（整条线已砍除，纯 Web 控制台） |
| FPK 打包 | ✅（`fnpack build` 出 `hanbao.fpk`，native 形态，离线镜像内置，2026-08-27 真机验证通过） |
| P0/P1 家庭助手能力 | ✅（记忆&档案面板 / 渠道健康监控 / 本地知识库 RAG / 飞牛生态联动，2026-09-01 实现 + 构建 + 部署验证通过） |
| 飞牛上架 | 🟡 进行中（下一步：提交飞牛应用中心审核） |

## 许可

hanbao 基于 QwenPaw v2.0.1（fork）并移植 v2.1.0 安全修复，遵循 [Apache License 2.0](LICENSE)。

原始项目：[QwenPaw](https://github.com/agentscope-ai/QwenPaw) — Copyright 2025 The QwenPaw Authors
