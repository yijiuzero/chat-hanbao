# hanbao 相对上游 QwenPaw 的修改记录

> 本文件是 Apache-2.0 §4(b)「修改标注」义务的核心载体，**必须随分发物一起提供**。
> 合规规范见 [`license-compliance.md`](./license-compliance.md)。

## 基线信息

| 项 | 值 |
|---|---|
| 上游项目 | QwenPaw |
| 上游版本 | v2.0.1 |
| 上游发布日期 | 2026-07-24 |
| 上游许可 | Apache License 2.0 |
| 上游版权 | Copyright 2025 The QwenPaw Authors |
| 上游仓库 | https://github.com/agentscope-ai/QwenPaw |
| 基线 Git commit | `9b86a976fffdc37b871fe31a7b689a8b6463c5b4`（短号 `9b86a97`） |
| 基线 Git tag | `upstream/v2.0.1` |
| 基线文件数 | 2846（与上游 release tarball 完全一致） |
| LICENSE SHA256 | `5906CE05514E804061D128A8B8CFB2C4743B62C934FA580F795FFFD1EFE96C49`（与上游一致） |

> **查看 hanbao 的全部改动**：`git diff upstream/v2.0.1..HEAD`

## 记录规范

1. **Git 首个 commit 必须是未修改的上游原始代码**，之后所有改动通过 `git diff <baseline>..HEAD` 可完整追溯。
2. 每完成一项改动，在下方对应阶段追加条目，格式：
   `- [类型] 路径 — 改动说明（关联 commit）`
3. 类型取值：`新增` / `修改` / `删除` / `重命名` / `配置`

---

## 阶段 0 · 源码就位

- [新增] `LICENSE` — 原样复制自上游 QwenPaw v2.0.1，字节一致（10768B），版权行完整保留
- [新增] `NOTICE` — hanbao 主动创建（上游无此文件），声明派生关系与修改事实
- [新增] `docs/license-compliance.md` — 项目开源许可合规强制规范
- [新增] `docs/CHANGES-FROM-UPSTREAM.md` — 本文件
- [新增] `docs/feasibility-analysis.md`、`docs/project-plan.md`、`docs/lifecycle-management.md` — hanbao 原创前期文档
- [新增] `docs/known-issues.md` — 移植过程发现的问题追踪清单（I-001 ~ I-007），含各问题的必须处理时机与验收方式
- [修改] `.gitignore` — 两处（均带 `[hanbao modification]` 标注）：
  1. `AGENTS.md` → `/AGENTS.md`：原规则误伤 `src/qwenpaw/agents/md_files/**/AGENTS.md`（Agent 运行时提示词资产，必须被追踪）
  2. 追加 `.workbuddy/`：排除本地 AI 助手工作记忆目录，非分发物组成部分
- [说明] 导入时对以下上游 `.gitignore` 命中的文件执行 `git add -f`，以保证仓库可完整复现构建（上游 release tarball 同样包含它们）：
  `console/package-lock.json`、`plugins/bundle/cloudpaw/ui/dist/`、`plugins/bundle/qwenpaw-pet/dist/`、`src/qwenpaw/agents/md_files/**/AGENTS.md`

## 阶段 1 · 构建跑通原版

_目标：先完整移植并跑通上游原版，确认改造基线。本阶段不改动上游业务逻辑，仅补足本地构建所需的最小参数。_

