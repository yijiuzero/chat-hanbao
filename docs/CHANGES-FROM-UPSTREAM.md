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

**收尾补齐（2026-08-21）：** 初始移除时漏网两处，本次补齐，确保「桌面端整条线砍掉」彻底无残留：
- `src/hanbao/app/_app.py` — 删除 `/api/desktop/shutdown` 端点（其函数体内 `from ..tauri.env import ...` 引用已删的 `src/hanbao/tauri` 侧车模块，属悬空引用，调用即 500）。
- `tests/unit/tauri/test_entry.py`、`tests/unit/tauri/test_sidecar_logging.py` — 删除仍 `import hanbao.tauri` 的两个必挂孤儿测试（pytest 收集期即 ImportError）。
- 验证：`_app.py` 经 `py_compile` 通过；`HANBAO_DESKTOP_PORT` 常量仍在 `constant.py`（port.py 顶层 import 安全）；频道 import 零残留；`desktop_cmd.py` 已不存在、无悬空引用。

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
- [已删] `console/scripts/verify-monaco-css.mjs` — 孤儿文件（.mjs 不被 tsc 编译、script 已删不调用），已于 2026-08-20 `9337598` 提交删除，`console/scripts/` 目录已清空

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
- **已验收（2026-08-18 重建后干净容器实测）**：`auth/status` → `{"enabled":true,"has_users":false}`，entrypoint 打印中文引导「Web Console 认证已启用：首次打开页面将进入注册页，请设置管理员密码」。详见阶段 4 venv 瘦身第一刀验收记录。
- **未做（待阶段 5 向导）**：FPK 安装向导收集管理员账号密码 → 注入 `QWENPAW_AUTH_USERNAME`/`QWENPAW_AUTH_PASSWORD` → `auto_register_from_env()` 首启自动建账号。依赖飞牛 FPK 打包规范（本环境暂无）。

### FPK 部署模式确定（2026-08-18）：预构建镜像随 FPK 分发，飞牛不执行 docker build
- **决策过程**：先后考虑「推 Docker Hub」→ 用户指出飞牛应用以 FPK 形式分发+更新，无需外部仓库 → 最终拍板**上架飞牛官方应用中心**、镜像随 FPK 自带（安装时 `docker load`，更新发新 FPK 覆盖）。
- **deploy/save-image.sh** [hanbao modification，新增]：`docker save hanbao:latest -o <tar>` 导出镜像随 FPK 打包；支持 `BUILD=0` 跳过构建、自定义输出路径。
- **deploy/fpk/info.md** [hanbao modification，新增]：应用信息清单草稿（应用 ID/展示名「函包 hanbao」/版本 0.1.0/协议 Apache-2.0/端口 8088/架构 linux/amd64/渠道微信+OneBot 等；[飞牛规范待定] 字段：manifest schema/图标/权限/镜像打包方式/安装向导凭据注入/数据持久卷）。
- **docker-compose.yml** [hanbao modification]：`image: agentscope/qwenpaw:latest` → `${HANBAO_IMAGE:-hanbao:latest}`（FPK 内置镜像用默认值即可，无需注入外部地址）；端口 `127.0.0.1` → `0.0.0.0`（LAN 可达，Web Console 认证已默认开，安全）。
- **保留**：`deploy/Dockerfile` 两个 agentscope 阿里云 ACR 构建镜像（node/uv）仅影响开发者本机构建（已缓存），与飞牛分发无关。
- **卡点（诚实）**：真正的 `.fpk` 封装（manifest/图标/权限/安装向导）需飞牛官方 FPK 打包规范，本地无文档。需用户开代理供查询或提供示例。

### FPK native 脚手架落地（2026-08-19）
- **形态拍板：native**（非 docker-project）。docker-project 由应用中心在生命周期钩子前就 `compose up`，离线内置镜像尚未 `docker load` 会报 No such image；native 由 `cmd/main` 自己 `docker load` + `up`，完全掌控时序。
- **新增 `deploy/fpk/` 脚手架（全部 [hanbao modification]）**：
  - `cmd/main`：原生生命周期控制器（start/stop/status/install/uninstall）；start 时先 `docker load` 内置 tar（已存在则跳过），再 source `$TRIM_PKGVAR/hanbao.env` 注入 `HANBAO_AUTH_*` 后 `docker compose up -d`。
  - `install_callback`：安装向导收集到的 `HANBAO_AUTH_USERNAME`/`HANBAO_AUTH_PASSWORD`（字段名=环境变量名，无 wizard_ 前缀）持久化到 `$TRIM_PKGVAR/hanbao.env`，供 cmd/main 每次 start 复用（I-007 首启自动建账号闭环）。
  - `app/docker/docker-compose.yaml`：`image: hanbao:latest` + `pull_policy: never` + `0.0.0.0:${TRIM_SERVICE_PORT:-8088}:8088` + named volume 持久化（hanbao-data/secrets/backups）。
  - `wizard` / `manifest` / `config/{resource,privilege}` / `app/ui/config`：安装向导、应用清单、资源/权限、桌面入口。
  - 图标：`ICON.PNG`(64) / `ICON_256.PNG`(256) + `app/ui/images/icon_64.png`、`icon_256.png`（2026-08-18 由用户原创水墨图中心裁切生成）。
- **修正 `deploy/save-image.sh`**：注释「飞牛自动 docker load」不实（仅 docker-project 形态），改为 native 由 cmd/main 自 load；默认输出路径改为 `deploy/fpk/app/hanbao-amd64.tar`（cmd/main 取值位置）。
- ✅ **schema 已于 2026-08-19 第二批对照官方规范逐条校正**（见下「FPK 脚手架按官方规范校正」）。`fnpack` 打包与飞牛实测仍需用户环境+代理。

### FPK 脚手架按官方规范校正（2026-08-19 第二批）
- **拉取官方规范**：developer.fnnas.com 本机直连可达（无需代理）。逐篇核对 应用框架 / fnpack / manifest / 环境变量 / 用户向导 / 应用入口 / 应用资源 / 应用权限 / Docker 案例，确认前批 native 脚手架与官方 schema 多处冲突（`fnpack build` 会直接报错）。
- **形态切换：native → docker-project**：官方规范仅以 docker-project 作为容器应用标准路径，`config/resource` 的 `docker-project` 声明即飞牛接管容器生命周期的开关；前批担心的「离线镜像未 load 就 compose up 报 No such image」由 `pull_policy: never` + `install_callback` 预载 tar 彻底化解。`cmd/main` 改为 status-only（start/stop 由飞牛管理），`install_callback` 负责 `docker load` 内置 tar + 写 `$TRIM_PKGETC/hanbao.env`。
- **schema 逐条校正**：
  - `manifest`：由臆造 YAML 改为官方 INI（`appname`/`display_name`/`desc`/`source`/`platform`/`maintainer`/`os_min_version`/`desktop_uidir`/`desktop_applaunchname`/`service_port`/`checkport`/`ctl_stop`）；移除非字段 `appid`/`name`/`description`/`icon`/`category`/`arch`。
  - `wizard`：由单文件改为 `wizard/` 目录（install/config/upgrade/uninstall 四个 JSON 数组向导），字段 `type`/`field`/`label`/`rules`/`password`。
  - `config/resource`：改为 `docker-project` JSON（`projects[].name=hanbao, path=docker`）。
  - `config/privilege`：改为 package 用户 JSON（`run-as: package`, `username/groupname=hanbao`）。
  - `app/ui/config`：改为 `.url` 入口（`hanbao.main`，`type: iframe`, `port: "8088"`, `url: "/"`, `allUsers: true`）。
  - `app/docker/docker-compose.yaml`：移除 `version`；`env_file: ${TRIM_PKGETC}/hanbao.env` 注入凭据；挂载 `$TRIM_PKGVAR:/app/working` 持久化（替代原 named volume）；`pull_policy: never`。
  - `deploy/save-image.sh`：输出路径改 `deploy/fpk/app/docker/hanbao-amd64.tar`（落 `app/docker/`，install 后位于 `$TRIM_APPDEST/docker/` 供 load）。
- **校验**：bash 语法 + 7 个 JSON 合法 + fnpack 必检结构（manifest/ICON.PNG/ICON_256.PNG/app/cmd/config/wizard + app/ui）全部齐备。
- ⚠️ 待 fnOS 实测确认项（**已于 2026-08-19 第三批按回退方案落地**）：compose `env_file: ${TRIM_PKGETC}/hanbao.env` 中 `TRIM_PKGETC` 是否由飞牛展开。无论飞牛是否展开，已改为双保险：`install_callback` 用 `tee` 同时写 `$TRIM_PKGETC/hanbao.env` 与 `$TRIM_APPDEST/docker/hanbao.env`，compose `env_file` 改用相对路径 `./hanbao.env`（指向 app/docker/ 下由 install_callback 生成文件），闭环不漏（I-007 首启自动建账号）。

### FPK 凭据回退落地 + I-019 闭环 + 文档清洗（2026-08-19 第三批，未构建）
- **FPK 凭据闭环缺口修复（🔴→✅）**：上批 compose 用 `env_file: ${TRIM_PKGETC}/hanbao.env`，但 install_callback 仅写 `$TRIM_PKGETC/hanbao.env`，若 fnOS 不展开 `TRIM_PKGETC` 则容器读不到凭据、退回首启注册页（重开 I-007 抢注窗口）。本批：`install_callback` 用 `tee` 双写 `$TRIM_PKGETC/hanbao.env` 与 `$TRIM_APPDEST/docker/hanbao.env`；compose `env_file` 改相对路径 `./hanbao.env`（飞牛 docker-project 执行 cwd 为 app/docker/，指向 install_callback 生成文件）。无论飞牛是否展开 TRIM 变量均成立。
- **I-019 彻底闭环（🔴→✅）**：`src/hanbao/agents/tools/file_io.py` 的 `read_file` 此前按纯文本读 .docx/.pdf/.xlsx（二进制乱码）。本批新增 `_read_file_text()`：按扩展名把 Office/PDF 路由到 `markitdown` CLI 转 Markdown（镜像内已装、PATH 可达；`shutil.which` 缺失则自动回退纯文本读），保留原行号/截断逻辑。Anthropic 侵权技能已删、markitdown（MIT）替代读能力正式接通。改/创建文档仍按计划放弃。
- **文档清洗（低风险编辑）**：
  - `README.md`：删 `docker pull/run yijiuzero/chat-hanbao`（未发布虚假 registry，与 FPK 离线自带镜像冲突）；快速开始改为「飞牛一键安装」为主 + 「手动 Docker 构建」为辅；FPK 状态 🚧→✅；版本口径统一为「基于 QwenPaw v2.0.1(fork) 并移植 v2.1.0」。
  - `deploy/fpk/info.md`：版本口径统一（fork v2.0.1 + 移植 v2.1.0）；镜像务实线标注「经用户 2026-08-19 拍板保留全部渠道 SDK 不砍，维持 1.78GB，≤1.5GB 目标作废」。
  - `docs/known-issues.md`：I-018 gitignore 根因已修 🟡→🟢；I-019 已闭环 🟡→🟢；I-021 LGPL 备案完成 🟡→🟢/已备案。
- **用户决策（2026-08-19）**：渠道 SDK **不砍**（即便当前仅启用微信+OneBot，其他渠道依赖保留不删），故镜像维持 1.78GB，≤1.5GB 瘦身目标作废。
- 校验：install_callback/compose bash 语法 OK；file_io.py `py_compile` 通过；`_read_file_text` 接入 `read_file` 调用链确认。
- 提交不构建（构建铁律）；R2 四文件全程零改动（CHANGES 仅手动追加本段，合规）。

_（其余 FPK 打包待执行：fnpack 封装 + 飞牛实测 + 上架）_

---

## 阶段 4.5 · 包名全量改名（qwenpaw → hanbao，2026-08-19）

**背景**：阶段 2 仅改了品牌展示名（Web/UI/TUI 文案），Python 包名 `qwenpaw`、环境变量 `QWENPAW_*`、数据目录 `~/.qwenpaw` 仍保留上游原名。2026-08-19 用户拍板全量改名——因 FPK 安装向导注入的凭据 env 名（`QWENPAW_AUTH_*`→`HANBAO_AUTH_*`）依赖改名，先于阶段 5 FPK 脚手架执行，避免三处 env 名返工。

**执行方式（带 R2 合规守卫）**：
- `src/qwenpaw` 目录 `git mv` → `src/hanbao`（含全部子模块）。
- 四档大小写映射 `QWENPAW→HANBAO` / `QwenPaw→Hanbao` / `Qwenpaw→Hanbao` / `qwenpaw→hanbao` 改写 **902 个文本文件**内容。
- 全局 `QWENPAW_*` 环境变量（含 `QWENPAW_AUTH_USERNAME`/`QWENPAW_AUTH_PASSWORD`/`QWENPAW_AUTH_ENABLED`）全部改名 `HANBAO_*`；`~/.qwenpaw` → `~/.hanbao`。
- `pyproject.toml`：`name = "hanbao"`，`[project.scripts]` 入口 `hanbao = "hanbao.cli.main:cli"`（保留 `copaw` 别名兼容）。
- 其余 6 个带 `qwenpaw` 文件名资产一并 `git mv`：`console/src/plugins/types/qwenpaw.d.ts`→`hanbao.d.ts`、`scripts/pack-tauri/qwenpaw.spec`→`hanbao.spec`、`website/public/qwenpaw-symbol.png|.svg`→`hanbao-*`、`website/public/qwenpaw_ip.png`→`hanbao_ip.png`、`website/src/components/QwenpawMascot.tsx`→`HanbaoMascot.tsx`。

