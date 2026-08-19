# hanbao（函包）· 飞牛 FPK 应用信息清单

> 本文件为 FPK 打包前的元信息草稿。标注 `[飞牛规范待定]` 的字段需等飞牛官方
> 应用中心打包规范确定后补全。

## 已确定信息
- 应用 ID（package id）：`hanbao`（需符合飞牛命名规则，[飞牛规范待定]）
- 展示名称：函包（hanbao）
- 类型：AI 聊天机器人（本地部署 / 家庭单用户）
- 版本：0.1.0（首发，[飞牛规范待定] 版本号规则）
- 一句话简介：飞牛 NAS 上的私人 AI 聊天助手（微信 + OneBot 渠道）
- 详细描述：fork 自 QwenPaw v2.1.0 (Apache-2.0) 减法式二次开发（品牌/包名已全量改名 hanbao，见 docs/CHANGES-FROM-UPSTREAM.md 阶段4.5），本地运行、数据自控、仅依赖云端 OpenAI 兼容 API。
- 开源协议：Apache-2.0
- 上游：基于 Hanbao v2.0.1 (Apache-2.0)，保留上游版权与 NOTICE（合规）
- 端口：8088（Web Console，已默认开启登录认证 I-007，LAN 暴露安全）
- 架构：linux/amd64
- 镜像体积（当前）：~1.78GB（venv 瘦身第一刀后；原 800MB 目标经实测评估极难达成，务实线 ≤1.5GB 待拍板）
- 渠道：微信 + OneBot（QQ / 钉钉 / 飞书 / Telegram 已关闭）

## 阶段5 FPK 脚手架进度（2026-08-19 已建 native 形态骨架）
- 形态拍板：**native**（非 docker-project）。镜像随 FPK 内置 tar，`cmd/main` 自己 `docker load` + `compose up`（docker-project 形态下应用中心会在 load 前就 `compose up` 导致 No such image）。
- 已落地文件：`deploy/fpk/manifest`、`cmd/main`、`install_callback`、`wizard`、`app/docker/docker-compose.yaml`、`app/ui/config`、`config/{resource,privilege}`、图标 `ICON.PNG`/`ICON_256.PNG` + `app/ui/images/*`。
- 凭据闭环：wizard 收集 `HANBAO_AUTH_USERNAME`/`HANBAO_AUTH_PASSWORD` → `install_callback` 持久化 `hanbao.env` → `cmd/main` start 时 source 注入容器（接 I-007 默认开认证，首启 `auto_register_from_env` 自动建账号，消除局域网抢注窗口）。

## 待飞牛官方规范核对（schema 级，非设计级）
- `manifest` / `wizard` / `config/resource` / `config/privilege` / `app/ui/config` 的**确切字段名与文件格式**需对照 developer.fnnas.com 官方 spec 校正（当前为 2026-08-19 调研最佳实践猜测，各文件头已标注 ⚠️）。
- 图标规格（尺寸/格式/命名）已按 64×64 + 256×256 生成，待官方确认。
- 数据存储目录：当前 compose 用 named volume（hanbao-data/secrets/backups），是否改用 NAS 持久卷绑定挂载待定。
- 更新机制：FPK 覆盖更新（含新镜像 tar）已设计，飞牛应用中心版本管理字段待规范。
- `fnpack` 打包命令与本地校验需飞牛环境/代理实测。

## 合规备忘（上架必带）
- `LICENSE` / `NOTICE` / `CHANGES-FROM-UPSTREAM.md` 已随镜像分发（I-002）
- 依赖树无 GPL / AGPL / SSPL 强传染（审计闭合，commit `3da3ae4`）
- 展示名已改 hanbao / 函包；包名 `qwenpaw`→`hanbao` 全量改名已于 2026-08-19 落地完成（见 docs/CHANGES-FROM-UPSTREAM.md 阶段4.5，R2 合规零违约）
- 商标提示：应用名 / 图标 / 描述勿用 Hanbao / AgentScope / Qwen / 通义，勿暗示官方背书
