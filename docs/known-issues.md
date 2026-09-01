# hanbao 已知问题与踩坑追踪

> 本文件记录移植 QwenPaw 过程中发现的**必须处理但当前阶段尚未处理**的问题。
> 每项都有明确的「必须处理时机」，到达对应阶段时**必须逐项核对**，未处理不得进入下一阶段。
>
> 状态取值：`🔴 待处理` / `🟡 处理中` / `🟢 已解决` / `⚪ 已确认无需处理`

## 索引

| 编号 | 问题 | 严重度 | 必须处理时机 | 状态 |
|---|---|---|---|---|
| [I-001](#i-001) | 上游 `.gitignore` 静默吞掉运行时必需文件 | 🔥 高 | 阶段 0（已完成） | 🟢 已解决 |
| [I-002](#i-002) | Dockerfile 缺 `COPY LICENSE NOTICE`（合规缺口） | 🔥 高（法务） | 阶段 4 容器化 | 🟢 已解决（2026-08-17） |
| [I-003](#i-003) | `.dockerignore` 的 `*.md` 会排除合规文档 | 🔥 高（法务） | 阶段 4 容器化 | 🟢 已解决（2026-08-17） |
| [I-004](#i-004) | 镜像含完整 XFCE4 桌面 + Chromium，体积巨大 | 🟠 中 | 阶段 4 容器化 | 🟢 已解决（1.78GB；800MB 目标经实测评估不可达，务实线 ≤1.5GB 待定） |
| [I-005](#i-005) | 基础镜像拉取失败（buildkit 并发鉴权 EOF） | 🟠 中 | 阶段 1 构建时 | 🟢 已解决（预拉规避） |
| [I-006](#i-006) | 上游自带遥测上报 | 🟠 中 | 阶段 2 删减定制 | 🟢 已解决（上报禁用+调用移除） |
| [I-007](#i-007) | Web Console 默认无认证（上游认证系统完整，仅默认关闭） | 🟠 中 | 阶段 5 FPK 打包 | 🟢 已解决（镜像层默认开认证） |
| [I-008](#i-008) | console 前端构建 OOM，4GB WSL 内存不足 | 🔥 高（曾阻塞） | 阶段 1 构建时 | 🟢 已解决 |
| [I-009](#i-009) | 构建机 C 盘 0GB 可用，Docker 无法写入 | 🔥 高（阻塞） | 阶段 1 构建时 | 🟢 已解决（迁 F 盘 Junction） |
| [I-010](#i-010) | WSL 崩溃转储吞噬 18.58GB 磁盘 | 🔥 高 | 阶段 1 构建前 | 🟢 已解决（crashDumpCount=0） |
| [I-011](#i-011) | Docker DataFolder 键对 WSL2 后端无效 | 🟠 中 | 阶段 1 构建前 | 🟢 已解决（Junction 重定向） |
| [I-012](#i-012) | 品牌名残留：JS 命名空间 `window.Hanbao` | 🟡 低 | 阶段 3 删减定制 | 🟢 已解决（2026-08-17 `window.hanbao`） |
| [I-013](#i-013) | 品牌名残留：localStorage keys (`hanbao_*`) | 🟡 低 | 阶段 3 删减定制 | 🟢 已解决（2026-08-17 `hanbao_*`） |
| [I-014](#i-014) | 品牌名残留：CSS 前缀 `hanbao` (Ant Design) | 🟡 低 | 阶段 3 删减定制 | 🟢 已解决（2026-08-17 `hanbao`） |
| [I-015](#i-015) | 包名全量改名：qwenpaw → hanbao（包/环境变量/标识符/目录） | 🟢 极低 | 阶段 5 FPK 前 | 🟢 已解决（2026-08-19 落地） |
| [I-016](#i-016) | 品牌名残留：插件 plugin.json author 字段 | 🟢 极低 | 无阻塞 | 🟢 保留上游署名（合规） |
| [I-017](#i-017) | sed 产生 JS 注释 `//` 污染 Python 文件 | 🔥 高 | 阶段 3 删减定制 | 🟢 已解决 |
| [I-018](#i-018) | git checkout 导致 gitignored 文件从磁盘消失 | 🔥 高 | 阶段 3 删减定制 | 🟢 已解决（gitignore 硬化） |
| [I-019](#i-019) | 文档处理能力：Anthropic 专有技能侵权移除；读用 markitdown，改/创建用自研 python-docx/openpyxl | 🔥 高 | 上架前必须解决 | 🟢 已解决（读 markitdown + 改/创建自研工具，2026-08-24） |
| [I-020](#i-020) | html2text 为 GPL-3.0 传染性依赖，违反 R5 红线 | 🔥 高 | 上架前必须解决 | 🟢 已解决（换 markdownify MIT） |
| [I-021](#i-021) | 依赖审计：4 个 LGPL 弱传染依赖（telegram-bot/rope/pytoolconfig/docstring-to-markdown） | 🟠 中 | 上架前备案 | 🟢 已备案 + 2026-08-21 telegram-bot 随 Telegram 频道砍除从依赖移除（LGPL 直接依赖清零） |
| [I-022](#i-022) | web_search 用 Tavily keyless（免费限速），重度使用会撞限速 | 🟡 低 | 上架后可优化 | 🟢 已解决（2026-08-24，env 变量方案） |
| [I-023](#i-023) | patch 累积 diff 的提交依赖（原「基线偏离」为误判，本地基线=官方 v2.0.1） | 🟡 低 | 移植靠后提交前先识别前置依赖 | 🟢 已澄清 |
| [I-024](#i-024) | Monaco 编辑器残留（Coding Mode 砍不干净） | 🟢 极低 | 阶段 3 收尾 | 🟢 已解决（依赖移除+占位符） |
| [I-025](#i-025) | 改 Dockerfile 触发 apt 层缓存失效，暴露 fonts-wqy-microhei 已从 Debian 源移除 → 构建失败 | 🟠 中 | 环境教训（已修复） | 🟢 已解决（移除 microhei，3b28257） |
| [I-026](#i-026) | 品牌色批量替换漏网：Spark 百炼紫 #615ced（50+ 处）与暖橘 rgba(255,157,77) 形式 | 🟠 中 | 去 qwenpaw 味专项（已修复） | 🟢 已解决（2d5973d/297cc80） |
| [I-027](#i-027) | 桌面线收尾：砍桌面端整条线时漏删的悬空 `/api/desktop/shutdown` 端点 + 孤儿 tauri 测试 | 🟠 中 | 桌面砍除收尾（已修复） | 🟢 已解决（2026-08-21 `d9a9875`） |
| [I-028](#i-028) | 前端界面两轮水墨化美化（边缘装饰→全面重做：登录页意境/聊天气泡/会话项/页眉） | 🟡 低 | 界面品牌化（已重建验收） | 🟢 已解决（2026-08-24 `a87fb07`+`59220ad`，镜像 `531ecf90e1ff`） |
| [I-029](#i-029) | ChannelDrawer 被砍频道死代码清理（10 频道 case 块 + 3 const + useEffect） | 🟢 极低 | 频道砍除收尾（已修复） | 🟢 已解决（2026-08-24 `5ed0391`） |
| [I-030](#i-030) | 运行配置页清理：auth.py 死白名单条目 + 隐藏 remeLightMemory TAB | 🟢 极低 | 界面收尾（已修复） | 🟢 已解决（2026-08-24 `039fa49`） |
| [I-031](#i-031) | header 被删模块占位：GitHub 后空 `<span>` + 双分隔线导致中间空一截 | 🟢 极低 | header 布局收尾（已修复） | 🟢 已解决（2026-08-24 `e27acfa`） |
| [I-032](#i-032) | 运行配置页下线：时区调整移入侧栏设置面板、整页删除 | 🟢 极低 | 界面收尾（已修复） | 🟢 已解决（2026-08-25） |
| [I-033](#i-033) | 删除 `append_file` 与 `delegate_external_agent` 两个后端工具及对应前端卡片/测试 | 🟢 极低 | 工具集减法（已修复） | 🟢 已解决（2026-08-25） |
| [I-034](#i-034) | FPK native 形态 `cmd/main` 执行 `docker load` 因权限失败 | 🔥 高 | 阶段 5 FPK 真机验证 | 🟢 已解决（2026-08-27 真机验证通过） |
| [I-035](#i-035) | 全局默认 LLM 支持在 UI 清空（新增 DELETE /active 端点 + 清除按钮） | 🟢 极低 | UI 增强 | 🟢 已解决（2026-08-27） |
| [I-036](#i-036) | 品牌展示名统一为 hanbao + 登录页去除用文字表达水墨风格的标语 | 🟢 极低 | 品牌展示层 | 🟢 已解决（2026-08-27） |

---

<a id="i-001"></a>
## I-001 · 上游 `.gitignore` 静默吞掉运行时必需文件

**严重度**：🔥 高 &nbsp;|&nbsp; **状态**：🟢 已解决（阶段 0，commit `419f4b4`）

### 现象
上游 release tarball 有 2846 个文件，但在本地 `git init && git add -A` 后只暂存了 2836 个。
差的 10 个文件**不是垃圾文件，全部是运行时必需资源**：

| 被吞的文件 | 数量 | 命中规则 | 丢了会怎样 |
|---|---|---|---|
| `src/hanbao/agents/md_files/**/AGENTS.md` | 7 | `.gitignore:109` 裸 `AGENTS.md` | Agent 提示词缺失，智能体行为异常 |
| `console/package-lock.json` | 1 | `.gitignore:82` | `npm ci` 失败，无法复现构建 |
| `plugins/bundle/cloudpaw/ui/dist/index.js` | 1 | `.gitignore:33` `dist/` | 插件加载失败 |

### 根因
上游仓库里这些文件是**已追踪状态**，Git 对已追踪文件不再应用 `.gitignore`，所以上游自己毫无感知。
而我们是从 **tarball 全新 `git init`**，所有文件都是未追踪状态，规则就全部生效了。

> ⚠️ **这类问题的危险性在于延迟爆发**：仓库能提交、能 clone，直到运行时才报莫名其妙的错，极难定位到"文件从来没进过仓库"。

### 处理
1. `git add -f` 强制纳入上述全部文件
2. 将 `.gitignore` 第 109 行 `AGENTS.md` 收窄为 `/AGENTS.md`（只匹配仓库根目录的开发者笔记）
3. 校验 `git ls-files | wc -l` == tarball 文件数 == 2846 ✅

### 可复用经验
**fork 任何他人项目时，必须比对 release 包文件数与 git 暂存文件数**，不一致就逐个核实。
核对命令：
```bash
find . -type f -not -path "./.git/*" | wc -l   # 磁盘文件数
git ls-files | wc -l                            # 已追踪文件数
git status --ignored --porcelain | grep "^!!"   # 被忽略的具体文件
```

---

<a id="i-002"></a>
## I-002 · Dockerfile 缺 `COPY LICENSE NOTICE`（合规缺口）

**严重度**：🔥 高（法务风险） &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-17） &nbsp;|&nbsp; **必须处理时机**：阶段 4 容器化

### 现象
上游 `deploy/Dockerfile` 中**没有任何拷贝 LICENSE / NOTICE 到镜像的指令**。
照原样构建出的镜像内部**不含许可文件**。

### 为什么上游没事而我们有事
| | 上游 QwenPaw | hanbao |
|---|---|---|
| 身份 | **版权方本人** | **再分发者（派生作品）** |
| 义务 | 自己的作品，随附与否自便 | Apache-2.0 §4(a)(b)(d) 强制随附 |

**只发镜像不发源码，同样构成"分发"**，义务照常生效 —— 这是最常见的误区之一（见 `license-compliance.md` §8）。

### 处理方案（阶段 3 执行）
在 `deploy/Dockerfile` 的 runtime 阶段追加：
```dockerfile
# [hanbao modification] Apache-2.0 compliance: ship license files inside the image
COPY LICENSE NOTICE /app/
COPY docs/CHANGES-FROM-UPSTREAM.md /app/docs/
```
并补充溯源 label：
```dockerfile
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.source="https://github.com/agentscope-ai/QwenPaw"
LABEL org.opencontainers.image.description="hanbao (函包), derived from QwenPaw v2.0.1"
```

### 验收
```bash
docker run --rm hanbao:<tag> sh -c "ls -l /app/LICENSE /app/NOTICE"
```
两个文件都在且非空，方可认为阶段 3 合规检查通过。

---

<a id="i-003"></a>
## I-003 · `.dockerignore` 的 `*.md` 会排除合规文档

**严重度**：🔥 高（法务风险） &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-17） &nbsp;|&nbsp; **必须处理时机**：阶段 4 容器化（与 I-002 同批）

### 现象
上游 `.dockerignore` 含 `*.md` 规则，会把 `docs/` 下所有 Markdown 排除出构建上下文。
这意味着**即便 I-002 里加了 `COPY docs/CHANGES-FROM-UPSTREAM.md`，构建也会直接失败**（文件不在上下文里）。

> 💡 I-002 和 I-003 是**连体问题**，必须同时修，只修一个会撞墙。

### 处理方案（阶段 3 执行）
在 `.dockerignore` 末尾追加白名单例外：
```
# [hanbao modification] keep license compliance artifacts in build context
!LICENSE
!NOTICE
!docs/CHANGES-FROM-UPSTREAM.md
!docs/license-compliance.md
```

### 验收
构建不报 "file not found" 且 I-002 的验收命令通过。

---

<a id="i-004"></a>
## I-004 · 镜像含完整 XFCE4 桌面 + Chromium，体积巨大

**严重度**：🟠 中 &nbsp;|&nbsp; **状态**：🟢 已解决（1.78GB，2026-08-18 第二刀瘦身验收；800MB 经实测评估极难达成，务实线 ≤1.5GB 待用户拍板） &nbsp;|&nbsp; **必须处理时机**：阶段 4 容器化

### 现象
`deploy/Dockerfile` 的 runtime 阶段安装了：
- **XFCE4 完整桌面环境** + **Xvfb** 虚拟显示服务器
- **Chromium** 浏览器（用于浏览器自动化 / 网页操作能力）
- **build-essential** 编译工具链

预估镜像 **2–4GB**。飞牛 NAS 通常内存 4–8GB、存储也不宽裕，这是实打实的负担。

### 历史：2026-08-14 依赖摸底结论
- Chromium 依赖链：`browser_control.py`（`browser_use` 工具）→ Playwright → Chromium（`PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium`）
- 桌面环境（XFCE4/Xvfb/dbus）无其他代码依赖，可安全删
- 中文字体（fonts-wqy-zenhei/microhei）渲染中文仍需要，保留
- **瘦身核心决策点**：浏览器工具 `browser_use` 去留 → 决定 Chromium（约 1-2GB）能否删
- 这是**全项目瘦身收益最大的一块**，预计可省 50%+ 体积

### 处理方案（2026-08-17 执行）
用户拍板「砍掉 browser_use + 桌面截图」后，本次一并完成代码摘除与镜像瘦身：

**1. 后端工具摘除（[hanbao modification]）**
- `src/hanbao/agents/tools/__init__.py` — 移除 `browser_use`、`desktop_screenshot` 两个内置工具注册
- `src/hanbao/agents/react_agent.py` — 移除两工具的 hook 超时注册
- `src/hanbao/agents/memory/proactive/proactive_responder.py` — 移除 `browser_use`/`desktop_screenshot` 的 import 与工具装配（FunctionTool 列表 + 多模态追加分支）
- `src/hanbao/agents/memory/proactive/proactive_utils.py` — 移除 `build_proactive_memory_context` 中"屏幕活动分析"调用块

**2. 依赖摘除（pyproject.toml）**
- 移除 `playwright>=1.49.0`（browser_use 专属）、`mss>=9.0.0`（desktop_screenshot 专属）、`pywebview>=4.0`（桌面 GUI，仅 `desktop_cmd.py` 惰性 import，缺失优雅降级）

**3. 镜像瘦身（deploy/Dockerfile + supervisord）**
- runtime 基础镜像 `node:slim` → **`agentscope/uv`（Python+uv）**，去掉 Node 运行时（约 200MB+）
- 删除 apt 安装的 XFCE4 / xfce4-terminal / Xvfb / dbus-x11 / Chromium + 15 个依赖库 / fonts-liberation / vim
- `build-essential` 改为「安装 → `uv pip install` → 末尾 `apt-get purge`」临时使用，不进最终镜像
- 移除 supervisord 的 `dbus`/`xvfb`/`xfce4` 三个程序，`app` 程序去掉 `DISPLAY`/`PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` 环境变量
- 保留 `HANBAO_RUNNING_IN_CONTAINER=1`（config 有 `/.dockerenv`+cgroup 兜底，保险仍设）
- 合规层 LICENSE/NOTICE/CHANGES + OCI labels（I-002）原样保留

**4. 待用户手动清理的孤儿文件（不 git rm，按环境安全规则留 orphan）**
- `src/hanbao/agents/tools/browser_control.py`、`browser_snapshot.py`、`desktop_screenshot.py` — 已无引用但仍被 `COPY src ./src` 带进镜像（约数十 KB，无害）
- `proactive_utils.py` 中 `_analyze_screen_activity` 函数已成死代码（调用方已删，内部 lazy import 不触发）

### 验收（待构建，按铁律先 commit 不立即 build）
```bash
docker build -f deploy/Dockerfile -t hanbao:0.0.1-slim .
docker images hanbao:0.0.1-slim   # 目标 ≤ 800MB
docker run --rm hanbao:0.0.1-slim sh -c "which chromium xvfb-run startxfce4 2>/dev/null; echo desktop-tools-removed"
```

### 构建验证（2026-08-18）
**构建方式**：`DOCKER_BUILDKIT=0` 直连（绕开 buildx 拉 `moby/buildkit` 构建器镜像时卡死的死代理）。前端 `npm run build`、Python `uv pip install` 直连 npmjs/pypi 均 200 可达，全链路通过。

**中途两处修复（[hanbao modification]）**：
1. runtime 基础镜像 `agentscope/uv:latest` → `python:3.12-slim`：`agentscope/uv` 是纯 uv 执行器（`Entrypoint=/uv`、无 `/bin/sh`、无 apt），导致 `RUN apt-get` 直接崩；换成有 shell+apt 的官方 Python slim 镜像（满足 `requires-python >=3.11,<3.14`）。
2. `COPY --chmod=755 ...` → `COPY ...` + `RUN chmod +x`：旧版构建器不支持 `--chmod` 语法。

**结果**：镜像 **1.91GB**（原 ~4GB，砍掉 Chromium+XFCE4 桌面+Node 运行时后砍半）。Chromium/Xvfb/xfce4 已确认不在镜像内。

### 最终重建 + 干净容器验收（2026-08-18 二次构建）
删除孤儿文件（`browser_control` / `browser_snapshot` / `desktop_screenshot`）与工作区草稿后重建，固化 P0 语法修复（`b95b02c`）。

**构建**：47/47 步全过，`BUILD_EXIT=0`，耗时 6m41s。镜像 **1.93GB**。
> 体积从 1.91GB → 1.93GB 的 +20MB 属**正常构建波动**（apt/pypi 上游包版本浮动，1.9GB 基数上约 1%）；删掉的 3 个 Python 文件仅数十 KB，对体积无实质影响。瘦身结论不变。

**干净容器验收**（`docker run -d --name hanbao_clean -p 18088:8088`，**不挂任何宿主目录**，避免上次"宿主 src 覆盖镜像内前端产物"的误判）：
| 验收项 | 结果 |
|---|---|
| 桌面栈剥离 | `chromium` / `chromium-browser` / `google-chrome` / `Xvfb` / `xvfb-run` / `xfce4-session` / `dbus-daemon` / `node` / `npm` 全部 `which` 无输出 ✅ |
| Python / uv | `Python 3.12.14`、`uv` 就位 ✅ |
| 前端产物在镜像内 | `/app/src/hanbao/console/`（`assets/` + `hanbao-logo.jpg` 243KB）✅ |
| 服务启动 | supervisord 仅 `app` 一个进程（桌面栈进程已从 template 移除），10s 后 `entered RUNNING` ✅ |
| 根路径真实性 | HTTP 200 且 body 为真实 React 页（`<title>hanbao Console</title>` + `<div id="root">` + `/assets/index-*.js`），**非** `console is not available` 错误 JSON ✅ |
| API | `auth/status` → `{"enabled":false,"has_users":false}`（I-007 设计，默认不启用认证）✅ |
| 静态资源 | `/hanbao-logo.jpg` → HTTP 200 ✅ |
| 日志异常扫描 | `traceback` / `IndentationError` / `ImportError` / `ModuleNotFound` / `browser_use` / `playwright` / `desktop_screenshot` **零命中** ✅ |

**P0 修复固化确认**：`provider_manager.py` 的孤立 `if` 曾使整条 import 链 `IndentationError`、服务完全起不来；本次干净容器中 app 稳定 RUNNING、日志零 `IndentationError`，即修复已固化进镜像。

**验证方法学备忘**（两个已踩过的坑，勿重犯）：
1. 验证容器**不要**挂宿主 `src`（`-v 宿主src:/app/src`）——会盖掉镜像内 `console/` 构建产物，导致假报"前端未构建"。
2. 只查 HTTP 状态码不够——`console is not available` 错误 JSON 也返回 200，**必须查 body**。

**体积构成（docker history + 容器 du）**：
- `/app/venv` **746MB**（Python 依赖）—— 绝对大头
- apt 运行时系统库 + 中文字体层 ~1GB（python:3.12-slim 基础 ~150MB + 运行时依赖）
- `/app/src` 39MB、`/usr/share/fonts` 25MB

**第二阶段：冲 800MB（已实施第一刀：砍本地模型残留）**

> ✅ **前置影响分析已完成（2026-08-18，源码+镜像 venv 实测）**，以下为实测结论，替代早前推测。

> ✅ **第一刀已落地验收（2026-08-18，commit `ccc0fe8` + 重建验证）**：
> - 删除主依赖 `transformers`(54M)/`modelscope`(33M)/`huggingface_hub`（本地 LLM 残留，src 零 import），`local` extra 清空（保留空定义兼容 `full` 引用）
> - 保留 `onnxruntime`/`sympy`（markitdown→magika→document_reader 技能链）
> - **结果**：镜像 **1.93GB → 1.78GB**（-150MB，含连带依赖），venv 746M→629M；干净容器验收全绿（认证默认开 `enabled:true`、18 渠道注册完整、markitdown CLI 实测可用）
> - 渠道 SDK（钉钉/飞书/短信等）**按用户拍板保留**（保持多渠道能力）

**渠道 SDK（2026-08-21 更新：10 个频道已砍，其 SDK 已从 `pyproject.toml` 移除）**：
- ✅ 已移除：`discord-py` / `python-telegram-bot` / `slack-bolt` / `paho-mqtt` / `matrix-nio` / `twilio`，以及 SIP extras（`pyVoIP` / `dashscope` / `dashscope-realtime` / `livekit`）——对应 10 个被砍频道（Discord/Telegram/Slack/MQTT/Matrix/语音/OneBot/元宝/SIP/Mattermost），删除前已确认 src 零 import；镜像重建后体积进一步下降（python-telegram-bot 的 LGPL 直接依赖也随之消除，见 I-021）
- 保留（家庭场景渠道）：`lark_oapi`（飞书）+ 钉钉全家桶 + `wecom-aibot-python-sdk`（企业微信）+ `dingtalk-stream`——按用户拍板保留多渠道能力；registry 独立 import + try/except 容错，SDK 缺失不崩

**本地模型残留（本地 LLM 已砍，纯云 API；src 零 import，纯依赖残留）**：
- `transformers` 54M + `modelscope` 33M + `huggingface_hub` → pyproject 主依赖声明，但 `src` 无任何直接/动态 import（`market/providers/modelscope.py` 仅 HTTP provider 名字撞包名，非包引用）；`google_genai` 依赖 transformers 仅 `extra == "local-tokenizer"`（未启用）
- ⚠️ **`onnxruntime` 50M 不能删**：`markitdown`→`magika`（`magika/magika.py:31` 顶层 `import onnxruntime as rt`）→ 文档读取技能 `document_reader`（I-019 保留功能）硬依赖链
- `sympy` 31M 被 `onnxruntime` 硬依赖（无 extra 条件）→ 连带保留
- `pandas` 42M：`openai` 依赖仅 `extra == "datalib"`、`agentscope` 仅 `extra == "rag"`、`markitdown` 仅 `extra == "all"`（均未启用），但 `fsspec`/`modelscope` 链路牵连，需结合上项删除后再复核

**可砍约 200MB+（渠道 SDK 全砍 + transformers/modelscope/hf_hub）**，砍后 venv 预计 ~500MB，总镜像预计 ~1.6GB。**结论：800MB 在当前单层依赖结构下仍极难达成**（venv 至少 ~500MB + 系统层 ~700MB+），需评估接受"≤1.5GB 务实线"或换 `python:3.12-alpine`（省 ~100MB 但 glibc→musl 可能破坏 onnxruntime/magika 等预编译 wheel）。此子阶段实施前须：① 用户拍板渠道 SDK 去留（功能取舍）；② 确认 document_reader 技能保留则 onnxruntime/sympy 必留；③ 实施时改 pyproject 主依赖（勿留 extra 声明）。

---

<a id="i-005"></a>
## I-005 · 基础镜像拉取失败（buildkit 并发鉴权 EOF）

**严重度**：🟠 中 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-10，预拉规避）

### 现象
首次 `docker build` 在加载基础镜像 metadata 阶段即失败：
```
ERROR: failed to authorize: failed to fetch anonymous token:
Get "https://dockerauth.ap-southeast-1.aliyuncs.com/auth?scope=...": EOF
```
`deploy/Dockerfile` 默认基础镜像指向阿里云 ACR 新加坡节点
（`agentscope-registry.ap-southeast-1.cr.aliyuncs.com`）。

### 排查过程与真实根因
初判"新加坡节点国内不可达"，但**逐个验证后结论相反**：

| 目标 | `docker manifest inspect` 结果 |
|---|---|
| 阿里云 ACR `agentscope/node:slim` | ✅ **可达** |
| `ghcr.io/astral-sh/uv:latest` | ✅ 可达 |
| Docker Hub `node:slim` | ❌ 不可达 |

即：**阿里云源本身没问题，反倒是 Docker Hub 不通**——若按第一直觉"换成 Docker Hub 官方镜像"，会从能用换成不能用。

真实原因是 buildkit 在 metadata 阶段**并发**向 `dockerauth.aliyuncs.com` 请求匿名 token，
经 Docker Desktop 代理（`http.docker.internal:3128`）时连接被重置（EOF）。
单线程 `docker pull` 则完全正常。

### 解决方案
构建前**预拉基础镜像到本地**，让 build 阶段直接命中本地缓存，绕开并发鉴权：
```bash
docker pull agentscope-registry.ap-southeast-1.cr.aliyuncs.com/agentscope/node:slim
docker pull agentscope-registry.ap-southeast-1.cr.aliyuncs.com/agentscope/uv:latest
docker build -f deploy/Dockerfile -t hanbao:<tag> .
```
实测两个镜像 63 秒拉完，随后构建正常推进。

### 备选方案（预拉也失败时）
上游留了 `--build-arg` 口子可换源，但**须先验证目标源可达**，别想当然：
```bash
docker build --build-arg NODE_IMAGE=node:22-slim \
             --build-arg UV_IMAGE=ghcr.io/astral-sh/uv:latest ...
```

> 💡 **可复用经验**：registry 报错先别急着换源。
> `docker manifest inspect <image>` 能在几秒内区分「源不可达」和「build 期鉴权问题」，
> 前者要换源，后者预拉即可——处理方式完全相反。

### ⚠️ 附带教训：Git Bash 下 `timeout` 是陷阱
排查时用 `timeout 60 docker manifest inspect ...` 测连通性，三个 registry 全报 FAIL。
实为 **Windows `timeout.exe` 抢占了命令名**（报「无效语法」直接退出非 0），
导致 docker 命令**根本没执行**，产生**全假阴性**，差点据此做出错误的换源决策。

Git Bash 下需要超时控制时，应使用 `timeout.exe` 之外的方式，例如：
```bash
/usr/bin/timeout 60 <cmd>      # 显式指定 GNU coreutils 路径
# 或直接省略 timeout，让工具自身超时
```

---

<a id="i-006"></a>
## I-006 · 上游自带遥测上报

**严重度**：🟠 中 &nbsp;|&nbsp; **状态**：🟢 已解决 &nbsp;|&nbsp; **必须处理时机**：阶段 2 删减定制

### 现象
`hanbao init` 等命令会向上游上报使用数据。

### 为什么必须处理
hanbao 将**分发给第三方用户**（飞牛应用中心下载）。让用户的数据在不知情的情况下上报给上游第三方，既不符合"本地数据主权"的产品定位，也存在隐私合规风险。

### 处理方案（阶段 2 执行）
定位遥测代码 → 默认关闭或彻底移除 → 在 CHANGES-FROM-UPSTREAM.md 记录该修改。
若保留任何形式的数据上报，必须在 FPK 安装向导中明确告知用户并提供开关。

### 已处置（2026-08-14）
- [修改] `src/hanbao/utils/telemetry.py` — `_upload_telemetry_sync` 改为 no-op（return False），删除 `TELEMETRY_ENDPOINT`（`hanbaoelemetry-*.fcapp.run` 上报地址）
- [修改] `src/hanbao/app/_app.py` — 移除启动时的自动上报调用
- [修改] `src/hanbao/cli/init_cmd.py` — 移除遥测代码块 + `TELEMETRY_INFO` 文案 + `_echo_telemetry_info_box`
- [确认] 前端 console 无遥测（grep 无 analytics/posthog/sentry 依赖与上报端点）
- 结果：hanbao 不再向 QwenPaw 官方上报任何数据，全链路零上报

---

<a id="i-007"></a>
## I-007 · Web Console 默认无认证

**严重度**：🟠 中 &nbsp;|&nbsp; **状态**：🟢 已解决（deploy/entrypoint.sh + Dockerfile 默认 `HANBAO_AUTH_ENABLED=true`，用户可 `-e HANBAO_AUTH_ENABLED=false` 关闭） &nbsp;|&nbsp; **必须处理时机**：阶段 5 FPK 打包（镜像层已落地）

### 现象
上游 QwenPaw Web Console（8088）默认不开启认证，设计假设是"个人本地使用"。

### 为什么必须处理
飞牛 NAS 常有公网映射 / 内网多用户场景。若用户把 8088 暴露到公网，**任何人都能直接操作其 AI 助手、读写其文件、消耗其 API 额度**。

### 处理方案
- 阶段 2：确认上游是否已有认证开关，能开则默认开启
- FPK 向导：强制要求用户设置访问密码，或明确警告"仅限内网访问"

### 调研结论（2026-08-17）：认证系统已完整存在，I-007 实为「默认关闭」而非「缺失」

经代码核查，上游 QwenPaw **已内置完整 Web 登录认证**，hanbao 原样继承、未破坏：

- **后端**：`src/hanbao/app/auth.py` — 盐化 SHA-256 口令哈希 + HMAC-SHA256 自签 token（无额外依赖）；`AuthMiddleware`（`BaseHTTPMiddleware`）在 `_app.py:603` 挂载；启动时 `_app.py:111` 调用 `auto_register_from_env()` 从环境变量建管理员。
- **开关**：`is_auth_enabled()` 读 `HANBAO_AUTH_ENABLED`（true/1/yes 即开）。关时中间件放行（当前默认行为）。
- **前端**：`console/src/pages/Login/index.tsx` 真实登录/注册页；`api/request.ts` 收到 401 自动跳 `/login`；token 存 `localStorage["hanbao_auth_token"]`（即 I-013 改名后的 key）。后端 + 前端双重拦截。
- **单用户**：仅允许注册一个账号，契合「单用户私人豆包」定位；忘密码删 `SECRET_DIR/auth.json` 重启即可重注册。
- **渠道不受影响**：中间件仅对 `/api/` 路径鉴权（`not path.startswith("/api/")` 即跳过），微信/OneBot 等渠道走独立连接，登录认证不干预。

**结论 / 处理方向**：I-007 不是「造认证」，而是「FPK 打包时默认开启 + 向导注入凭据」：
1. FPK 阶段（`阶段 5`）在默认 env / docker-compose 设 `HANBAO_AUTH_ENABLED=true`；
2. FPK 安装向导收集管理员账号密码 → 以 `HANBAO_AUTH_USERNAME`/`HANBAO_AUTH_PASSWORD` 注入，首次启动 `auto_register_from_env()` 自动建账号（上游专为 Docker/面板自动化部署设计）；
3. 保留 entrypoint.sh 的 SECURITY NOTICE 警告（auth 关闭时提示），并保留 `security.allow_no_auth_hosts` 回环免登（NAS 本机访问便利）。
4. ⚠️ 阶段 5 实施前需确认 `security.allow_no_auth_hosts` 默认值不误放行 LAN 访问（应为仅 loopback）。

### 实施记录（2026-08-18）：镜像层落地，默认开启认证
- **默认值确认（安全前置）**：`src/hanbao/config/config.py:2361` `SecurityConfig.allow_no_auth_hosts` 默认 `["127.0.0.1","::1"]`，**仅 loopback、不开 LAN**；`trusted_proxies` 默认空，配合 `_should_skip_auth` 的"direct peer 须同为 loopback"防御纵深——开认证后不会被误免登，无需改动。
- **deploy/entrypoint.sh**：新增 `export HANBAO_AUTH_ENABLED="${HANBAO_AUTH_ENABLED:-true}"`（默认开，用户 `-e ...=false` 可关）+ `print_auth_banner()`：开启且无凭据 env 时提示"首次打开页面设管理员密码"，有凭据 env 时提示"自动建账号"。原 `warn_if_auth_off_container_bind` 仅当用户显式关闭时触发。
- **deploy/Dockerfile**：新增 `ENV HANBAO_AUTH_ENABLED=true` 双保险（即便绕过 entrypoint 直接 exec app，仍默认开）。
- **行为说明（上游设计）**：`auth.py:_should_skip_auth` 首行 `if not is_auth_enabled() or not has_registered_users(): return True`——**未注册账号前跳过认证**（首次注册模式）。故默认开认证但无凭据 env 时，安装后第一个打开页面的人可设密码（单用户家庭场景可接受；FPK 阶段应由向导注入凭据消除此窗口）。
- **已建并校正（2026-08-19，阶段5 FPK 脚手架，docker-project 形态）**：FPK 安装向导（`deploy/fpk/wizard/install`）收集 `HANBAO_AUTH_USERNAME`/`HANBAO_AUTH_PASSWORD` → `install_callback` 预载镜像 tar + 持久化 `$TRIM_PKGETC/hanbao.env` → compose `env_file` 注入容器 → `auto_register_from_env()` 首启自动建账号（I-007 抢注窗口消除）。✅ `manifest`/`wizard/`/`config/{resource,privilege}`/`app/ui/config` 字段格式已于 2026-08-19 对照飞牛官方规范（developer.fnnas.com，本机直连可达无需代理）逐条校正；剩 `fnpack build` + fnOS 实测验证。
- 改完按铁律未立即构建，待用户说"测一下"再重建镜像验证。

### 关联改动（2026-08-14，非本项解决）
- **OneBot 反向 WS 服务端**获独立加固（上游 v2.1.0 #6676，P0-2）：`ws_host` 默认改 loopback，非 loopback 绑定强制 `access_token`（常量时间比较，拒绝 query-param token）。见 `CHANGES-FROM-UPSTREAM.md` 阶段 3 对应条目。
- ⚠️ 上述加固**只覆盖 OneBot 渠道的 WS 服务端**，本 I-007 专指 **Web Console 8088 本身无认证**，二者是不同攻击面。Console 8088 认证已于本 I-007 镜像层落地（默认开启）；#6676 仅加固 OneBot WS，不替代本项。

---

<a id="i-008"></a>
## I-008 · console 前端构建 OOM，4GB WSL 内存不足

**严重度**：🔥 高（**曾阻塞构建**） &nbsp;|&nbsp; **状态**：🟢 已解决（8GB WSL 下构建成功 `hanbao:0.0.1-upstream`） &nbsp;|&nbsp; **必须处理时机**：阶段 1 构建时

### 现象
`console-builder` 阶段执行 `npm ci --include=dev && npm run build`（即 `tsc -b && vite build`）时
Node 堆内存耗尽，构建中断：
```
FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
1: 0x8f2d8b node::OOMErrorHandler(...)
Aborted (core dumped)   → exit code 134
```

### 实测记录（Windows + Docker Desktop / WSL2）

| # | WSL 内存 | node heap 参数 | 结果 | 耗时 |
|---|---|---|---|---|
| 1 | 7.65GB（旧 VM） | 默认 | ❌ node heap OOM（exit 134） | 8m15s |
| 2 | 3.82GB | `--max-old-space-size=4096` | ❌ **buildkit 断连**（VM 整体崩溃） | 2m26s |
| 3 | 3.82GB | `--max-old-space-size=2816` | ❌ node heap OOM（exit 134） | ~9m |
| 4 | 4GB（`.wslconfig`） | `--max-old-space-size=2048` | ❌ node heap OOM（exit 134，`Aborted (core dumped)`）；buildkit 并行跑 console-builder 与 stage 2 抢内存 | ~10m |
| 5 | 8GB（`.wslconfig` memory=8GB/processors=6） | `--max-old-space-size=4096` | ✅ **构建成功**，镜像 `hanbao:0.0.1-upstream`（4.02GB），实测 `npm ci && npm run build` 通过 | ~90m |

### ⚠️ 核心教训：node heap 上限必须小于容器可用内存
第 2 次比第 1 次**更糟**，原因是 `--max-old-space-size=4096`（4GB）**大于 WSL VM 总内存 3.82GB**。
这等于告诉 node「你可以放心用到 4GB」，于是 node 在触发自身 heap 保护前，
**整个 VM 先被内核 OOM-killer 打死** → 报错从可读的 `heap out of memory`
恶化为莫名其妙的 `rpc error: code = Unavailable ... EOF`。

> **规则**：`--max-old-space-size` 必须 **显著小于** 容器/VM 可用内存（建议留 25~30% 余量）。
> 设得比可用内存大，只会把「优雅报错」换成「整机崩溃」，问题反而更难定位。

### 另一个排查陷阱：VM 崩溃会静默改变环境
第 2 次失败后 `docker info` 从 `7.65GB / 8 CPU` 变成 `3.82GB / 4 CPU`。
原因是 **WSL VM 崩溃重启，重启后才加载了 `.wslconfig` 里早已写好但未生效的 `memory=4GB`**。
即：**构建环境在排查过程中被悄悄改变了**，若不重新读取 `docker info`，
会拿着旧的内存假设去分析新的失败现象，得出完全错误的结论。

> **规则**：每次构建失败后，重新执行 `docker info` 确认资源配额，不要沿用上一次的认知。

### 根因
console 依赖体量大（`antd` + `@ant-design/x` + `@agentscope-ai/chat` + `@agentscope-ai/design` 等），
`tsc -b` 全量类型检查叠加 `vite build` 打包，峰值堆占用超过 3GB。
4GB 的 WSL VM 扣除系统与 npm 自身开销后，**无论如何调 heap 参数都无法满足**。

### 解决方案
**首选：提高 WSL 内存配额**，编辑 `%USERPROFILE%\.wslconfig`：
```ini
[wsl2]
memory=8GB
processors=6
```
随后 `wsl --shutdown` 并重启 Docker Desktop 使其生效。

> WSL 的 `memory` 是**上限而非预留**，不使用时不占用宿主机内存，设大无副作用。
> 宿主机 15.8GB 物理内存，分配 8GB 后仍余 7.8GB 给 Windows。

**备选（宿主机内存也紧张时）**：在宿主机本地构建 console，Dockerfile 改为直接 `COPY console/dist`。
代价是牺牲「容器内可复现构建」，且 FPK 发布流程需额外处理，**不推荐作为长期方案**。

### hanbao 已做的相关修改
`deploy/Dockerfile` console-builder 阶段新增（带 `[hanbao modification]` 标注）：
```dockerfile
ARG NODE_BUILD_HEAP_MB=4096
ENV NODE_OPTIONS=--max-old-space-size=${NODE_BUILD_HEAP_MB}
```
保留 `--build-arg` 口子，便于按构建机内存调整。

<a id="i-009"></a>
## I-009 · 构建机 C 盘 0GB 可用，Docker 无法写入

**严重度**：🔥 高（**阻塞构建**） &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-10，Docker 数据盘迁 F 盘 Junction） &nbsp;|&nbsp; **必须处理时机**：阶段 1 构建时

### 现象
构建日志写入时报 `tail: write error: No space left on device`。
排查磁盘后发现构建机 **C 盘可用空间为 0**：

| 盘符 | 已用 | 可用 |
|---|---|---|
| **C** | 136.5 GB | **0 GB** |
| D | 0.6 GB | 25.7 GB |
| E | 174.6 GB | 576.9 GB |
| F | 16.7 GB | 163.3 GB |

Docker Desktop 的数据盘默认位于 C 盘：
`C:\Users\<user>\AppData\Local\Docker\wsl\disk\docker_data.vhdx`（6.55 GB）

### 影响（比想象中广）
不只是「装不下新镜像」：
- 构建中间层无处写入 → 各种**看似无关的诡异错误**（可能是此前 buildkit 断连的共因之一）
- **连 `docker image prune` 删除操作都会挂起**（实测超过 5 分钟无响应）——
  删除同样需要写入元数据，磁盘全满时 Docker 自身也会陷入僵局
- Windows 系统本身受影响：虚拟内存、系统更新、临时文件均异常

> ⚠️ **排查启示**：容器构建出现难以解释的失败时，
> **先查磁盘空间，再查内存**。磁盘满的表现极具迷惑性，
> 会伪装成网络错误、OOM、daemon 断连等完全不同的症状。

### 解决方案

**A. 治本 —— Docker 数据盘迁出 C 盘（推荐）**
Docker Desktop → Settings → Resources → Advanced → *Disk image location*
改为 `F:\docker-data`（163 GB 可用），Docker 会自动迁移现有数据。

**B. 应急 —— 清理 Docker 占用**
```bash
docker builder prune -af      # 构建缓存
docker image prune -f         # 悬空（无 tag）镜像
docker system prune -a        # 激进：清除所有未被容器引用的镜像
```
> ⚠️ **两个坑**：
> 1. 磁盘已满时 prune 本身可能挂起，需先手工腾出少量空间
> 2. **删除镜像后 `.vhdx` 不会自动收缩**，C 盘空间不会立即回收。
>    需 `wsl --shutdown` 后执行 `Optimize-VHD -Path <vhdx> -Mode Full`（需 Hyper-V 模块）
>    或使用 `diskpart` 的 `compact vdisk`

**C. 容量评估**
hanbao 镜像预估 2–4 GB，叠加构建中间层与 apt 缓存，
**构建机应预留至少 20 GB 可用空间**。仅靠清理 Docker（可回收约 2 GB）不足以支撑。

### 实测：应急清理的真实收益（2026-08-10）
执行 `docker builder prune -af` + `docker image prune -f`：

| 指标 | 清理前 | 清理后 |
|---|---|---|
| Docker Images 占用 | 2.373 GB | 683.2 MB |
| Build Cache | 120.2 MB | 0 B |
| Docker 内部回收 | — | **1.688 GB** |
| **C 盘实际可用** | 0 GB | **仅 1.03 GB** |
| `docker_data.vhdx` 文件大小 | 6.55 GB | **6.55 GB（未变）** |

**结论：Docker 内部回收 1.8GB，但 C 盘只多出 1.03GB，vhdx 文件大小纹丝不动。**
这印证了前述的坑 —— **删除镜像不会让 `.vhdx` 收缩**，
腾出的只是 vhdx *内部* 的空闲块，宿主机层面并未归还。
且 `docker image prune` 在磁盘全满时耗时 **7分41秒**（正常应为秒级）。

因此本项目最终采用**方案 A（迁移数据盘）**：应急清理已被实测证明不足以支撑构建。

> ✅ **最终落地方案（2026-08-10 实测）**：Docker Desktop 的 *Disk image location* 图形项与 `settings-store.json` 的 `DataFolder` 键在 **WSL2 后端下均不生效**（见 I-011）。实际采用 **NTFS 目录联接（Junction）**：将 `C:\Users\<user>\AppData\Local\Docker\wsl\disk` 重命名为 `disk.OLD-hanbao` 备份，再在该路径建 Junction → `F:\docker-data`。Docker 启动后透明使用 F 盘 `docker_data.vhdx`，原 5 个镜像零丢失，容器内写入测试证实数据落 F 盘。详见 I-011。

---

<a id="i-010"></a>
## I-010 · WSL 崩溃转储吞噬 18.58GB 磁盘（C 盘归零真凶）

**严重度**：🔥 高 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-10） &nbsp;|&nbsp; **必须处理时机**：阶段 1 构建前

### 现象与根因
构建期容器内 node 进程 OOM 崩溃时，WSL2 把**整个 VM 内存镜像**转储到 `%TEMP%\wsl-crashes\wsl-crash-*-_usr_local_bin_node-*.dmp`。每次崩溃约 **9.29GB**，本日两次构建崩溃共生成 **2 个、合计 18.58GB** 转储文件（时间戳 10:46、11:05，与两次构建失败吻合）。

> ⚠️ 这正是「C 盘从 ~10GB 跌到 2GB 再归零」的真因——**不是清理导致的，是崩溃转储喂掉的**。且形成恶性循环：磁盘越满 → 构建越易 OOM → 又写转储 → 更满。

### 处理
1. 删除 `%TEMP%\wsl-crashes\` 下两个 dump（释放 18.58GB）。
2. 在 `C:\Users\<user>\.wslconfig` 追加 `crashDumpCount=0`（保留既有 `memory=4GB` / `processors=4`），禁止再生成转储。
3. `wsl --shutdown` 使配置生效。

### 验收
`wsl-crashes` 目录清空；后续构建即便 OOM 也不再产生 GB 级 dump（仅进程退出）。

---

<a id="i-011"></a>
## I-011 · Docker `DataFolder` 键对 WSL2 后端无效，Junction 为解

**严重度**：🟠 中 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-10） &nbsp;|&nbsp; **必须处理时机**：阶段 1 构建前

### 现象
为把 Docker 数据盘从 C 盘迁走，曾在 `C:\Users\<user>\AppData\Roaming\Docker\settings-store.json` 加 `"DataFolder": "F:\\docker-data"`。但 Docker 读取后规范化键名、且 **WSL2 后端根本不认该键**（仅 Hyper-V 后端生效）。重命名 C 盘旧 `docker_data.vhdx` 后，Docker 反而在 C 盘新建空 1.51GB vhdx、原 5 个镜像全丢。

### 根因
WSL2 后端的 Docker 数据盘路径由 `AppData\Local\Docker\wsl\disk\docker_data.vhdx` 硬编码决定，`settings-store.json` 的 `DataFolder` 不影响它。

### 处理（已回滚误改并采用 Junction）
1. 恢复 `settings-store.json` 原样（移除无效 `DataFolder` 键，备份 `settings-store.json.bak-hanbao-20260810`）。
2. 采用 Junction 透明重定向（详见 I-009 末尾「最终落地方案」）：
   - 重命名 `...\Docker\wsl\disk` → `disk.OLD-hanbao`
   - `mklink /J "...\Docker\wsl\disk" "F:\docker-data"`
3. 启动 Docker，验证 F 盘 `docker_data.vhdx` 被 `LOCKED`、镜像完好、容器内写入落 F 盘。

### 经验
- Docker Desktop + WSL2：**别改 `DataFolder`**，改迁数据盘请直接用 **Junction 重定向 `...\Docker\wsl\disk`**。
- 误改后镜像丢失别慌：`wsl --shutdown` → 删掉 C 盘空 vhdx → 恢复原 vhdx → 恢复 settings，镜像即回。

---

---

<a id="i-012"></a>
## I-012 · 品牌名残留：JS 命名空间 `window.Hanbao`

**严重度**：🟡 低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-17 `window.hanbao` 别名 + 向后兼容） &nbsp;|&nbsp; **必须处理时机**：阶段 3 删减定制

- `window.Hanbao` 是前端插件系统的宿主 API 命名空间，所有外部插件通过它获取 React/antd 等依赖。
- **不能直接改名**：改了会让所有已安装插件失效。需要在阶段 3 评估兼容方案（如同时暴露 `window.hanbao` 别名 + 保留 `window.Hanbao` 过渡期）。

<a id="i-013"></a>
## I-013 · 品牌名残留：localStorage keys (`hanbao_*`)

**严重度**：🟡 低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-17 `hanbao_*` 迁移） &nbsp;|&nbsp; **必须处理时机**：阶段 3 删减定制

- 5 个 localStorage key 使用 `hanbao_` 前缀（auth_token、agent-storage、theme、sidebar_mode 等）。
- **不能直接改名**：会导致所有用户丢失登录态和偏好设置。需要迁移逻辑：读旧 key → 写新 key → 删旧 key。

<a id="i-014"></a>
## I-014 · 品牌名残留：CSS 前缀 `hanbao` (Ant Design ConfigProvider)

**严重度**：🟡 低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-17 `hanbao` 前缀 + 同步 less 选择器） &nbsp;|&nbsp; **必须处理时机**：阶段 3 删减定制

- `App.tsx` 中 `ConfigProvider prefix="hanbao" prefixCls="hanbao"` 控制所有 Ant Design 组件的 CSS 类名前缀。
- **不能直接改名**：改了会让所有样式失效。需同步更新所有 `.less` 文件中的 `&:global(.hanbao-*)` 选择器。

<a id="i-015"></a>
## I-015 · 包名全量改名：qwenpaw → hanbao（Python 包 / 环境变量 / 标识符 / 目录）

**严重度**：🟢 极低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-19 全量改名落地） &nbsp;|&nbsp; **必须处理时机**：阶段 5 FPK 前

### 范围与结果（2026-08-19）
- `src/qwenpaw` → `src/hanbao`（`git mv` 目录）；`pyproject.toml` `name = "hanbao"`；`[project.scripts]` 入口 `hanbao = "hanbao.cli.main:cli"`。
- 四档大小写映射 `QWENPAW→HANBAO` / `QwenPaw→Hanbao` / `Qwenpaw→Hanbao` / `qwenpaw→hanbao` 改写 902 个文本文件；`QWENPAW_*` 环境变量（含 `QWENPAW_AUTH_USERNAME/PASSWORD`）全部改名 `HANBAO_*`。
- **合规红线 R2 守住**：LICENSE / NOTICE / docs/license-compliance.md / docs/CHANGES-FROM-UPSTREAM.md 四个文件**零改动**。
- **上游署名保留（I-016）**：8 个 `plugins/*/plugin.json` 的 `"author": "QwenPaw Team"`、locale `copyright: Qwenpaw PRIVATE LIMITED`、review-bot `QwenPaw Maintainer Team`、startup_profile `Author` 等署名行未改。
- **外部资源 URL 保留**：`github.com/agentscope-ai/QwenPaw`、`qwenpaw.agentscope.io`（CDN/文档/referer）、pypi `qwenpaw` 路径、`modelscope.cn` 等真实上游链接不改（避免伪造不存在的地址）。
- **历史文档保留**：`website/public/release-notes/*`、`website/public/blog/*`、`docs/upstream-v2.1.0-adoption.md` 等叙述性历史内容不改写（避免失真）。
- 全仓残留 `qwenpaw` 仅存在于上述四类（R2 / 署名 / 外部 URL / 历史文档）；代码标识符、import、`QWENPAW_*` env 已零残留。

<a id="i-016"></a>
## I-016 · 品牌名残留：插件 plugin.json author 字段

**严重度**：🟢 极低 &nbsp;|&nbsp; **状态**：🟢 保留上游署名（合规，不改写） &nbsp;|&nbsp; **必须处理时机**：无阻塞

- `plugins/*/plugin.json` 中 `author: "QwenPaw Team"` 等字段为上游署名，按合规要求保留（R2 红线：不得擦除上游版权/署名）。
- 用户看不到这些元数据，不影响功能。包名已改（见 I-015），仅署名行保留。

---

<a id="i-017"></a>
## I-017 · sed 产生 JS 注释 `//` 污染 Python 文件

**严重度**：🔥 高 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-12）

### 现象
在 `_app.py` 中用 sed 注释掉 `app.include_router(coding_mode_router)` 时，sed 替换产生了 `// [hanbao] Coding mode router removed.`。Python 不认识 `//`，导致 `SyntaxError`，容器启动后 app 进程反复 `exit status 1`。

### 根因
用 sed 删代码时习惯性地写了 JS/TS 风格的 `//` 注释，忘了 Python 要求 `#`。

### 处理
手动改为 `# [hanbao]`。同时修复了 `contextvars_hook.py` 中另一处同类错误。

### 可复用经验
**sed 操作 Python 文件时必须用时 `#` 而非 `//` 作为注释前缀。** 建议在 sed 命令中显式使用 `#` 避免思维惯性。

---

<a id="i-018"></a>
## I-018 · git checkout 导致 gitignored 跟踪文件从磁盘消失

**严重度**：🔥 高 &nbsp;|&nbsp; **状态**：🟢 已解决 &nbsp;|&nbsp; **必须处理时机**：阶段 3 完成前

### 现象
在阶段 3 删减定制过程中，多次出现执行 `git checkout HEAD -- <path>` 恢复文件后，`console/src/api/` 和 `src/hanbao/app/routers/` 等目录下的文件从磁盘消失。具体表现为：

1. **第一次**（2026-08-11）：`git checkout` 后 `console/src/api/modules/` 目录整个变空，Docker 构建阶段 `tsc` 报 200+ 个 `TS2307: Cannot find module`。
2. **第二次**（2026-08-12）：`src/hanbao/app/routers/__init__.py` 被清空，容器启动后 `ImportError: cannot import name 'create_agent_scoped_router'`。
3. **第三次**（2026-08-12）：`routers/` 下 5 个 `.py` 文件（`_backup_helpers.py`, `tool_calls.py`, `tools.py`, `voice.py`, `workspace.py`）同时消失。

### 根因
这些文件在上游 tarball 中存在，但被 `.gitignore` 规则（主要是 `dist/`、`*.md` 的变体影响）匹配。初始建仓时虽然 `git add -f` 强制纳入了，但后续的 `git rm --cached` 或 check-ignore 路径匹配导致它们从 staging area 丢失。一旦文件不在 git index 中，`git checkout` 无法恢复它们。

### 临时方案
- 从上游本地源码（`E:\浏览器下载\Hanbao-2.0.1\`）用 `cp -r` 恢复缺失文件
- 或用 `git checkout HEAD -- <path>` 恢复（仅对仍在 index 中的文件有效）

### 根本修复方向

> ✅ **已落地（2026-08-12）**：`.gitignore` 硬化（`dist/` → `/dist/`、`console/package-lock.json` 取消忽略，见变更历史 L836），I-001/I-018 同类吞文件问题已闭合；基线计数改为动态校验（打包前 `git check-ignore` 全量复核）。
1. 彻底审核 `.gitignore` 中所有可能误伤的规则（已做：`dist/` → `/dist/`，`console/package-lock.json` 取消忽略）
2. 建立验证脚本：每次 git 操作后运行 `git ls-files | wc -l` 对比基线 2846
3. 优先用 `cp -r` 从上游恢复而非依赖 `git checkout`

---

## I-019 · 文档处理能力：Anthropic 专有技能侵权移除，读用 markitdown，改/创建用自研 python-docx/openpyxl

**严重度**：🔥 高 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-24 自研改/创建工具落地） &nbsp;|&nbsp; **必须处理时机**：上架前

### 现象
上游 QwenPaw 内置的 4 个文档处理技能 `docx`/`pdf`/`pptx`/`xlsx`，其 `LICENSE.txt` 为 **Anthropic 专有许可**（`© 2025 Anthropic, PBC. All rights reserved.`），明确禁止「分发 / 复制 / 衍生作品 / 销售」。Anthropic 官方仓库也确认这 4 个文档技能是 **source-available, not open source**（源码可见但非开源）。

函包作为 fork QwenPaw 的再分发者，把这 4 个技能打包进 FPK 上架飞牛 = **著作权侵权**，比商标红线（R2）更严重。

### 已确认事实
- 4 个侵权技能：`docx` / `pdf` / `pptx` / `xlsx`（含 SKILL.md + scripts + LICENSE.txt，全 Anthropic 专有）
- 其余 7 个内置技能：无 license 字段，继承 Apache-2.0，安全
- 上游 QwenPaw 自己把这些技能标 `Proprietary` 并附 Anthropic LICENSE.txt（知情）

### 决策（2026-08-13 泽零拍板）
- **方案 A**：接受「只能读不能改/创建」，暂时放弃文档创建/编辑能力
- **读文档**：用 `markitdown`（微软，MIT）替代——docx/pdf/pptx/xlsx → Markdown，纯读不碰原文件
- **改文档**：暂不补（依赖 python-docx/openpyxl + 技能指引，微信场景低频）
- **创建文档**：暂不补（后续需要再自研或评估开源替代质量）

### 能力现状对照
| 能力 | 状态 |
|---|---|
| 读 docx/pdf/pptx/xlsx 内容 | 🟢 已接入（markitdown 路由到 file_io.read_file） |
| 改 docx/xlsx 内容 | 🟢 已接入（自研 `document_edit` 工具：python-docx/openpyxl，MIT，2026-08-24） |
| 创建 docx/xlsx | 🟢 已接入（自研 `document_edit` 工具，同上） |
| 改/创建 pptx | ❌ 不可（pptx 创建/编辑复杂度高，维持放弃；读取仍由 markitdown 支持） |

### 待办
1. [x] 删除 4 个 Anthropic 专有技能目录（docx/pdf/pptx/xlsx 的中英双语 + LICENSE.txt + scripts）—— ✅ 已删除（2026-08-13）
2. [x] 接入 `markitdown`（加依赖 `markitdown[pdf,docx,pptx,xlsx]>=0.1.0` + 新增 `document_reader` 技能中英双语）—— ✅ 已完成（2026-08-13，构建验证通过 hanbao:0.0.12）
3. [x] 补「改/创建文档」能力（自研简化版 python-docx/openpyxl）—— ✅ 2026-08-24 落地（见下）

### 已处置（2026-08-24，自研改/创建工具）
移除 Anthropic 专有技能后，函包一度「只能读不能改/创建」。本次以**许可干净的自研实现**补齐改/创建能力（不引入任何专有/传染性依赖）：

- 新增 `src/hanbao/agents/tools/document_edit.py`，4 个 AgentScope `@tool_descriptor` 工具（与 `web_search`/`web_fetch` 同形态，Agent 直接调用、零前端改动）：
  - `create_docx(file_path, content, title)` — 纯文本建 Word（每行一段，可选标题）
  - `edit_docx(file_path, operation, ...)` — append 追加段落 / replace 段内查找替换
  - `create_xlsx(file_path, rows, sheet_name)` — 制表符分隔行建 Excel
  - `edit_xlsx(file_path, operation, ...)` — append_row 追加行 / write_cell 写单元格（支持 `Sheet!A1`）
  - 复用 `file_io._resolve_file_path` 路径解析 + `io_utils.get_path_lock` 并发锁；python-docx/openpyxl **lazy import**，缺失时返回明确错误而非崩溃。
- `src/hanbao/agents/tools/__init__.py` — 导入 4 个工具，装饰器自动注册进全局工具表。
- `pyproject.toml` — 加 `python-docx>=1.1.0` + `openpyxl>=3.1.0`（均 MIT，Apache-2.0 再分发合规；正是此前被删 Anthropic 技能的合法替代）。
- 范围为「简化版」：无样式引擎/模板系统，仅满足 Agent 代用户产出与微调 Office 文档的基本需求。pptx 创建/编辑维持放弃（复杂度高、收益低）。
- 验证：`py_compile` + `ast.parse` 通过；依赖未本地装，运行期验证待「测一下」镜像重建（届时 pip 安装新依赖 + 容器实测 4 工具可用）。

---

## I-020 · html2text 为 GPL-3.0 传染性依赖，违反 R5 红线

**严重度**：🔥 高 &nbsp;|&nbsp; **状态**：🟢 已解决 &nbsp;|&nbsp; **必须处理时机**：上架前

### 现象
工具依赖审计发现 `pyproject.toml` 中的 `html2text>=2024.2.26`（用于 `web_search.py` 的 `web_fetch` 把 HTML 转 Markdown）为 **GPL-3.0** 许可（Aaron Swartz 原作，PyPI 明确 "distributed under the GPLv3"）。

GPL 是 copyleft 传染性许可，与 Apache-2.0 闭源分发目标冲突，违反合规规范 **R5 红线**（禁止引入 GPL/AGPL/SSPL 依赖）。

### 处置
- [修改] `pyproject.toml` — `html2text>=2024.2.26` → `markdownify>=1.0.0`（MIT 许可）
- [修改] `src/hanbao/agents/tools/web_search.py` — `import html2text` → `from markdownify import markdownify as md`；`_html_to_text` 改用 `md(html, heading_style="ATX", strip=["img","script","style"])`
- 删除 `_new_html2text()` 函数（原 html2text 转换器）

### 教训
上游 QwenPaw 虽然整体 Apache-2.0，但**依赖树里可能藏 GPL 库**（html2text 是 Aaron Swartz 的老牌 GPL 项目）。fork 项目必须做一次**全依赖 license 审计**，不能只看顶层许可证。

---

## I-021 · 依赖审计：4 个 LGPL 弱传染依赖

**严重度**：🟠 中 &nbsp;|&nbsp; **状态**：🟢 已备案 &nbsp;|&nbsp; **必须处理时机**：上架前备案

### 审计结论（2026-08-13，全依赖树扫描 200+ 包）
1. ✅ **无 GPL/AGPL/SSPL 强传染依赖**（html2text 已换 markdownify，见 I-020）
2. ⚠️ 发现 4 个 **LGPL 弱传染**依赖
3. ✅ 82 个 license 元数据为空的包 = 知名 Apache/MIT/BSD 库（agentscope/cryptography/playwright/numpy/fastapi/pydantic 等），实际安全

### LGPL 依赖清单
| 依赖 | License | 性质 | 处置 |
|---|---|---|---|
| `python-telegram-bot` | LGPLv3 | **直接依赖**（Telegram 渠道） | 保留 + NOTICE 补声明 |
| `rope` | LGPLv3+ | python-lsp-server 传递依赖（编码工具） | ✅ 已消除（2026-08-13 删 python-lsp-server） |
| `pytoolconfig` | LGPL-3.0 | rope 依赖 | ✅ 已消除（同上） |
| `docstring-to-markdown` | LGPLv2+ | pylint 传递依赖 | 随 pylint 保留（开发依赖） |

### 关键判断：LGPL ≠ GPL
- **GPL/AGPL/SSPL**（强传染）＝ 链接即强制整个分发物开源 → 禁止
- **LGPL**（弱传染）＝ 动态链接（Python import）可闭源，仅需附 license 文本 + 不修改库本身

### 已处置
- [x] `NOTICE` 补 LGPL 声明（4 个 LGPL 依赖 + license 文本链接）—— ✅ 2026-08-13
- [x] 删编码工具 + `python-lsp-server`/`ast-grep-cli` 依赖 → rope/pytoolconfig 两个 LGPL 传递依赖随之消除 —— ✅ 2026-08-13
- ✅ **备案完成（2026-08-13）**：`NOTICE` 含全部 LGPL 依赖 license 文本链接；仅剩 `python-telegram-bot`（直接依赖，保留并声明）+ `docstring-to-markdown`（pylint 传递，保留）。上架合规材料齐备，I-021 关闭。
- ✅ **2026-08-21 跟进**：Telegram 频道已砍除，`python-telegram-bot` 已从 `pyproject.toml` 依赖移除（src 零 import 确认）→ **LGPL 直接依赖清零**，仅剩 `docstring-to-markdown`（pylint 传递，弱传染）。NOTICE 中既有 LGPL 声明保留不删（多余声明无害，合规更保守）。

---

## I-022 · web_search 用 Tavily keyless（免费限速），重度使用会撞限速

**严重度**：🟡 低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-24，env 变量方案） &nbsp;|&nbsp; **必须处理时机**：上架后可优化（非阻塞）

### 现象
`web_search` 工具用 Tavily **keyless** 模式（`X-Tavily-Access-Mode: keyless`），免费、无密钥、开箱即用，但 **Tavily 官方定位是"探索/轻量使用"**，明确说"生产环境换 API key"。keyless 有严格速率限制。

### 风险（非侵权，是服务条款/体验层面）
- 函包上架后用户多了 → 集体触发 Tavily keyless 限流
- Tavily 可能视函包为"第三方产品滥用免费额度"，甚至封禁
- 重度用户（天天让 Agent 联网搜）体验差

### 现状
- `web_search` 工具：默认用 keyless，无需任何配置
- `config.py` 已预留 `tavily_search` MCP 配置（`enabled=False` + `TAVILY_API_KEY=""`），填了 key 才启用

### 已处置（2026-08-24）
采用**环境变量方案**（贴合本项目"配置走 env"哲学，零前端改动、零新增依赖）：
- `src/hanbao/agents/tools/web_search.py` — 新增 `_TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")` 与 `_tavily_headers()`：有 key 时发 `Authorization: Bearer <key>` 认证请求（用部署者自己的额度），无 key 时回退 `X-Tavily-Access-Mode: keyless`。默认行为不变（仍零配置可用）。
- `docker-compose.yml` — 在 `environment` 示例注释中加 `TAVILY_API_KEY=${TAVILY_API_KEY:-}`，提示部署者可透传自有 key 避限速。
- 速率超限时的 fallback 提示文案补充「可设 TAVILY_API_KEY」。

### 待办（可选增强，非必须）
1. [ ] 设置页加"搜索 API key"可选入口（前端 UI），让终端用户自助填 key —— 当前 env 方案已消除"集体撞限速"风险，UI 入口属体验优化，按需再做
2. [ ] 或评估换免费无 key 的搜索源（DuckDuckGo / SearXNG 自建）

### 备注
`web_fetch`（HTTP GET + markdownify MIT）基本合规，抓取公开网页属信息访问；仅缺 robots.txt 检查（礼貌问题，非侵权），可后续补。

---

<a id="i-023"></a>
## I-023 · patch 累积 diff 的提交依赖（原「基线偏离」判断为误判）

**严重度**：🟡 低 &nbsp;|&nbsp; **状态**：🟢 已澄清（误判已更正） &nbsp;|&nbsp; **必须处理时机**：移植靠后提交前先识别前置依赖

### 现象（真实）
移植上游 patch（v2.0.1→v2.1.0）里靠后的提交时，`git apply` 报「上下文不匹配」失败：
- 实例 1（#6676 / P0-2）：`channel.py` 缺 `_normalize_media_ref` → 实际是 **PATCH 072 `feat(onebot): improve outbound text and media`** 引入的新函数。
- 实例 2（#6237 / P1-9）：`memoryspace.py` 的 `expand()` 结构不同 → 实际是 **PATCH 066 `fix(scroll): preserve session IDs`** 把 `expand()` 从 `WHERE seq BETWEEN` 改成了 scope 过滤版。

### ⚠️ 误判澄清（2026-08-14 更正，重要）
- **曾误判**为「本地基线 `upstream/v2.0.1` ≠ 官方 v2.0.1」。
- **经核实**：`git clone --branch v2.0.1 https://github.com/agentscope-ai/QwenPaw`（官方 tag = `ed5857b`）后，`git diff --no-index --ignore-cr-at-eol` 逐文件比对，**本地基线 `9b86a97` 与官方 v2.0.1 完全一致**（唯一差异是 `.git` 目录本身）。
- 之前 `diff -rq` 报「几乎所有文件 differ」是 **CRLF/LF 换行符假象**（Windows 下载的 tarball 是 CRLF，git clone 是 LF），非实质差异。

### 根因（正确）
- patch 是 v2.0.1→v2.1.0 的 **212 个提交的累积 diff**。靠后的提交基于「v2.0.1 + 前面所有提交」的状态。
- 本地只有 v2.0.1，所以移植靠后提交时，它引用的前置提交新增的函数/结构在本地不存在，`git apply` 因上下文不匹配而失败。
- 这是**提交依赖问题**，不是基线问题。

### 处理
1. 移植靠后提交前，先用 `grep` 定位它引用的「新函数/新结构」是 patch 里哪个提交（`+def xxx` 首次出现位置）引入的，**先移植前置依赖提交，再移植目标提交**。
2. 或用 `git apply --3way` 自动做 3-way merge。

### 已确认的依赖链
- **PATCH 066**（preserve session IDs，改 memoryspace.py `expand`）→ **PATCH 097 #6237**（scroll 重构）→ **PATCH 162 #6824**（中文召回）
- **PATCH 072**（onebot outbound text/media，引入 `_normalize_media_ref`）→ **#6676**（P0-2）

### 当前状态
- P0-2 #6676 已通过「类定义前插 helper」绕过依赖，落地完成。
- P1-9 待办：先移植 PATCH 066，再依次 #6237 → #6824。

---

## I-024 · Monaco 编辑器残留（Coding Mode 砍不干净）

**严重度**：🟢 极低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-14） &nbsp;|&nbsp; **必须处理时机**：阶段 3 收尾

### 现象（2026-08-14，移植 P1-20 时发现）
函包已砍 Coding Mode（编码模式），但 Monaco 编辑器组件未一并清理，残留：
- `console/package.json` 依赖 `monaco-editor`（0.55.1）+ `@monaco-editor/react`（^4.7.0）
- `console/src/monacoSetup.ts`（Monaco 离线加载配置，注释明确"为 Coding page 文件预览/编辑服务"）
- `console/src/main.tsx` 的 `import "./monacoSetup"`

### 解决（2026-08-14 阶段 3 收尾）
- `console/package.json`：删 `monaco-editor` + `@monaco-editor/react` 依赖、删 `verify:monaco-css` script、`build`/`build:prod` 去掉 `&& npm run verify:monaco-css`
- `console/package-lock.json`：`npm install --package-lock-only` 同步（纯删 62 行，零版本漂移）
- `console/src/main.tsx`：删 `import "./monacoSetup"` 及注释
- `console/src/monacoSetup.ts`：清空为占位符（`export {}`），因 `tsc -b` 会编译 src 下所有 .ts，直接删依赖会 TS2307
- `console/scripts/verify-monaco-css.mjs`：保留为孤儿（.mjs 不被 tsc 编译、script 已删不调用），**待用户手动删**

> ⚠️ 环境教训：本机 git rm 删除文件曾触发整个 `console/` 目录 553 文件从磁盘消失（文件系统异常，类似 I-018），故本轮未用 git rm 删文件，改用「清空占位 + 留孤儿文件」，物理删除交用户手动。

---

## 变更历史

| 日期 | 变更 |
|---|---|
| 2026-08-10 | 创建，登记 I-001 ~ I-007；I-001 已解决 |
| 2026-08-10 | I-005 实测解决（预拉规避 buildkit 并发鉴权）；新增 I-008 构建 OOM |
| 2026-08-10 | I-009 结案（迁 F 盘 Junction）；新增 I-010（WSL 崩溃转储 18.58GB）、I-011（DataFolder 无效 / Junction 方案）；C 盘回收站仍压 8.19GB 本轮 vhdx 待用户手动清 |
| 2026-08-12 | I-001 复现确认（git checkout 再次吞文件）；新增 I-012~I-016（品牌残留登记）；新增 I-017（sed JS 注释污染 Python）、I-018（git checkout 吞文件）；I-017 已解决 |
| 2026-08-12 | .gitignore 进一步硬化：`dist/` → `/dist/`；`console/package-lock.json` 取消忽略。这些修改确认 I-001 不会再因相同原因复现 |
| 2026-08-13 | 阶段 3 完成构建跑通（hanbao:0.0.10）；Security 设置页/语音转写删除、沙箱默认开启；新增经验：删功能用 stub 而非硬删（避免 5+ 次连锁报错），已在 CHANGES 记录 |
| 2026-08-13 | 审批流程移除：governance 主路径 ASK→ALLOW、沙箱违规→DENY、runtime fallback ASK→ALLOW；灾难级命令拦截保留。前端审批 UI 变死代码暂不删（耦合 App/Sidebar/Channels）。定位修正：函包主要靠微信等渠道聊天，非 Web 为主 |
| 2026-08-13 | 插件管理页、备份功能删除；内置技能砍 6 个（QA_source_index/guidance/browser_cdp/browser_visible/dingtalk_channel/himalaya）。工具清单评估：编码工具（LSP/AST）+ 浏览器/桌面工具（browser_control/snapshot/desktop_screenshot）有依赖链（_app.py/proactive/scroll），并入 I-004 阶段4 随 Chromium 瘦身统一处理 |
| 2026-08-13 | 新增 I-019（P0 侵权红线）：docx/pdf/pptx/xlsx 4 个技能为 Anthropic 专有，禁止分发。决策：放弃文档改/创建能力，用 markitdown（MIT）补「读文档」；删除 4 个侵权技能待办 |
| 2026-08-13 | 新增 I-020（R5 红线）：html2text 为 GPL-3.0 传染性依赖，已换 markdownify（MIT）。教训：fork 项目必须做全依赖 license 审计，不能只看顶层 Apache-2.0 |
| 2026-08-13 | 新增 I-021：全依赖树 license 审计完成（200+ 包）。无 GPL/AGPL/SSPL；4 个 LGPL 弱传染依赖（python-telegram-bot 直接依赖保留，rope/pytoolconfig/docstring-to-markdown 随阶段4 砍编码工具消除）。NOTICE 已补 LGPL 声明 |
| 2026-08-13 | 编码工具删除（LSP×3 + ast_tool + python-lsp-server/ast-grep-cli 依赖），连带消除 rope/pytoolconfig 两个 LGPL。新增 I-022：web_search 用 Tavily keyless 免费限速，上架后需支持可选 API key |
| 2026-08-14 | I-006 解决：遥测上报彻底移除（telemetry.py 上传禁用 + 删上报地址、_app.py/init_cmd.py 调用移除）。前端确认无遥测。工具侵权审计补全：make-skill 借鉴的 skill-creator 是 Apache-2.0（非专有），合规 |
| 2026-08-14 | 上游 v2.1.0 安全修复 #6676 落地（P0-2）：OneBot 反向 WS 绑定改 loopback 默认 + 非 loopback 强制 access_token（常量时间比较、拒 query-param token）。改 3 文件，py_compile 通过，CHANGES 已记。新增 I-023：本地基线 `upstream/v2.0.1` 与官方 v2.0.1 不一致（channel.py 缺 `_normalize_media_ref`），下次合并上游前必须核对重打基线 |
| 2026-08-14 | v2.1.0 P0/P1 移植第一批（P0-4/8/9/11 + P1-26 后端 + P1-28 + P0-1#6382 + P1-12/15/20）全部落地，commit `315294d` + 后续 #6382/#6907/#6709/#6639。新增 I-024：Monaco 编辑器残留（Coding Mode 砍不干净，阶段3 收尾清理） |
| 2026-08-14 | v2.1.0 移植第二批（P1-14 #6543/#6769 + P1-26 前端 UI + P0-10 #6495）落地，commit `5154f61`/`cad5be0`/`70db5c5`。**I-023 更正**：曾误判「本地基线≠官方 v2.0.1」，经 clone 官方 v2.0.1 逐文件 diff 确认基线完全一致，真实原因是 patch 累积 diff 的提交依赖（#6237 依赖 PATCH 066、#6676 依赖 PATCH 072） |
| 2026-08-17 | I-002/I-003 解决：deploy/Dockerfile 追加 COPY LICENSE NOTICE + docs/CHANGES-FROM-UPSTREAM.md 进镜像 + 3 个 OCI labels（licenses/source/description）；.dockerignore 加 !LICENSE/!NOTICE/!docs/CHANGES-FROM-UPSTREAM.md/!docs/license-compliance.md 白名单例外，使合规文件进入构建上下文（连体问题，同批改） |
| 2026-08-18 | I-004 构建验证通过：镜像 1.91GB（原 ~4GB），Chromium/XFCE4/Node 已剥离；中途修复 runtime 基础镜像 agentscope/uv→python:3.12-slim（无 shell 导致 apt 崩）+ COPY --chmod→RUN chmod（旧构建器不支持）。剩余 800MB 目标需 venv 依赖树瘦身（钉钉/飞书/Twilio/本地模型 SDK 死重 ~300MB+，dingtalk 为顶层 import 有风险），列为独立子阶段 |
| 2026-08-18 | I-004 venv 瘦身**前置影响分析完成**（源码+镜像 venv 实测）：① 渠道注册 `get_channel_registry()` 逐渠道独立 import + try/except 容错（仅 console 必加载）→ 移除钉钉/飞书等 SDK 不会致启动崩溃，渠道自动缺席；② `transformers`54M/`modelscope`33M/hf_hub 为本地 LLM 残留（src 零引用，可砍）；③ ⚠️ `onnxruntime`50M 经 markitdown→magika 硬依赖链被 document_reader 技能使用，**不能删**，sympy 连带保留；④ 可砍 ~200MB+，venv 预计降至 ~500MB、总镜像 ~1.6GB，800MB 仍极难达成（需评估 ≤1.5GB 务实线）。实施前需用户拍板渠道 SDK 去留 |
| 2026-08-18 | I-004 瘦身**第一刀落地验收**：用户拍板「保持多渠道，只砍本地模型残留」→ 删 transformers/modelscope/hf_hub（`ccc0fe8`）。重建后镜像 **1.93GB→1.78GB**（-150MB 含连带依赖），venv 746M→629M。干净容器全绿：认证默认开 `{"enabled":true}`、18 渠道注册完整、markitdown CLI 实测可用（onnxruntime 链完好）。800MB 经实测评估极难达成，I-004 状态改 🟢（务实线 ≤1.5GB 待拍板） |
| 2026-08-18 | 发现并修复 **P0**：`provider_manager.py` 残留孤立 `if provider_id is not None:`（v2.1.0 移植 d4eb42a 遗留）致 `IndentationError`、整条 import 链崩、服务完全无法启动，commit `b95b02c`。清理 browser_use/desktop_screenshot 残留引用（`750e15b`）并删除 3 个孤儿文件 `browser_control.py`/`browser_snapshot.py`/`desktop_screenshot.py`（`2e54cab`）；工作区 15 个 `.diff`/`.patch` 草稿 + `.tmp_console_dist/` 已清理 |
| 2026-08-18 | I-004 **最终重建 + 干净容器验收通过**：47/47 步、`BUILD_EXIT=0`、镜像 1.93GB（+20MB 属上游包版本波动）。干净容器（不挂宿主目录）实测：桌面栈全剥离、supervisord 仅 app 进程、真实 React 页 `hanbao Console` 返回 200、`auth/status` 正常、日志零异常。固化两条验证方法学：①验证容器勿挂宿主 src（会盖掉镜像内前端产物）②勿只看 HTTP 状态码（错误 JSON 也返 200，必须查 body） |
| 2026-08-19 | I-015 **包名全量改名 qwenpaw→hanbao 落地**：`src/qwenpaw`→`src/hanbao`（`git mv`）、`pyproject.toml` `name="hanbao"`、入口 `hanbao=hanbao.cli.main:cli`；四档大小写映射改写 902 文本文件，`QWENPAW_*`→`HANBAO_*`；R2 四文件零改动、8 个 plugin.json 上游署名保留、外部 URL/历史文档保留。改名后 FPK 向导注入凭据须用 `HANBAO_AUTH_USERNAME/PASSWORD`（接 I-007 默认开认证）。已知文档 I-012/013/014/015/016 状态统一为 🟢 |
| 2026-08-19 | **界面品牌化启动（阶段6）**：用户要求「加法 + 大改界面有品牌特点」。T5 品牌基础完成——配色 A 蜜橘暖暖 `#FF8C42`（App.tsx token + 全仓旧橙/蓝硬编码统一）、图形化「函包」logo（logo-dark/light.svg）、favicon 新建 hanbao-icon.svg。品牌红线：Mikasa 肖像（online.svg）是既定 hanbao 图标，保持不换。`vite build` 成功（2m43s）+ `vite preview :4173` 本地预览验证。待 T6~T9（关键页重做 / 时间感知 P0+P1）。踩坑：npm install 被 10min Bash 超时打断致 `@agentscope-ai/icons` 解压不全，单独补包修复 |
| 2026-08-20 | **时间感知 P0+P1 实现（阶段6 线1，未提交）**：根治「用户感冒跨天被当当前事实」。① `_annotate_memory_dates()` 扫描检索答案中 `YYYY-MM-DD`（每日笔记路径自带）前置「记忆关联日期+N天前属历史」提示，注入 `auto_memory_search`(:560) 与 `memory_search`(:489)；② `build_env_context`(:185) 日期独立醒目块+时间感知指引，默认时区 `UTC`→`Asia/Shanghai`（修 UTC+8 深夜差一天）；③ `prompts.py` MEMORY_GUIDANCE 中/英加「🕒 时间感知」小节；④ P1 写入端经 `dream`(:518)/`summarize`(:603) 的 `hint`/`memory_hint` 喂 `as-of+TTL≤7天` 指令（能否生效取决于 ReMe 是否消费该 hint，检索端已兜底）。涉及 `app/chats/utils.py` / `agents/memory/reme_light_memory_manager.py` / `agents/memory/prompts.py`，均加 `[hanbao modification]`，py_compile 通过。改动未提交（铁律：用户说「提交」才提交） |
| 2026-08-20 | **Logo 二次品牌化（T5b，阶段6 线2，已提交 45ebdd8）**：用户上传一张 1024×1024 水墨古典肖像（黑发东方女性 + 龙纹旗袍 + 流苏耳坠），要求把 logo/favicon 全切到此图，**品牌基调整体从「可爱治愈」改为「水墨古风」**。Mikas 聊天头像 `online.svg` **红线保留不动**（不改）。`logo-light.svg`/`logo-dark.svg`（605B→103KB）替换为白底水墨肖像卡片+宋体 wordmark「hanbao」，React 端零改动（路径/文件名不变）；`hanbao-icon.svg`（454B→104KB）换为水墨肖像 favicon；新增 `hanbao-portrait-{source,logo,favicon}.png` + `scripts/_make_hanbao_{portrait,logos}.py`（PIL+base64，写入 `[hanbao modification]`）；删除孤儿 `hanbao-logo.jpg`（243KB，无引用，`rm + git add -u` 按铁律不用 `git rm`）。doc/CHANGES/MEMORY 已同步；已提交 `45ebdd8`；docker 镜像重建 + 容器实测 T1 见下条。 |
| 2026-08-20 | **T6+T7 界面全量水墨化（阶段6 线2，已提交 45ebdd8）**：用户要求「内部整体界面还是 qwenpaw 的样子，大改界面、直接就都偏水墨风」。根因：`App.tsx` 视觉基底是 `@agentscope-ai/design` 的 bailianTheme（上游百炼设计系统），T5 只贴了主色膏药，大量 `.module.less` 仍残留上游暖橙/暖棕/蓝/冷灰硬编码。用户拍板：**主色从暖橘 `#FF8C42` 切换为墨黑+朱砂红**（亮 `#9E2B25`/暗 `#C0392B`，暖橘仅 logo 保留）、关键面子页加水墨装饰。改动：① `App.tsx` antd token 全套水墨 seed（全站含后台自动变色）；② `layout.css` 亮/暗底色换宣纸米白 `#F2EEE4`/墨灰 `#161616`、16 处暗色强调→朱砂红、追加 `.ink-title/.ink-divider/.ink-card/.ink-seal` 工具类 + `--colorPrimary` 全局变量桥接（`var(--colorPrimary,…)` 随明暗切红）；③ `Login/index.tsx` 蓝灰渐变→水墨意境背景+书法标题；④ `layouts/index.module.less` 侧边栏/顶栏暖色批量换水墨；⑤ **46 文件 195 处**硬编码色经 `scripts/_inkwash_rebrand_colors.py`（`[hanbao modification]`，二进制读写保换行符）批量映射：`#FF8C42→#C0392B`、`rgba(255,127,22,*)→rgba(192,57,43,*)`、`rgba(43,18,0,*)→rgba(31,31,31,*)`、`#1677ff/#3b82f6→#5C6B73`（图表 canvas 安全）等；`channelIcons.test.ts` 期望同步。**保留不动**：`@agentscope-ai/*` import、外部 qwenpaw.agentscope.io/PyPI URL（合规 R2）、中性灰 antd 回退值、Mikasa 头像红线。复验全仓品牌色 grep **零残留**。已提交 `45ebdd8`（62 文件 +632/−324，含 T5b logo + T6/T7 + 文档）；镜像重建 + 容器实测 T1 见本表下一条。 |
| 2026-08-20 | **合规修正（R2 上游署名）**：维护 md 时发现改名映射（`QwenPaw→Hanbao` 四档之一）误伤了**指上游的署名语境**——docs 里 "fork 自 Hanbao v2.0.1"/"上游基线：Hanbao v2.0.1"/"基于 Hanbao 修改"、`deploy/Dockerfile` LABEL "derived from Hanbao v2.0.1" 把上游 QwenPaw 写成 Hanbao。**核实 R2 红线未触发**：`LICENSE` 版权行 `Copyright 2025 The QwenPaw Authors` 完好、`NOTICE` 上游归属完整、README 已留"基于 QwenPaw 开发"出处；`.py` 无逐文件版权头（合规规范已确认）。已修复：`deploy/Dockerfile` LABEL + `docs/{handoff,project-plan,lifecycle-management,feasibility-analysis,known-issues}.md` 共约 20 处指上游语境改回 `QwenPaw`（保留项：用户下载目录路径 `Hanbao-2.0.1`、I-012 `window.Hanbao` 技术标识、改名映射历史记录）。plugins/website 产品文档里的 "Hanbao" 属**有意产品改名**（README/LICENSE/NOTICE 出处已保留），不改。 |
| 2026-08-20 | **T1 镜像重建 + 干净容器验收全绿（用户「测一下」触发）**：`DOCKER_BUILDKIT=0` 48/48 步构建成功，新镜像 `c52b22bb54e8`/`hanbao:latest`（1.79GB；console-builder 因 console/src 改动重编前端，后端层全缓存）。干净容器 `hanbao_verify`（不挂宿主 src）实测：等 ~60s 起、curl :8088 body `<title>hanbao Console</title>`（真实页非错误 JSON）、`/api/auth/status`=`{"enabled":true,"has_users":false}`、`/var/log/app.err.log` 无 traceback/FATAL/ERROR（计数 0）。**验收全绿**；容器保留运行中供预览（http://localhost:8088，`docker rm -f hanbao_verify` 可停）。⚠️ 本次镜像 LABEL 仍为旧文案 "derived from Hanbao v2.0.1"（构建读旧 Dockerfile），LABEL 已修复为 QwenPaw 下次重建生效（仅元数据）。 |
| 2026-08-20 | **去 qwenpaw 味重构（已提交 f2e3468/2d5973d/297cc80/a788cdf）**：用户镜像实测后要求「全部页面尽量重构、不要有 qwenpaw 味道」。根因：`@agentscope-ai/design`（Spark Design）= 上游 UI 库，bailianTheme 注入默认 token + Spark 组件（antd 薄封装）+ 阿里 CDN 空态插画 + 百炼紫 `#615ced`。改动：① `App.tsx` token 全量化覆盖 bailian 默认（colorPrimary 系/灰阶/fill/语义色/boxShadow 全套）；② 隐藏 Spark Empty CDN 插画（断 gw.alicdn.com 依赖）+ 空态文字水墨化 + 卡片 hover 墨影；③ 清百炼紫 9 文件 46 处→朱砂红 + 暖橘 rgba(255,157,77) 6 处；④ 聊天页欢迎语 hanbao 化（"你好，我是 hanbao。"，去"旅程/问技能"腔，中英 locale + fallback）。保留：Spark 图标（40+ 种，替换风险大）、聊天气泡 SDK 深层样式、外部 qwenpaw URL（合规）。全仓品牌色 + locale 品牌名**零残留**。 |
| 2026-08-20 | **T1b 镜像二次重建 + 验收全绿（提交 3b28257）**：改 Dockerfile LABEL 触发 apt 层缓存失效真跑，暴露 `E: Unable to locate package fonts-wqy-microhei`（Debian 源已移除该包）→ 移除 microhei 重建成功（`c9d492804176`/1.78GB，apt+前端+uv 全重跑）。干净容器验收全绿：`:8088` `<title>hanbao Console</title>`、auth/status 正常、err.log 异常 0。容器保留供预览。 |
| 2026-08-21 | **砍 10 频道（f8fdce0）+ 砍桌面端整条线（e9c6d08）+ 桌面线收尾（d9a9875）**：频道仅留 8 个（imessage/dingtalk/feishu/qq/console/wecom/xiaoyi/wechat），对应 pyproject SDK 移除（LGPL 直接依赖清零）；桌面端 Header/App 死代码、pywebview/tauri mock、`scripts/pack-tauri/`、7 个桌面 Actions、`@tauri-apps/*` 依赖全清；收尾删悬空 `/api/desktop/shutdown` 端点 + 孤儿 tauri 测试（I-027）。均 grep 彻查零悬空、未构建（待用户「测一下」）。 |
| 2026-08-24 | **I-019/I-022 落地 + 前端两轮水墨化 + 重建验收全绿**：自研 `document_edit.py` 4 工具（create/edit docx/xlsx，python-docx/openpyxl MIT，pptx 放弃）补 I-019；`web_search` 支持可选 `TAVILY_API_KEY` 解 I-022；前端第一轮（a87fb07 字体/闲章/动效）+ 第二轮（59220ad 全面水墨化：登录页意境/聊天气泡/会话项/页眉）按用户拍板「全面水墨化」做实质性重做。**重建镜像 `531ecf90e1ff`/`hanbao:latest`（1.74GB）**，干净容器验收全绿：`<title>hanbao Console</title>`、auth/status `{"enabled":true,"has_users":false}`、err.log 零 traceback、`/api/desktop/shutdown` 404、I-019 依赖就绪。**🔴 构建教训**：shell 的 `HTTP_PROXY/HTTPS_PROXY` 被自动注入构建容器，Clash 没起时 npm/pip 假死——构建须 `--build-arg HTTP_PROXY= --build-arg HTTPS_PROXY=` 清空，走宿主直连（+ daemon mirror），无需 Clash。 |
| 2026-08-24 | **auth.py 死条目清理 + remeLightMemory TAB 隐藏（039fa49）+ ChannelDrawer 死代码清理（5ed0391）+ MD 维护（1aeb83d）**：前者删 `auth.py` `_PUBLIC_PATHS` 漏清的 `/api/desktop/shutdown`、运行配置页隐藏记忆后端 TAB 仅留 reactAgent（时区）；后者删 10 频道 `case` 块(667 行)+3 const+useEffect（noUnusedLocals 须连带删），活频道表单逻辑不受影响。均 grep 彻查零悬空。**本轮回测「测一下」重建 `hanbao:latest`（`1067ffd5c99f`，1.74GB）验收全绿**：`<title>hanbao Console</title>`、auth/status `{"enabled":true,"has_users":false}`、err.log 零 traceback、前端 tsc/vite 编译通过。 |
| 2026-08-24 | **header 被删模块占位清理（e27acfa）**：`Header.tsx` 的 `<Space size="middle">` 中 GitHub 按钮后残留「分隔线 + 空 `<span>` + 分隔线」，空 span 为上游 QwenPaw header（Docs/FAQ/Changelog 等减法删除模块）的占位（git blame 源自基线 9b86a97）。去掉空 span 与冗余分隔线，保留 GitHub 与语言/主题切换间单条分隔线；纯布局清理、无逻辑改动。 |
| 2026-08-25 | **运行配置页下线（I-032）**：时区调整移入侧栏设置面板 `SidebarSettingsPanel`（新增 `TimezoneRow`，复用 `getUserTimezone/updateUserTimezone`/`useTimezoneOptions`），整页 `pages/Agent/Config/` 删除；连带清理 `builtinRoutes` 路由、`builtinMenu` 菜单项、`Sidebar` 简单模式白名单、`constants/backendMappings`（死代码+悬空 import）、`LoopModeSelector` 死链按钮。grep 零悬空（`noUnusedLocals` 安全）。待「测一下」重建验收。 |
| 2026-08-25 | **删除 append_file / delegate_external_agent 两工具（I-033）**：`file_io.py` 移除 `append_file` 定义（含 `@tool_descriptor` 装饰器、清理未用 `append_text_async` 导入）；`tools/__init__.py` 去除两个 import；`security/tool_guard` 的 `file_guardian`/`utils` 移除对应守卫项。前端 `ToolCards/cards` 删除 `AppendFileCard`/`DelegateExternalAgentCard` 并改写注册表，`Agent/Tools/index.tsx` 移除 `delegate_external_agent` 异步执行入口。删 `delegate_external_agent.py` 与端到端测试 `test_acp_runner.py`；修 3 个测试文件悬空 import/断言（`test_file_io` / `test_unified_tool_registration` / `test_utils`），并将 plugin 所有权测试 `builtin_name` 改为仍存在的 `read_file`。**保留 `agents/acp/` 共享子系统**（网页配置 API/TUI/核心 hook 仍依赖），仅删工具本身。grep 全仓零悬空（acp 子系统内注释除外，无害）；py_compile 通过。待「测一下」重建验收。 |

## I-025 · 改 Dockerfile 触发 apt 层缓存失效，暴露 fonts-wqy-microhei 已从 Debian 源移除

- **现象**：`DOCKER_BUILDKIT=0` 重建时 Step 23 `apt-get install` 报 `E: Unable to locate package fonts-wqy-microhei`，exit 100。
- **根因**：此前 Dockerfile 长期未变，apt 层一直缓存命中从未真跑；55e2819 改了 Dockerfile（LABEL），legacy builder 缓存链失效 → apt 真跑 → 暴露 Debian 源已无 fonts-wqy-microhei 包。
- **修复**：移除 `fonts-wqy-microhei`（保留 `fonts-wqy-zenhei` 文泉驿正黑，已覆盖中文字体渲染），提交 3b28257。
- **教训**：改 Dockerfile 任意指令（哪怕后段 LABEL/注释）会使后续 RUN 层缓存失效真跑，可能暴露从未真跑过的环境问题（源变更/包移除）。**改 Dockerfile 后的构建要格外留意 apt/系统层**。

## I-026 · 品牌色批量替换漏网：Spark 百炼紫 #615ced 与暖橘 rgba 形式

- **现象**：用户反馈"还有 qwenpaw 味道"后全量扫描，发现 **百炼紫 `#615ced`/`rgba(97,92,237,*)` 9 文件 46 处**（ThemeToggleButton 选中、ModelSelector 激活、Agent/Skills、ImportHubModal 等）+ 暖橘 **`rgba(255,157,77,1)` 6 处**（=#FF9D4D 的 rgba 形式，Header/Sidebar 小红点）。
- **根因**：① 前两轮批量替换只覆盖"qwenpaw 品牌橙/蓝"，**漏了 Spark 设计系统主题色百炼紫**（最典型的 qwenpaw 色）；② T5 映射过 `#ff9d4d` hex 但**漏了其 rgba 形式**。
- **修复**：`_inkwash_rebrand_colors.py` 追加百炼紫两条规则 + 手工替换暖橘 rgba，提交 2d5973d/297cc80；全仓品牌色 15 色系 grep 零残留。
- **教训**：品牌色批量替换要**穷举上游设计系统的全部主题色**（含 hex + rgba 两种形式），不能只处理印象中的"品牌色"；去味专项应系统性扫描 `@agentscope-ai/design` 的 theme JSON（如 bailianTheme.json 的 token 值）逐项核对。

<a id="i-027"></a>
## I-027 · 桌面线收尾：砍桌面端整条线时漏删的悬空端点 + 孤儿测试

**严重度**：🟠 中 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-21 收尾 `d9a9875`） &nbsp;|&nbsp; **必须处理时机**：桌面砍除收尾

### 现象（2026-08-21「测一下」静态复查发现）
08-11 那轮「Tauri 桌面端移除」把 Header/App 的桌面死代码、pywebview/tauri mock、`scripts/pack-tauri/`、桌面 GitHub Actions、`@tauri-apps/*` 依赖都清了，但漏了三处：
1. `src/hanbao/app/_app.py` 仍注册 `/api/desktop/shutdown` 端点，函数体内 `from ..tauri.env import ...` 指向**已删除**的 `src/hanbao/tauri` 侧车模块——虽是局部 import（app 启动不崩），但一调用即 500，与「桌面端整条线砍掉」目标矛盾。
2. `tests/unit/tauri/` 两个测试仍 `import hanbao.tauri`，pytest 收集期必 ImportError（孤儿测试）。
3. `src/hanbao/tauri/` 目录已不存在（确认）。

### 处理
- 删除 `_app.py` 的 `/api/desktop/shutdown` 端点（含 `[hanbao modification]` 注释说明）。
- 删除 `tests/unit/tauri/test_entry.py` + `test_sidecar_logging.py`（`rm` + `git add -u`，不用 `git rm`），目录随之清理。
- 验证：`_app.py` `py_compile` 通过；`HANBAO_DESKTOP_PORT` 常量仍在 `constant.py`（`port.py` 顶层 import 安全，无启动 FATAL）；被砍频道 import 全仓零残留；`desktop_cmd.py` 已不存在、无悬空。

### 关键教训
**大功能减法后必须 grep 启动路径**（`_app.py` 路由注册、tests）确认无悬空引用，不能只看「删了文件」就认为干净。端点删了但注册还在 = 调用期 500，比启动期 FATAL 更隐蔽。

<a id="i-028"></a>
## I-028 · 前端界面两轮水墨化美化（边缘装饰 → 全面重做）

**严重度**：🟡 低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-24 `a87fb07` 第一轮 + `59220ad` 第二轮，镜像 `531ecf90e1ff` 重建验收全绿） &nbsp;|&nbsp; **必须处理时机**：界面品牌化

### 背景
此前阶段6（T5~T7）已完成水墨古典基调（墨黑+朱砂红、logo、全局换色、去 qwenpaw 味），但用户 2026-08-24 实测反馈「界面还是没怎么变，只是加了点动效」——根因是第一轮美化（a87fb07）仅在既定水墨方向内做边缘装饰（字体/闲章/轻动效），未动布局与质感。

### 已处置
- **第一轮（a87fb07）**：正文无衬线/标题衬线字体分工、空态朱砂圆环印、登录页右上角「函」闲章、页面入场淡入动效。
- **第二轮（59220ad，按用户拍板「全面水墨化」）**：
  - 登录页重写为真实水墨意境双栏（左墨黑品牌立轴 + 右宣纸登录卡 + 朱砂闲章）。
  - 聊天气泡水墨化（user/assistant 宣纸底 + 墨边 + 柔影，含暗色模式）。
  - 会话项 hover 朱砂左条、active 宣纸底+朱砂左边框+衬线名；**修复 QwenPaw 漏网青绿状态点 `rgba(20,184,166)` → 朱砂脉冲**。
  - 宣纸纹理背景升级（noise + 墨晕 + 纤维纹理）。
  - 聊天页眉标题统一衬线字体。
- 合规：均加 `[hanbao modification]`；`online.svg`/Mikasa 红线零碰触；LICENSE/NOTICE 未动。

### 验收
2026-08-24 重建镜像 `531ecf90e1ff`（前端重编 tsc+vite 通过），干净容器实测：`<title>hanbao Console</title>`、auth/status `{"enabled":true,"has_users":false}`、err.log 零 traceback、`/api/desktop/shutdown` 404（悬空端点确认删除）、I-019 依赖 `docx/openpyxl` 就绪。

### 关键教训
**「改完即 commit、禁止改完即构建」铁律 + 用户「测一下」才构建** 在本项目成立，但**静态复查必须在 commit 前做**（I-027 就是 commit 后才在复查发现漏网）。本次还发现 shell 的 `HTTP_PROXY/HTTPS_PROXY` 会被自动注入构建容器，Clash 没起时导致 npm/pip 假死——构建必须清代理 env（见 CHANGES 阶段 6.x 末注）。

<a id="i-029"></a>
## I-029 · ChannelDrawer 被砍频道死代码清理

**严重度**：🟢 极低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-24 `5ed0391`） &nbsp;|&nbsp; **必须处理时机**：频道砍除收尾

### 背景
2026-08-21 砍除 10 个频道（Discord/Telegram/元宝/Matrix/SIP/Mattermost/MQTT/Slack/语音/OneBot）时，其 `ChannelDrawer.tsx` 专属 `case` 表单块因 registry 仅剩 8 频道而永不命中，属无害死代码，当时留作后续收。本次按「删功能先查依赖」铁律清除。

### 处理
- 删 10 个被砍频道 `case` 块（共 667 行）+ 3 个 `Form.useWatch` const（`matrixAuthMethod`/`isMatrixPasswordAuth`/`onebotMediaBase64`）+ matrix 的 `useEffect` + `useEffect` import。
- 因 `tsconfig.app.json` `noUnusedLocals:true`，删 case 必须连带删 const/import，否则 `tsc` 阶段报错。
- `constants.ts`/`channelIcons.ts` 此前已清理干净，本次无改动；无 ChannelDrawer 专属测试。

### 验证
全仓 grep `useEffect`/三 const 在 ChannelDrawer 归零；`case "` 恰为 7 活频道（imessage/dingtalk/feishu/qq/wecom/xiaoyi/wechat）；活频道表单逻辑不受影响。**已随 `hanbao:latest`（`1067ffd5c99f`）「测一下」重建验收全绿**：干净容器 `<title>hanbao Console</title>`、auth/status `{"enabled":true,"has_users":false}`、err.log 零 traceback，`tsc`/`vite` 编译通过。

<a id="i-030"></a>
## I-030 · 运行配置页清理：auth.py 死白名单条目 + 隐藏 remeLightMemory TAB

**严重度**：🟢 极低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-24 `039fa49`） &nbsp;|&nbsp; **必须处理时机**：界面收尾

### 处理
- `src/hanbao/app/auth.py`：`_PUBLIC_PATHS` 删 `/api/desktop/shutdown`（桌面端点路由早删、请求 404 无害，白名单漏清的死条目）。0 依赖风险。
- `console/src/pages/Agent/Config/index.tsx`：移除 `MEMORY_MANAGER_BACKEND_MAPPINGS` import + `memoryBackend` useWatch + dynamicTabs 里按 backend 动态 push 记忆 TAB 的逻辑 → 运行配置页**只剩 reactAgent（用户时区）一个 TAB**。`reme_light_memory_config` 后端默认值照常加载、保存时 `...original` 兜底不丢；`ReMeLightMemoryCard.tsx` 文件保留（backendMappings 仍映射供其它页）。

### 验证
`py_compile` 通过；前端 `tsc`/`vite` 编译 + 运行期待「测一下」镜像重建确认。**已随 `hanbao:latest`（`1067ffd5c99f`）重建验收全绿**：`<title>hanbao Console</title>`、auth/status `{"enabled":true,"has_users":false}`、err.log 零 traceback，运行配置页仅余 reactAgent TAB 前端编译通过。

<a id="i-031"></a>
## I-031 · header 被删模块占位：GitHub 后空 `<span>` + 双分隔线导致中间空一截

**严重度**：🟢 极低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-24 `e27acfa`） &nbsp;|&nbsp; **必须处理时机**：header 布局收尾

### 现象
Console 顶栏 `<Space size="middle">` 中，GitHub 按钮后紧接「分隔线 + 空 `<span>` + 分隔线」，空 `<span>` 无任何子节点，桌面端（`.hideOnMobile`）渲染为空占位，使 header 中间空出一截——用户从 devtools 看到 `hanbao-space-horizontal hanbao-space-align-center hanbao-space-gap-row-middle ...`（即该 antd `<Space>`，因 `App.tsx` 设 `prefixCls="hanbao"` 而带 `hanbao-` 前缀）。

### 根因
`git blame` 显示这几行源自基线 `9b86a97`（上游 QwenPaw v2.0.1 未改）。上游 header 在 GitHub 后还有 Docs/FAQ/Changelog 等模块按钮，减法式二次开发删除这些模块时，按钮内容被清掉，但其 `<span>` 占位与两侧分隔线残留，形成空位。

### 处理
- `console/src/layouts/Header.tsx`：删除空 `<span className={styles.hideOnMobile}>` 与冗余的一条 `headerDivider`，保留 GitHub 与 `<LanguageSwitcher/>`/`<ThemeToggleButton/>` 之间单条分隔线。改动后 header Space 子项：`GitHub` → `divider` → `LanguageSwitcher` → `ThemeToggleButton` → 移动端 `Dropdown`（桌面隐藏）。
- 纯布局清理，无逻辑/依赖改动；移动端 `.hideOnMobile` 与 `.headerDivider` 本就在 ≤768px 隐藏，无副作用。

### 验证
`tsc`/`vite` 编译待「测一下」镜像重建确认（本次为纯 JSX 布局删减，属低风险）。

---

## I-032 · 运行配置页下线：时区调整移入侧栏设置面板、整页删除

**严重度**：🟢 极低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-25） &nbsp;|&nbsp; **必须处理时机**：界面收尾

### 背景
运行配置页（`/agent-config`）经多轮减法后，仅剩「ReAct 智能体」一个 TAB，且该 TAB 只暴露「时区调整」一项。为家庭单用户场景精简入口，将该功能移入侧栏底部 `collapseToggle` 设置齿轮弹出的 `SidebarSettingsPanel`（与语言/主题/模式并列），并彻底删除独立运行配置页。

### 处理
- **新增时区行**：`console/src/layouts/SidebarSettingsPanel.tsx` 增加 `TimezoneRow` 组件——挂载时 `api.getUserTimezone()` 拉取当前时区，`Select`（`useTimezoneOptions()`）选择后 `api.updateUserTimezone()` 保存，复用既有 `agentConfig.timezone*` locale 键；样式沿用面板既有 `.row`/`.label` 结构。
- **删除运行配置页**：整目录 `console/src/pages/Agent/Config/`（index.tsx、useAgentConfig.tsx + 测试、components 全套卡片 + 测试、index.module.less）删除。
- **清理入口与死链**：`builtinRoutes.tsx` 移除 lazy 导入与 `/agent-config` 路由；`builtinMenu.ts` 移除 `core.agent-config` 菜单项（含 `SparkModifyLine` 图标导入，因仅此一处使用一并移除）；`Sidebar.tsx` 的 `SIMPLE_MODE_WHITELIST` 移除 `core.agent-config`。
- **连带死代码**：`constants/backendMappings.ts`（及其测试）仅被已删的 `useAgentConfig` 消费，且 import 了已删的 `LightContextCard`/`ReMeLightMemoryCard`/`ADBPGConfigCard`，一并删除；`LoopInput/LoopModeSelector.tsx` 原「去设置」按钮 `navigate("/agent-config?tab=agentLoop")` 成死链，移除该按钮并清理因此变未用的 `navigate`/`useNavigate`/`Settings2` 导入（避免 `noUnusedLocals` 编译失败）。

### 验证
grep 全仓复核：`Agent/Config`、`useAgentConfig`、`ReactAgentCard`、`/agent-config`、`core.agent-config`、`backendMappings`、`SparkModifyLine` 均零残留；`SidebarSettingsPanel` 时区行结构与既有行一致。前端 `tsc`/`vite` 编译待「测一下」镜像重建确认（低风险纯删减 + 一行新组件）。

---

## I-033 · 删除 append_file 与 delegate_external_agent 两个后端工具

**严重度**：🟢 极低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-25） &nbsp;|&nbsp; **必须处理时机**：工具集减法

### 背景
`append_file`（`file_io.py`，`@tool_descriptor` 装饰、`enabled_by_default=False`）与 `delegate_external_agent`（`delegate_external_agent.py`，通过 ACP 协议调度外部编码 agent，如 claude_code/codex/opencode）均为继承自 QwenPaw 的休眠工具，家庭单用户聊天机器人场景用不到。用户拍板一并砍除。

### 依赖分析（删功能先查依赖）
- `append_file`：仅被 `tools/__init__.py` import + `security/tool_guard` 两处守卫字典引用，完全孤立，干净可砍。
- `delegate_external_agent`：单向 import `agents/acp/`（client/service/tool_adapter/node_runtime/permissions），但 **`agents/acp/` 是共享基础设施**——`app/routers/config.py` 的 `get_acp_config`/`set_acp_config` 网页配置 API、`cli/tui/`、`cli/acp_cmd.py`（`hanbao acp` 服务端）、`hooks/session/session_hook.py`、`runtime/builder.py` 均依赖 `acp.meta` 与子系统。**整删会拖垮控制台配置页与核心 hook**，故**只删工具本身、保留 `agents/acp/` 子系统**。
- `write_file`/`edit_file`：与治理层 `governance/detectors.py`、系统提示词 `app/chats/utils.py`、默认工具预设深度耦合且默认开启，**不在本次两工具范围**，保留。

### 处理
- **后端**：`file_io.py` 删除 `append_file` 定义（含 `@tool_descriptor` 装饰器块）并清理因此变未用的 `append_text_async` 导入；`tools/__init__.py` 去除两个 import；`security/tool_guard/guardians/file_guardian.py` 与 `security/tool_guard/utils.py` 移除对应守卫项（`_TOOL_FILE_PARAMS` / `_DEFAULT_GUARDED_TOOLS`）。
- **删除文件**：`src/hanbao/agents/tools/delegate_external_agent.py`、`tests/integration/test_acp_runner.py`（整文件即端到端测该工具）。
- **前端**：`ToolCards/cards` 删除 `AppendFileCard.tsx`/`DelegateExternalAgentCard.tsx` 并改写 `index.ts` 注册表；`pages/Agent/Tools/index.tsx` 移除 `delegate_external_agent` 异步执行入口（`{["execute_shell_command"]}`）。
- **测试收尾**：`test_file_io.py` 移除 `append_file` import 与 `TestAppendFile` 整类；`test_unified_tool_registration.py` 移除两工具 import 与 `test_delegate_external_agent_disabled_by_default`/`test_append_file_disabled_by_default` 两方法，并将 plugin 所有权测试 `builtin_name` 由已删的 `append_file` 改为仍存在的 `read_file`；`test_utils.py` 的 `_DEFAULT_GUARDED_TOOLS` 期望集合移除 `append_file`。

### 验证
- `python -m py_compile` 四个改动后端文件全部通过。
- grep 全仓：后端 `src/hanbao`（除 `agents/acp/` 子系统内历史注释/docstring，无害）、`tests/`、`console/src` 中 `append_file` / `delegate_external_agent` 功能引用**零残留**（仅 acp 子系统注释提及，因该子系统保留故不清理）。
- 所有修改文件加 `[hanbao modification]` 标记。
- 前端 `tsc`/`vite` 编译待「测一下」镜像重建确认（低风险纯删减）。

---

<a id="i-034"></a>

## I-034 · FPK native 形态 `cmd/main` 执行 `docker load` 因权限失败

**严重度**：🔥 高 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-27 真机验证通过） &nbsp;|&nbsp; **必须处理时机**：阶段 5 FPK 真机验证

### 现象
真机安装 hanbao FPK 后点击「启用」，弹窗报错：
```
[hanbao][main][err] docker load 失败：/vol1/@appcenter/hanbao/docker/hanbao-amd64.tar
```

### 根因
- 本应用为 **native 形态**，容器启停由 `cmd/main` 自行负责，启动阶段需要执行 `docker load` + `docker compose up`。
- `config/privilege` 原设置为 `run-as: package`，应用以专用用户运行；该用户不在宿主机 `docker` 组，无法访问 Docker daemon socket（`/var/run/docker.sock` 通常为 `root:docker 660`）。
- 参考同类离线镜像 FPK 实践（MiBee NVR、1Panel v2、Lucky 等），第三方应用要在生命周期脚本里调用 docker，通常需要 `run-as: root`。

### 处理方案
1. `deploy/fpk/config/privilege`：`run-as` 由 `package` 改为 `root`。
2. `deploy/fpk/cmd/main`：
   - 改用 `/bin/bash`；
   - 增加持久日志 `${TRIM_PKGVAR}/hanbao-main.log`，完整记录 `docker version/load/compose` 的输出；
   - `run_docker` 封装：失败时把 stderr 第一行回写到 `TRIM_TEMP_LOGFILE`，避免 UI 只显示"原因未知"；
   - 启动前先 `docker version` 探测 daemon 连通性。
3. 重新 `fnpack build` 产出 `hanbao.fpk`。

### 验收
- 真机侧载新 FPK 后，启用不再报 `docker load 失败`。
- 容器成功进入 running，8088 端口可访问。
- 若仍失败，读取 `/vol1/@appdata/hanbao/hanbao-main.log` 可见 Docker 真实错误。

### 风险/后续
- `run-as: root` 是官方文档标注的"仅建议官方合作开发者使用"的权限模式；但社区多个第三方离线镜像 FPK（MiBee NVR、1Panel v2、Lucky 等）实测手动安装可行。
- 若未来飞牛收紧该模式导致安装被拒，可回退为 `run-as: package` + `join-groups: ["docker"]`，但需先验证目标系统存在 `docker` 组且飞牛会生效附加组。

## I-035 · 全局默认 LLM 支持在 UI 清空

**严重度**：🟢 极低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-27） &nbsp;|&nbsp; **必须处理时机**：阶段 6 界面打磨

### 背景
用户要求全局「默认 LLM」出厂即为空，且能在 UI 上把已设置的默认值清空回空，让每个 Agent 在聊天页自行选择模型。后端 `active_llm` 出厂默认本就是 `None`（`provider_manager` 初始化 `self.active_model = None`），但前端 `ModelsSection` 没有清除入口，且 `canSave` 强制两个 Select 都必须选值，无法把已设的默认改回空。

### 处理方案
- [后端] `src/hanbao/app/routers/providers.py` 新增 `DELETE /models/active` 端点，复用已有 `ProviderManager.clear_active_model()`（无参即清全局），返回最新 `ActiveModelsInfo`。带 `[hanbao modification]` 标注。
- [前端 api] `console/src/api/modules/provider.ts` 新增 `clearActiveLlm()`（`DELETE /models/active`）。带 `[hanbao modification]` 标注。
- [前端 UI] `console/src/pages/Settings/Models/components/sections/ModelsSection.tsx`：
  - 新增 `handleClear`：调用 `api.clearActiveLlm()`，成功后清空本地选择并触发 `onSaved()`；
  - 当 `activeModels?.active_llm` 存在时，在保存按钮下方显示「清除默认模型」危险按钮（`DeleteOutlined`）。带 `[hanbao modification]` 标注。
- [文案] `zh.json` / `en.json` 的 `models` 段新增 `clearDefaultLlm`（清除默认模型 / Clear default model）与 `llmModelCleared`（已清除默认 LLM / Default LLM cleared）。

### 验收
- 未设置默认时，`activeModels.active_llm` 为 `null`，pill 显示 `— / —`，清除按钮不显示。
- 已设置默认后，点「清除默认模型」→ 调 `DELETE /models/active` → 全局默认清空，pill 回到 `— / —`，聊天页各 Agent 使用各自选择。

---

### I-036 · 品牌展示名统一为 hanbao + 登录页去水墨文案

**严重度**：🟢 极低 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-27） &nbsp;|&nbsp; **必须处理时机**：阶段 6 品牌展示层收敛

### 现象
- 飞牛应用中心安装后，应用显示名是「函包 hanbao」，用户希望直接叫 `hanbao`。
- 登录/注册页品牌区显示「函包」，且有一句标语「墨痕未干，对话已成。家庭本地 · 水墨文人对话」，用户认为用文字表达水墨风格很违和——水墨只是界面视觉风格，不该用文字写出来。

### 根因
- `deploy/fpk/manifest` 的 `display_name=函包 hanbao` 带了中文名。
- 登录页 `console/src/pages/Login/index.tsx` 左栏主标题写死「函包」、副标「HANBAO」、诗句标语「墨痕未干，对话已成。」、底标「家庭本地 · 水墨文人对话」，且两枚朱砂闲章内填「函」字（旧品牌字）。

### 处理方案
1. `deploy/fpk/manifest`：`display_name` 由 `函包 hanbao` 改为 `hanbao`。
2. `console/src/pages/Login/index.tsx`：
   - 左栏主标题「函包」→ `hanbao`；删除冗余副标「HANBAO」。
   - 删除诗句标语「墨痕未干，对话已成。」。
   - 底标「家庭本地 · 水墨文人对话」→「家庭本地 · 私人 AI 聊天助手」（仅保留事实定位，去掉「水墨文人」这类用文字表达风格的措辞）。
   - 左栏与右卡两枚朱砂闲章去掉内填的「函」字，改为纯装饰印记（边框 + 旋转，无文字）。
3. 各改动文件均加 `[hanbao modification]` 标注。

### 验收
- 飞牛应用中心显示名为 `hanbao`。
- 登录页品牌主标题为 `hanbao`，无诗句/水墨文人标语，印章为纯装饰无文字。
- 界面水墨视觉风格（宣纸底、朱砂红、衬线字体、`ink-title` 等）保留，仅去除文字层面的风格表达。

### 风险/后续
- 本次仅改用户指定的两个展示面（飞牛显示名 + 登录页）。README / 文档里「函包」作为中文展示名仍可保留或后续统一，需用户确认是否要全域改 `hanbao`；图标 `console/public/online.svg`（Mikasa 肖像 = hanbao 图标）按红线零碰触、保持不变。

---

### I-037 · FPK 分发物合规补全 + 上游品牌残留清理（2026-08-28）

**严重度**：🔴 高（合规红线） &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-28） &nbsp;|&nbsp; **必须处理时机**：阶段 5 FPK 打包 / 阶段 7 上架前

### 现象（全模块合规扫描发现）
- `hanbao.fpk` 包内**未随附 LICENSE / NOTICE / CHANGES-FROM-UPSTREAM.md**（违反 `license-compliance.md` §4 阶段5 与 §8）。Apache-2.0 二进制分发同样必须随附 LICENSE（§7 误区表）。
- `manifest` 缺 `license=Apache-2.0` 字段（§4 阶段5 明确要求）。
- 品牌改名（QwenPaw→hanbao）漏网三处对外引用：
  - `src/hanbao/cli/update_cmd.py` 的 `_PYPI_JSON_URL` 仍指向 `qwenpaw` PyPI（更新检查会查错包）。
  - `console/src/layouts/constants.ts` 的 `PYPI_URL` 同上。
  - `src/hanbao/providers/openrouter_provider.py` 的 `HTTP-Referer` 仍带 `qwenpaw.agentscope.io` 上游域名（对外请求头暴露上游标识）。
- 其余全仓命中（AgentScope 注释 / `@agentscope-ai/*` 外部库 import / DashScope 真实服务名 / 内部变量名）均属合法引用（R2 红线保留外部库名；§8 要求展示上游仓库链接），不视为违规。

### 处理方案
1. 合规文件随附：`LICENSE` 放 `deploy/fpk/`（顶层，fnpack 自动打包）；`NOTICE` 与 `CHANGES-FROM-UPSTREAM.md` 放 `deploy/fpk/app/`（进 app.tgz，因 fnpack 仅打包约定文件 + 顶层 LICENSE，忽略顶层其他文件）。重新 `fnpack build` 验证三者均在包内。
2. `deploy/fpk/manifest` 增 `license=Apache-2.0`（带 `[hanbao modification]` 注释）。
3. 三处品牌残留改为 hanbao 标识，均带 `[hanbao modification]` 标注：
   - `update_cmd.py` `_PYPI_JSON_URL` → `https://pypi.org/pypi/hanbao/json`
   - `constants.ts` `PYPI_URL` → 同上
   - `openrouter_provider.py` `HTTP-Referer` → `https://github.com/yijiuzero/chat-hanbao`

### 验收
- `tar -tzf hanbao.fpk`：顶层含 `LICENSE`；`app.tgz` 内含 `NOTICE` + `CHANGES-FROM-UPSTREAM.md`。
- `manifest` 含 `license = Apache-2.0`。
- 全仓对外可见商标（QwenPaw/AgentScope/Qwen/通义）仅存于合法内部引用与上游仓库链接，无暗示官方背书的展示。

### 风险/后续
- `website/`（125+ 篇 Docusaurus 文档站）的品牌残留本次未扫描（量太大），建议后续单独一轮审计；若上架需官网级品牌一致，再处理。
- 关于页是否实际可访问 LICENSE（§4 阶段6）尚未实现，作为上架前可选增强项记录。

## I-038 · website/ 文档站上游品牌残留清理（2026-08-28）

**严重度**：🟠 中（品牌合规，上架前必须） &nbsp;|&nbsp; **状态**：🟢 已解决（heroLine 中性化 + 4 项功能性上游链接清理 + FeatureDemoGallery 文档 URL 按 §8 保留上游署名 + 残量上游社媒全量移除） &nbsp;|&nbsp; **必须处理时机**：阶段 7 上架前

### 现象（website/ 审计）
- `website/index.html` 的 `canonical` / `og:url` / `og:image`·`twitter:image` 指向可爬取上游域名 `qwenpaw.agentscope.io`；含 3 个搜索引擎站点验证 token（属上游站点）。
- `config.ts` / `site.config.json` 的 `repoUrl` 指向 `agentscope-ai/QwenPaw`（hanbao 自己仓库应指向 `yijiuzero/chat-hanbao`）。
- `testimonials.ts` 含 "Python + AgentScope" 上游背书措辞。
- i18n `clientVoices` 含阿里云/通义背书（"阿里云开发工程师"、"阿里通义这次出手很稳"、"通义实验室的 Hanbao"）；`footer.copyright` 为虚假法律主体 "© 2026 Qwenpaw PRIVATE LIMITED"。
- Nav/Footer/Contributors/FinalCTA/FAQ/QuickStart 组件 GitHub·releases·issues·install 链接指向 `agentscope-ai/QwenPaw` / `qwenpaw.agentscope.io`。

### 处理方案（已落地，本轮）
1. index.html 可爬取元信息清掉，og:image 改本地 `/hanbao_ip.png`，验证 token 移除（均加 `[hanbao modification]`）。
2. repoUrl / modelScopeForkUrl → `yijiuzero/chat-hanbao`（ModelScope 作占位，待发布 studio）。
3. testimonials 去 AgentScope 背书；i18n 去阿里云/通义背书、copyright 改 `© 2026 hanbao`。
4. 全部组件 GitHub/releases/issues/install 链接改 hanbao 仓库；install 脚本指向 `raw.githubusercontent.com/yijiuzero/chat-hanbao/main/scripts/install.*`。
5. 各改动文件加 `[hanbao modification]` 标注，未做全仓 `sed`（遵守 R2）。
6. heroLine（zh/en/pt-BR 三语种）改中性表述：去掉 "Qwen Personal Agent Workstation / Qwen 的智识，Paw 的温度" 关联，改为 "个人智能体工作台 / 有温度的数码陪伴"。理由：R4 红线，避免暗示与 Qwen/通义 的关联背书（用户拍板：改为中性表述）。
7. `QuickStart.tsx` 的 `DOCKER_IMAGE` 由 `agentscope/hanbao:latest` → `hanbao:latest`（上游 `agentscope` 命名空间非 hanbao 所有；FPK 已内置镜像，`docker pull` 非必需）。
8. `Downloads/constants.ts` 的 `CDN_BASE` 由 `https://download.qwenpaw.agentscope.io` → `https://raw.githubusercontent.com/yijiuzero/chat-hanbao/main`（hanbao 无自建 CDN；下载元数据托管为后续 TODO，见下「待决策·残量」）。
9. 导航「社区福利」入口整体移除：删 `NavCommunityBenefits.tsx`（含上游 `opc.aliyun.com/qwenpaw` 权益页链接），Nav.tsx 去除 import / 状态 / 三处面板与点击外部 / ESC 处理中的相关逻辑。
10. FollowUs.tsx 与 Footer.tsx 的上游 `@agentscope_ai` X 账号链接移除（Footer 同步移除未使用的 `XIcon` import）。
11. 残量上游社媒全量移除：Footer.tsx 的 `socialLinks` 仅保留 GitHub(`yijiuzero/chat-hanbao`)，移除 Discord/钉钉/小红书/微信/抖音 5 项及对应 alicdn `qrCode` 资源，并清理未使用的 `DiscordIcon`/`WChatIcon`/`DouyinIcon`/`DingTalkIcon` import；删除已无任何引用的 `FollowUs.tsx`（含小红书链接 + Discord/DingTalk 社区二维码，均指向上游 AgentScope）；三语种 locale 同步清理 orphaned key：`nav.benefit1~4*`/`nav.communityBenefits*`(en+zh)、`follow.*`(zh/en/pt-BR 整块)、`footer.social.{x,discord,dingtalk,xiaohongshu,wechat,douyin,youtube}`(仅留 github)。
12. `FeatureDemoGallery.tsx` 8 处 `qwenpaw.agentscope.io/docs/...` 文档 URL 按 §8 上游署名决议**保留**（不改代码），此处登记为已决。
13. FAQ.tsx "help" FAQ 项移除上游 AgentScope DingTalk 群(`qr.dingtalk.com`)与 Discord 邀请(`discord.com/invite`)社群链接，仅保留 hanbao 自有 GitHub Issues(`yijiuzero/chat-hanbao/issues`)；清理对应 orphaned i18n key：`homeFaq.troubleshooting.help.{s1Prefix,s1Mid,s1Suffix,dingtalk,discord}`(zh/en/pt-BR)。

### 保留项（§8 上游署名，不改）
- `public/docs`、`public/blog`、`public/release-notes` 内上游仓库/issue 链接与 `qwenpaw.agentscope.io` 文档链接 — 必须展示上游出处。
- `FeatureDemoGallery.tsx` 8 处 `qwenpaw.agentscope.io/docs/...` 文档 URL — 用户拍板按 §8 保留上游署名（不改代码）。

### 待决策（已全部解决）
- **`FeatureDemoGallery.tsx` 8 处文档 URL**（`qwenpaw.agentscope.io/docs/...`）：用户拍板**保留上游外链**（按 §8 必须展示上游出处），已登记为 §8 保留项，不改代码。
- **残量上游社媒（Footer/FollowUs）**：用户拍板**一并移除，仅保留 GitHub**（`yijiuzero/chat-hanbao`）。Footer 移除 Discord/钉钉/小红书/微信/抖音，删除已无引用的 `FollowUs.tsx`，并清理对应 orphaned i18n key（见处理方案 11）。

### 后续 TODO（非阻塞，不在 I-038 范围）
- **Downloads 元数据托管**：`CDN_BASE` 已改 GitHub raw 基址，但 `metadata/index.json` 尚未在仓库发布，下载页当前走空态；需在仓库内维护该索引或改用 GitHub Releases API（另立 issue 跟踪）。

### 验收
- `grep -rn "qwenpaw.agentscope.io" website/src`：仅剩 `FeatureDemoGallery` 8 处文档 URL（按 §8 保留）；其余活动引用零。`Downloads` CDN 已改 GitHub raw；index.html 内仅剩 `[hanbao modification]` 自述注释；无 canonical/og 可爬取元信息。
- `grep -rn "download.qwenpaw.agentscope.io\|opc.aliyun.com/qwenpaw\|agentscope_ai\|agentscope/hanbao" website/src`：零命中。
- `grep -rn "discord.gg\|discord.com/invite\|qr.dingtalk.com\|xiaohongshu.com\|mp.weixin.qq.com\|douyin.com\|xhslink.com" website/src`：零命中（残量上游社媒 + FAQ 社群链接全移除，仅留 GitHub）。
- `grep -rn "函包\|墨痕未干\|水墨文人" website/`：零命中（品牌铁律）。
- `website/src` 内 `agentscope-ai/QwenPaw` 链接零命中（仅剩 `[hanbao modification]` 自述与 §8 署名）。

---

### I-039 · website/ 文档正文安装命令指向错误上游（会装成 QwenPaw）

**严重度**：🟡 中 &nbsp;|&nbsp; **状态**：🟢 已解决（2026-08-31） &nbsp;|&nbsp; **必须处理时机**：阶段 7 上架前文档收尾

### 现象
I-038 审计聚焦 `website/src` 代码/文案层，`website/public/docs/*.md`（125 篇文档正文）未纳入。验收时发现 `quickstart.*.md` 与 `faq.*.md` 的安装命令仍指向上游 `qwenpaw.agentscope.io/install.sh|install.ps1|install.bat`，及 `faq` 的「下载页」链接 `qwenpaw.agentscope.io/downloads`。用户照做会用上游一键脚本装成 **QwenPaw 而非 hanbao**，属功能性错误（hanbao 实际走 fnOS FPK 分发）。

### 处理方案
- `quickstart.en.md` / `quickstart.zh.md`：「Option 2 / 方式二：脚本安装」整块（含上游 install.sh/ps1/bat 命令、Windows LTSC 说明、版本/源码参数）替换为 **「fnOS app center (FPK) / 飞牛应用中心（FPK）」**，说明从飞牛应用中心安装或侧载 `.fpk`，并补 Docker 备选说明。
- `faq.en.md` / `faq.zh.md`：「一键安装」条目改为「fnOS app center (FPK)」并标注上游脚本不适用；自引「快速开始」链接改本地 `/docs/quickstart`；「下载页」链接改 `https://github.com/yijiuzero/chat-hanbao/releases`。
- `comparison.en.md` / `comparison.zh.md`：安装方式对比里的「One-line script installation / 一行脚本安装」改为「fnOS FPK install / 飞牛 FPK 安装」（hanbao 无上游式一键脚本）。
- 均加 `[hanbao modification]` 标注。

### 保留（合法，§8）
- `release-notes/*`、`blog/*` 等上游历史发布/博客中提及 `install.sh`/`install.bat` 属历史记录，按 §8 保留。
- `pip install hanbao` 为正确包名，不动；`practice-agent-team` 的 `higress.ai/hiclaw/install.sh` 是第三方教程装 higress，不动。

### 验收
- `grep -rn "qwenpaw.agentscope.io/install\|qwenpaw.agentscope.io/downloads" website/public/docs/`：零命中。
- 改动文件：`quickstart.en/zh.md`、`faq.en/zh.md`、`comparison.en/zh.md` 共 6 个。


---

### I-040 · P0/P1 功能已知限制与风险（2026-09-01）

**严重度**：🟡 中 &nbsp;|&nbsp; **状态**：🟢 已记录（功能已实现，以下为设计性限制 / 待真机验证项） &nbsp;|&nbsp; **必须处理时机**：飞牛真机分发前

### 现象 / 限制
1. **RAG 仅词法检索（BM25）**：为守住「家庭数据不出 NAS」与瘦身镜像，未引入向量库 / embedding API。语义相近但字面不同的查询（如「电费多少」vs「这个月交了多少钱」）可能召回不全。属设计权衡，非缺陷。
2. **fnOS 无官方第三方 API**：飞牛 fnOS 未公开官方开放 API，本实现按「仅本地网络调用飞牛内网 API」假设封装（端口/路径来自社区逆向，未官方确认）。默认关闭，调用失败优雅降级；真机须用户填写地址/端口并经 `working.secret` 存 token，尚未在真实设备上验证。
3. **渠道健康检查依赖各渠道实现 `health_check`**：微信/QQ/钉钉/飞书/Telegram 若未实现 `health_check`，状态页回退为 unknown 且不触发自动重连（仅收消息重试路径仍可用）。
4. **记忆面板编辑限于 agent 自身记忆保险库**：删除/纠正仅作用于 `<working>/memory|digest|PROFILE.md` 路径内，不触碰 ReMe 自主写路径（遵循 6.ak 治理边界）；跨 ReMe auto_dream 层的真删除核对需 fork ReMe，本轮未做。

### 处理方案
- 以上均为减法式新增的设计性限制，已在代码注释与 `docs/license-compliance.md` 约束内实现；不引入新依赖、不破坏既有路径。
- fnOS 联动在真机验证前保持「默认关闭 + 优雅降级」，避免误连。

### 验收
- RAG：建索引 + 检索冒烟通过（CJK+BM25），无网络调用。
- fnOS：未配置时 `search_fnos_media` 返回降级提示（已验证）；配置/媒体接口受 auth 保护。