**合规守卫（R2 红线，零违约）**：
- **整体跳过** `LICENSE` / `NOTICE` / `docs/license-compliance.md` / `docs/CHANGES-FROM-UPSTREAM.md` 四文件（本文件未被批量改写，仅此处手动追加记录）。
- **保留上游署名（I-016）**：8 个 `plugins/*/plugin.json` 的 `"author": "QwenPaw Team"`、locale `copyright: Qwenpaw PRIVATE LIMITED`、review-bot `QwenPaw Maintainer Team`、startup_profile `Author` 等署名行未改。
- **保留外部真实 URL**：`github.com/agentscope-ai/QwenPaw`、`qwenpaw.agentscope.io`、pypi `qwenpaw` 路径、`modelscope.cn` 等上游链接未伪造。
- **保留历史内容**：`website/public/release-notes/*`、`website/public/blog/*`、`docs/upstream-v2.1.0-adoption.md` 叙述性历史未改写。

**验收（全绿）**：
- `src/hanbao` 内零 `from/import qwenpaw`、零 `QWENPAW_*`（`__pycache__/*.pyc` 构建产物含旧串，已 gitignore）。
- `src/qwenpaw` 目录消失、`src/hanbao` 就位；`git diff --name-only HEAD` 共 **1328** 文件变更（含 7 个 `git mv` 重命名）。
- `deploy/` 下 `HANBAO_AUTH_ENABLED` 等已落地；R2 四文件 `git diff` 为空。
- 全仓残留 `qwenpaw` 仅余四类预期项：R2 合规文件、上游署名行、外部真实 URL、历史文档叙述。

**对已知条目的影响**：阶段 5「I-007 镜像层落地」中记录的 `QWENPAW_AUTH_ENABLED`/`QWENPAW_AUTH_USERNAME`/`QWENPAW_AUTH_PASSWORD` 现已统一为 `HANBAO_AUTH_*`（见 `deploy/entrypoint.sh`、`deploy/Dockerfile`、`docker-compose.yml`）。FPK 安装向导后续须注入 `HANBAO_AUTH_USERNAME`/`HANBAO_AUTH_PASSWORD`。

---

---

## 阶段 6 · 界面品牌化（前端视觉重做 + 加法，2026-08-19 起）

**背景**：用户要求「针对 hanbao 做一次加法，并且界面大改、有品牌特点」。接手核查发现：代码层产品名已是 `hanbao`、主色沿用 qwenpaw 同款橙 `#FF7F16`，但视觉骨架（logo/布局/组件/插画）仍是上游模板，仅换了名字未做差异化。故启动「界面品牌化 + 时间感知加法」双线。

**方向拍板（2026-08-19 用户）**：
- 界面品牌化**先做**（线2），时间感知**P0+P1 一次做全**（线1）。
- 配色 **A 蜜橘暖暖 `#FF8C42`** + 图形化「函包」logo + 可爱治愈风。
- 加法核心：解决「用户说感冒，跨天后还被当当前事实」痛点（根因：长期记忆 `MEMORY.md` 无时间戳/无 TTL，system prompt 日期注入显著性低）。

**方向二次调整（2026-08-20 用户）**：上传了一张高对比度水墨古典肖像（黑发东方女性 + 龙纹旗袍 + 流苏耳坠），要求把 logo（图 + favicon）全切到此图，**整体品牌基调从「可爱治愈」全切到「水墨古风」**。Mikas 聊天头像 **online.svg（红线）保留不动**，其它品牌元素（T6~T7 后续页面）顺势跟进。配色 token（`#FF8C42` 主色、辅助梯度）暂不动，待 T6 重做页面时再评估是否需要整体换色调（主色在水墨基底上还算和谐，留作待评估项）。**当日午后进一步拍板（AskUserQuestion）**：① 主色基调选「**墨黑 + 朱砂红**」——主色切换为朱砂红（亮 `#9E2B25` / 暗 `#C0392B`），原暖橘 `#FF8C42` 弃用、仅 logo 保留暖橘点缀（推翻 T5 的 A 暖橘主色）；② 装饰深度选「**关键面子页加水墨装饰**」（Login/侧边栏/聊天/控制台），后台几十个表单页仅靠 antd token 自动染水墨色、不改结构。详见下方「界面全量水墨化（T6+T7）」。

### 品牌基础（T5，2026-08-19，已完成）

- [修改] `console/src/App.tsx` — antd `ConfigProvider` token：`colorPrimary "#FF7F16"` → `"#FF8C42"`（脱离 qwenpaw 同款橙）+ `borderRadius: 10` + 辅助色 token（`colorPrimaryBg`/`colorPrimaryBorder`/`colorPrimaryLink` 统一为 A 方案暖橙梯度）。
- [修改] `console/src/**/*.{ts,tsx,less,css}` — 全仓散落硬编码品牌色统一为 A 方案：旧橙 `#ff7f16`/`#FF7F16`、蓝残留 `#1677ff` fallback、辅助 `#ff9d4d`/`#fff7e6` 全部替换为 `#FF8C42`/对应暖橙梯度（Python 脚本二进制读写保换行符，不污染图表数据系列色）。
- [修改] `console/public/logo-dark.svg` + `logo-light.svg` — 占位文字 logo → **图形化「函包」**（圆角信封/包裹抽象 + 暖橙高光，可爱治愈风，暗/亮双版）。
- [新增] `console/public/hanbao-icon.svg` — 函包图形 favicon；`console/index.html` `<link rel="icon">` 由 `/online.svg` 改为 `/hanbao-icon.svg`。
- **关键发现 + 品牌红线（用户拍板）**：`console/public/online.svg` 实为 0.3MB base64 **Mikasa 肖像**，是项目早就定的 **hanbao 图标（聊天头像/app 图标）**，注释 `[hanbao modification]`，被 `Chat/index.tsx` 与 `OptionsPanel/defaultConfig.ts` 引用。**保持 Mikasa 头像不换成函包图形**；后续任何品牌化不得擅自覆盖 `online.svg` 的 Mikasa 身份。favicon 是否也改回 Mikasa 待定（当前用函包图形）。

### 构建验证（2026-08-19，前端本地预览）

- console 依赖此前未安装；`npm install` 被本环境 10 分钟 Bash 超时打断，导致 `node_modules/@agentscope-ai/icons` 解压不全（`vite build` 报 `Could not resolve "./src/js/SparkEcommerceProductLine.js"`）。
- 修法：`rm -rf node_modules/@agentscope-ai/icons && npm install --prefer-offline --no-audit --no-fund`（缓存命中，约 1min 补齐缺失包）。
- `npx vite build`（跳过 `tsc` 全量类型检查，避免上游无关类型告警卡住）成功，耗时 2m43s，`dist/` 产出；`npx vite preview --port 4173` 起本地预览服务（HTTP 200，`<title>hanbao Console</title>`，favicon=hanbao-icon.svg）供查看品牌化效果。
- ⚠️ 该预览为纯前端（未接后端），仅能看到登录页/外壳品牌化；完整 UI（聊天页 Mikasa 头像等）需后端 + 认证，走 T1 镜像重建后在容器实测。
- 改动**未提交**（本次仅构建预览验证，尚未 commit；按铁律 docker 镜像重建 T1 待用户开 daemon+代理后执行）。

### Logo 二次品牌化（T5b，2026-08-20，已替换实现，待 commit）

背景：用户上传一张 1024×1024 高对比度水墨古典肖像（黑发东方女性 + 龙纹旗袍 + 流苏耳坠），要求把 logo（含 favicon）全切到此图，**品牌基调整体从「可爱治愈」改为「水墨古风」**。Mikas 聊天头像 `online.svg` **红线保留不动**。

- [新增] `console/public/hanbao-portrait-source.png`（824 KB，源图归档，1024×1024）；`scripts/_make_hanbao_portrait.py`（Pillow 缩放脚本 + `[hanbao modification]` 标注，处理：源图归档 + logo 用 240px 高缩图 + favicon 用 256×256 头肩特写裁剪）。
- [新增] `console/public/hanbao-portrait-logo.png`（77 KB，**水墨肖像 logo 用图**，比例缩到高 240px）；`console/public/hanbao-portrait-favicon.png`（77 KB，**水墨肖像 favicon 用图**，裁剪脸部+胸口上半部分，特写更紧凑）。`scripts/_make_hanbao_logos.py`（PIL+base64 写入脚本 + `[hanbao modification]`）。
- [修改] `console/public/logo-light.svg`（605 B → 103 KB）— 圆角信封+暖橙函包 → **白底水墨肖像卡片 + 深色 `#1f1f1f` 宋体 wordmark「hanbao」**（`viewBox="0 0 320 60"`，肖像卡片 `rect` 白底圆角 8 + 浅灰描边，SVG `<image>` 嵌 PNG base64，避免 React 端引入额外请求）。
- [修改] `console/public/logo-dark.svg`（605 B → 103 KB）— 同款肖像卡片（**白底不变**，适配暗色 header 上的"水墨卷轴/画框"质感），wordmark 改浅色 `#f5f5f5`；卡片描边在暗背景下换用 `#3a3a3a` 让"画框感"更稳（不会因白底在深色 header 上"飘"）。
- [修改] `console/public/hanbao-icon.svg`（454 B → 104 KB）— 函包图形 favicon → **水墨肖像 favicon**（`viewBox="0 0 64 64"`，clipPath 圆角 12，嵌上半身特写 PNG，整体图片 fill 区域 + 浅灰描边）。
- [删除] `console/public/hanbao-logo.jpg`（243 KB，8/17 旧 logo jpg，无任何引用，是孤儿；用 `rm + git add -u` 删除，按铁律不用 `git rm`）。
- **React 端零改动**：`Header.tsx:250` 与 `Login/index.tsx:103` 仍引用 `/logo-light.svg` 与 `/logo-dark.svg`，`index.html` 仍引用 `/hanbao-icon.svg`，路径与文件名全部不变。
- **品牌红线（Mikas 头像）**：未触碰 `console/public/online.svg`、未动 `Chat/index.tsx:2534` 与 `OptionsPanel/defaultConfig.ts:30` 的 `"/online.svg"` 引用。Mikas 仍是聊天头像/app 图标。
- **未 commit**（铁律：改完即 commit；本次含 7 个新文件 + 3 svg 重写 + 1 jpg 删除，工作树待提交。镜像重建视用户后续指令走「测一下」）。
- **遗留/待办（更新 2026-08-20 午后）**：① ~~亮色主题下登录页蓝灰渐变 + 水墨肖像 + `#FF8C42` 按钮的"水墨+暖橘"组合~~ —— 已被下方 T6 全量水墨化解决（登录页改水墨意境背景、按钮改朱砂红）；② ~~T6 时把 patch 米白/暗色页背景带入水墨风格做整体场景化~~ —— 已实现；③ Mikas 聊天头像在新品牌基线下"古典少女陪现代 AI" 是否违和——目前按红线不动，等用户反馈再议。

### 界面全量水墨化（T6+T7，2026-08-20，已实现并提交 45ebdd8）

背景：用户要求「内部整体界面还是 qwenpaw 的样子，大改界面样式、具 hanbao 特色，直接就都偏水墨风」。排查根因：`App.tsx` 视觉基底是 `@agentscope-ai/design` 的 `bailianTheme/bailianDarkTheme`（上游百炼设计系统），此前 T5 只是在上面贴了 `#FF8C42` 主色膏药；大量组件/页面 `.module.less` 仍残留上游 qwenpaw 硬编码暖橙/暖棕/蓝/冷灰。本次从根上重做（详见上文「方向二次调整」的拍板：墨黑 + 朱砂红、关键面子页加水墨装饰）。

- [修改] `console/src/App.tsx` — antd `ConfigProvider` token 全套重写为水墨 seed：`colorPrimary` 朱砂红（亮 `#9E2B25`/暗 `#C0392B`）、`colorLink` 同红系、`colorTextBase` 墨黑 `#1F1F1F`（暗 `#ECE9E3`）、`colorBgBase` 宣纸米白 `#F7F4ED`（暗墨灰 `#1A1A1A`）、`colorBgLayout` `#F2EEE4`（暗 `#161616`）、`colorBgContainer`/`colorBgElevated`、`colorBorder` 墨/白细分、`borderRadius 8`、`colorPrimaryBg/BgHover/Border` 朱砂浅底、`colorError` 朱砂红。**这是全站（含后台 T7 全部表单页）自动染水墨的杠杆点**。
- [修改] `console/src/styles/layout.css`（全局样式层）— 亮色 `body`/`.hanbao-layout`/`.ant-layout*`/`.page-content` 背景统一宣纸米白 `#F2EEE4`（带极淡墨晕 radial-gradient），暗色 `#141414` → 墨灰 `#161616`；16 处暗色强调 `#FF8C42` → 朱砂红 `#C0392B`；亮色菜单选中暖棕 → 朱砂浅底；追加水墨工具类（`.ink-title` 书法衬线标题 / `.ink-divider` 墨线 / `.ink-card` 宣纸卡片 / `.ink-seal` 朱砂印）；末尾新增**全局品牌变量桥接** `:root{--colorPrimary:#9E2B25}` + `html.dark-mode{--colorPrimary:#C0392B}`——组件里 `var(--colorPrimary,…)` 自动随明暗切红。
- [修改] `console/src/pages/Login/index.tsx` — 背景从上游蓝灰渐变（暗 `#0f0c29→#302b63` / 亮 `#f5f7fa→#c3cfe2`）→ **水墨意境**：亮色宣纸米白 + 双层淡墨晕 radial-gradient，暗色墨灰 + 顶部淡白晕；卡片白底细墨边；标题挂 `.ink-title` 书法体。
- [修改] `console/src/layouts/index.module.less`（侧边栏/顶栏）— qwenpaw 暖橙/暖棕（`#FF8C42`、`rgba(255,127,22,…)`、`rgba(43,18,0,…)`、`#f9f8f4`、`#d45b0a` 等）批量替换为水墨色系（朱砂红 `#C0392B`、墨灰 `#161616`、宣纸 `#F2EEE4`）。
- [修改] 全仓 **46 个组件/页面文件**（`.module.less`/`.tsx`/`.ts`）— [新增] `scripts/_inkwash_rebrand_colors.py`（`[hanbao modification]`，二进制读写保换行符）统一映射 **195 处**：`#FF8C42→#C0392B`、`rgba(255,127,22,*)→rgba(192,57,43,*)`、`rgba(43,18,0,*)→rgba(31,31,31,*)`（暖棕→墨色）、`#f9f8f4/#f9f7f3→#F2EEE4`、`#1a1a1a→#161616`、`#1677ff/#3b82f6→#5C6B73`（qwenpaw 蓝→石板灰，图表 canvas 安全）、`#d45b0a→#9E2B25`；测试期望（`channelIcons.test.ts`）同步更新。残留冷蓝灰 `#f5f7fa`/`#f7f8fc`（ApprovalCard、Models）手工换宣纸 `#F2EEE4`。
- **保留不动**：`@agentscope-ai/*` 组件库 import、外部文档 URL（`qwenpaw.agentscope.io`、PyPI——合规 R2「外部 URL/历史文档保留」）、中性灰（`#f5f5f5`/`#fafafa`/`#f0f0f0` 等 antd border/fill 回退值，水墨兼容）；**Mikasa 头像 `online.svg` 红线零碰触**。
- **复验**：全仓品牌色 grep **零残留**（`#FF8C42/#FF7F16/#1677ff/#3b82f6/#f5f7fa/#f7f8fc/rgba(255,127,22,…)/rgba(43,18,0,…)` 全部归零）。
- **已提交（2026-08-20，commit 45ebdd8，62 文件 +632/−324）**：含 T5b logo 二次品牌化 + T6/T7 全量水墨化 + 文档同步。镜像重建（T1）按用户「测一下」指令于同日执行，见下方「镜像重建与容器验收（T1，2026-08-20）」。

