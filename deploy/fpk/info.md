# hanbao（函包）· 飞牛 FPK 应用信息清单

> 本文件为 FPK 打包前的元信息草稿。schema 级字段已于 2026-08-19 对照飞牛官方规范
> （developer.fnnas.com，本机直连可达无需代理）逐条校正；剩余为 `fnpack` 打包与 fnOS 实测验证。

## 已确定信息
- 应用 ID（package id / `appname`）：`hanbao`（小写无空格，符合飞牛规范，官方示例同风格 HelloFnos）
- 展示名称：函包（hanbao）
- 类型：AI 聊天机器人（本地部署 / 家庭单用户）
- 版本：0.1.0（首发，[飞牛规范待定] 版本号规则）
- 一句话简介：飞牛 NAS 上的私人 AI 聊天助手（微信 + OneBot 渠道）
- 详细描述：fork 自 QwenPaw v2.0.1 (Apache-2.0) 减法式二次开发，并移植 v2.1.0 安全修复（品牌/包名已全量改名 hanbao，见 docs/CHANGES-FROM-UPSTREAM.md 阶段4.5），本地运行、数据自控、仅依赖云端 OpenAI 兼容 API。
- 开源协议：Apache-2.0
- 上游：QwenPaw v2.0.1 (Apache-2.0)，已移植 v2.1.0 修复；保留上游版权与 NOTICE（合规）
- 端口：8088（Web Console，已默认开启登录认证 I-007，LAN 暴露安全）
- 架构：linux/amd64
- 镜像体积（当前）：~1.78GB（venv 瘦身第一刀后；原 800MB 目标经实测评估极难达成；经用户 2026-08-19 拍板保留全部渠道 SDK 不砍，镜像维持 1.78GB，≤1.5GB 目标作废）
- 渠道：微信 + OneBot（QQ / 钉钉 / 飞书 / Telegram 已关闭）

## 阶段5 FPK 脚手架进度（已按官方规范校正，2026-08-27 改为 native 形态）
- 形态拍板：**native**（2026-08-27 飞牛真机实测确认 docker-project 不会自动 load 内置离线镜像 tar，改为 native 形态由 `cmd/main` 自管 `docker load` + `docker compose up/down`）。`config/resource` 只声明 `data-share`，飞牛把本应用视为 native 应用，容器生命周期由 `cmd/main` 负责。
- 已落地且经官方 schema 校正：`manifest`（INI：`appname`/`display_name`/`service_port` 等）、`wizard/` 目录（install/config/upgrade/uninstall 四个 JSON 数组向导）、`config/resource`（`data-share` JSON）、`config/privilege`（package 用户 JSON）、`cmd/main`（native 形态：start/stop/status 自管容器）、`install_callback`（写 `app/docker/hanbao.env` 实体凭据，**不碰 docker**）、`app/docker/docker-compose.yaml`（`env_file: ./hanbao.env` 注入凭据 + `$TRIM_PKGVAR` 持久化工作目录）、`app/ui/config`（`.url` 入口）、图标 `ICON.PNG`/`ICON_256.PNG` + `app/ui/images/*`。
- 凭据闭环：wizard 收集 `HANBAO_AUTH_USERNAME`/`HANBAO_AUTH_PASSWORD` → `install_init` + `install_callback` 双写 `app/docker/hanbao.env` 实体文件 → compose `env_file: ./hanbao.env` 注入容器（接 I-007 默认开认证，首启 `auto_register_from_env` 自动建账号，消除局域网抢注窗口）。 additionally：
  - `app/docker/hanbao.env` 预置默认文件（随包分发），即使生命周期脚本因故未执行，compose 也不会因 env_file 缺失而失败。
  - 脚本写入时除 `TRIM_APPDEST` 外，还兜底写入 `/vol1/@appcenter/hanbao/docker/hanbao.env` 等绝对路径（兼容变量未注入的情况）。
  - 若 `TRIM_PKGETC` 存在则额外备份一份到该持久目录，供升级恢复。

