# hanbao（函包）· 飞牛 FPK 应用信息清单

> 本文件为 FPK 打包前的元信息草稿。标注 `[飞牛规范待定]` 的字段需等飞牛官方
> 应用中心打包规范确定后补全。

## 已确定信息
- 应用 ID（package id）：`hanbao`（需符合飞牛命名规则，[飞牛规范待定]）
- 展示名称：函包（hanbao）
- 类型：AI 聊天机器人（本地部署 / 家庭单用户）
- 版本：0.1.0（首发，[飞牛规范待定] 版本号规则）
- 一句话简介：飞牛 NAS 上的私人 AI 聊天助手（微信 + OneBot 渠道）
- 详细描述：基于 Hanbao v2.0.1 (Apache-2.0) 减法式二次开发，本地运行、数据自控、仅依赖云端 OpenAI 兼容 API。
- 开源协议：Apache-2.0
- 上游：基于 Hanbao v2.0.1 (Apache-2.0)，保留上游版权与 NOTICE（合规）
- 端口：8088（Web Console，已默认开启登录认证 I-007，LAN 暴露安全）
- 架构：linux/amd64
- 镜像体积（当前）：~1.93GB（后续 venv 瘦身目标 ≤800MB）
- 渠道：微信 + OneBot（QQ / 钉钉 / 飞书 / Telegram 已关闭）

## 待飞牛规范确认字段 [飞牛规范待定]
- FPK 包目录结构 / manifest 文件名与 schema
- 图标规格（尺寸、格式、命名）
- 权限声明（端口、存储目录、设备权限）
- 镜像打包方式：FPK 内含镜像 tar 由飞牛自动 load，或引用飞牛托管仓库
- 安装向导可否收集管理员密码并注入 `HANBAO_AUTH_USERNAME` / `HANBAO_AUTH_PASSWORD`（I-007 闭环，消除首启抢注窗口）
- 数据存储目录（建议挂载 NAS 持久卷，配置与对话持久化）
- 更新机制：FPK 覆盖更新 / 飞牛应用中心版本管理

## 合规备忘（上架必带）
- `LICENSE` / `NOTICE` / `CHANGES-FROM-UPSTREAM.md` 已随镜像分发（I-002）
- 依赖树无 GPL / AGPL / SSPL 强传染（审计闭合，commit `3da3ae4`）
- 展示名已改 hanbao / 函包；包名 `hanbao` 全量改名排独立子阶段（暂不影响上架合规）
- 商标提示：应用名 / 图标 / 描述勿用 Hanbao / AgentScope / Qwen / 通义，勿暗示官方背书