### 镜像重建与容器验收（T1，2026-08-20，用户「测一下」触发）

- 环境：Docker daemon 29.6.2 在跑；`DOCKER_BUILDKIT=0` 直连构建（基础镜像层缓存命中 + 无代理 npm 直连），**48/48 步成功**，新镜像 `c52b22bb54e8` / `hanbao:latest`（1.79GB，前端 dist 重编 + 后端层全缓存）。
- console-builder 阶段**重新构建前端**（console/src 在 45ebdd8 改动 → npm ci + tsc + vite build 重跑，输出正常），新 dist 已 COPY 进镜像。
- 干净容器验收（`hanbao_verify`，**不挂宿主 src**）：等 ~60s 启动完成 → `curl :8088` body 含 `<title>hanbao Console</title>`（真实前端页，非错误 JSON）；`/api/auth/status` = `{"enabled":true,"has_users":false}`（I-007 认证默认开）；`/var/log/app.err.log` 无 traceback/FATAL/ERROR（计数 0，正常 INFO 日志含 "Background startup completed"）。**验收全绿**。
- ⚠️ 本次构建的镜像 LABEL 仍为旧文案 "derived from Hanbao v2.0.1"（构建读的是启动时旧 Dockerfile）；LABEL 已修复为 "derived from QwenPaw v2.0.1"（合规修正，见 known-issues 变更历史），**下次重建生效**，仅元数据差异不影响功能。

### 去 qwenpaw 味重构（2026-08-20，f2e3468 ~ a788cdf，已提交）

背景：用户镜像实测后反馈「界面视觉差不多了，但全部页面尽量重构、不要有 qwenpaw 味道」。排查根因：`@agentscope-ai/design`（AgentScope Spark Design，MIT）= 上游 qwenpaw 的 UI 库，经 `bailianTheme` 注入大量 Spark 默认 token + Spark 自研组件（antd 薄封装，视觉由 antd token 控）+ 阿里 CDN 空态插画 + Spark 图标 + **百炼紫 `#615ced`**（Spark 主题主色，两轮批量替换均漏网）。

- [f2e3468] 界面细节打磨 6 处：亮色 header/sider 加细墨分割线（解决同色"一片平"）、登录页 logo drop-shadow + 卡片微宣纸渐变、聊天输入区/欢迎区纯白→宣纸白 `#FDFCF9`、菜单 hover 极淡朱砂底。
- [2d5973d] **全站去味 v1**：① `App.tsx` antd token **全量化覆盖 bailianTheme 默认值**（补全 colorPrimaryHover/Active/Text 系、colorText 灰阶、colorFill 系、colorBgSpotlight/Mask、colorInfo/Success/Warning/Error 语义色、boxShadow 系、borderRadiusSM）——antd/Spark 组件形态全面脱离百炼默认，全站生效；② `layout.css` 隐藏 Spark Empty 阿里 CDN 插画（`hanbao-empty-image`，断外网依赖）+ 空态文字水墨化 + 亮色卡片 hover 墨影；③ 清漏网旧暖橘 `rgba(255,157,77,1)` 6 处（Header/Sidebar 小红点、激活指示、SkillPool Badge）→ 朱砂红。
- [297cc80] **百炼紫清理**：`#615ced`/`rgba(97,92,237,*)` **9 文件 46 处** → 朱砂红（ThemeToggleButton 主题切换选中、ModelSelector 模型激活、Agent/Skills/Workspace、Settings/Agents/Models、ImportHubModal、Control/Sessions、layout.css 选中/激活指示）；`scripts/_inkwash_rebrand_colors.py` 追加百炼紫两条规则（幂等可重跑）。
- [a788cdf] **聊天页欢迎语 hanbao 化**：`locales/zh.json`+`en.json`+`OptionsPanel/defaultConfig.ts` fallback——greeting "你好，我今天能帮你做什么？"→"你好，我是 hanbao。"、description 去"智能助手"腔→函包人设（陪伴+记忆+工具能力）、prompt1/prompt2 去"旅程/问技能"腔→"跟我聊聊今天怎么样？"/"看看我能帮你做什么？"。Mikasa 头像 `/online.svg` 红线未动。
- **保留项（决策）**：Spark 图标库（40+ 种遍布全站，线条图标较中性，替换 antd 映射风险大收益低）；聊天气泡 SDK 深层样式（CSS-in-JS 哈希类名+动态渐变，覆盖风险高）；`@agentscope-ai/design` import（组件即 antd 封装，token 已控）；外部 qwenpaw 文档 URL（合规 R2）。
- **复验**：全仓品牌色 grep **零残留**（暖橘/百炼蓝/百炼紫/暖棕/冷灰 15 种色系全无）；locale 品牌名残留 0。

### 镜像二次重建与容器验收（T1b，2026-08-20，用户「测一下」触发）

- [3b28257] **踩坑修复**：Dockerfile 的 LABEL 修复（55e2819）触发 legacy builder apt 层缓存失效真跑，暴露 `E: Unable to locate package fonts-wqy-microhei`（**Debian 源已移除该包**，此前一直靠缓存未真跑）→ 移除 microhei（保留 zenhei 文泉驿正黑已够中文字体）。
- **重建成功**：`DOCKER_BUILDKIT=0` 48/48 步，新镜像 `c9d492804176`/`hanbao:latest` **1.78GB**（apt 真跑成功 + console-builder 重编去味前端 + uv 全依赖真装）。
- **干净容器验收全绿**（`hanbao_verify`，不挂宿主 src）：等 ~60s → `:8088` `<title>hanbao Console</title>`、`/api/auth/status`=`{"enabled":true,"has_users":false}`、`/var/log/app.err.log` 异常计数 0。容器保留运行中供预览。
- **教训**：改 Dockerfile 任意指令（哪怕后段 LABEL）会使 legacy builder 后续 apt/RUN 层缓存失效真跑，可能暴露此前从未真跑的环境问题——改 Dockerfile 后的构建要格外留意系统层。

### 待做（T6~T9，2026-08-19 排期）

- [x] **[T6] 关键页面品牌化（2026-08-20 已实现并提交 45ebdd8）**——登录页/侧边栏/顶栏/全局底色全面水墨化 + 水墨工具类（详见上方「界面全量水墨化（T6+T7）」）；聊天页/控制台剩余深度装饰（空态插画/气泡质感微调）可随镜像实测后的视觉反馈再打磨。
- [x] **[T7] 后台页统一换色（2026-08-20 已实现并提交 45ebdd8）**——Agent 配置/MCP/技能/工具/工作区、Control 渠道/定时任务等全部保留上游布局，仅靠 antd token 自动染水墨色 + 46 文件硬编码色批量替换清残留（详见上方）。
- [x] **[T8] 时间感知 P0（2026-08-20 已实现，commit d838618）**：① 新增 `_annotate_memory_dates()`（`reme_light_memory_manager.py`，扫描答案中 `YYYY-MM-DD`，取自每日笔记 `YYYY-MM-DD.md` 路径）前置「记忆关联日期 + N天前，属历史记忆」提示，注入 `auto_memory_search`（:560）与 `memory_search` 工具（:489）——直接治「跨天还说我现在感冒」；② `build_env_context`（:185）日期行改为独立醒目块 + 时间感知指引（「旧记忆属历史不代表当前状态」）；默认时区 `UTC`→`Asia/Shanghai`（修 UTC+8 深夜「今天」差一天）。
- [x] **[T9] 时间感知 P1（2026-08-20 已实现，commit d838618）**：① 写入端 as-of 日期 + 临时状态 TTL 指令通过 `dream`（:518）/ `summarize`（:603）的 `hint`/`memory_hint` 参数喂入 ReMe（`_MEMORY_TIME_HINT` 常量：临时身体状态默认有效期≤7天）；② 记忆指引加时间提示——`agents/memory/prompts.py` MEMORY_GUIDANCE 中/英模板新增「🕒 时间感知」小节（引用用户当前状态前先确认记忆是否近期）。⚠️ P1 写入端能否真正生效取决于 ReMe 内部是否消费 `hint`/`memory_hint`（ReMe 为外部 pip 包，其 prompt 不可在本仓改）；检索端 T8 已提供稳健兜底。
- 加法延伸（待定）：文档改/创建能力（I-019 关联，需 python-docx/openpyxl 自研简化版）按用户后续需求评估。

### 记忆/上下文增强·轻量补强（2026-08-20，用户确认「稍微加强一点」）

_背景：核查确认 `PROFILE.md` + `MEMORY.md` + `AGENTS.md` + `SOUL.md` + ReMe 语义记忆 + T8/T9 时间感知 已组成完整的「认识你」基础设施，功能无缺失。唯一短板是默认人设模板仍是上游 QwenPaw 调性（"使魔/成为某个人/机器里的幽灵"），不是 hanbao「定制化豆包」定位。本次为纯文本、零架构改动的轻量补强（zh+en）。_

- [修改] `src/hanbao/agents/md_files/zh/SOUL.md` — 人设从 qwenpaw「成为某个人」怪味改为 hanbao「懂你、长期陪伴的家庭 AI 助手」；frontmatter 加 `hanbao_modification` 标记（提示词加载时整段 frontmatter 会被剥离，不污染 system prompt）。
- [修改] `src/hanbao/agents/md_files/en/SOUL.md` — 同上英文版。
- [修改] `src/hanbao/agents/md_files/zh/PROFILE.md` — 重写：加 hanbao 身份种子 + 明确「用户资料」分区（称呼/偏好/家人/重要日期/习惯/忌讳）+ 「边聊边更新」指引。
- [修改] `src/hanbao/agents/md_files/en/PROFILE.md` — 同上英文版。
- [修改] `src/hanbao/agents/memory/prompts.py` — `MEMORY_GUIDANCE_ZH/EN` 模板新增「👤 用户画像（PROFILE.md）」小节，明确指示 agent 把 PROFILE.md 当长期用户画像仓库、学到 durable 事实（偏好/家人/重要日期/习惯）**主动用 `edit_file` 回写**，不止首次 BOOTSTRAP；顶部 `[hanbao modification]` 注释同步更新。
- [修改] `src/hanbao/agents/md_files/zh/BOOTSTRAP.md` — 去掉 "更怪的东西" 怪味措辞，改为贴合主人需要的定位。
- [修改] `src/hanbao/agents/md_files/en/BOOTSTRAP.md` — 同上英文版。
- **未改动**：`AGENTS.md`（zh/en）经核对已为中性措辞、无 qwenpaw 残留，保持不变；`LICENSE`/`NOTICE`/`license-compliance.md`/`CHANGES-FROM-UPSTREAM.md` 红线文件未触碰（仅本文件追加本条记录）。
- **影响范围**：改的是 `md_files/` 模板，仅影响**新装/首次初始化**的 agent（FPK 首装即拿到 hanbao 人设）；已部署 workspace 的 `PROFILE.md`/`SOUL.md` 因 copy 默认 `only_if_missing` 不会被自动覆盖，需手动刷新或重跑首次引导。
- **下一步**：按纪律改完即 commit、不构建；待用户「测一下」再重建镜像验收。

---

### 运行配置界面精简·reactAgent TAB（2026-08-20）

_背景：用户要求「运行配置」6 个 TAB 中，reactAgent 只保留用户时区、其余按默认不展示；其余 5 个 TAB 后续单独确认。_

- [修改] `console/src/pages/Agent/Config/components/ReactAgentCard.tsx` — 仅保留用户时区 Form.Item；删除语言选择器、shell 命令超时/可执行文件、自动生成会话标题开关、context/memory backend 选择器及 backendRestart 警告；清理无用 import（`Input`/`InputNumber`/`Switch`/`Alert`/`LANGUAGE_OPTIONS`/backend 选项常量）与 props（仅留 `timezone`/`savingTimezone`/`onTimezoneChange`）。顶部加 `[hanbao modification]` 注释。
- [修改] `console/src/pages/Agent/Config/index.tsx` — 移除 `ReactAgentCard` 的 `language`/`savingLang`/`onLanguageChange` 传参，以及 `useAgentConfig` 解构与 `dynamicTabs` 依赖项中的对应项。
- [修改] `console/src/pages/Agent/Config/useAgentConfig.tsx` — 移除已无 UI 的 `shell_command_timeout`/`shell_command_executable` 的 `setFieldsValue`；其余字段（loop/llm_*/backend/嵌套 config）由 `handleSave` 的 `...original` 兜底，保存时不丢失默认值。语言获取/切换逻辑保留未删（仅不再在 UI 暴露），避免破坏既有测试。
- [修改] `src/hanbao/config/timezone.py` — `detect_system_timezone()` 在无系统时区可检测时回落值由 `UTC` 改为 `Asia/Shanghai`（[hanbao modification]），新装 hanbao 默认中国标准时间；已显式设置时区的 config.json 不受影响。
- **未改动**：其余 5 个 TAB（agentLoop/llmRetry/llmRateLimiter/lightContext/remeLightMemory）本次未动，待用户后续指示；`LICENSE`/`NOTICE`/`license-compliance.md` 红线文件未触碰。
- **下一步**：改完即 commit、不构建；待用户「测一下」一并重建镜像验收。