- [配置] `deploy/Dockerfile` — console-builder 阶段新增（带 `[hanbao modification]` 标注）：
  ```dockerfile
  ARG NODE_BUILD_HEAP_MB=4096
  ENV NODE_OPTIONS=--max-old-space-size=${NODE_BUILD_HEAP_MB}
  ```
  原因：`tsc -b && vite build` 在默认 Node 堆上限下 OOM 中断（exit 134）。保留 `--build-arg` 口子以适配不同内存规格的构建机。详见 [known-issues I-008](./known-issues.md#i-008)。
- [构建] 成功构建镜像 `hanbao:0.0.1-upstream`（4.02GB，含上游完整 XFCE4 桌面 + Chromium）。构建环境：Windows + Docker Desktop / WSL2，WSL 内存 8GB，`NODE_BUILD_HEAP_MB=4096`。
- [验证] 容器验证：映射 8088 后，本机 `curl localhost:8088` 返回完整 QwenPaw Console 首页（HTTP 200），确认原版 Web 聊天可访问。
- [说明] 镜像偏大（4.02GB）源于上游为"远程桌面/GUI 访问"打包的 XFCE4 + Chromium，纯 Web 聊天用不到，将在阶段 4（容器化）瘦身。

## 阶段 2 · 品牌改造

### 品牌展示名替换：QwenPaw → hanbao（2026-08-10）

**范围**：仅改品牌展示层（Web 标题、UI 文本、TUI 显示、启动 banner），不涉及：
- Python 包名 `qwenpaw`（保持不动）
- `QWENPAW_*` 环境变量（保持不动）
- `LICENSE` / `NOTICE` / `docs/license-compliance.md` / `docs/CHANGES-FROM-UPSTREAM.md`（合规红线 R2）
- 图标 / favicon / logo（待后续单独处理）
- 文档 README（待后续单独处理）

**改动文件清单（24 个文件）：**

| 文件 | 改动内容 |
|---|---|
| `console/index.html` | `<title>QwenPaw Console</title>` → `<title>hanbao Console</title>` |
| `console/tauri.html` | `<title>QwenPaw Desktop</title>` → `<title>hanbao Desktop</title>` |
| `console/src/layouts/Header.tsx` | Logo `alt="QwenPaw"` → `alt="hanbao"` |
| `console/src/pages/Login/index.tsx` | Logo `alt="QwenPaw"` → `alt="hanbao"` |
| `console/src/tauri/BackendLoadingPage.tsx` | Logo `alt="QwenPaw"` → `alt="hanbao"` |
| `console/src/pages/Chat/index.tsx` | 默认昵称 `"QwenPaw"` → `"hanbao"` |
| `console/src/pages/Chat/OptionsPanel/defaultConfig.ts` | 标题 `"Work with QwenPaw"` → `"Work with hanbao"` |
| `console/src/locales/*.json` (7 文件) | 所有翻译字符串中 `QwenPaw` → `hanbao`（en/zh/ja/ru/pt-BR/id/vi） |
| `src/qwenpaw/utils/startup_display.py` | 启动 banner 标题 + docstring |
| `src/qwenpaw/cli/main.py` | CLI `prog_name` + docstring |
| `src/qwenpaw/cli/tui/app.py` | 终端窗口标题 + 错误消息 + 帮助文本 |
| `src/qwenpaw/cli/tui/launch.py` | docstring |
| `src/qwenpaw/cli/tui/themes.py` | docstring |
| `src/qwenpaw/cli/tui/__init__.py` | 模块 docstring |
| `src/qwenpaw/cli/tui/widgets/__init__.py` | 模块 docstring |
| `src/qwenpaw/cli/tui/widgets/messages.py` | 聊天通道标签 `"qwenpaw"` → `"hanbao"` |
| `src/qwenpaw/cli/tui/widgets/status_bar.py` | 状态栏版本显示 |
| `src/qwenpaw/cli/tui/widgets/theme_picker.py` | 主题选择器标题 |

**未改动**（代码注释 / 内部引用 / 变量名）：`src/qwenpaw/cli/tui/app.py:275,627`、`compat.py:40`、`normalize.py` 全部、`events.py:113`、`acp.py` 全部、`paths.py:4`、`messages.py:142` 等 —— 这些是内部开发注释或变量引用，非用户可见展示名。

- [删除] `README_ja.md`、`README_ru.md`、`README_vi.md` — 上游多语言 README（ja/ru/vi）。产品定位：函包仅做**中英双语**（英文 `README.md` + 中文 `README_zh.md`），其他语言不维护。技术零风险：README 纯文档不被代码依赖，且 `deploy/Dockerfile` 仅 `COPY README.md` 进镜像，ja/ru/vi 从未进镜像。合规允许：保留 `LICENSE`/`NOTICE`/`README.md`/`README_zh.md` 即可（Apache-2.0 不要求保留所有语言 README）。关联 commit `a5fcbc9`。

### Docker 构建优化：COPY 重排利用层缓存（2026-08-10）

**目标**：日常改代码后 Docker 重建从 12 分钟 → 3.5 分钟。

**console 构建阶段**：拆 `COPY console → npm ci && npm run build` 为两步：
1. `COPY package*.json → npm ci`（仅依赖变更时失效，常规改动永久缓存）
2. `COPY console → npm run build`（仅改代码时跑，约 2 min）

**Python 安装阶段**：用 minimal stub package 让 uv 先装依赖、后装代码：
1. 先创建 stub `src/qwenpaw/__init__.py`（含 `__version__`），`uv pip install .` 装全部 236 个包 → 永久缓存
2. 再 `COPY src` 真实源码 + `uv pip install --no-deps .` 仅装包本体 → 约 10s

**改动文件**：`deploy/Dockerfile`

### 语言精简 + QA Agent 禁用 + 更多展示名替换（2026-08-11）

**语言精简**（仅中英双语，默认中文）：
| 文件 | 改动 |
|---|---|
| `console/src/i18n.ts` | 移除 ja/ru/pt-BR/id/vi import，`lng` 默认值 `"en"` → `"zh"` |
| `console/src/components/LanguageSwitcher/index.tsx` | LANGUAGE_LIST 仅保留 en/zh |
| `src/qwenpaw/app/routers/settings.py` | `_VALID_LANGUAGES` → `{"en","zh"}`，GET 默认 `"zh"` |
| `src/qwenpaw/app/routers/skills_stream.py` | 描述 `"en, zh, ru"` → `"en, zh"` |
| `console/src/locales/ja.json` 等 5 文件 | 删除 |

**QA Agent 禁用**：
| 文件 | 改动 |
|---|---|
| `src/qwenpaw/app/_app.py` | 注释 `ensure_qa_agent_exists()` 调用 |
| `src/qwenpaw/cli/init_cmd.py` | 注释调用 + import |

**Logo + 图标替换**：
| 文件 | 改动 |
|---|---|
| `console/public/logo-dark.svg` | 替换为 hanbao 文字 Logo |
| `console/public/logo-light.svg` | 替换为 hanbao 文字 Logo |
| `console/public/qwenpaw.png` | 替换为 hanbao 图标（保留旧文件名避免改引用） |

**更多展示名替换**：
| 文件 | 改动 |
|---|---|
| `console/src/layouts/Header.tsx` | 更新说明正则匹配 `QwenPaw` → `hanbao` |
| `console/src/layouts/constants.ts` | 更新说明 Markdown 中产品名 |
| `console/src/pages/Settings/PluginManager/components/MarketPluginList.tsx` | 插件兼容标签 |
| `console/src/pages/Settings/Market/components/SkillIcon.tsx` | 技能来源标签 + 首字母图标 |
| `console/src-tauri/tauri.conf.json` | productName / 窗口标题 / NSIS 语言清单 |
| `console/src-tauri/Cargo.toml` | description / authors |

**已知品牌残留（记入 I-012~I-016，阶段 3 处理）**：JS 命名空间 `window.QwenPaw`、localStorage keys、CSS 前缀、测试/e2e/website、插件 metadata。

## 阶段 3 · 删减定制

hanbao 定位为「个人 AI Web 聊天」，以下上游功能对 hanbao 不适用或属冗余，已移除。

### 编码模式（Coding Mode）移除（2026-08-11~12）

hanbao 不做代码编辑器/项目开发场景，Coding Mode（代码项目上下文、编码智能体、多 Tab 编辑器等）全部移除。

**前端 files 删除：**
- `console/src/pages/Coding/`（完整目录）
- `console/src/stores/codingModeStore.ts` / `codingTabsStore.ts` / `useSyncCodingMode.ts`（含 `.test.ts`）
- `console/src/stores/codeFileCacheStore.ts` / `loopStore.ts`（含 `.test.ts`）

**后端 files 删除：**
- `src/qwenpaw/modes/coding/`（完整目录：`__init__.py`, `hooks.py`, `mixin.py`）
- `src/qwenpaw/app/routers/coding_mode.py`
- `src/qwenpaw/app/routers/coding_project.py`

**后端 修改 required to remove dangling imports：**
- `src/qwenpaw/app/_app.py` — 注释 `app.include_router(coding_mode_router)`
- `src/qwenpaw/app/routers/__init__.py` — 移除 `coding_project_router` import & include
- `src/qwenpaw/runtime/builder.py` — CodingMode 从 mode 注册移除，coding_project_dir 传 `None`
- `src/qwenpaw/runtime/react_agent.py` — `CodingModeMixin` 从 ReactAgentChat MRO 移除
- `src/qwenpaw/config/config.py` — 注释 `CodingModeConfig`
- `src/qwenpaw/runtime/prompt_contributors.py` — `CodingModeContributor` 移除
- `src/qwenpaw/agents/agent_context.py` — coding_mode 引用替换为 `None`
- `src/qwenpaw/agents/fork_project.py` — coding_project_dir 引用替换为 `None`
- `src/qwenpaw/app/routers/fork.py` — coding_mode 引用替换为 `None`
- `src/qwenpaw/app/workspace/bootstrap_factory.py` — `CodingMode` import 移除
- `src/qwenpaw/hooks/request_setup/contextvars_hook.py` — coding_mode 分支替换为 `None`

**前端 修改：**
- `console/src/layouts/registry/builtinRoutes.tsx` — 移除 Coding 路由 & DefaultRedirect
- `console/src/layouts/Header.tsx` — 移除 CodingModeToggle
- `console/src/pages/Chat/index.tsx` — 移除 useCodingMode, codingMode 重定向, lastEditorCopy
- `console/src/pages/Chat/components/ChatSessionInitializer/index.tsx` — mode 固定为 `"chat"`

### Tauri 桌面端移除（2026-08-11）

hanbao 仅做 Web 聊天，桌面打包（Tauri + Rust）需求不存在。

**文件删除：**
- `console/src-tauri/`（完整目录，含 Cargo.toml, Rust src, icons, NSIS installer）
- `src/qwenpaw/tauri/`（完整目录，Python 后端侧车进程支持）
- `console/src/tauri/`（完整目录，Tauri 前端运行时）
- `console/tauri.html`（Tauri 入口 HTML）
- `console/src/contexts/DesktopUpdateContext.tsx`（桌面端更新检查）
- `console/src/components/UpdateTakeoverPage/`（桌面端更新拦截页）

**前端修改：**
- `console/src/App.tsx` — 移除 DesktopUpdateProvider, UpdateTakeoverGate, isTauri
- `console/src/layouts/Header.tsx` — 移除 invoke/useDesktopUpdate/isDesktopApp，onDesktop 固定 `false`，desktop stub 化
- `console/src/layouts/SidebarSettingsPanel.tsx` — 移除关闭窗口偏好设置（Tauri-only）
- `console/src/utils/openExternalLink.ts` — `isDesktopTauriRuntime()` 固定 `false`
- `console/src/utils/downloadFileFromUrl.ts` — 移除 Tauri invoke/save import
- `console/src/pages/Agent/ACP/index.tsx` — 移除 Tauri 文件选择器

### QwenPaw Pet 桌面宠物插件移除（2026-08-18）

hanbao 仅做 Web 聊天且容器已砍桌面栈（I-004），桌面宠物（依赖 PySide6 + 独立桌面进程 `qwenpaw_pet_desktop`）既不在部署镜像内（`Dockerfile` 仅 `COPY src ./src`，根目录 `plugins/` 从未 COPY），也失去运行环境，故整目录移除。

**文件删除：**
- `plugins/bundle/qwenpaw-pet/`（完整目录：backend `plugin.py`/`emitter.py`/`patch_approval.py`/`patch_runner.py`/`pet_paths.py`/`router.py`、桌面端 `qwenpaw_pet_desktop/`（PySide6 GUI）、前端 `frontend/`、`plugin.json`/`README.md`/`requirements.txt` 等共 34 文件）

**依赖分析结论（删前已核查，按铁律不做无依据删除）：**
- 主程序零引用（`grep qwenpaw[_-]?pet` 除自身外无命中）；无集中注册清单；运行时 `PluginLoader` 不自动拷贝 `plugins/bundle/` 进 `WORKING_DIR/plugins`；无测试引用。删除无悬空引用、无运行时崩溃风险。
- `website/public/blog/play-with-qwenpaw-pet.*.md` 与 `website/public/release-notes/` 仍含 QwenPaw Pet 叙述（营销站，不进镜像），作为上游历史记录保留，未随删。

**文档同步：**
- `docs/known-issues.md` `dist/` 误吞表项：`{cloudpaw/ui,qwenpaw-pet}` → `cloudpaw/ui`（qwenpaw-pet 已删）。

### 品牌资源替换（2026-08-12）

- [修改] `console/public/online.svg` — favicon 替换为 hanbao 图标（墨风角色肖像）
- [删除] `console/public/qwenpaw.png` — 默认 Agent 头像，Chat 代码改为 fallback `/online.svg`
- [删除] `console/public/qwenpawBack.png` — 未使用的品牌背景图
- [修改] `console/src/pages/Chat/index.tsx:2703` — `"/qwenpaw.png"` → `"/online.svg"`
- [修改] `console/src/layouts/constants.ts` — `GITHUB_URL` → 本项目仓库
- [修改] `.gitignore` — `dist/` 收窄为 `/dist/`（防误伤）；`console/package-lock.json` 取消忽略

### UI 功能精简（2026-08-12~13）

- [删除] Resources 下拉菜单（Header 中 QwenPaw 文档/教程/FAQ 链接）
- [删除] 心跳（Heartbeat）设置页面（前端 only：page/API/路由/菜单；后端 Agent 心跳核心保留）
- [删除] 应用中心 / PawApps（前端 only：AppCenter 页面、PawApps 设置页、pawapp-sdk、API 模块；后端 pawapp 路由保留未触）
- [删除] ACP（Agent 级配置）设置页面（前端 only：`pages/Agent/ACP/`、`api/modules/acp.ts`、`api/types/acp.ts`、路由/菜单；后端 `agent_scoped.py` 中间件与 `agents/acp/` 通信协议保留未触）
- [删除] 环境变量设置页面（`pages/Settings/Environments/`；后端 `routers/envs.py` 保留未触）
- [删除] 语音转写（`pages/Settings/VoiceTranscription/` 设置页 + Chat 麦克风按钮 `WhisperSpeechButton` + 录音快捷键；后端 `audio_transcription.py` 保留未触）
- [删除] 插件管理页面（`pages/Settings/PluginManager/` 全部 18 文件 + `api/modules/plugin.ts` + `api/modules/pluginMarket.ts` + 路由/菜单；插件加载基础设施 `console/src/plugins/` 与后端 `plugins/`/`src/qwenpaw/plugins/` 保留未触，渠道 azure_bot 与图像工具插件正常加载）
- [删除] 备份功能（前端 `pages/Settings/Backups/` 全部 37 文件 + `api/modules/backup.ts` + `api/types/backup.ts` + 路由/菜单；后端 `routers/backup.py` + `routers/_backup_helpers.py` + `routers/__init__.py` 注册。**保留** `src/qwenpaw/backup/_utils/safe_swap.py` 及 `_mount_swap.py`——被 `app/_app.py` 启动清理与 `envs/store.py` 环境变量存储共用，不可删。数据保护交由飞牛 NAS 快照/volume 持久化）

### 内置技能精简（2026-08-13）

hanbao 定位私人聊天机器人，移除与 QwenPaw 官方答疑、浏览器自动化、桌面、邮件、编码无关的技能（每个技能中英双语各删一份）：

- [删除] `QA_source_index`（查 QwenPaw 官方文档）、`guidance`（QwenPaw 安装配置问答）—— 改 hanbao 后无意义
- [删除] `browser_cdp`、`browser_visible`（浏览器自动化，依赖 Chromium，阶段4 瘦身）
- [删除] `dingtalk_channel`（靠浏览器自动配置钉钉；钉钉渠道后端保留）
- [删除] `himalaya`（邮件客户端）
- [修改] `src/qwenpaw/constant.py` — `BUILTIN_QA_AGENT_SKILL_NAMES` 清空为 `()`（原引用已删的 guidance/QA_source_index）
- [保留] 7 个技能：`channel_message`、`chat_with_agent`、`multi_agent_collaboration`、`make_plan`、`make-skill`、`cron`、`file_reader`
- [保留] 联网搜索：`web_search`（Tavily keyless API，免费无密钥）+ `web_fetch` 已内置，无需额外 skill/API key

### 文档处理技能：Anthropic 专有 → 删除 + markitdown 替代（2026-08-13，P0 侵权红线）

上游 `docx`/`pdf`/`pptx`/`xlsx` 4 个技能的 `LICENSE.txt` 为 **Anthropic 专有许可**（禁止分发/复制/衍生/销售），Anthropic 官方确认这 4 个文档技能是 source-available 而非开源。hanbao 作为再分发者打包 FPK = 侵权。

- [删除] `docx`、`pdf`、`pptx`、`xlsx` 4 个技能（含中英双语 SKILL.md + scripts + Anthropic LICENSE.txt，共 8 目录）—— ✅ 已删除
- [决策] 放弃文档「创建/编辑」能力（微信聊天场景低频），仅保留「读文档」
- [替代] 读文档用 `markitdown`（微软，MIT 许可）：docx/pdf/pptx/xlsx → Markdown 供 Agent 读取 —— ✅ 已接入
- [修改] `pyproject.toml` — 新增依赖 `markitdown[pdf,docx,pptx,xlsx]>=0.1.0`
- [新增] `document_reader` 技能（中英双语 `agents/skills/document_reader-{en,zh}/SKILL.md`）—— 用 markitdown 读 PDF/Office 文档转 Markdown，明确「只读不改」
- [缺陷] 记录为 I-019：改文档（需 python-docx/openpyxl）与创建文档暂不提供，后续需要再评估自研简化版

### 编码工具删除（2026-08-13）

编码模式（Coding Mode）已在阶段 3 早期移除，其配套的编码工具现为死代码，本轮清除：

- [删除] `src/qwenpaw/agents/tools/_lsp_client.py`、`_lsp_servers.py`、`lsp_tool.py`（LSP 代码辅助，`make_lsp_tool` 无任何加载点）
- [删除] `src/qwenpaw/agents/tools/ast_tool.py`（AST 代码分析 `ast_search`）
- [修改] `src/qwenpaw/agents/react_agent.py` — 移除 `ast_search` 与 5 个 `lsp_*` 工具注册
- [修改] `src/qwenpaw/agents/tools/__init__.py` — 移除 `ast_tool` import
- [修改] `pyproject.toml` — 移除 `python-lsp-server[all]` 与 `ast-grep-cli` 依赖（连带消除 rope/pytoolconfig 两个 LGPL 传递依赖，见 I-021）

### 待办：浏览器/桌面工具（阶段4 随 Chromium 瘦身一并处理）

- `browser_control`（被 `_app.py` stop_all_browsers 依赖）、`browser_snapshot`、`desktop_screenshot`（被 proactive 依赖）
- 上述工具与 Chromium/XFCE 绑定，阶段4 瘦身时统一移除并清依赖链

### 安全策略：默认锁定 + 删配置页（2026-08-13）

hanbao 定位「私人版豆包」，面向飞牛 NAS 普通用户，**无需也不该暴露安全配置**。

- [删除] Security 设置页面（`pages/Settings/Security/` 全部 16 文件 + `api/modules/security.ts` + `utils/scanError.ts` + 路由/菜单）
- [修改] `src/qwenpaw/config/config.py` — `sandbox_enabled` 默认值 `False` → `True`（沙箱默认开启，Agent 工具调用隔离执行，无法触碰 NAS 数据）
- [保留] 后端安全运行时：`sandbox/`（bubblewrap/landlock/seatbelt/win）、`security/tool_guard/`（引擎 + 文件/Shell 守卫）—— 静默生效
- [保留] `app/approvals/` 审批服务后端代码（不再被主路径调用，属死代码；见下方「审批流程移除」）
- [保留] Skill Scanner 后端（内置 skill 加载时扫描，无害）；前端以 no-op stub 兼容
- [修改] `console/src/utils/scanError.ts` — 重写为 no-op stub（`checkScanWarnings` 恒返回 `{passed:true}`、`handleScanError` 恒返回 `false`）
- [修改] `console/src/api/modules/security.ts` — 重写为类型兼容 stub
- [修改] `console/src/pages/Agent/Skills/useSkills.ts` / `useSkillsPage.tsx` / `Settings/SkillPool/useSkillPool.tsx` — 移除对已删 `api.getBlockedHistory`/`api.getSkillScanner` 的调用，替换为内联 stub

### 审批流程移除（2026-08-13）

hanbao 定位私人豆包，主要通过聊天渠道（微信等）交互，交互式审批卡片不可行；且沙箱已默认开启隔离文件访问，审批的「确认」环节冗余。故移除审批，保留灾难级命令拦截与沙箱兜底。

- [修改] `src/qwenpaw/governance/tool_adapter.py`（主路径 `PolicyGuardedTool.check_permissions`）— `GovernanceAction.ASK` 分支改为直接 `ALLOW`（敏感文件/中风险不再弹审批，靠沙箱挡越界）
- [修改] `src/qwenpaw/governance/tool_adapter.py`（主路径 `__call__` 沙箱违规）— 沙箱违规由「审批问用户」改为直接返回 `DENIED`（越界即拒绝，附 `_NO_RETRY_INSTRUCTION` 让 Agent 向用户解释）
- [修改] `src/qwenpaw/runtime/tool_guard.py`（fallback 路径 `GuardedFunctionTool`，governor 缺失时）— `_ask_user_approval` 调用改为直接 `ALLOW`
- [保留] 灾难级命令拦截（`rm -rf /`、`mkfs`、`dd`、fork bomb 等）仍在 policy 层 DENY，不受影响
- [保留] 前端审批 UI（`ApprovalCard`/`ApprovalContext`/`ApprovalLevelToggle`/`PendingApprovalsDrawer`）—— 后端不再发 ASK，已变死代码不再弹窗；因深度耦合 App/Sidebar/Chat/Inbox/Channels，暂不硬删，待后续单独清理

### 审批前端 UI 清理（2026-08-14）

审批事件产生函数 `_ask_user_approval` 已零调用点，前端审批 UI 永远空，故清理全部前端审批死代码：

- [修改] `console/src/pages/Inbox/index.tsx` — 删收件箱「审批」Tab（`TabKey` 收紧为 `messages`、删 `handleApproveRequest`/`handleRejectRequest`/`handleCancelTask`、删 `GlobalApprovalCard`/`useApprovalContext`/`commandsApi`/`chatApi`/`sessionApi`/`PackageOpen` import、删 tab 记忆 localStorage）
- [修改] `console/src/pages/Agent/Config/index.tsx` + `useAgentConfig.tsx` — 删「工具执行安全」Tab（`ToolExecutionLevelCard`）及 `approvalLevel` 状态/加载/保存/返回
- [修改] `console/src/pages/Chat/index.tsx` — 删 6 个审批 import + `ApprovalMessageData` 接口 + `sessionApprovalLevelRef`/`runningConfigApprovalLevel`/`approvals`/`approvalRequests` 状态 + 消费 useEffect + `handleApprove`/`handleDeny` + `applyApprovalLevelToRequestBody` 调用 + `ApprovalLevelToggle`/`ApprovalCard` 渲染 + 依赖数组
- [修改] `console/src/components/ConsolePollService/index.tsx` — 删审批轮询（保留推送消息气泡）
- [修改] `console/src/App.tsx` — 删 `ApprovalProvider` 挂载 + import
- [修改] `console/src/pages/Agent/Config/useAgentConfig.test.tsx` — 删 3 个审批相关测试用例
- [保留] 孤儿文件（已无引用，物理删除待用户手动）：`ApprovalContext.tsx`、`ApprovalCard.tsx`（全局+Inbox）、`ApprovalLevelToggle.tsx`、`approvalPayload.ts`、`utils/approval.ts`、`useAgentRunningConfigApprovalLevel.ts`、`ToolExecutionLevelCard.tsx`
- [保留] 后端 `approvals/` 服务 + `routers/approval.py` —— 仍被 ACP server/console/协调器调用，非纯死代码，暂不动

### 遥测移除（2026-08-14，I-006）

hanbao 是独立 fork 产品，分发给第三方用户，不应把「多少人装了函包」透露给 QwenPaw 官方，也不符合「本地数据主权」定位。

- [修改] `src/qwenpaw/utils/telemetry.py` — `_upload_telemetry_sync` 改为 no-op（恒 `return False`），删除 `TELEMETRY_ENDPOINT`（`https://qwenpawelemetry-*.fcapp.run` 上报地址）；模块其余函数（marker 机制）保留供 `clean_cmd.py` 引用
- [修改] `src/qwenpaw/app/_app.py` — 移除启动时「未 opt-out 且未上报过则自动上报」的 try 块
- [修改] `src/qwenpaw/cli/init_cmd.py` — 移除遥测代码块、`TELEMETRY_INFO` 文案、`_echo_telemetry_info_box`（init 交互模式的 "Share usage data?" 提示一并删除）
- [确认] 前端 console 无遥测（无 analytics/posthog/sentry 依赖，无上报端点）

### Monaco 编辑器残留清理（2026-08-14，I-024，阶段 3 收尾）

Coding Mode 移除时 Monaco 编辑器未一并清理，本次收尾：

- [修改] `console/package.json` — 删 `monaco-editor` + `@monaco-editor/react` 依赖、删 `verify:monaco-css` script、`build`/`build:prod` 去掉 `&& npm run verify:monaco-css`
- [修改] `console/package-lock.json` — `npm install --package-lock-only` 同步（纯删 62 行，零版本漂移）
- [修改] `console/src/main.tsx` — 删 `import "./monacoSetup"` 及注释
- [修改] `console/src/monacoSetup.ts` — 清空为占位符 `export {}`（`tsc -b` 会编译 src 下所有 .ts，直接删依赖报 TS2307）
- [保留] `console/scripts/verify-monaco-css.mjs` — 孤儿文件（.mjs 不被 tsc 编译、script 已删不调用），物理删除待用户手动执行

> ⚠️ 环境教训：本机 `git rm` 删除文件曾触发整个 `console/` 目录 553 文件从磁盘消失（文件系统异常，类似 I-018），故未用 git rm，改用「清空占位 + 留孤儿文件」，物理删除交用户手动。

### 品牌残留清理：window.QwenPaw / localStorage / CSS 前缀（2026-08-17，I-012/013/014）

函包 v0.0.1 未上架、无存量用户，品牌残留可直接改名（无需迁移/兼容）：

- [修改] `console/src/App.tsx` — `prefix`/`prefixCls` `qwenpaw` → `hanbao`
- [修改] `console/src/**/*.less` — CSS 前缀 `qwenpaw-` → `hanbao-`（151 处）
- [修改] `console/src/**/*.ts/.tsx` — localStorage key `qwenpaw_` → `hanbao_`（14 个 key）、`window.QwenPaw` → `window.hanbao`、UI 文案/console 日志中的 QwenPaw → hanbao
- [保留] `constants.ts` 安装命令、`Header.tsx` 文档正则、`GITHUB_URL` 测试（指向上游）、接口名 `QwenPawXxxNamespace`、文件名 `qwenpaw.d.ts`（归包名改名子阶段）

### 本地模型 provider 品牌残留（2026-08-17）

- [修改] `src/qwenpaw/providers/provider_manager.py` — `qwenpaw-local` → `hanbao-local`、`name="QwenPaw Local"` → `"hanbao Local"`
- [修改] `console/src/pages/Settings/Models/components/providerIcon.ts` — `hanbao-local` 图标从上游 CDN 换成函包自有 logo `/hanbao-logo.jpg`（新增 `console/public/hanbao-logo.jpg`）
- [修改] `src/qwenpaw/app/auth.py` — 删遗留白名单 `/qwenpaw-symbol.svg`（console 已改用 logo-dark/light）

### 本地 LLM 模型删除（2026-08-17）

函包定位渠道聊天 + 仅云 API，本地 LLM 模型（hanbao-local/QwenPaw Local + ollama/lmstudio + llama.cpp 子系统）整体删除：

- [删除] `src/qwenpaw/providers/provider_manager.py` — `PROVIDER_QWENPAW`/`PROVIDER_OLLAMA`/`PROVIDER_LMSTUDIO` 定义 + `_add_builtin` 注册 + `model_validate` ollama 分支 + `_normalize_provider_id`/`_migrate_copaw_config`/`_resume_local_model`/`start_local_model_resume` legacy 迁移与恢复逻辑
- [删除] `src/qwenpaw/local_models/` — `manager`/`model_manager`/`download_manager`/`llamacpp` 清空占位；`__init__.py` 清空
- [保留] `src/qwenpaw/local_models/tag_parser.py` — 通用 `<tool_call>` 标签解析，被 `openai_chat_model_compat.py` 使用，非本地模型专属
- [删除] `src/qwenpaw/app/routers/local_models.py` 清空 + `routers/__init__.py` 注册移除
- [删除] `src/qwenpaw/app/_app.py` — `LocalModelManager` 初始化 + `start_local_model_resume` + shutdown 逻辑
- [删除] `src/qwenpaw/agents/utils/audio_transcription.py` — ollama provider 判断分支
- [删除] `src/qwenpaw/cli/doctor_checks.py`/`doctor_cmd.py`/`providers_cmd.py` — 本地模型诊断、llama.cpp 检查、本地模型 CLI 命令（download/list/remove）
- [删除] `src/qwenpaw/constant.py` — `DEFAULT_LOCAL_PROVIDER_DIR`
- [删除] `src/qwenpaw/agents/routing_chat_model.py` 清空（孤儿，本地/云路由已无意义）
- [删除] 前端 — `localModel` API + 类型、`LocalModelManageModal`/`LocalModelRow`/`LocalRuntimePanel`/`LocalProviderCard`/`shared` 清空、`providerIcon`/`providerLetterIcon`/`ProviderCard`/`ModelManageModal`/`utils` 的本地模型分支
- [保留] ReMe 记忆的 ollama embedding（走 AgentScope 层，独立）、Local Whisper 语音转写（openai-whisper，独立）
- [保留] `config.py` 的 `llm_routing` 配置结构（无存量用户，local slot 不会被使用）

### 构建修复记录

- 修复 2 处 Python 文件中误用的 `// [hanbao]` 注释（JS 语法，Python 解析报错）→ 改为 `# [hanbao]`
- 修复 `src/qwenpaw/app/routers/__init__.py` 因 git 操作被静默清空导致 `ImportError` — 已从上游恢复
- 修复 `builtinRoutes.tsx` / `builtinMenu.ts` / `Chat/index.tsx` 删除功能后遗留的孤儿代码（悬空 `{`/`},`、孤儿 `try/catch`、未用变量）→ 用 Python 内容匹配精确清理
- 测试文件 `acp.test.ts` / `backup.test.ts` 因引用已删模块改为空 stub

### 上游 v2.1.0 安全修复采纳：OneBot 反向 WS 鉴权加固（2026-08-14，P0-2 / #6676）

hanbao 定位「渠道聊天为主」（微信/QQ/Telegram 等），OneBot v11 反向 WebSocket 是核心渠道之一。上游 v2.1.0 的 **#6676** 修复了「`ws_host` 默认 `0.0.0.0` 且无 `access_token` 时，反向 WS 服务端暴露全网且无鉴权」的漏洞。该修复对 hanbao 属 **P0（安全）**，故从上游 patch 手工移植（未整仓库 `git am`，避免连带引入无关改动），仅移植 #6676 相关 hunk。

**移植方式**：从 `qwenpaw_v201_v210.patch` 提取 #6676 的 3 个文件 diff；因手工提取截断末段 hunk 导致 `git apply --check` 报 corrupt patch，改用 Edit 工具逐文件移植 #6676 专属 hunk，其余 OneBot 改动不动。

**改动文件清单（3 个）：**
- [修改] `src/qwenpaw/utils/http.py` — 新增 `[hanbao]` helper `_WILDCARD_PROBE_HOSTS`（通配符绑定地址 → 对应 loopback 探测地址）与 `probe_host_for_bind_host()`，供 OneBot 健康检查时安全连接自身 listener。已有的 `is_loopback_host()` 为上游原函，直接复用。（上游同名改动，语义一致）
- [修改] `src/qwenpaw/app/channels/onebot/channel.py` — 核心安全逻辑（带 `[hanbao modification]` 标注）：
  - 新增 `import hmac`、`from ....utils.http import is_loopback_host, probe_host_for_bind_host`
  - 模块级常量 `_DEFAULT_WS_HOST = "127.0.0.1"`、`_AUTH_SCHEMES = frozenset({"bearer","token"})` 与 helper `_extract_auth_token` / `_tokens_match`（`hmac.compare_digest` 常量时间比较）/ `_log_remote`（清洗 `request.remote` 防日志注入）
  - `ws_host` 默认值 `0.0.0.0` → `127.0.0.1`（`__init__` / `from_env` / `from_config` 三处）
  - `_auth_required = not is_loopback_host(self._ws_host)`：绑定 loopback 不强制 token，绑定非 loopback **强制** `access_token`
  - `_handle_ws_connection` 重写：缺 token 且 `_auth_required` → 401；token 校验仅走 `Authorization` header（**拒绝 query-param token**，防 URL 记录泄漏）；`_token_authorized` 用常量时间比较
  - `_is_server_healthy` 改用 `probe_host_for_bind_host(self._ws_host)` 探测；连接/断开日志改用 `_log_remote(request)`
- [修改] `src/qwenpaw/config/config.py` — `OneBotConfig.ws_host` 默认值 `"0.0.0.0"` → `"127.0.0.1"`；docstring 注明「非 loopback 绑定需 `access_token`」

**验证**：`python -m py_compile` 三文件通过；grep 确认 `probe_host_for_bind_host` / `is_loopback_host` / `_auth_required` / `_token_authorized` / `_log_remote` 符号均存在。

**合规**：本改动源自上游 Apache-2.0 代码，仅移植安全 hunk，未触碰 LICENSE/NOTICE/合规文档（R2 红线守住）。

> 关联：完整 v2.1.0 采纳规划见 [`upstream-v2.1.0-adoption.md`](./upstream-v2.1.0-adoption.md)；本项为其中 P0-2 的首个落地。

### 上游 v2.1.0 P0 修复移植：日志隐私/配置健壮性/微信语音/中文路径（2026-08-14，P0-4/8/9/11）

按 `upstream-v2.1.0-adoption.md` 最终敲定清单，从上游 patch 手工移植 4 个 P0 修复（均为小改动，核心文件未被子包改动，测试文件因函包已改/非运行时必需而跳过）：

- [修改] `src/qwenpaw/agents/command_handler.py` — P0-4 / #6692：`logger.info(f"...args: {args}")` → `logger.info("Processing command: %s", command)`，命令参数可能含凭据（如 /compact 提示里的 API key），不再落日志
- [修改] `src/qwenpaw/config/config.py` — P0-8 / #6615：`load_agent_config` 的 `json.load` 包 try/except，`UnicodeDecodeError`/`json.JSONDecodeError` 转可恢复 `ConfigurationException`（损坏配置不再崩启动）
- [修改] `src/qwenpaw/agents/utils/message_processing.py` + `src/qwenpaw/runtime/message_convert.py` — P0-9 / #6573：新增 `_audio_text_block`（dict/Pydantic 两种表示兼容）与 `_process_local_data_block`，修复渠道音频（微信语音）在 Pydantic DataBlock 路径下不被转写的问题；`message_convert` 补 audio `data` 字段为 URL 候选
- [修改] `src/qwenpaw/_compat/message.py` + `src/qwenpaw/runtime/message_convert.py` — P0-11 / #6873：`_ensure_url_scheme` 从 message_convert 移到 _compat（去重 + 增强 UNC/百分号编码路径），修复 legacy 会话本地路径媒体（中文文件名）无法重新加载

**移植方式**：从 `qwenpaw_v201_v210.patch` 提取各提交纯 diff，`git apply --include` 只应用核心文件（跳过测试文件，函包测试已改且非运行时必需）；已应用文件均补 `[hanbao modification]` 标注。

**验证**：`hanbao:0.0.15` 构建成功，容器跑通（`/api/version` 正常，无 import 错误）。

**跳过项（已判定不适用）**：P0-3 备份（函包已砍备份 UI）、P0-5 沙箱 PYTHONHOME（Windows 沙箱专属，函包 Linux）、P0-7 导入安全（编码模式已砍，`coding_project.py` 已删）、P0-6 沙箱降级（依赖 Windows 非提权沙箱的 `detect_platform_mode`，价值边际）。

### 上游 v2.1.0 P1 重点修复移植：MCP 会话恢复 / token 统计后端（2026-08-14，P1-28 / P1-26）

- [修改] `src/qwenpaw/drivers/handlers/mcp_stateful_client.py` — P1-28 / #6894：`_is_transport_error` 识别 `McpError`（"session terminated"/"connection closed"）与嵌套异常；`list_tools` 在会话失败时返回缓存 tool schema 并等待重连重试；`_handle_transport_error` 返回 bool
- [修改] `src/qwenpaw/drivers/manager.py` — P1-28 / #6894：`list_capabilities` 的 handler 循环加 try/except（单个 Driver 失败不影响整体）；注：上游 hunk 含 `scope_id` 参数（函包 v2.0.1 无），故手工移植核心逻辑而非 git apply
- [修改] `src/qwenpaw/agent_stats/models.py` + `service.py` — P1-26 / #6503：新增 `agent_prompt_tokens`/`agent_completion_tokens`/`agent_llm_calls` 字段；`_extract_turn_usage_tokens` 从 per-turn metadata 提取当前 Agent token 用量（独立于全局 overlay）
- [修改] `console/src/api/types/agentStats.ts` — P1-26 / #6503：`DailyStats`/`AgentStatsSummary` 加 `agent_prompt_tokens`/`agent_completion_tokens`/`agent_llm_calls` 可选字段（后端数据结构类型对齐）
- [修改] `console/src/pages/Settings/AgentStats/index.tsx` + `index.module.less` — P1-26 / #6503 前端 UI（两提交 #6503 + 「narrow」叠加）：页面收窄为「当前 Agent」视角——顶部标题改为 `getAgentDisplayName` 显示的 Agent 名；删「全部 Agent 汇总」区（全局 prompt/completion/llmCalls 卡片 + 全局 token 趋势图）；当前 Agent 区保留 session/message/当前 Agent token/Recorded Turns/toolCalls 卡片 + 当前 Agent token 趋势图 + LLM 轮次&工具趋势图。类型 `ChartDataItem` 删 `displayDate`/`totalMessages`/`promptTokens`/`completionTokens`/`llmCalls`，加 `agentLlmCalls`
- [修改] `console/src/locales/{en,zh}.json` — P1-26：agentStats 段删 10 个废弃 key（`description`/`llmCalls`/`channel`/`sessionCount`/`sessions`/`messages`/`promptTokensTooltip`/`completionTokensTooltip`/`llmCallsTooltip`/`tokenTrendTooltip`），新增 5 个 `currentAgent*` key，改 `llmAndToolTrendTooltip`（跳过 id/ja/ru/vi/pt-BR）

**验证**：`hanbao:0.0.16` 构建成功，容器跑通无 import 错误。

### 上游 v2.1.0 Scroll 中文(CJK) 召回 + 检索重构（2026-08-14，P1-9）

按依赖顺序移植三个提交（见 known-issues I-023「patch 提交依赖」）：

- [修改] **PATCH 066 #6068**（前置依赖，仅取 memoryspace.py 片段）：`expand()` 从 `WHERE seq BETWEEN` 改为带 `session_id`/`agent_id` scope 过滤版（`where.append` + `AND.join`），保留 `agent_id IS NULL` 兼容早期迁移。**其余 session 迁移重构（sync.py/history.py/session.py）为独立功能，未纳入**。
- [修改] **#6237 `feat(scroll): improve exchange and date-aware history recall`**：scroll 记忆检索核心重构。`memoryspace.py`/`recall_tool.py`/`repl.py`/`manager.py`/`history.py` git apply 干净；`_app.py`/`builder.py`/`command_handler.py` 手工移植（scroll 组件构建同步化后，用 `run_sync_io` 异步包装，`_build_scroll_components` 改 `async def`）。
- [修改] **#6824 `fix(scroll): recall CJK substrings as complete turns`**：中文召回核心——`_CJK_QUERY_RE` 识别 CJK 字符，查询含中文时路由到 LIKE 字面子串搜索（绕过 `unicode61` 不做 CJK 分词的缺陷）；`_or_query_groups` 支持大写 OR 组；LIKE 路径多词 AND + OR；`recall_tool._normalize_expand_args` 拒绝反向 `lo>hi` span。

**验证**：`hanbao:0.0.24` 构建成功，容器跑通无报错。

### 上游 v2.1.0 视频传递修复：跨 provider 视频数据（2026-08-14，P0-10 #6495）

函包只走 OpenAI 兼容，故跳过 `openai_response_provider.py`（Responses API）与 `anthropic_provider.py`（Anthropic）两个 provider 专属改动，只移植通用核心。

- [修改] `src/qwenpaw/agents/model_factory.py` — 视频传递边界修复 + response_api 支持：`_format_openai_video_block` 加 `response_api` 参数（`input_video` vs `video_url`）；`_substitute_video_blocks` 跳过 `assistant` role（视频块在 assistant 内容里多数 provider 不合法）；`_replace_video_placeholders` 只处理 `user`/`tool`/`system`；`_promote_tool_result_videos` 同步 `response_api`
- [修改] `src/qwenpaw/providers/multimodal_prober.py` — 新增 `evaluate_video_probe_answer`（视频颜色探测答案评估抽成公共模块，供所有 provider 复用同一套蓝系关键词 + 日志）
- [修改] `src/qwenpaw/providers/openai_provider.py` — `_evaluate_video_response` 委托给 `evaluate_video_probe_answer`（删本地 `_BLUE_KW` 重复逻辑）

**验证**：`hanbao:0.0.23` 构建成功，容器跑通无报错。

### 上游 v2.1.0 渠道修复移植：渠道身份泄漏 / 自定义网关端点（2026-08-14，P0-1#6382 / P1-12#6907）

- [修改] `console/src/pages/Chat/sessionApi/index.ts` — P0-1 / #6382：新增 `resetWindowIdentity()`；`getSessionIdentity()` 增强（window 全局仅在仍能解析到当前列表 session 时才信任，否则 fallback 默认，防止切 Agent 后继承旧 channel/已删除渠道）
- [修改] `console/src/pages/Chat/index.tsx` — P0-1 / #6382：4 处改用 `sessionApi.getSessionIdentity()` 替代直接读 `window.currentUserId/currentChannel`；切 Agent 时调用 `resetWindowIdentity()`
- [修改] `src/qwenpaw/app/channels/{feishu,qq,wecom,xiaoyi,yuanbao}/` + `config.py` — P1-12 / #6907：渠道 `domain` 支持自定义 http(s) 网关端点（私有/自定义部署）；feishu 新增 `_sdk_domain()` 统一返回 SDK base URL

**验证**：`hanbao:0.0.17` 构建成功（前端 TSX 重新编译），容器跑通无报错。

**后续**：P0-1 #6546/#6602 见下方「渠道完整性修复」小节；P1-14 #6543/#6769 见下方「OneBot 文本/媒体 + 引用回复」小节。

### 上游 v2.1.0 渠道/构建修复移植：钉钉凭据 / Monaco CSS 守卫（2026-08-14，P1-15 / P1-20）

- [修改] `src/qwenpaw/app/channels/qrcode_auth_handler.py` — P1-15 / #6709：钉钉组织应用审批的二维码认证，新增 `_DINGTALK_PENDING_STATUSES`/`_DINGTALK_FAILED_STATUSES` 与 `_clean_str`（中间态持续轮询、`null` 不转 `"None"`）
- [修改] `console/package.json` + `console/vite.config.ts` + 新增 `console/scripts/verify-monaco-css.mjs` — P1-20 / #6639：生产构建守卫（断言 Monaco 样式表未被 stub 掉）

> ⚠️ 备注：P1-20 是针对 Coding Mode 的 Monaco 编辑器 CSS。函包虽已砍 Coding Mode，但 `monaco-editor` 依赖 + `monacoSetup.ts` + `main.tsx` import 仍残留（见 I-024）。该修复对函包价值存疑但无害，已保留；Monaco 残留待阶段3 收尾清理。

### 上游 v2.1.0 渠道完整性修复：切 Agent 会话恢复 / session integrity（2026-08-14，P0-1 #6546 / #6602）

P0-1 渠道完整性三个提交全部落地（#6382 已在前一小节）。

- [修改] P0-1 #6546「切 Agent 会话恢复」：引入 `sessionApi.getActiveOwner/isActiveOwner` epoch 机制（切 Agent 后丢弃旧 Agent 的异步结果）+ `isLocalTimestampId` 过滤临时本地 session id。`sessionApi`/`useSessionListData`/`ChatSessionInitializer`/`agentStore`/`sessionListStore` git apply 干净；`ChatSessionDrawer`/`Chat/index.tsx` 因函包已删 `codingMode` 致上下文偏移，手工移植
- [修改] P0-1 #6602「session integrity」：客户端消息 ID（`clientMessageId`/`QWENPAW_CLIENT_MESSAGE_ID_KEY`）+ 重连快进（`wrapReplayFastForward`）+ 会话分组持久化（`useCollapsedSessionGroups`）。14 个文件 git apply 干净；`Chat/index.tsx`/`ChatSessionDrawer/index.tsx`/`chats/utils.py`/`constant.py` 手工移植（含依赖确认 `SYNTHETIC_USER_MESSAGE_TAGS` 函包已有、`_is_synthetic_user_message` 核心逻辑独立于 scroll 重构）

**验证**：`hanbao:0.0.19` 构建成功，容器跑通无报错。

### 上游 v2.1.0 OneBot 文本/媒体顺序 + 引用回复（2026-08-14，P1-14 #6543 / #6769）

P1-14 两个提交全部落地（均手工移植，因 onebot/channel.py 已被 P0-2 #6676 安全加固改过 125 行，import 区 / `_EVENT_TASK_HARD_CAP` 后 / `__init__` 三处叠加冲突）。

- [修改] P1-14 #6543「文本/媒体顺序 + 媒体 base64」：
  - 新增链接清理（`_clean_links`/`_clean_inline_text`/`_clean_onebot_plain_text`，Markdown 链接转裸 URL 供 QQ 自动识别）+ 媒体 base64（`_local_path_from_media_ref`/`_local_media_base64_ref`/`_normalize_media_ref[_sync]`）
  - `send`/`send_media`/`_send_file` 重构：新增 `send_content_parts`（按原文/媒体顺序发送）、`_resolve_target`/`_send_segments` 抽公共发送逻辑
  - `config.py` OneBotConfig 新增 `media_base64`/`media_base64_max_mb`；前端 `channel.ts` + `ChannelDrawer.tsx`（开关 + 大小上限）+ en/zh locale（跳过 id/ja/ru/vi/pt-BR）
- [修改] P1-14 #6769「引用回复保真」：QQ 群聊引用回复时，拉取被引用消息（`get_msg`）并拼入上下文。新增 `_unescape_cq_value`（CQ 码反转义）+ `_normalize_onebot_segments`（array/CQ 码字符串统一解析）+ `_reply_message_id`/`_get_quoted_message_segments`/`_with_quoted_context` 等 11 个 helper；`_handle_message_event` 重构（self_id 提前设置 + 引用处理放在 mention 门之后避免无谓 I/O）；`_resolve_file_urls` 改为按 file segment 索引提取 file_id

**验证**：`hanbao:0.0.21` 构建成功，容器跑通无报错。

## 阶段 4 · 容器化

### 容器镜像合规：随附 LICENSE / NOTICE / 修改记录（2026-08-17，I-002 / I-003）

hanbao 是 QwenPaw 的派生作品（再分发者），即便只分发镜像（不含源码），Apache-2.0 §4(a)(b)(d) 仍强制随附许可文件。上游 `deploy/Dockerfile` 原样不含任何 LICENSE/NOTICE 拷贝，故本轮修复：

- [修改] `deploy/Dockerfile`（runtime 阶段，带 `[hanbao modification]` 标注）— 追加：
  ```dockerfile
  COPY LICENSE NOTICE /app/
  COPY docs/CHANGES-FROM-UPSTREAM.md /app/docs/
  LABEL org.opencontainers.image.licenses="Apache-2.0"
  LABEL org.opencontainers.image.source="https://github.com/agentscope-ai/QwenPaw"
  LABEL org.opencontainers.image.description="hanbao (函包), derived from QwenPaw v2.0.1"
  ```
  镜像内 `/app/LICENSE`、`/app/NOTICE`、`/app/docs/CHANGES-FROM-UPSTREAM.md` 随分发物提供，履行 §4 义务。
- [修改] `.dockerignore`（带 `[hanbao modification]` 标注）— 末尾追加白名单例外：
  ```
  !LICENSE
  !NOTICE
  !docs/CHANGES-FROM-UPSTREAM.md
  !docs/license-compliance.md
  ```
  原因：`.dockerignore` 第 6 行 `*.md` 会排除 `docs/*.md`，若不放开白名单，上方 `COPY docs/CHANGES-FROM-UPSTREAM.md` 会报 file not found。I-002 与 I-003 为连体问题，必须同批改（仅改一个会撞墙）。
- [验证方式] 构建后执行 `docker run --rm hanbao:<tag> sh -c "ls -l /app/LICENSE /app/NOTICE /app/docs/CHANGES-FROM-UPSTREAM.md"`，三者均存在且非空。
- [合规] 本改动仅触及分发物合规层，未触碰 R2 红线文件（LICENSE/NOTICE/合规文档本身未被批量替换修改）。

### 容器镜像瘦身：砍桌面栈 + Chromium，基础镜像换 Python+uv（2026-08-17，I-004）

浏览器工具 `browser_use` 已确认砍掉（渠道聊天为主，浏览器自动化用不上），本次完成镜像瘦身：

- [修改] `src/qwenpaw/agents/tools/__init__.py` — 移除 `browser_use`、`desktop_screenshot` 两个内置工具注册
- [修改] `src/qwenpaw/agents/react_agent.py` — 移除两工具的 hook 超时注册
- [修改] `src/qwenpaw/agents/memory/proactive/proactive_responder.py` — 移除 `browser_use`/`desktop_screenshot` 的 import 与工具装配
- [修改] `src/qwenpaw/agents/memory/proactive/proactive_utils.py` — 移除 proactive 记忆的"屏幕活动分析"调用块
- [修改] `pyproject.toml` — 移除 `playwright`/`mss`/`pywebview` 三个依赖（browser_use / desktop_screenshot / 桌面 GUI 专属；pywebview 仅在 `desktop_cmd.py` 惰性 import，缺失优雅降级）
- [修改] `deploy/Dockerfile` — runtime 基础镜像 `node:slim` → `agentscope/uv`（Python+uv，去 Node 运行时）；删除 XFCE4/Xvfb/dbus-x11/Chromium+依赖库/fonts-liberation/vim；`build-essential` 改为临时安装后 `apt-get purge` 不进最终镜像；精简 supervisord 的 `app` 程序环境变量
- [修改] `deploy/config/supervisord.conf.template` — 移除 `dbus`/`xvfb`/`xfce4` 三个程序（仅服务浏览器 GUI），`app` 程序去掉 `DISPLAY`/`PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH`
- [保留] LICENSE/NOTICE/CHANGES + OCI labels（见 I-002，合规层不动）
- [删除] 孤儿文件 `browser_control.py`/`browser_snapshot.py`/`desktop_screenshot.py` 已于 2026-08-18 经用户授权删除（commit `2e54cab`）。删除方式：`rm` + `git add -u`，**未使用 `git rm`**（本环境 `git rm` 曾因陈旧 `.git/index.lock` 误暂存删除整个 `src/qwenpaw/agents/` 子树 92 文件，已 `git reset --hard` 全量救回，零损失）
- [目标] 镜像体积从 ~4GB 降至 ≤800MB
- [构建验证 2026-08-18] `DOCKER_BUILDKIT=0` 直连构建成功，镜像 **1.91GB**（~4GB 砍半）。中途两处修复（[hanbao modification]）：① runtime 基础镜像 `agentscope/uv` → `python:3.12-slim`（`agentscope/uv` 为纯 uv 执行器、无 `/bin/sh`、无 apt，导致 `RUN apt-get` 崩）；② `COPY --chmod=755` → `COPY` + `RUN chmod +x`（旧版构建器不支持 `--chmod`）。体积构成：venv 746MB（Python 依赖绝对大头）+ apt 系统库/字体层 ~1GB；Chromium/Xvfb/xfce4 已确认剥离。剩余 800MB 目标需 venv 依赖树瘦身（钉钉/飞书/Twilio/本地模型 SDK 死重 ~300MB+，dingtalk 为顶层 import 有风险），列为独立子阶段，按铁律不在此会话闷头执行（详见 known-issues I-004）。
- [最终验收 2026-08-18] 删死代码 + 固化 P0 修复后重建：47/47 步、`BUILD_EXIT=0`、镜像 **1.93GB**（相较 1.91GB 的 +20MB 属上游 apt/pypi 包版本波动，非回退）。**干净容器验收全绿**（`docker run` 不挂任何宿主目录）：桌面栈（chromium/Xvfb/xfce4/dbus/node/npm）`which` 全无输出；`Python 3.12.14` + uv 就位；镜像内前端产物 `/app/src/qwenpaw/console/`（assets + hanbao-logo.jpg）完好；supervisord 仅 `app` 单进程（桌面栈进程已从 template 移除）10s 后 RUNNING；根路径返回真实 React 页（`<title>hanbao Console</title>`、`<div id="root">`）而非 `console is not available` 错误 JSON；`auth/status` → `{"enabled":false,"has_users":false}`；容器日志 `traceback`/`IndentationError`/`ImportError`/`browser_use`/`playwright`/`desktop_screenshot` 零命中。
- [venv 瘦身第一刀 2026-08-18] 前置影响分析（known-issues I-004）确认：渠道注册逐渠道独立 import + try/except 容错（仅 console 必加载），移除 SDK 不会崩启动。用户拍板「保持多渠道，只砍本地模型残留」→ 删 `transformers`(54M)/`modelscope`(33M)/`huggingface_hub`（本地 LLM 已砍，src 零 import，`local` extra 清空），**保留 `onnxruntime`**（markitdown→magika→document_reader 技能链，连带 sympy）。重建后镜像 **1.93GB → 1.78GB**（-150MB 含连带依赖），venv 746M→629M。干净容器验收全绿：认证默认开 `{"enabled":true,"has_users":false}`（I-007 生效，entrypoint 打印中文首设密码引导）、18 渠道注册完整、markitdown CLI 实测可用。**800MB 经实测评估极难达成**（venv 629M + 系统层 ~700M+，需评估 ≤1.5GB 务实线）。

### P0 修复 · provider_manager 语法错误致服务无法启动（2026-08-18）
- **文件**：`src/qwenpaw/providers/provider_manager.py`
- **问题**：v2.1.0 移植（`d4eb42a`）遗留一处孤立的 `if provider_id is not None:`（无 body），触发 `IndentationError`，导致整条 import 链崩溃、服务完全无法启动（属 P0 阻断级）。
- **修复**：删除该孤立 `if`，保留下方语义完整的 `if (provider_id is not None and self.active_model.provider_id != provider_id): return False`。commit `b95b02c`。
- **验证**：干净容器中 app 稳定 RUNNING、8088 返回 200、日志零 `IndentationError`。

## 阶段 5 · FPK 打包

### I-007 镜像层落地（2026-08-18）：默认开启 Web Console 认证
- **前置确认**：`config.py:2361` `allow_no_auth_hosts` 默认 `["127.0.0.1","::1"]`（仅 loopback），`trusted_proxies` 默认空，开认证后 LAN 不会被误免登，安全无需改。
- **deploy/entrypoint.sh** [hanbao modification]：新增 `export QWENPAW_AUTH_ENABLED="${QWENPAW_AUTH_ENABLED:-true}"`（默认开，用户 `-e ...=false` 可关）+ `print_auth_banner()` 开启引导；原 `warn_if_auth_off_container_bind` 仅显式关闭时触发。
- **deploy/Dockerfile** [hanbao modification]：新增 `ENV QWENPAW_AUTH_ENABLED=true` 双保险。
- **未做（待阶段 5 向导）**：FPK 安装向导收集管理员账号密码 → 注入 `QWENPAW_AUTH_USERNAME`/`QWENPAW_AUTH_PASSWORD` → `auto_register_from_env()` 首启自动建账号。依赖飞牛 FPK 打包规范（本环境暂无）。
- 改完按铁律未立即构建，待用户说"测一下"再重建验证。

_（其余 FPK 打包待执行）_

---

## 未修改声明

除本文件记录的改动外，hanbao 中其余代码均来自上游 QwenPaw v2.0.1，其著作权归 The QwenPaw Authors 所有，按 Apache License 2.0 条款授权使用。
