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

_（待执行）_

## 阶段 4 · 容器化

_（待执行；须同批修复 I-002 `COPY LICENSE NOTICE` 与 I-003 `.dockerignore` 白名单）_

## 阶段 5 · FPK 打包

_（待执行）_

---

## 未修改声明

除本文件记录的改动外，hanbao 中其余代码均来自上游 QwenPaw v2.0.1，其著作权归 The QwenPaw Authors 所有，按 Apache License 2.0 条款授权使用。