---

### 运行配置界面精简·agentLoop TAB（2026-08-21）

_背景：用户确认 agentLoop TAB（循环工程：防呆/迭代上限/烂尾检查 + Goal/Mission/Custom 高级编排）对家庭非技术用户既无必要、也该避免误操作，要求整页隐藏。_

- [修改] `console/src/pages/Agent/Config/index.tsx` — 从 `baseTabs` 移除 `key: "agentLoop"` 整个 tab 段；移除 `import AgentLoopCard`。TAB 不再展示；`AgentLoopCard.tsx` 文件、`components/index.ts` 中的导出、相关 i18n 文案、既有测试文件均**保留未删**（死代码无害，符合「只隐藏不删文件」保守策略）。
- [未改动] 后端 `LoopConfig` schema（`config.py:1288`）各子项 `default_factory` 默认值齐全；前端 `handleSave` 用 `...original` 兜底，隐藏字段保存时默认值不丢——循环行为（含 Default 模式防呆/迭代上限/烂尾检查等安全护栏）保持出厂默认，家庭用户无法误操作。
- **未改动**：`LICENSE`/`NOTICE`/`license-compliance.md` 红线文件未触碰；reactAgent/llmRetry/llmRateLimiter/lightContext/remeLightMemory 各 TAB 不受影响。
- **下一步**：改完即 commit、不构建；待用户「测一下」一并重建镜像验收。

---

### 运行配置界面精简·llmRetry/llmRateLimiter/lightContext TAB（2026-08-21）

_背景：用户确认 llmRetry（重试退避）、llmRateLimiter（并发/QPM/429 暂停）、lightContext（上下文压缩阈值/工具结果裁剪/历史留存天数）对家庭非技术用户偏底层、无需暴露，要求整页隐藏；remeLightMemory（记忆配置，关联「认识你」体验）保留展示。_

- [修改] `console/src/pages/Agent/Config/index.tsx` —
  - 从 `baseTabs` 移除 `key:"llmRetry"`、`key:"llmRateLimiter"` 两个固定 tab 段；移除对应 `import LlmRetryCard`/`LlmRateLimiterCard`。
  - 移除 `contextMapping` 动态推送块（lightContext 由 contextBackend 映射），仅保留 `memoryMapping`（remeLightMemory）。
  - 清理仅服务于 lightContext 的死代码：`maxInputLength`/`refreshEffectiveContextWindow`/两个 `useEffect`/`selectedAgent`/`api`/`useAgentStore`/`contextBackend`/`llmRetryEnabled`，以及 `useCallback`、`CONTEXT_MANAGER_BACKEND_MAPPINGS` 导入——避免 noUnusedLocals 下次构建报错。
- [保留] `LlmRetryCard.tsx`/`LlmRateLimiterCard.tsx`/`LightContextCard.tsx` 文件、其在 `components/index.ts` 的导出、相关 i18n 文案、既有测试均保留未删（只隐藏不删文件，死代码无害）。
- [未改动] 后端各 schema 默认值齐全；前端 `handleSave ...original` 兜底，隐藏字段保存时默认值不丢——重试/限流/上下文压缩保持出厂默认，家庭用户无法误操作；remeLightMemory 仍正常展示。
- **未改动**：`LICENSE`/`NOTICE`/`license-compliance.md` 红线文件未触碰。
- **下一步**：改完即 commit、不构建；待用户「测一下」一并重建镜像验收。

### 记忆增强·自动记忆搜索默认开启 + 默认 Embedding 占位（2026-08-21）

_背景：remeLightMemory 是运行配置里唯一保留的记忆 TAB，其中「自动记忆搜索(Beta)」默认关闭。该功能让 agent 每轮对话自动语义检索长期记忆并注入上下文（"越用越懂你"的核心体感）。经核查 embedder 完全独立读取 `embedding_model_config`、不复用主 LLM provider 凭证，且 api_key 为私有无法硬编码；故采用"默认开启 + 通用 embedding 占位 + 前端引导"的减法式方案。_

- [修改] `src/hanbao/config/config.py` —
  - `AutoMemorySearchConfig.enabled` 默认 `False`→`True`（[hanbao modification]），新装 hanbao 默认开启自动记忆搜索。
  - `EmbeddingModelConfig.model_name` 默认 `""`→`"BAAI/bge-m3"`（[hanbao modification]，backend 已为 `openai`）；api_key 留空（用户私有，无法硬编码）。新装即带通用 OpenAI 兼容 embedding 起点，硅基流动等"一个 key 通 LLM+Embedding"服务开箱即用。
- [修改] `console/src/pages/Agent/Config/components/ReMeLightMemoryCard.tsx` —
  - `autoMemorySearch` 折叠面板顶部加 `Alert` 引导：开启后需在本页下方 Embedding 配置填 API Key 才生效，推荐与对话模型同服务商。
- [修改] `console/src/locales/zh.json` + `en.json` — 新增 `agentConfig.autoMemorySearchEnableHint` 中英双语引导文案。
- [安全] 已部署 workspace 的 `agent.json` 因 `only_if_missing` 不覆盖；无 embedding 时 `auto_memory_search` 静默失败、安全降级（每轮空转一次检索，不崩、不影响聊天）；`doctor` 会提示"enabled 但无 key"。
- [未改动] `LICENSE`/`NOTICE`/`license-compliance.md` 红线文件未触碰。
- **下一步**：改完即 commit、不构建；待用户「测一下」一并重建镜像验收。

### 人设模板维护·id/ru 对齐 hanbao 人设 + 全语言标记补全（2026-08-21）

_背景：用户要求"维护所有 MD 文件"。经排查 `src/hanbao/agents/md_files/` 全体系：zh/en 的 SOUL/PROFILE/BOOTSTRAP 已在之前轻量补强中改为 hanbao「懂你、长期陪伴的家庭助手」人设；但 id/ru 整套仍为上游 QwenPaw 原味（"menjadi seseorang"/"Creature"/"становитесь кем-то"/"фамильяр? дух в машине?"/更奇怪的东西 等怪味残留）；qa/（内置 QA Agent）、local/（本地小模型 Agent）的 zh/en/ru 均已 hanbao 化；AGENTS/HEARTBEAT/MEMORY 为中性基础设施模板，无品牌味。_

- [修改] `md_files/id/SOUL.md`、`md_files/id/PROFILE.md`、`md_files/id/BOOTSTRAP.md` —
  从上游印尼语 QwenPaw 味翻译对齐 zh/en 的 hanbao 人设（身份=hanbao 家庭助手 / 用户资料分区：称呼·偏好·家人·重要日期·背景 / 去"更奇特生物"框架），frontmatter 加 `hanbao_modification` 标记。
- [修改] `md_files/ru/SOUL.md`、`md_files/ru/PROFILE.md`、`md_files/ru/BOOTSTRAP.md` —
  从上游俄语 QwenPaw 味翻译对齐 hanbao 人设，frontmatter 加 `hanbao_modification` 标记（去"使魔/机器里的幽灵/更奇怪的东西"框架）。
- [修改] `md_files/zh/BOOTSTRAP.md`、`md_files/en/BOOTSTRAP.md` —
  此前轻量补强已改内容（去"更怪的东西"），本次补加 `hanbao_modification` 标记，使所有 hanbao 改过的人设文件 frontmatter 一致可追溯（SOUL/PROFILE/BOOTSTRAP 四语言共 11 处标记齐备）。
- [未改动] `qa/*`、`local/*`（已 hanbao 化）、`AGENTS.md`/`HEARTBEAT.md`/`MEMORY.md`（中性基础设施模板，含 id/ru，无品牌味，维持原样）。
- [验证] Grep 全 `md_files/`：上游怪味词（menjadi seseorang / Creature / становитесь кем-то / фамильяр / дух в машине / weirder / familiar / becoming / journey / ghost 等）已清零。
- [未改动] `LICENSE`/`NOTICE`/`license-compliance.md` 红线文件未触碰。
- **下一步**：改完即 commit、不构建；仅影响新装/首次初始化 agent；已部署 workspace 的 md 因 `only_if_missing` 不覆盖，待用户「测一下」一并重建镜像验收。

---

### 频道模块减法·砍除 10 个频道（2026-08-21）

_背景：hanbao 定位为飞牛 NAS 家庭单用户本地聊天（微信+控制台为主）。用户要求再砍频道，仅保留家庭场景所需。本次砍除：**Discord、Telegram、元宝(Yuanbao)、Matrix、SIP、Mattermost、MQTT、Slack、语音(Twilio Voice)、OneBot** 共 10 个；保留 imessage/dingtalk/feishu/qq/console/wecom/xiaoyi/wechat 8 个（含注册中心必需 console）。所有改动均从"删功能=高危、先查依赖"纪律出发，全仓 grep 彻查悬空引用，不做构建验证（待用户「测一下」）。_

- [修改] `src/hanbao/app/channels/registry.py` — `_BUILTIN_SPECS` 移除 10 条目（discord/telegram/yuanbao/matrix/sip/mattermost/mqtt/slack/voice/onebot）。这是权威删除点：`get_available_channels()` 与前端 `channelTypes` API 均由此派生，频道自此不加载、不显示。
- [修改] `src/hanbao/config/config.py` —
  - 删除 10 个频道 config 类：`DiscordConfig`/`OneBotConfig`/`TelegramConfig`/`MQTTConfig`/`MattermostConfig`/`MatrixConfig`/`VoiceChannelConfig`/`SIPChannelConfig`/`YuanbaoConfig`/`SlackConfig`（均加注释标记）。
  - `ChannelConfig` 移除对应 10 个字段（`extra="allow"` 兜底，旧配置多余 key 静默忽略）。
  - `ChannelConfigUnion` 移除 8 个被砍类型（discord/telegram/mattermost/mqtt/matrix/voice/sip/slack）。
- [修改] `src/hanbao/app/channels/schema.py` — `BUILTIN_CHANNEL_TYPES` 移除 discord/telegram/mqtt/voice/sip/slack/yuanbao（该常量当前无引用方，属遗留清理）。
- [修改] `src/hanbao/cli/channels_cmd.py` — 移除 `DiscordConfig`/`TelegramConfig`/`VoiceChannelConfig` import、`configure_discord`/`configure_telegram`/`configure_voice` 三个交互配置函数、`_ALL_CHANNEL_NAMES` 与 `_ALL_CHANNEL_CONFIGURATORS` 中对应条目。
- [修改] `src/hanbao/cli/doctor_connectivity.py` — 移除 6 个 config 类 import、7 个 `_probe_*` 函数（mqtt/mattermost/matrix/telegram/discord/onebot/voice）、`_BUILTIN_PROBES` 对应 7 条目。
- [修改] `src/hanbao/cli/doctor_checks.py` — `enabled_channel_notes` 移除 discord/telegram/mattermost/mqtt/matrix/voice 六个凭证校验分支，首条改为 `if` 防 elif 语法错。
- [修改] `src/hanbao/app/routers/config.py` — 移除 7 个被砍 config 类 import；`_CHANNEL_CONFIG_CLASS_MAP` 移除 telegram/discord/voice/sip/mattermost/mqtt/matrix 7 条目（仅被 `.get()` 消费，删后安全）。
- [删除] `src/hanbao/app/routers/voice.py` + `src/hanbao/app/_app.py` 移除 `voice_router` 的 import 与 `include_router`（Twilio 端点 `/voice/*` 随语音频道一并移除）。
- [删除] 10 个频道包目录：`src/hanbao/app/channels/{discord_,telegram,yuanbao,matrix,sip,mattermost,mqtt,slack,voice,onebot}/`（含各自 `__init__.py`/`channel.py`/helper 模块）。
- [删除] 悬空测试 18 个：`tests/unit/channels/` 下 10 个（test_yuanbao/test_voice/test_telegram/test_slack/test_sip_memory_bounds/test_onebot_channel/test_mqtt/test_mattermost/test_matrix/test_discord）、`tests/contract/channels/` 下 7 个契约测试、`tests/unit/cli/test_doctor_connectivity.py`。
- [修改] `tests/unit/config/test_channel_display_migration.py` — 示例频道 `slack`→`wecom`（测的是迁移函数本身，与具体频道无关）。
- [修改] 前端数据层（被砍频道不再显示/可选）：
  - `console/src/constants/channel.ts`（`CHANNELS`/`CHANNEL_COLORS` 删 10 key）
  - `console/src/api/types/channel.ts`（删 10 个 config 接口 + `ChannelConfig` 10 字段 + `SingleChannelConfig` 10 项）
  - `console/src/pages/Control/Channels/useChannels.ts`（`builtinOrder` 删 5 项）
  - `console/src/pages/Control/Channels/components/constants.ts`（`CHANNEL_LABELS` 删 10）、`channelIcons.ts`（图标 URL 与头像色删 10）
  - `console/src/pages/Control/Channels/components/ChannelDrawer.tsx`（`CHANNELS_WITH_ACCESS_CONTROL` 删 8、文档 URL map 删 10）
  - `console/src/pages/Agent/Skills/components/SkillDrawer.tsx`（技能绑定频道下拉删 4）
  - `console/src/pages/Agent/MCP/accessPolicy.ts`（`MCP_CHANNEL_SOURCE_VALUES` 删 8）
  - `console/src/pages/Inbox/types.ts`（`PushMessage.channelType` 联合删 slack/telegram/discord）
  - 同步 4 个前端测试（constants/channel.test.ts、useChannels.test.ts、components/constants.test.ts、channelIcons.test.ts，断言改为保留频道 qq 等）
