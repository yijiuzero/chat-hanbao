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

## 阶段5 FPK 脚手架进度（2026-08-19 已按官方规范校正）
- 形态拍板：**docker-project**（2026-08-19 拉取 developer.fnnas.com 官方规范后，由首版的 native 改为 docker-project）。官方规范仅以 docker-project 作为容器应用标准路径，`config/resource` 的 `docker-project` 声明即飞牛接管容器生命周期的开关；**离线镜像由 fnOS 按 docker-project 声明自动 `docker load` 内置 tar + `docker compose up`（全程不拉外网）**，`pull_policy: never` 作为双保险。应用生命周期脚本**不应、也不能手动调 docker**（安装期脚本执行环境无 docker 客户端，手动 load 必非 0 退出 → 触发"执行脚本出错且原因未知"）。
- 已落地且经官方 schema 校正：`manifest`（INI：`appname`/`display_name`/`service_port` 等）、`wizard/` 目录（install/config/upgrade/uninstall 四个 JSON 数组向导）、`config/resource`（`docker-project` JSON）、`config/privilege`（package 用户 JSON）、`cmd/main`（status-only，容器由飞牛管理）、`install_callback`（仅写 `$TRIM_PKGETC/hanbao.env` 凭据，**不调 docker**）、`app/docker/docker-compose.yaml`（env_file 注入凭据 + `$TRIM_PKGVAR` 持久化工作目录）、`app/ui/config`（`.url` 入口）、图标 `ICON.PNG`/`ICON_256.PNG` + `app/ui/images/*`。
- 凭据闭环：wizard 收集 `HANBAO_AUTH_USERNAME`/`HANBAO_AUTH_PASSWORD` → `install_callback` 持久化 `$TRIM_PKGETC/hanbao.env` → compose `env_file` 注入容器（接 I-007 默认开认证，首启 `auto_register_from_env` 自动建账号，消除局域网抢注窗口）。

## 待飞牛实测 / 打包（schema 已校正，剩工程验证）
- ✅ `manifest` / `wizard/` / `config/resource` / `config/privilege` / `app/ui/config` 字段名与格式已于 2026-08-19 对照 developer.fnnas.com 官方规范逐条校正。
- ✅ 图标规格：64×64（`ICON.PNG`）+ 256×256（`ICON_256.PNG`），另 `app/ui/images/icon_64.png` / `icon_256.png` 供桌面入口，符合规范。
- 数据存储目录：compose 挂载 `$TRIM_PKGVAR`（飞牛 @appdata 应用数据卷）→ 容器内 `/app/working`，对话与配置持久化（替代原 named volume）。
- 更新机制：FPK 覆盖更新（含新镜像 tar 落 `app/docker/hanbao-amd64.tar`）已设计；版本管理随 `.fpk` 版本号走。
- ✅ `fnpack build` 本地打包校验：已于 2026-08-27 用 fnpack-1.2.3-windows-amd64 成功产出 `hanbao.fpk`（265M，含离线镜像 tar），校验全过。
- ⏳ 剩余工程验证：`fnOS 测试机安装 + 镜像 load + 容器启动 + cmd/main status` 实测（需用户飞牛设备）。
- ⚠️ 一处待 fnOS 实测确认：compose `env_file: ${TRIM_PKGETC}/hanbao.env` 中 `TRIM_PKGETC` 是否由飞牛在 docker-project 执行时展开；若否，回退为 compose 改用相对路径 `./hanbao.env` 即可——`install_callback` 已将该路径软链到 `$TRIM_PKGETC/hanbao.env`（同一持久文件，升级不丢），无需 install_callback 再额外写文件。

## 安装失败根因与修复（2026-08-27 飞牛真机实测踩坑）
> 首版 `hanbao.fpk` 在飞牛应用中心安装报 **"执行脚本出错且原因未知"**。

