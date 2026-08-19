# hanbao（函包）· 飞牛 FPK 应用信息清单

> 本文件为 FPK 打包前的元信息草稿。schema 级字段已于 2026-08-19 对照飞牛官方规范
> （developer.fnnas.com，本机直连可达无需代理）逐条校正；剩余为 `fnpack` 打包与 fnOS 实测验证。

## 已确定信息
- 应用 ID（package id / `appname`）：`hanbao`（小写无空格，符合飞牛规范，官方示例同风格 HelloFnos）
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

## 阶段5 FPK 脚手架进度（2026-08-19 已按官方规范校正）
- 形态拍板：**docker-project**（2026-08-19 拉取 developer.fnnas.com 官方规范后，由首版的 native 改为 docker-project）。官方规范仅以 docker-project 作为容器应用标准路径，`config/resource` 的 `docker-project` 声明即飞牛接管容器生命周期的开关；离线镜像担忧由 `pull_policy: never` + `install_callback` 预载内置 tar 解决（全程不拉外网）。
- 已落地且经官方 schema 校正：`manifest`（INI：`appname`/`display_name`/`service_port` 等）、`wizard/` 目录（install/config/upgrade/uninstall 四个 JSON 数组向导）、`config/resource`（`docker-project` JSON）、`config/privilege`（package 用户 JSON）、`cmd/main`（status-only，容器由飞牛管理）、`install_callback`（预载镜像 tar + 写 `$TRIM_PKGETC/hanbao.env`）、`app/docker/docker-compose.yaml`（env_file 注入凭据 + `$TRIM_PKGVAR` 持久化工作目录）、`app/ui/config`（`.url` 入口）、图标 `ICON.PNG`/`ICON_256.PNG` + `app/ui/images/*`。
- 凭据闭环：wizard 收集 `HANBAO_AUTH_USERNAME`/`HANBAO_AUTH_PASSWORD` → `install_callback` 持久化 `$TRIM_PKGETC/hanbao.env` → compose `env_file` 注入容器（接 I-007 默认开认证，首启 `auto_register_from_env` 自动建账号，消除局域网抢注窗口）。

## 待飞牛实测 / 打包（schema 已校正，剩工程验证）
- ✅ `manifest` / `wizard/` / `config/resource` / `config/privilege` / `app/ui/config` 字段名与格式已于 2026-08-19 对照 developer.fnnas.com 官方规范逐条校正。
- ✅ 图标规格：64×64（`ICON.PNG`）+ 256×256（`ICON_256.PNG`），另 `app/ui/images/icon_64.png` / `icon_256.png` 供桌面入口，符合规范。
- 数据存储目录：compose 挂载 `$TRIM_PKGVAR`（飞牛 @appdata 应用数据卷）→ 容器内 `/app/working`，对话与配置持久化（替代原 named volume）。
- 更新机制：FPK 覆盖更新（含新镜像 tar 落 `app/docker/hanbao-amd64.tar`）已设计；版本管理随 `.fpk` 版本号走。
- ⏳ 剩余工程验证：`fnpack build` 本地打包校验、`fnOS 测试机安装 + 镜像 load + 容器启动 + cmd/main status` 实测（需用户飞牛设备 + `deploy/save-image.sh` 先导出 tar）。
- ⚠️ 一处待 fnOS 实测确认：compose `env_file: ${TRIM_PKGETC}/hanbao.env` 中 `TRIM_PKGETC` 是否由飞牛在 docker-project 执行时展开；若否，回退为 `install_callback` 额外写 `app/docker/hanbao.env` 并改用相对路径 `./hanbao.env`。

## 合规备忘（上架必带）
- `LICENSE` / `NOTICE` / `CHANGES-FROM-UPSTREAM.md` 已随镜像分发（I-002）
- 依赖树无 GPL / AGPL / SSPL 强传染（审计闭合，commit `3da3ae4`）
- 展示名已改 hanbao / 函包；包名 `qwenpaw`→`hanbao` 全量改名已于 2026-08-19 落地完成（见 docs/CHANGES-FROM-UPSTREAM.md 阶段4.5，R2 合规零违约）
- 商标提示：应用名 / 图标 / 描述勿用 Hanbao / AgentScope / Qwen / 通义，勿暗示官方背书