- [保留·说明] `ChannelDrawer.tsx` 中被砍频道的专属表单 switch-case（matrix/discord/telegram/slack/mqtt/mattermost/voice/yuanbao/onebot 等 case 块）、`locales/zh.json`/`en.json` 中对应频道文案——为死代码/死文案（频道不再从 API 返回，抽屉永不打开、永不渲染），留着无害，未删以免大文件盲改风险；如需连 UI 代码彻底清干净可再单独一轮处理。
- [验证] 全仓 grep 零残留：`src/hanbao` 无任何被砍 config 类名/频道包 import；`tests/` 无被砍频道 import；10 个改动 Python 文件 `ast.parse` 语法全部通过。未做构建/镜像验证（纪律：改完即 commit，待用户「测一下」）。
- [未改动] `LICENSE`/`NOTICE`/`license-compliance.md` 红线文件未触碰。
- **下一步**：改完即 commit、不构建；与运行配置精简/记忆增强等一并待用户「测一下」重建镜像验收（本次改动会显著减小镜像体积：10 个频道含 Twilio/SIP/Matrix/slack-bolt 等重依赖被移除）。

---

### 频道砍除跟进·pyproject 依赖清理 + md 文件频道残留（2026-08-21）

_背景：上一轮砍 10 个频道后复查发现两处遗漏——① `pyproject.toml` 仍挂着被砍频道的 SDK 依赖（不改镜像体积不降、且 python-telegram-bot 的 LGPL 直接依赖不消除）；② 运行时 md 模板（AGENTS.md 四语言、channel_message 技能）仍提及被砍频道。本轮一并清理。_

- [修改] `pyproject.toml` —
  - 移除 6 个被砍频道 SDK：`discord-py`/`python-telegram-bot`/`slack-bolt`/`paho-mqtt`/`matrix-nio`/`twilio`（删除前确认 `src/` 与 `plugins/`/`e2e/` 零 import）。
  - 移除 `sip` / `sip-livekit` 两个 optional extras（`pyVoIP`/`dashscope`/`dashscope-realtime`/`audioop-lts`/`livekit`/`livekit-api`）；`full` extra 保留（仍含 local+whisper）。已核对 `scripts/pack` 仅引用 `hanbao[full]`，无断裂。
  - package-data 移除 `app/channels/yuanbao/proto/**`（yuanbao 目录已删）。
  - description 更新：渠道列表 "DingTalk, Feishu, QQ, Discord, iMessage" → "DingTalk, Feishu, QQ, WeChat, iMessage"。
- [修改] `src/hanbao/agents/md_files/{zh,en,id,ru}/AGENTS.md` — 表情回应示例 "Discord, Slack" → "QQ、飞书"（四语言），frontmatter 补 `hanbao_modification` 标记。
- [修改] `src/hanbao/agents/skills/channel_message-{zh,en}/SKILL.md` — `--channel` 参数示例更新为保留频道（console/dingtalk/feishu/qq/wechat/...）。
- [修改] `docs/known-issues.md` — 「渠道 SDK 死重」段更新为 08-21 状态（10 频道 SDK 已移除、保留渠道 SDK 清单）；I-021 状态追加「python-telegram-bot 已随 Telegram 频道砍除从依赖移除，LGPL 直接依赖清零」。
- [未改动] `NOTICE`/`LICENSE`/`license-compliance.md` 红线文件：NOTICE 中既有 LGPL 声明**保留不删**（多余声明无害、合规更保守）。
- [验证] 删除前 grep 确认 `src/` 对 discord/telegram/slack_bolt/twilio/paho/matrix_nio/livekit/pyVoIP/dashscope 零 import；`tomllib` 解析 `pyproject.toml` 通过；`src/hanbao/agents/` 下 md 文件被砍频道词零残留。
- **下一步**：改完即 commit、不构建；本次依赖瘦身叠加频道砍除，镜像重建后体积预期明显下降（-100MB+ 量级）。

### 频道设置抽屉·上游文档按钮清除（2026-08-21）

_背景：上一轮砍 10 频道后，ChannelDrawer 抽屉标题里仍保留"Doc"按钮（class `dingtalkDocBtn` / `spark-button`），点击会跳转到上游 `qwenpaw.agentscope.io/docs/channels` 文档页。用户要求把这些按钮全部清除。_

- [删除] `console/src/pages/Control/Channels/components/ChannelDrawer.tsx` —
  - 抽屉标题三处外部文档按钮全部移除：① 内置频道 `CHANNEL_DOC_EN_URLS`/`CHANNEL_DOC_ZH_URLS` 驱动的"Doc"按钮；② 插件频道 `schema.doc_url` 驱动的"Doc"按钮（IIFE 分支）；③ `voice` 频道的 Twilio 控制台链接按钮。
  - 连带移除仅被这些按钮使用的符号，避免 `noUnusedLocals` 构建报错：`CHANNEL_DOC_EN_URLS`/`CHANNEL_DOC_ZH_URLS`/`TWILIO_CONSOLE_URL` 三个常量（含指向 `qwenpaw.agentscope.io` 的 URL）、`const currentLang`、`import { LinkOutlined }`（`@ant-design/icons`）、`import { openExternalLink }`（`utils/openExternalLink`）。
  - 抽屉标题现仅保留渠道名 + 设置文案。
  - 加 `[hanbao modification]` 注释标注本次移除。
- [删除] `console/src/pages/Control/Channels/index.module.less` — 移除仅被上述按钮使用的 `.dingtalkDocBtn` 样式类。
- [保留·说明] `channelSchema`/`resolveLocalized`/`i18n`/`Button` 等在表单渲染中仍使用，保留。`t("channels.voiceSetupLink")` 等 locale key 变为未引用（非编译错误，属死文案，未清理）。
- [未改动] `LICENSE`/`NOTICE`/`license-compliance.md` 红线文件未触碰。
- [验证] 全仓 grep `CHANNEL_DOC_`/`TWILIO_CONSOLE_URL`/`currentLang`/`openExternalLink`/`LinkOutlined`/`dingtalkDocBtn` 在 Channels 目录下零残留；`Button` 仍在 footer 使用。未做构建/镜像验证（纪律：改完即 commit，待用户「测一下」）。

### 顶栏/侧边栏上游文档链接清除（2026-08-21）

_背景：上一轮清完频道抽屉的 QwenPaw 文档按钮后，用户要求把顶栏 FAQ 与更新弹窗里仍残留的 `qwenpaw.agentscope.io` 链接一并清掉。_

- [删除] `console/src/layouts/constants.ts` — 移除 4 个指向 `qwenpaw.agentscope.io` 的 URL 函数：`getDocsUrl`（`/docs/intro`）、`getFaqUrl`（`/docs/faq`）、`getReleaseNotesUrl`（`/release-notes`）、`getFeatureDemosUrl`（`/docs/functiondemo`）。`getWebsiteLang` 通用 helper 保留。
- [删除] `console/src/layouts/constants.test.ts` — 移除上述 3 个函数（getDocsUrl/getFaqUrl/getReleaseNotesUrl）的测试用例与 import；顶部注释同步更新。
- [修改] `console/src/layouts/Header.tsx` —
  - `handleOpenUpdateModal` 里拉取上游 `qwenpaw.agentscope.io/docs/faq.{lang}.md` 提取"如何更新"的逻辑，改为直接使用本地 `UPDATE_MD`（原本就是兜底内容，功能不变、去掉上游网络请求）。加 `[hanbao modification]` 注释。
  - 更新弹窗 web 端的 "view releases" 按钮（调用 `getReleaseNotesUrl`）整体移除（仓库此前已将 `PYPI_URL` 标 `Disabled — no release channel yet`，方向一致）。移除 `getReleaseNotesUrl` import。
- [保留·说明] `getWebsiteLang` 仍被自身测试覆盖；`styles.updateViewReleasesBtn` CSS 类与 `t("sidebar.updateModal.viewReleases")` locale key 变为未引用（非编译错误，死代码未清理）。`utils/openExternalLink.test.ts` 中 `qwenpaw.agentscope.io` 是 URL 净化器的**测试夹具**（非应用链接），未改动。
- [未改动] `LICENSE`/`NOTICE`/`license-compliance.md` 红线文件未触碰。
- [验证] 全仓 grep `qwenpaw.agentscope.io` 在应用代码中仅剩 `openExternalLink.test.ts` 测试夹具；`getReleaseNotesUrl`/`getDocsUrl`/`getFaqUrl`/`getFeatureDemosUrl` 零引用。未做构建/镜像验证（纪律：改完即 commit，待用户「测一下」）。

### 死代码清理·viewReleases locale key（2026-08-21）

_背景：上一轮移除更新弹窗 web 端 "view releases" 按钮（走 `getReleaseNotesUrl`）后，其对应 locale key `sidebar.updateModal.viewReleases` 成为死 key。本次清理，严守上游 Apache-2.0 约定。_

- [删除] `console/src/locales/zh.json` / `en.json` — 移除 `sidebar.updateModal.viewReleases` 死 key（按钮已删，全仓 `t(...)` 零引用）。两文件均经 `JSON.parse` 校验合法。
- [保留·纠正] `.updateViewReleasesBtn` CSS 类（Header 的 `index.module.less`）**未删**：复查发现 desktop 端 "install" 按钮（onDesktop 分支）仍使用该类，删之会导致桌面安装按钮丢样式——此前误判为死代码，本次纠正。
- [未改动·合规] `LICENSE`/`NOTICE`/`license-compliance.md`/`CHANGES-FROM-UPSTREAM.md` 红线文件未触碰（R2 严禁 blanket 替换波及）。JSON 无法嵌注释，修改标注由本文件 + `git diff` 承担，符合 license-compliance.md §6 简化策略（§4(b) "prominent notices" 未强制逐文件头部）。`PYPI_URL`（`pypi.org/pypi/qwenpaw/json`）仍处禁用态且有 `constants.test.ts` 对应断言，暂保留不碰。
- [验证] 全仓 grep `viewReleases` 零残留；两 locale 文件 `JSON.parse` 通过。未做构建/镜像验证（纪律：改完即 commit，待用户「测一下」）。

### 砍除桌面端整条线（2026-08-21/2026-08-24）

_背景：用户要求"桌面端整条线都给他砍掉"，并顺带确认仓库里有没有残留的 Tauri 构建脚手架。经核查确认：仓库源码树内无 Rust 版 `src-tauri/`、`tauri.conf.json`、`Cargo.toml`，但存在 `scripts/pack-tauri/` 打包脚本、`@tauri-apps/*` 依赖、`build:tauri-bootstrap` 脚本及整套桌面 GitHub Actions——全部属于桌面线残留，本次一并清除。hanbao 定位为 Web 控制台（后端同源托管），桌面 shell 无任何消费者，`onDesktop=false` 早已写死，砍除为纯减法、零功能损失。_