- **根因**：docker-project 形态下 fnOS **在应用生命周期脚本的执行环境里不提供 docker 客户端/daemon**；镜像由系统按 `config/resource` 自动 load。我此前为"加固"风险#1 在 `install_init` 与 `install_callback` 里手动 `docker load -i`，脚本一执行就非 0 退出，`set -eu` 立刻让脚本崩，fnOS 把 stderr 吞掉只报"原因未知"。这是典型的方向反了——手动 load 反而破坏了安装。
- **修复（提交于 2026-08-27）**：
  1. `cmd/install_init`、`cmd/install_callback`、`cmd/upgrade_callback` 全部移除 `docker` 调用，镜像加载彻底交还 fnOS。
  2. `install_callback` / `upgrade_callback` 去掉 `set -eu`、改用 `${VAR:-}` 默认值，任何异常仅告警不中断安装（避免真机变量名未实测时再次硬崩）。
  3. `cmd/main` 去掉 `set -eu`（与官方模板一致）；`status` 的 `docker inspect` 本就在 `if` 条件中、`set -e` 不生效，逻辑安全。
  4. `config/resource` 补齐 `data-share` 段（对齐官方 docker 模板）。
- **结论**：脚本不再触碰 docker 后，安装应可越过"执行脚本出错"。若仍失败，多半是镜像未被 fnOS 自动 load（见下方 Checklist B 的 `No such image` 分支，届时需改 native 形态）。

## 飞牛真机实测 Checklist（fnpack build 后上机验证）
> 目标：在飞牛测试机跑通 `fnpack build` 产物 `.fpk` 的安装与运行，并确认两个 fnOS 运行时行为。
> 本小节随 `6310dff` 新增；两项风险结论确认后请回填此处与今日日志。

### A. 打包（Linux / 飞牛开发机）
- [ ] `fnpack build deploy/fpk` 成功产出 `hanbao.fpk`，无 schema 报错
- [ ] 产物内含离线镜像 tar（266MB），`manifest` 的 `changelog` 字段被正确读取展示

### B. 安装（fnOS 应用中心「手动安装」侧载）
- [ ] 应用中心选中 `.fpk`，向导正常展示（管理员账号 / 密码两项，可留空）
- [ ] 安装完成后镜像已 load：`docker images | grep hanbao`（= fnOS 已按 docker-project 自动 load 内置 tar，应用脚本不负责 load）
  - 若报 `No such image` → ⚠️ fnOS 未自动 load 离线镜像（罕见）；需改回 native 形态（cmd/main 自管 `docker load`+`docker compose up`），或确认 `app/docker/hanbao-amd64.tar` 命名/位置符合 fnOS 预期
- [ ] 容器启动：`docker ps` 见 `hanbao` running，且 `cmd/main status` 退出码 0

### C. 凭据注入（风险#2：TRIM_PKGETC 是否展开）
- [ ] compose 成功读到 `${TRIM_PKGETC}/hanbao.env`（容器内 `HANBAO_AUTH_ENABLED=true` 生效）
  - 若 compose 报 env_file 找不到 / 变量未展开 → ⚠️ 触发风险#2：把 `app/docker/docker-compose.yaml` 第18行回退为 `./hanbao.env`（install_callback 已将其软链到同一持久文件，无需改 install_callback）
- [ ] 桌面入口「函包 hanbao」打开 Web Console，首启用向导账号自动建档 / 或走注册页

### D. 升级持久化（凭据与数据不丢）
- [ ] 升到下一版本 `.fpk` 后，旧管理员凭据仍在（`$TRIM_PKGETC` 持久目录未被 app/ 覆盖）
- [ ] 对话与配置数据仍在（`$TRIM_PKGVAR` 应用数据卷）

### E. 收尾
- [ ] 两项风险确认结论回填本文件 + 今日日志（决定是否需要 native 形态回退）

## 合规备忘（上架必带）
- `LICENSE` / `NOTICE` / `CHANGES-FROM-UPSTREAM.md` 已随镜像分发（I-002）
- 依赖树无 GPL / AGPL / SSPL 强传染（审计闭合，commit `3da3ae4`）
- 展示名已改 hanbao / 函包；包名 `qwenpaw`→`hanbao` 全量改名已于 2026-08-19 落地完成（见 docs/CHANGES-FROM-UPSTREAM.md 阶段4.5，R2 合规零违约）
- 商标提示：应用名 / 图标 / 描述勿用 Hanbao / AgentScope / Qwen / 通义，勿暗示官方背书