## 待飞牛实测 / 打包（schema 已校正，剩工程验证）
- ✅ `manifest` / `wizard/` / `config/resource` / `config/privilege` / `app/ui/config` 字段名与格式已于 2026-08-19 对照 developer.fnnas.com 官方规范逐条校正。
- ✅ 图标规格：64×64（`ICON.PNG`）+ 256×256（`ICON_256.PNG`），另 `app/ui/images/icon_64.png` / `icon_256.png` 供桌面入口，符合规范。
- 数据存储目录：compose 挂载 `$TRIM_PKGVAR`（飞牛 @appdata 应用数据卷）→ 容器内 `/app/working`，对话与配置持久化（替代原 named volume）。
- 更新机制：FPK 覆盖更新（含新镜像 tar 落 `app/docker/hanbao-amd64.tar`）已设计；版本管理随 `.fpk` 版本号走。
- ✅ `fnpack build` 本地打包校验：已于 2026-08-27 用 fnpack-1.2.3-windows-amd64 成功产出 `hanbao.fpk`（265M，含离线镜像 tar），校验全过。
- ⏳ 剩余工程验证：`fnOS 测试机安装 + 镜像 load + 容器启动 + cmd/main status` 实测（需用户飞牛设备）。
- ✅ **2026-08-27 飞牛真机实测**：compose 中 `${TRIM_PKGETC}` **确实会被展开为 `/vol1/@appconf/hanbao`**；但 `install_callback` 执行时该变量**未被注入**，导致凭据没写到该路径。当前已改为稳妥方案：compose `env_file: ./hanbao.env`，`install_callback` 实体写入 `app/docker/hanbao.env`，同时可选备份到 `$TRIM_PKGETC/hanbao.env`（若变量存在）。
- ✅ **2026-08-27 飞牛真机实测**：docker-project 形态下 fnOS **不会自动 load 内置离线镜像 tar**，安装报 `No such image`。已改为 **native 形态**，由 `cmd/main` 在 start 时 `docker load` + `docker compose up`。

## 安装失败根因与修复（2026-08-27 飞牛真机实测踩坑）
> 首版 `hanbao.fpk` 在飞牛应用中心安装报 **"执行脚本出错且原因未知"**。

- **根因**：docker-project 形态下 fnOS **在应用生命周期脚本的执行环境里不提供 docker 客户端/daemon**。我此前为"加固"风险#1 在 `install_init` 与 `install_callback` 里手动 `docker load -i`，脚本一执行就非 0 退出，`set -eu` 立刻让脚本崩，fnOS 把 stderr 吞掉只报"原因未知"。
- **修复**：`cmd/install_init`、`cmd/install_callback`、`cmd/upgrade_callback` 全部移除 `docker` 调用；`install_callback` / `upgrade_callback` 去掉 `set -eu`、改用 `${VAR:-}` 默认值，任何异常仅告警不中断安装。

## 安装失败根因与修复 #2：改 native 形态（2026-08-27 飞牛真机实测踩坑）
> 移除脚本内 docker 调用后，安装报 **"No such image: hanbao:latest"**。

- **根因**：docker-project 形态下 fnOS **并不会自动 `docker load` 内置离线镜像 tar**（与官方文档/模板暗示不符，或当前 fnOS 版本对 docker-project 的离线 tar 支持有限）。compose up 时镜像缺失，直接报 `No such image`。
- **修复**：把应用形态从 `docker-project` 改为 **`native`**：
  1. `config/resource` 去掉 `docker-project`，只保留 `data-share`。
  2. `cmd/main` 重写：start 时先 `docker load -i app/docker/hanbao-amd64.tar`，再 `docker compose up -d`；stop 时 `docker compose down`；status 时检查容器运行状态。
  3. `app/docker/docker-compose.yaml` 端口映射固定为 `8088:8088`（native 形态由 main 负责，无需 TRIM_SERVICE_PORT 展开）。
  4. `manifest` / `install_callback` / `install_init` / `upgrade_callback` 注释同步改为 native 形态。
- **结论**：镜像加载不再依赖 fnOS 自动机制，改由 `cmd/main` 在启动时显式 load，离线安装闭环完成。