- [修改] `console/src/layouts/Header.tsx` — 删除 `const desktop={...} as any` 桩、`onDesktop=false`、logo 8 连击 DevTools 手势（`handleLogoClick`/`logoClicksRef`）、桌面更新检查 useEffect、`handleStartInstall/UpdateLater/RestartNow`、后台下载/就绪/失败状态计算与对应 JSX（Popover/Tooltip 指示器）、更新弹窗 footer 的 desktop 安装/稍后按钮、`modalVersion/latestVersion`；清理仅被上述代码使用的 import（`Popover`、`SyncOutlined`、`CheckCircleOutlined`、`ExclamationCircleOutlined`、`useRef`）。版本徽标保留（`hasUpdate=false` 常闭，web 更新检查本已禁用）。
- [修改] `console/src/App.tsx` — 移除 `isDesktopTauriRuntime`、`interceptBlankLinkClicks` 导入；删除两个桌面专用 useEffect（右键菜单拦截禁 DevTools、Tauri `_blank` 链接重路由）。
- [修改] `console/src/utils/openExternalLink.ts` — 精简为纯浏览器：移除 `@tauri-apps/api/core`、pywebview 依赖及 `isDesktopTauriRuntime/hasTauriInternals/detectExternalLinkRuntime` 与 tauri/pywebview 分支，`openExternalLink` 只走 `window.open`；保留 `resolveExternalUrl/isHttpExternalUrl/resolveSupportedExternalUrl` 纯 URL 校验导出。加 `[hanbao modification]`。
- [修改] `console/src/utils/downloadFileFromUrl.ts` — 精简为纯浏览器：移除 `@tauri-apps/api/core`、`@tauri-apps/plugin-dialog`、pywebview 依赖及 `downloadWithPyWebView/getTauriSavePath/downloadWithTauri`，仅保留 fetch+blob 下载路径。加 `[hanbao modification]`。
- [删除] `console/src/utils/pywebview.ts`、`console/src/utils/interceptBlankLinkClicks.ts`（+`interceptBlankLinkClicks.test.ts`）、`console/src/test/tauri-mock.ts`（vite 测试别名目标）。
- [修改] `console/src/vite-env.d.ts` — 移除 `PyWebViewAPI` 与 `Window.pywebview` 全局声明。
- [修改] `console/vite.config.ts` — 移除 `@tauri-apps/api/core`、`@tauri-apps/plugin-dialog` 测试别名与 `**/src/tauri/**` exclude 项。
- [修改] `console/package.json` — 移除 `@tauri-apps/api`、`@tauri-apps/plugin-dialog`、`@tauri-apps/cli` 依赖及 `build:tauri-bootstrap` 脚本（其引用 `src-tauri/vite.bootstrap.config.ts` 与 `scripts/pack-tauri/*`，均已不存在）。两文件均 `JSON.parse` 校验通过。
- [删除] `scripts/pack-tauri/`（11 个文件）— pyinstaller + Tauri bootstrap 打包脚本，桌面构建脚手架残留。
- [删除] GitHub Actions 桌面线（7 个文件）— `desktop-build.yml`、`desktop-publish.yml`、`desktop-promote.yml`、`desktop-release.yml`、`fork-verify-desktop.yml`、`.github/actions/verify-tauri-macos/action.yml`、`verify-tauri-windows/action.yml`。
- [修改] `.github/workflows/release.yml` — 移除 `build-desktop`/`publish-desktop`/`promote-desktop` 三个 job 及其在各 publish/finalize job `needs:` 中的引用；移除 resolve job 里仅桌面验证用的 `HANBAO_DASHSCOPE_API_KEY` 检查；头部注释同步去掉 desktop 提及。Web/Docker/PyPI/插件发布线不受影响。
- [修改] `.github/workflows/release-duty.yml` + `.github/release-duty-roster.yml` — 移除 macOS/Windows Desktop 验证清单与轮值名单；`actionlint.yaml` 移除 `tauri_updater_*` 变量声明与 `desktop-release.yml` paths 项。
- [修改] `console/src/utils/openExternalLink.test.ts` — 重写为纯浏览器行为用例（移除 pywebview/tauri/`DownloadCancelledError` 相关用例与 `tauri-mock` 导入）。
- [修改] `console/src/api/modules/workspace.test.ts` — 移除已无必要的 `@tauri-apps/*` mock（`downloadFileFromUrl` 本就整体 mock）。
- [清理] `console/src/locales/zh.json`/`en.json` — `updateModal` 区块除 `title` 外全部为桌面更新流程文案（`installDesktopUpdate`/`desktopInstallHint`/`checking`/`downloading`/`readyToInstall`/`updateLater`/`backgroundDownloading` 等 22 个 key），代码零引用，全部删除；`title` 保留。`index.module.less` 删除 `.updateViewReleasesBtn` 类（纠正 2026-08-21 记录：该类的唯一使用者是 desktop install 按钮，按钮已删，类随之删除）。`externalLinkComponents.tsx` 顶部注释更新为纯浏览器描述。
- [合规] `LICENSE`/`NOTICE`/`license-compliance.md` 红线文件未触碰；逐文件改动均已加 `[hanbao modification]` 注释（JSON/LESS 无法嵌注释的由本记录 + `git diff` 承担标注，符合 §4(b) 简化策略）。
- [验证] 全仓 grep `onDesktop|isDesktopTauriRuntime|__TAURI__|pywebview|@tauri-apps|getPyWebViewApi|interceptBlankLinkClicks|updateViewReleasesBtn` 在 `console/src` 仅剩本次新增的 `[hanbao modification]` 注释文本，无任何代码引用；`.github` 无 desktop/tauri 残留；三份 JSON 校验通过；`scripts/pack-tauri`、`src-tauri` 目录已不存在。`console/package-lock.json` 中 `@tauri-apps/*` 条目（43 处）为锁文件残留，npm 生态惯例由下次 `npm install` 自动清除，不手改 lock（避免误伤哈希/依赖树）；`npm ci`/`npm install` 均不受 lock 多余条目影响。未做构建/镜像验证（纪律：改完即 commit，待用户「测一下」）。

---

## 阶段 6.x · I-022 web_search 支持可选 Tavily key（2026-08-24）

`web_search` 工具原本写死 `X-Tavily-Access-Mode: keyless` 免费模式，上架后重度使用会集体撞 Tavily 限速（I-022）。改为支持可选 `TAVILY_API_KEY` 环境变量：

- [修改] `src/hanbao/agents/tools/web_search.py` — 新增 `_TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")` 与 `_tavily_headers()`：有 key 时发 `Authorization: Bearer <key>` 认证请求（用部署者自有额度避限速），无 key 时回退 keyless 零配置。`py_compile` 通过。
- [修改] `docker-compose.yml` — `environment` 示例注释加 `TAVILY_API_KEY=${TAVILY_API_KEY:-}`，提示部署者透传自有 key。
- [修改] `docs/known-issues.md` — I-022 状态 🔴→🟢（env 方案），设置页 UI 入口列为可选增强。
- [合规] `LICENSE`/`NOTICE`/红线文件未触碰；改动加 `[hanbao modification]`。

> **重建验收（2026-08-24，用户「测一下」触发）**：本项随第二轮前端美化一并入镜像 `531ecf90e1ff` 重建验收全绿——`docker exec` 实测 `docx`/`openpyxl` 可正常 import（运行期 4 工具可用），err.log 零 traceback。详见下方「前端界面全面水墨化（第二轮）」验收条。

---

## 阶段 6.x · I-019 自研文档改/创建工具（2026-08-24）

移除 Anthropic 专有 docx/xlsx 技能后函包一度「只能读不能改/创建」，本次以许可干净的自研实现补齐（I-019 待办 #3）：

- [新增] `src/hanbao/agents/tools/document_edit.py` — 4 个 AgentScope `@tool_descriptor` 工具：`create_docx`/`edit_docx`/`create_xlsx`/`edit_xlsx`（与 `web_search`/`web_fetch` 同形态，Agent 直接调用、零前端改动）。复用 `file_io._resolve_file_path` + `io_utils.get_path_lock`；python-docx/openpyxl **lazy import** 缺失优雅降级。`py_compile`+`ast.parse` 通过。
- [修改] `src/hanbao/agents/tools/__init__.py` — 导入 4 工具，装饰器自动注册。
- [修改] `pyproject.toml` — 加 `python-docx>=1.1.0` + `openpyxl>=3.1.0`（均 MIT，合法替代被删的 Anthropic 专有技能，Apache-2.0 再分发合规）。
- [说明] 范围「简化版」：无样式引擎/模板，仅满足 Agent 代用户产出与微调 Office 文档；pptx 创建/编辑维持放弃。运行期验证待「测一下」镜像重建（pip 装新依赖 + 容器实测 4 工具）。
- [合规] `LICENSE`/`NOTICE`/红线文件未触碰；新增文件含 `[hanbao modification]` 溯源注释。

> **重建验收（2026-08-24，用户「测一下」触发）**：本项随第二轮前端美化一并入镜像 `531ecf90e1ff` 重建验收全绿——`uv pip install` 拉取 python-docx/openpyxl 成功，`docker exec` 实测可 import，4 工具运行期可用。

---

## 阶段 6.x · 前端界面水墨美化（2026-08-24）

上游 QwenPaw 仅改过颜色、结构仍是原样。本次在既定水墨古典品牌方向内自主打磨界面质感（不另起炉灶、不触碰 `online.svg`/Mikasa 红线）：

- [修改] `console/src/App.tsx` — `ConfigProvider` token 新增 `fontFamily: "var(--font-sans)"`，全站无衬线正文（含中文 PingFang/雅黑/Noto）统一；与 `.ink-title` 衬线立骨形成反差。
- [修改] `console/src/styles/layout.css` —
  - `:root` 新增 `--font-serif`/`--font-sans` 离线系统字体栈（不引外网，适配家庭 LAN NAS 离线场景）。
  - `.ink-title` 与卡片/弹窗/抽屉/页眉标题统一改 `--font-serif` 衬线，立「文人水墨」骨相。
  - 空态（`ant-empty`/`hanbao-empty`）补一枚朱砂圆环印（`::before`，随明暗切换），替代被隐藏的百炼插画，走极简水墨留白。
  - `.page-content` 淡入、`.page-header` 缓升的轻入场动效（仅透明度/位移，规避 fixed 包含块问题）。
  - `html,body` 注入 `--font-sans` 兜底正文。
- [修改] `console/src/pages/Login/index.tsx` — 登录卡片右上角落一枚朱砂方印「函」（闲章），呼应「函包」品牌，立水墨文人气质。
- [说明] 字体走系统衬线/无衬线栈、不加载 Web Font，保证离线可用；登录页闲章为纯 CSS 装饰、无外部资源。运行期视觉效果待「测一下」镜像重建后在浏览器确认。
- [合规] `LICENSE`/`NOTICE`/红线文件未触碰；`online.svg`/Mikasa 肖像零碰触；改动均加 `[hanbao modification]`。

> **重建验收（2026-08-24 第二轮，用户「测一下」触发）**：本项与第一轮美化一并入镜像 `531ecf90e1ff` 重建验收全绿（前端重编 tsc+vite 通过），但用户实测反馈「还是没怎么变」——根因正是本轮仅在既定水墨方向内做边缘装饰，未动布局与质感，直接催生了下方「前端界面全面水墨化（第二轮）」。

---

## 阶段 6.x · 前端界面全面水墨化（2026-08-24 第二轮）

用户实测上一轮「水墨美化」后反馈「界面还是没怎么变，只是加了点动效」——根因是上一轮仅在既定水墨方向内做边缘装饰（字体/闲章/动效），未动布局与质感。本轮按用户拍板的「全面水墨化」做实质性视觉重做（不另起炉灶、不碰 `online.svg`/Mikasa 红线）：

- [修改] `console/src/styles/layout.css`（全局水墨层）—
  - 宣纸纹理背景：body 在既有米白底上叠加双角墨晕 + 极淡朱砂点染 + 纵向纤维纹理（`repeating-linear-gradient`），告别「一片平」的纯色。
  - 聊天气泡水墨化（Spark 外部组件，用稳定 class 片段钩子）：助手气泡=宣纸白 `#FBF8F1`+细墨边+柔影，用户气泡=朱砂淡宣纸+朱砂边；暗色模式对应墨灰/朱砂。仅改背景/边框/圆角/柔影，不碰 SDK 内部布局（避免流式渲染破坏）。
  - 气泡内链接统一朱砂（`a { color:#9E2B25 }`）。
  - 聊天输入区顶部加一道墨线，与消息区留白分界。
  - `.page-content` 叠极淡纸影（「宣纸托起」层次）；`.ant-layout-content`/`.page-container` 铺极淡墨晕，避免纯白平板。
  - 登录页响应式：窄屏（≤900px）隐藏水墨品牌立轴，仅留宣纸登录卡。
- [修改] `console/src/components/SessionItem/sessionItem.module.less`（会话项水墨化）—
  - `.sidebar`/`.drawer` 项 hover 加朱砂左条（`inset` 阴影，不挤布局）；`.active` 加朱砂左条 + 衬线名（`var(--font-serif)`），立「文人立骨」。
  - 修复 QwenPaw 漏网青绿状态点 `rgba(20,184,166)` → 朱砂脉冲（`statusDotActive` + `chatStatusBreathe` 关键帧 glow 改朱砂），去 qwenpaw 味。
- [重写] `console/src/pages/Login/index.tsx` — 登录页从「居中宣纸卡片+闲章」升级为**水墨意境双栏**：左墨黑品牌立轴（朱砂圆晕 + 衬线 wordmark「函包」+ 闲章「函」+ 标语「墨痕未干，对话已成」），右宣纸登录卡（logo + 衬线标题 + 表单 + 右上角朱砂闲章）；窄屏自动收起左轴。暗/亮双版。
- [修改] `console/src/pages/Chat/components/ChatHeaderTitle/index.module.less` — 聊天页眉标题与下拉会话名统一衬线（`var(--font-serif)`），与全局 `.ink-title` 立骨一致；hover/激活本就朱砂，无需改。
- [说明] 本轮为纯视觉/样式层改动，逻辑零改；字体走系统栈不引外网、登录页为纯 CSS 装饰，均离线可用。运行期视觉验收待用户「测一下」镜像重建后在浏览器确认。
- [合规] `LICENSE`/`NOTICE`/红线文件未触碰；`online.svg`/Mikasa 肖像零碰触；改动均加 `[hanbao modification]`。

> **重建验收（2026-08-24，用户「测一下」触发）**：提交 `59220ad` 后重建镜像 `531ecf90e1ff`/`hanbao:latest`（1.74GB，前端重编 tsc+vite 通过、uv 装文档依赖），干净容器实测全绿：`:8091` `<title>hanbao Console</title>`、`/api/auth/status`=`{"enabled":true,"has_users":false}`、`/var/log/app.err.log` 零 traceback、`/api/desktop/shutdown` 404（悬空端点确认删除）、I-019 依赖 `docx 1.2.0`/`openpyxl 3.1.5` 就绪。浏览器预览见 `http://localhost:8091`。
>
> **🔴 构建教训（同批实测）**：shell 的 `HTTP_PROXY`/`HTTPS_PROXY=127.0.0.1:7897` 会被 docker 自动注入构建容器，Clash 没起时 npm/pip 全走死代理假死（表现为 build 卡住）。必须 `--build-arg HTTP_PROXY= --build-arg HTTPS_PROXY= --build-arg http_proxy= --build-arg https_proxy=` 清空，走宿主直连 + daemon mirror，无需 Clash。基础镜像默认 `agentscope/node:slim`（阿里云 ACR）因 Clash 对 aliyuncs 授权 EOF 拉不动，改用 `--build-arg NODE_IMAGE=node:20-slim`（Docker Hub，走 daemon mirror 直通）。

---

## 阶段 6.x · 运行配置页清理：auth.py 死白名单条目 + 隐藏 remeLightMemory TAB（2026-08-24）

_背景：自动记忆搜索(Beta) 默认开着，家庭场景无需用户配置记忆后端，遂把 remeLightMemory 运行配置 TAB 隐藏，仅留 reactAgent（用户时区）；顺手清掉 auth.py 漏清的桌面端点白名单死条目。_

- [修改] `src/hanbao/app/auth.py` — `_PUBLIC_PATHS` 删 `/api/desktop/shutdown`（桌面端点路由已于 `d9a9875` 删除，请求 404 无害，白名单漏清的死条目）。0 依赖风险，`py_compile` 通过。
- [修改] `console/src/pages/Agent/Config/index.tsx` — 移除 `MEMORY_MANAGER_BACKEND_MAPPINGS` import + `memoryBackend` useWatch + dynamicTabs 里按 backend 动态 push 记忆 TAB 的逻辑 → 运行配置页**只剩 reactAgent（用户时区）一个 TAB**。`reme_light_memory_config` 后端默认值照常加载、保存时 `...original` 兜底不丢；`ReMeLightMemoryCard.tsx` 文件保留（backendMappings 仍映射供其它页）。
- [合规] `LICENSE`/`NOTICE`/红线文件未触碰；改动均加 `[hanbao modification]`。
- [验证] 前端编译 + 运行期待「测一下」镜像重建确认。**已随 `hanbao:latest`（`1067ffd5c99f`）「测一下」重建验收全绿**：`<title>hanbao Console</title>`、auth/status `{"enabled":true,"has_users":false}`、err.log 零 traceback，运行配置页仅余 reactAgent TAB 前端编译通过。

---

## 阶段 6.x · ChannelDrawer 被砍频道死代码清理（2026-08-24）

_背景：2026-08-21 砍除 10 个频道时，其 `ChannelDrawer.tsx` 专属 `case` 表单块因 registry 仅剩 8 频道而永不命中，属无害死代码，当时留作后续收。本次按「删功能先查依赖」铁律清除。_

- [删除] `console/src/pages/Control/Channels/components/ChannelDrawer.tsx` — 删 10 个被砍频道 `case` 块（共 667 行）+ 3 个 `Form.useWatch` const（`matrixAuthMethod`/`isMatrixPasswordAuth`/`onebotMediaBase64`）+ matrix 的 `useEffect` + `useEffect` import。
- [说明] `tsconfig.app.json` `noUnusedLocals:true`：删 case 必须连带删 const/import，否则 `tsc` 阶段报错。
- [保留] `constants.ts`/`channelIcons.ts` 此前已清理干净，本次无改动；无 ChannelDrawer 专属测试。locales JSON 仍含被砍频道翻译键（无害死文案，未清理）。
- [合规] `LICENSE`/`NOTICE`/红线文件未触碰。
- [验证] 全仓 grep `useEffect`/三 const 在 ChannelDrawer 归零；`case "` 恰为 7 活频道（imessage/dingtalk/feishu/qq/wecom/xiaoyi/wechat）；活频道表单逻辑不受影响。**已随 `hanbao:latest`（`1067ffd5c99f`）「测一下」重建验收全绿**：`<title>hanbao Console</title>`、auth/status `{"enabled":true,"has_users":false}`、err.log 零 traceback，前端 tsc/vite 编译通过。

---

## 阶段 6.y · 删除 append_file / delegate_external_agent 两工具（2026-08-25）

_背景：两者均为继承自 QwenPaw 的休眠工具（`enabled_by_default=False`），家庭单用户聊天机器人场景用不到，用户拍板砍除。_

- [删除] `src/hanbao/agents/tools/file_io.py` — 移除 `append_file` 定义（含其 `@tool_descriptor` 装饰器块）及因此变未用的 `append_text_async` 导入；`src/hanbao/agents/tools/__init__.py` 去除 `append_file` 与 `delegate_external_agent` 两处 import；`security/tool_guard/guardians/file_guardian.py` 与 `security/tool_guard/utils.py` 移除对应守卫项。
- [删除] `src/hanbao/agents/tools/delegate_external_agent.py`、`tests/integration/test_acp_runner.py`（整文件即端到端测该工具）。
- [删除·前端] `console/src/components/Chat/ToolCards/cards/AppendFileCard.tsx`、`DelegateExternalAgentCard.tsx` 并改写 `index.ts` 注册表；`console/src/pages/Agent/Tools/index.tsx` 移除 `delegate_external_agent` 异步执行入口。
- [保留·关键] `src/hanbao/agents/acp/` 共享子系统**保留**——网页配置 API（`get_acp_config`/`set_acp_config`）、`cli/tui/`、`cli/acp_cmd.py`、核心 `session_hook`/`runtime/builder` 均依赖之，整删会拖垮控制台与 hook；本次仅删工具本身，不动 acp 子系统与其 `config.py` 的 `ACPConfig`。
- [保留] `write_file`/`edit_file` 与治理层 `governance/detectors.py`、系统提示词深度耦合且默认开启，不在本次两工具范围。
- [测试收尾] `test_file_io.py`（移除 `append_file` import + `TestAppendFile` 整类）、`test_unified_tool_registration.py`（移除两工具 import 与两测试方法，plugin 所有权测试 `builtin_name` 改 `read_file`）、`test_utils.py`（`_DEFAULT_GUARDED_TOOLS` 期望集移除 `append_file`）。
- [合规] `LICENSE`/`NOTICE`/红线文件未触碰；改动文件加 `[hanbao modification]`。
- [验证] `python -m py_compile` 四个后端文件通过；grep 全仓 `append_file`/`delegate_external_agent` 功能引用零残留（仅 `agents/acp/` 子系统内历史注释提及，无害）。待「测一下」重建验收。

---

## 阶段 6.z · 镜像瘦身：构建工具链移出最终镜像层（2026-08-25）

_背景：镜像 `hanbao:latest` 实测 1.74GB。拆解发现约 200MB 为「仅在编译期需要」的构建工具链（gcc-14 ~48MB、libc6-dev ~17MB、libgcc-14-dev ~16MB、libssl-dev ~22MB、git ~15MB、g++/libstdc++-14-dev/make/binutils/dpkg-dev ~85MB）。原 `Dockerfile` 在基础 apt 层（461MB 那层）装这些包，再在**独立新层** `apt-get purge`，而 Docker 后层 purge 减不掉前层已固化的体积——工具链因此死死留在最终镜像里。_

- [修改] `deploy/Dockerfile` 基础 apt 层 — 移除 `git` / `libssl-dev` / `build-essential`（构建专用），仅留运行时包 `curl`/`supervisor`/`gettext-base`/`python3`/`python3-venv`/`fonts-wqy-zenhei`。
- [修改] `deploy/Dockerfile` 构建步 — 源码 `COPY src` 提前到 `uv pip install` 之前（去掉原来的 `__init__.py`/`__version__.py` stub 技巧），并将 `build-essential git libssl-dev` 的 **install → `uv pip install .` → `apt-mark manual`(运行时包) → `apt-get purge` → `apt-get autoremove --purge`** 合并进**同一个 RUN**，使工具链不落盘。
- [删除] `deploy/Dockerfile` 原独立 purge 步，其功能已并入上方合并 RUN。
- [修改] `deploy/Dockerfile` 合并 RUN — `uv pip install` 完成后追加 `rm -f /bin/uv`，将仅构建期使用的 uv 二进制（58MB）从最终镜像剔除。已全仓核验：entrypoint 仅跑 `hanbao init`+`supervisord`，无任何运行时 subprocess 调用 `uv`/`pip`；插件安装走 CLI→HTTP `/plugins/install`→服务端热加载，服务端 handler 无 `uv/pip install` 调用，删 uv 不影响装插件。
- [预期体积] 最终镜像约 **1.49GB**（较 1.74GB 减 ~250MB），**零功能损失**，仅改动 Dockerfile。
- [风险·git] 最终镜像不再含 `git`（pyproject 无 git 源依赖，构建/安装不受影响；若某 skill 运行时 shell 调用 `git` 会失败，运行时风险低，已知无此类依赖）。
- [风险·libssl-dev] 仅提供头文件/符号链接，运行时 `cryptography` 链接 base 镜像自带的 `libssl3`，purge `-dev` 不影响运行时。
- [合规] `LICENSE`/`NOTICE`/红线文件未触碰；Dockerfile 改动均加 `[hanbao modification]`。
- [验证] 待用户「测一下」触发重建，对比 `docker images` 体积，并 `dpkg -l | grep -E 'gcc|g\+\+|make|git'` 确认最终镜像内已无构建工具链。

---

## 阶段 6.aa · 前端导航收敛：移除独立「技能池」入口（2026-08-25）

_背景：单用户本地 NAS 场景下，上游多租户「共享技能池」范式属过度设计。前端同时存在「技能」(`/skills`) 与「技能池」(`/skill-pool`) 两个并列入口，用户感知冲突；且「技能」页（`pages/Agent/Skills`）已内建从池下载 / 上传到池 / hub 安装 / 市场浏览全套能力，独立「技能池」页为重复入口（其独有「广播到多 agent」对单用户无意义）。_

- [修改] `console/src/layouts/registry/builtinRoutes.tsx` — 移除 `core.skill-pool` 路由注册及 `SkillPoolPage` 懒加载 import（同步删 import 以免 `noUnusedLocals` 编译失败）。底部 `[hanbao modification]` 注释已补充本次减法。
- [修改] `console/src/layouts/registry/builtinMenu.ts` — 移除 `core.skill-pool` 导航菜单项（`primary.settings` 分组下），保留注释化参考以便还原。
- [保留] 底层 `SkillPoolService` / `SkillService` / 内置技能自动同步 / hub 安装 / 「技能」页内「从池下载 / 上传到池」能力**全部保留**；`pages/Settings/SkillPool/` 页面代码保留但不再经由路由/菜单可达。
- [零破坏] 仅收敛导航入口，不删数据、不删页面源码、不改动任何后端逻辑；如需还原，恢复上述两处注册即可。后续深化（见 6.ab）：已将「技能」页内「上传到池 / 从池下载」措辞收敛为「我的技能库」语义（UX 文案层，2026-08-25 已落地）。
- [合规] 改动文件均含 `[hanbao modification]` 标注；`LICENSE`/`NOTICE`/红线文件未触碰。

---

## 阶段 6.ab · 前端文案收敛：消除「技能池」概念（2026-08-25）

_背景：阶段 6.aa 收敛了导航入口，但「技能」页（可达）内部仍向用户暴露「技能池 / Skill Pool」字样（按钮、提示、弹窗、空状态、升级与语言切换确认等）。单用户视角下「池」是多租户术语噪音，应彻底无感。_

- [修改] `console/src/locales/zh.json` — 用户可见文案中的「技能池」统一改为「技能库」；同步收敛嵌套措辞「池技能」→「技能库技能」、「池中（有 / 缺失 / 副本）」→「技能库中（有 / 缺失 / 副本）」，含侧边栏与设置区 `skillPool` label（其菜单/页面入口已不可达，仅收敛口径）。中文零残留「池」字。
- [修改] `console/src/locales/en.json` — 对应英文 `Skill Pool` → `Skill Library`（覆盖 `skill pool` / `pool skills` / `the pool` / `pool copy` / `in pool` / `local pool` 全部组合），双语同步。残留 `pool`/`Pool` 仅存于 i18n **key 名**（如 `skillPool` / `uploadToPool` / `deletedFromPool`，属代码标识符，不可改）。
- [保留] 底层 `SkillPoolService` / `SkillService` 机制、API（`/skills/pool/*`）、`pages/Settings/SkillPool/` 页面代码**全部不动**；仅是 UI 文案视角把「共享技能池」改称为「技能库」。
- [零破坏] 纯 locale 文案层改动，未改任何 `.tsx` / `.py` 逻辑；JSON 已校验合法。若需还原措辞，回退本提交即可。
- [合规] locale 文件无法行内注释，故于此记录；`LICENSE` / `NOTICE` / 红线文件未触碰。

---

## 阶段 6.ac · Agent 人格文档（md_files）维护补全（2026-08-25）

_背景：阶段 6 品牌化后，agent 人格五件套（AGENTS/SOUL/PROFILE/BOOTSTRAP/HEARTBEAT）的 hanbao 化已覆盖 en/zh/id/ru 四套核心，但 `qa/` 与 `local/` 子目录缺 `hanbao_modification` 标注，且 `zh/SOUL.md` 标注误写「豆包」（字节跳动竞品 Doubao 笔误，正文已正确用「hanbao」）。本次补全标注口径一致性。_

- [修正] `src/hanbao/agents/md_files/zh/SOUL.md` — frontmatter `hanbao_modification` 标注中「定制化豆包」→「定制化函包」（笔误修正，正文「你是 hanbao」无误）。
- [补标注] `qa/{en,zh,ru}/{AGENTS,PROFILE,SOUL}.md`（9 个）— 补 `hanbao_modification` 字段，注明内容已用 Hanbao 品牌名、copaw legacy 路径（`~/.copaw` / `COPAW_*`）作为 `HANBAO_WORKING_DIR` fallback 有意保留。
- [补标注] `local/{en,zh}/SOUL.md`（2 个）— 补 `hanbao_modification` 字段，注明为通用本地 Agent 模板直接采用、无品牌专属改动。
- [零破坏] 仅 frontmatter 增字段 + 一处笔误修正，未改任何正文语义；YAML 结构校验通过。HEARTBEAT.md 为空模板占位（无标注，合理）。
- [合规] 五件套扫描：QwenPaw / AgentScope / 通义 等上游品牌词 0 命中，已砍功能词（Tauri / Chromium / 本地 LLM / 多租户）0 命中；`LICENSE` / `NOTICE` / 红线文件未触碰。

---

## 未修改声明

除本文件记录的改动外，hanbao 中其余代码均来自上游 QwenPaw v2.0.1，其著作权归 The QwenPaw Authors 所有，按 Apache License 2.0 条款授权使用。

---

## 阶段 6.ad · 减法改造：删除内置 QA/Local agent 类型与主人格 id/ru 语言，仅留中英双语（2026-08-25）

_背景：用户确认 hanbao 只做中英双语（en/zh），其余语言与多余内置 agent 类型一律干掉。原 `md_files/` 下主人格有 en/zh/id/ru 四语言，另有 `qa/`、`local/` 两个**独立 agent 类型**（内置 QA 助手 / 本地模型 Agent）；`templates.py` 据此暴露 `default`/`qa`/`local` 三种 agent 模板。本次把主人格收敛到 en/zh，并把 `qa`/`local` 两类型整体删除（含目录与全部后端接线）。_