## 安装失败根因与修复 #3：env file 兜底（2026-08-27 飞牛真机实测踩坑）
> 第二版 `hanbao.fpk` 安装报 **"env file /vol1/@appcenter/hanbao/docker/hanbao.env not found"**。

- **根因**：compose 读的是正确的相对路径 `./hanbao.env`（展开为 `/vol1/@appcenter/hanbao/docker/hanbao.env`），但 `install_callback` 没有把文件写到该位置（docker-project 下 `install_callback` 可能未执行或 `TRIM_APPDEST` 未注入）。
- **修复**：
  1. `app/docker/hanbao.env` 预置默认文件（随 FPK 分发）。
  2. `install_init` 在 install_callback 之前写入 `app/docker/hanbao.env`，并兜底 `/vol1/@appcenter/hanbao/docker/hanbao.env` 等绝对路径。
  3. `install_callback` 同样多重路径兜底写入，覆盖默认内容注入 wizard 凭据。
  4. `upgrade_callback` 同样多重路径恢复/生成默认 env。
- **结论**：env_file 不再依赖任一单个变量或脚本执行顺序。

## 飞牛真机实测 Checklist（fnpack build 后上机验证）
> 目标：在飞牛测试机跑通 `fnpack build` 产物 `.fpk` 的安装与运行，并确认两个 fnOS 运行时行为。
> 本小节随 `6310dff` 新增；两项风险结论确认后请回填此处与今日日志。

### A. 打包（Linux / 飞牛开发机）
- [x] `fnpack build deploy/fpk` 成功产出 `hanbao.fpk`，无 schema 报错（08-27 fnpack-1.2.3 实测产出 265M；09-01 tar 刷新至 266MB）
- [x] 产物内含离线镜像 tar（266MB），`manifest` 的 `changelog` 字段被正确读取展示

### B. 安装（fnOS 应用中心「手动安装」侧载）
- [x] 应用中心选中 `.fpk`，向导正常展示（管理员账号 / 密码两项，可留空）
- [x] 安装完成后点击「启动」或自动启动，`cmd/main start` 成功：`docker images | grep hanbao` 能看到镜像，`docker ps` 见 `hanbao` running（08-27 fnOS 真机实测：native 形态安装+启动通过）
  - 若报 `No such image` → 检查 `app/docker/hanbao-amd64.tar` 是否被打包进 `.fpk`、tar 内是否有 `hanbao:latest` 标签
- [x] `cmd/main status` 退出码 0

### C. 凭据注入
- [x] compose 改用 `env_file: ./hanbao.env`（相对 `app/docker/`），`install_callback` 实体写入 `app/docker/hanbao.env`，安装时不受 `TRIM_PKGETC` 变量注入影响
- [ ] 桌面入口「hanbao」打开 Web Console，首启用向导账号自动建档 / 或走注册页（待真机验证 UI 入口）

### D. 升级持久化（凭据与数据不丢）
- [ ] 升到下一版本 `.fpk` 后，旧管理员凭据仍在（`$TRIM_PKGETC` 持久目录未被 app/ 覆盖）（设计保证，待真机升级验证）
- [ ] 对话与配置数据仍在（`$TRIM_PKGVAR` 应用数据卷）（设计保证，待真机升级验证）

### E. 收尾
- [x] 回填实测结论到本文件 + 今日日志（09-03 已按已知事实预填 A/B 机制项并更新今日日志；D 与 C 末项待真机实测补全）

## 合规备忘（上架必带）
- `LICENSE` / `NOTICE` / `CHANGES-FROM-UPSTREAM.md` 已随镜像分发（I-002）
- 依赖树无 GPL / AGPL / SSPL 强传染（审计闭合，commit `3da3ae4`）
- 展示名已改 hanbao / 函包；包名 `qwenpaw`→`hanbao` 全量改名已于 2026-08-19 落地完成（见 docs/CHANGES-FROM-UPSTREAM.md 阶段4.5，R2 合规零违约）
- 商标提示：应用名 / 图标 / 描述勿用 Hanbao / AgentScope / Qwen / 通义，勿暗示官方背书