- [删除·目录] `src/hanbao/agents/md_files/{id,ru,qa,local}/`（21 个文件）— 主人格 id/ru 语言变体 + qa/local 两 agent 类型目录整体移除；仅留 `en/`、`zh/`。`SUPPORTED_AGENT_LANGUAGES` 由 `_discover_agent_languages()` 动态发现，删目录后自动收敛到 `{en, zh}`。
- [修改] `src/hanbao/agents/templates.py` — 移除 `build_local_agent_tools_config`/`build_qa_agent_tools_config` 与 `BUILTIN_QA_AGENT_*` 导入；`SUPPORTED_AGENT_TEMPLATES = (DEFAULT_AGENT_TEMPLATE,)`（删 `LOCAL_AGENT_TEMPLATE`/`QA_AGENT_TEMPLATE`/`LOCAL_TEMPLATE_SKILL_NAMES`/`QA_TEMPLATE_DESCRIPTION`）；`get_workspace_md_template_id` 恒返 `None`；`build_agent_template` 仅留 default 分支 + `raise ValueError`。
- [修改] `src/hanbao/constant.py` — 删「Builtin Q&A helper profile」注释块；fallback `frozenset({"en","zh","ru"})` → `frozenset({"en","zh"})`；删除 `BUILTIN_QA_AGENT_*` 常量。**保留 `LEGACY_QA_AGENT_ID = "CoPaw_QA_Agent_0.1beta1"`**——其为刻意保留的 CoPaw 遗留迁移逻辑（`migration._apply_legacy_qa_disable_for_migration` 仍引用），删则运行时 `ImportError`，故保留并加注释说明。
- [删除] `src/hanbao/agents/utils/setup_utils.py` 的 `copy_builtin_qa_md_files` 函数及其在 `__init__.py` 的 import / `__all__` 条目。
- [删除] `src/hanbao/config/config.py` 的 `build_qa_agent_tools_config()` 与 `build_local_agent_tools_config()` 两函数。
- [修改] `src/hanbao/app/migration.py` — import 精简（删 `QA_AGENT_TEMPLATE` / `BUILTIN_QA_AGENT_ID`）；`_fallback_active_agent_id` 仅候选 `("default",)`；用脚本删除文件末尾 `ensure_qa_agent_exists` + `_do_ensure_qa_agent` 两函数（102 行）；保留 `_apply_legacy_qa_disable_for_migration`。
- [修改] `src/hanbao/app/multi_agent_manager.py` — 删 `BUILTIN_QA_AGENT_ID` import；`core_agent_ids` 仅 `["default"]`；docstring 收敛为单一核心 agent。
- [修改] `src/hanbao/app/routers/workspace.py` — 删 `BUILTIN_QA_AGENT_ID` import 与 `or ("qa" if ...)` 回退；`md_template_id=get_workspace_md_template_id(agent_config.template_id)`。
- [修改] `src/hanbao/app/_app.py` + `cli/init_cmd.py` — 确认内置 QA Agent 自动创建逻辑此前已注释停用，本次仅清理残留注释指针，无新增自动创建。
- [同步测试] `tests/unit/app/test_multi_agent_manager_startup.py`、`tests/unit/agents/utils/test_setup_utils.py`、`tests/integration/test_agents.py` — 移除 `BUILTIN_QA_AGENT_ID` 引用，单核心断言改写（default 为唯一核心 agent，禁用 default 时返回 `{}` 且不触发回调）。
- [零破坏] 仅 default agent 为内置核心语义不变；QA 自动创建此前已停用，local LLM 已删，删除爆炸半径锁定在后端接线，前端无 qa/local 模板选择器依赖（grep 复核全为 `localStorage`/`antd/locale` 噪声）。
- [验证] `py_compile` 改动 13 文件全绿；全仓（src/hanbao）grep 删除符号零残留引用；`git grep` 确认 `LEGACY_QA_AGENT_ID` 在 constant.py 已恢复、migration.py 引用可解析。
- [合规] 改动文件均含 `[hanbao modification]` 标注；`LICENSE` / `NOTICE` / 红线文件未触碰。

### 附：cloudpaw 插件人格文档标注审计（2026-08-25，无改动）

_用户「要」触发：对 `plugins/bundle/cloudpaw/agents/{executor,orchestration,verifier}/{en,zh}/{PROFILE,SOUL}.md`（12 个）做 `[hanbao modification]` 标注 / 品牌合规审计。_

- [结论] **无需改动。** 12 文件均随 `9b86a97`（pristine QwenPaw v2.0.1 导入）进入仓库后**从未被 hanbao 修改**；按 R2 合规规则，`[hanbao modification]` 仅标于 hanbao 改过的文件，故这些文件不加标注即为正确状态（加了反而不合规）。
- [品牌] 正文使用插件自身名 `CloudPaw-*`（非禁用商标 QwenPaw/AgentScope/Qwen/通义）；12 文件 0 命中禁用商标词。
- [双语] 仅 en/zh，无 id/ru/qa/local，与本次收敛决策一致。
- [依赖] 全插件 grep `qa`/`local` agent 类型引用 0 命中，未引用已删的 `BUILTIN_QA` 机制；其引用的 `alicloud_cli` / `iac-code` / ACP Runner / Mission Mode 均属插件自身能力，仍有效。
- [旁注] `cloudpaw/README*.md` 引用了 `raw.githubusercontent.com/agentscope-ai/QwenPaw/...` 的图片 URL（上游仓库地址，非正文商标）——属人格文档审计范围外，且仅为外链图片，不影响分发合规；若后续要做品牌彻底去上游化可单独处理。

## 阶段 6.ae · Dockerfile 国内镜像源加速（2026-08-26）

_背景：构建验证时直连 `deb.debian.org` / `npmjs.org` / `pypi.org` 在 CN 网络下极慢，buildx 卡死在 runtime 阶段 `apt-get install build-essential`（gcc 工具链，约 480s 无输出）。注入国内镜像源实现无代理直连构建；同时保留原代理 ARG/ENV 通道，代理环境仍可用 `--build-arg HTTP_PROXY=...` 覆盖。该改动对飞牛 FPK 的无代理 `fnpack build` 环境同样有利。_

- [修改] `deploy/Dockerfile` — 三处注入国内镜像源，均带 `[hanbao modification]` 标注：
  - console-builder 阶段 `npm ci` 前新增 `RUN npm config set registry https://registry.npmmirror.com`
  - runtime 阶段（`python:3.12-slim`, trixie）首次 `apt-get update` 前新增 `RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources`（Debian 13 用 deb822 源，格式经 `docker run --rm python:3.12-slim` 核实）
  - `uv pip install --no-cache-dir .` 改为 `uv pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ .`
  - _（2026-08-26 修正）原 `pypi.tuna.tsinghua.edu.cn` 在构建时拉 `certifi` 抽风超时（124s×3 retries 失败），已切 Aliyun PyPI 源；对飞牛 FPK 无代理 `fnpack build` 环境同样更稳。_
- [验证] sed 替换目标经容器内 `cat /etc/apt/sources.list.d/debian.sources` 核实 deb822 格式正确（两处 `URIs: http://deb.debian.org/...`）；Aliyun PyPI 源构建已验证通过（镜像产出 + 冒烟全绿）。
- [合规] 未触碰 `LICENSE` / `NOTICE` / 红线文档；代理通道保留，重写分发（镜像/FPK）仍随附 LICENSE + NOTICE。

## 阶段 6.af · 全局默认 LLM 支持 UI 清空（2026-08-27）

_背景：用户要求全局「默认 LLM」出厂为空且可在 UI 上清空回空。后端 `active_llm` 出厂默认已为 `None`，缺的是清除入口。_

- [修改] `src/hanbao/app/routers/providers.py` — 新增 `DELETE /models/active` 端点，复用已有 `ProviderManager.clear_active_model()`（带 `[hanbao modification]` 标注）。
- [修改] `console/src/api/modules/provider.ts` — 新增 `clearActiveLlm()`（带 `[hanbao modification]` 标注）。
- [修改] `console/src/pages/Settings/Models/components/sections/ModelsSection.tsx` — 新增 `handleClear` 与「清除默认模型」危险按钮（带 `[hanbao modification]` 标注）。
- [修改] `console/src/locales/zh.json` / `en.json` — `models` 段新增 `clearDefaultLlm`、`llmModelCleared`。
- [文档] `docs/known-issues.md` 登记 I-035；I-034 状态更新为已解决（真机验证通过）。

## 阶段 6.ag · 品牌展示名统一为 hanbao + 登录页去水墨文案（2026-08-27）

_用户要求：飞牛应用中心显示名直接叫 hanbao（不要「函包 hanbao」）；登录/注册页品牌也用 hanbao，且不要通过文字表达水墨风格（原标语「墨痕未干，对话已成。家庭本地 · 水墨文人对话」很违和）。_

- [修改] `deploy/fpk/manifest` — `display_name` 由 `函包 hanbao` 改为 `hanbao`。
- [修改] `console/src/pages/Login/index.tsx`：
  - 左栏品牌主标题「函包」→ `hanbao`；删除冗余副标「HANBAO」与诗句标语「墨痕未干，对话已成。」；底标由「家庭本地 · 水墨文人对话」改为「家庭本地 · 私人 AI 聊天助手」（仅保留事实定位，去文字层面的风格表达）。
  - 左栏与右卡两枚朱砂闲章去掉内填「函」字，改为纯装饰印记（边框 + 旋转，无文字）。
- [合规] 改动文件均含 `[hanbao modification]` 标注；图标 `console/public/online.svg`（Mikasa 肖像 = hanbao 图标）按红线零碰触、保持不变。
- [文档] `docs/known-issues.md` 登记 I-036（🟢 已解决）。

## 阶段 6.ah · FPK 分发物合规补全 + 上游品牌残留清理（2026-08-28）

_背景：全模块合规扫描发现 `hanbao.fpk` 未随附 LICENSE/NOTICE/CHANGES（违反 §4 阶段5 与 §8），`manifest` 缺 `license` 字段，且品牌改名漏网三处对外引用（PYPI_URL 两处、OpenRouter Referer 一处）。_

- [合规] `deploy/fpk/` 新增 `LICENSE`（顶层，fnpack 自动打包）；`deploy/fpk/app/` 新增 `NOTICE` 与 `CHANGES-FROM-UPSTREAM.md`（进 app.tgz，因 fnpack 仅打包约定文件 + 顶层 LICENSE）。重新 `fnpack build` 验证三者均在包内。
- [修改] `deploy/fpk/manifest` — 增 `license=Apache-2.0`（带 `[hanbao modification]` 标注）。
- [修改] `src/hanbao/cli/update_cmd.py` — `_PYPI_JSON_URL` 由 `qwenpaw` → `hanbao`（带 `[hanbao modification]` 标注）。
- [修改] `console/src/layouts/constants.ts` — `PYPI_URL` 同上。
- [修改] `src/hanbao/providers/openrouter_provider.py` — `HTTP-Referer` 由 `qwenpaw.agentscope.io` → `github.com/yijiuzero/chat-hanbao`（带 `[hanbao modification]` 标注）。
- [文档] `docs/known-issues.md` 登记 I-037（🔴 合规红线，🟢 已解决）；`website/` 品牌残留留作后续单独审计。

## 阶段 6.ai · website/ 文档站上游品牌残留审计与清理（2026-08-28）

_背景：I-037 风险项明确 `website/` 品牌残留留作后续单独审计。本轮对 website/ 代码与文案层（index.html / config.ts / site.config.json / testimonials.ts / i18n locales / Nav·Footer·Contributors·FinalCTA·FAQ·QuickStart 组件 / Ecosystem·FollowUs）做减法式品牌清理，目标是消除一切暗示「hanbao 即上游 QwenPaw / 获阿里·通义背书」的对外展示。_

- [修改] `website/index.html` — 删除可爬取上游元信息：`canonical` / `og:url` / `og:image`·`twitter:image` 指向 `qwenpaw.agentscope.io` 的链接改本地 `/hanbao_ip.png`；移除 3 个搜索引擎验证 token（Google/Bing/Baidu，属上游站点）。均加 `[hanbao modification]` 注释。
- [修改] `website/src/config.ts` + `website/public/site.config.json` — `repoUrl` 由 `agentscope-ai/QwenPaw` → `github.com/yijiuzero/chat-hanbao`；`modelScopeForkUrl` target 由 `AgentScope/QwenPaw` → `yijiuzero/chat-hanbao`（hanbao 尚未发布 ModelScope studio，作占位，见 I-038）。
- [修改] `website/src/data/testimonials.ts` — 移除 mock 证言中 "Python + AgentScope" 上游背书措辞。
- [修改] `website/src/i18n/locales/{zh,en,pt-BR}.json` — `clientVoices` 中阿里云/通义背书（t1 头衔、t2、t6 文本）移除；`footer.copyright` 由虚假法律主体 "© 2026 Qwenpaw PRIVATE LIMITED" → "© 2026 hanbao"。
- [修改] `Nav.tsx`/`Footer.tsx`/`Contributors.tsx`/`FinalCTA.tsx`/`FAQ.tsx`/`QuickStart.tsx` — GitHub / releases / issues 链接由 `agentscope-ai/QwenPaw` → `yijiuzero/chat-hanbao`；QuickStart 安装脚本由 `qwenpaw.agentscope.io/install.*` → `raw.githubusercontent.com/yijiuzero/chat-hanbao/main/scripts/install.*`；各文件加 `[hanbao modification]` 头注释。
- [保留] `public/docs`、`public/blog`、`public/release-notes` 中的上游仓库/issue 链接与 `qwenpaw.agentscope.io` 文档链接 — 按 §8 必须展示上游出处，作署名保留，不在本轮改动。
- [待决策] heroLine（"Qwen Personal Agent Workstation / Qwen 的智识"）、`DOCKER_IMAGE=agentscope/hanbao`、`FeatureDemoGallery` 文档 URL、`Downloads` CDN_BASE、NavCommunityBenefits 阿里权益页、FollowUs/Footer 的 `@agentscope_ai` 社媒账号 — 见 I-038。
- [文档] `docs/known-issues.md` 登记 I-038。
