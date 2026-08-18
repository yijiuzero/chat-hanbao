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
| [I-004](#i-004) | 镜像含完整 XFCE4 桌面 + Chromium，体积巨大 | 🟠 中 | 阶段 4 容器化 | 🟡 已实施（构建通过 1.91GB，800MB 待 venv 瘦身） |
| [I-005](#i-005) | 基础镜像拉取失败（buildkit 并发鉴权 EOF） | 🟠 中 | 阶段 1 构建时 | 🟢 已解决（预拉规避） |
| [I-006](#i-006) | 上游自带遥测上报 | 🟠 中 | 阶段 2 删减定制 | 🟢 已解决（上报禁用+调用移除） |
| [I-007](#i-007) | Web Console 默认无认证（上游认证系统完整，仅默认关闭） | 🟠 中 | 阶段 5 FPK 打包 | 🟡 方案已明确 |
| [I-008](#i-008) | console 前端构建 OOM，4GB WSL 内存不足 | 🔥 高（曾阻塞） | 阶段 1 构建时 | 🟢 已解决 |
| [I-009](#i-009) | 构建机 C 盘 0GB 可用，Docker 无法写入 | 🔥 高（阻塞） | 阶段 1 构建时 | 🟢 已解决（迁 F 盘 Junction） |
| [I-010](#i-010) | WSL 崩溃转储吞噬 18.58GB 磁盘 | 🔥 高 | 阶段 1 构建前 | 🟢 已解决（crashDumpCount=0） |
| [I-011](#i-011) | Docker DataFolder 键对 WSL2 后端无效 | 🟠 中 | 阶段 1 构建前 | 🟢 已解决（Junction 重定向） |
| [I-012](#i-012) | 品牌名残留：JS 命名空间 `window.QwenPaw` | 🟡 低 | 阶段 3 删减定制 | 🟢 已解决（2026-08-17 `window.hanbao`） |
| [I-013](#i-013) | 品牌名残留：localStorage keys (`qwenpaw_*`) | 🟡 低 | 阶段 3 删减定制 | 🟢 已解决（2026-08-17 `hanbao_*`） |
| [I-014](#i-014) | 品牌名残留：CSS 前缀 `qwenpaw` (Ant Design) | 🟡 低 | 阶段 3 删减定制 | 🟢 已解决（2026-08-17 `hanbao`） |
| [I-015](#i-015) | 品牌名残留：测试/e2e/website 中的 QwenPaw | 🟢 极低 | 无阻塞 | 🟡 归入包名改名子阶段 |
| [I-016](#i-016) | 品牌名残留：插件 plugin.json author 字段 | 🟢 极低 | 无阻塞 | 🟢 保留上游署名（合规） |
| [I-017](#i-017) | sed 产生 JS 注释 `//` 污染 Python 文件 | 🔥 高 | 阶段 3 删减定制 | 🟢 已解决 |
| [I-018](#i-018) | git checkout 导致 gitignored 文件从磁盘消失 | 🔥 高 | 阶段 3 删减定制 | 🟡 处理中 |
| [I-019](#i-019) | 文档处理能力降级：Anthropic 技能侵权，只能读不能改/创建 | 🔥 高 | 上架前必须解决 | 🟡 处理中（已定方案 A + markitdown） |
| [I-020](#i-020) | html2text 为 GPL-3.0 传染性依赖，违反 R5 红线 | 🔥 高 | 上架前必须解决 | 🟢 已解决（换 markdownify MIT） |
| [I-021](#i-021) | 依赖审计：4 个 LGPL 弱传染依赖（telegram-bot/rope/pytoolconfig/docstring-to-markdown） | 🟠 中 | 上架前备案 | 🟡 处理中（NOTICE 已补声明） |
| [I-022](#i-022) | web_search 用 Tavily keyless（免费限速），上架后重度使用会撞限速 | 🟡 低 | 上架后可优化 | 🔴 待处理 |
| [I-023](#i-023) | patch 累积 diff 的提交依赖（原「基线偏离」为误判，本地基线=官方 v2.0.1） | 🟡 低 | 移植靠后提交前先识别前置依赖 | 🟢 已澄清 |
| [I-024](#i-024) | Monaco 编辑器残留（Coding Mode 砍不干净） | 🟢 极低 | 阶段 3 收尾 | 🟢 已解决（依赖移除+占位符） |

---

<a id="i-001"></a>
## I-001 · 上游 `.gitignore` 静默吞掉运行时必需文件

**严重度**：🔥 高 &nbsp;|&nbsp; **状态**：🟢 已解决（阶段 0，commit `419f4b4`）

### 现象
上游 release tarball 有 2846 个文件，但在本地 `git init && git add -A` 后只暂存了 2836 个。
差的 10 个文件**不是垃圾文件，全部是运行时必需资源**：

| 被吞的文件 | 数量 | 命中规则 | 丢了会怎样 |
|---|---|---|---|
| `src/qwenpaw/agents/md_files/**/AGENTS.md` | 7 | `.gitignore:109` 裸 `AGENTS.md` | Agent 提示词缺失，智能体行为异常 |
| `console/package-lock.json` | 1 | `.gitignore:82` | `npm ci` 失败，无法复现构建 |
| `plugins/bundle/{cloudpaw/ui,qwenpaw-pet}/dist/index.js` | 2 | `.gitignore:33` `dist/` | 插件加载失败 |

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

**严重度**：🟠 中 &nbsp;|&nbsp; **状态**：🟡 已实施（构建通过 1.91GB，800MB 待 venv 依赖树瘦身） &nbsp;|&nbsp; **必须处理时机**：阶段 4 容器化

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
- `src/qwenpaw/agents/tools/__init__.py` — 移除 `browser_use`、`desktop_screenshot` 两个内置工具注册
- `src/qwenpaw/agents/react_agent.py` — 移除两工具的 hook 超时注册
- `src/qwenpaw/agents/memory/proactive/proactive_responder.py` — 移除 `browser_use`/`desktop_screenshot` 的 import 与工具装配（FunctionTool 列表 + 多模态追加分支）
- `src/qwenpaw/agents/memory/proactive/proactive_utils.py` — 移除 `build_proactive_memory_context` 中"屏幕活动分析"调用块

**2. 依赖摘除（pyproject.toml）**
- 移除 `playwright>=1.49.0`（browser_use 专属）、`mss>=9.0.0`（desktop_screenshot 专属）、`pywebview>=4.0`（桌面 GUI，仅 `desktop_cmd.py` 惰性 import，缺失优雅降级）

**3. 镜像瘦身（deploy/Dockerfile + supervisord）**
- runtime 基础镜像 `node:slim` → **`agentscope/uv`（Python+uv）**，去掉 Node 运行时（约 200MB+）
- 删除 apt 安装的 XFCE4 / xfce4-terminal / Xvfb / dbus-x11 / Chromium + 15 个依赖库 / fonts-liberation / vim
- `build-essential` 改为「安装 → `uv pip install` → 末尾 `apt-get purge`」临时使用，不进最终镜像
- 移除 supervisord 的 `dbus`/`xvfb`/`xfce4` 三个程序，`app` 程序去掉 `DISPLAY`/`PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` 环境变量
- 保留 `QWENPAW_RUNNING_IN_CONTAINER=1`（config 有 `/.dockerenv`+cgroup 兜底，保险仍设）
- 合规层 LICENSE/NOTICE/CHANGES + OCI labels（I-002）原样保留

**4. 待用户手动清理的孤儿文件（不 git rm，按环境安全规则留 orphan）**
- `src/qwenpaw/agents/tools/browser_control.py`、`browser_snapshot.py`、`desktop_screenshot.py` — 已无引用但仍被 `COPY src ./src` 带进镜像（约数十 KB，无害）
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

**体积构成（docker history + 容器 du）**：
- `/app/venv` **746MB**（Python 依赖）—— 绝对大头
- apt 运行时系统库 + 中文字体层 ~1GB（python:3.12-slim 基础 ~150MB + 运行时依赖）
- `/app/src` 39MB、`/usr/share/fonts` 25MB

**第二阶段：冲 800MB（待做，独立子阶段）**
剩余大头是 `venv` 里"已关闭功能"对应的 SDK 死重（容器 `du` + `grep src` 确认）：
- `alibabacloud_dingtalk` 36M + `lark_oapi` 48M → 钉钉/飞书（已关闭渠道）；⚠️ `dingtalk/channel.py` 为**顶层 import**，砍依赖前须确认不被启动急切加载，否则 import 崩溃；`feishu/channel.py` 为函数内**惰性 import**，删之安全
- `twilio` 24M → 短信渠道（hanbao 不需要）
- `transformers` 53M + `modelscope` 30M + `onnxruntime` 49M → 本地模型相关（本地 LLM 已砍，纯云 API）；`src` 中**无直接 import**，纯依赖残留
- `pandas` 42M / `sympy` 30M → 部分工具链

以上可砍约 **300MB+**，但砍完后总镜像仍预计 >1GB（venv 仍 ~400MB+，叠加系统层）。**结论：800MB 在当前单层依赖结构下极难达成**，需评估是否接受"≤1.5GB 务实线"或进一步拆分（多阶段剥离 venv 编译残留 / 换 `python:3.12-alpine`）。此子阶段须先做完整依赖影响分析（尤其 dingtalk 顶层 import），按铁律"删功能高危先分析"，**不在此会话闷头执行**。

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
`qwenpaw init` 等命令会向上游上报使用数据。

### 为什么必须处理
hanbao 将**分发给第三方用户**（飞牛应用中心下载）。让用户的数据在不知情的情况下上报给上游第三方，既不符合"本地数据主权"的产品定位，也存在隐私合规风险。

### 处理方案（阶段 2 执行）
定位遥测代码 → 默认关闭或彻底移除 → 在 CHANGES-FROM-UPSTREAM.md 记录该修改。
若保留任何形式的数据上报，必须在 FPK 安装向导中明确告知用户并提供开关。

### 已处置（2026-08-14）
- [修改] `src/qwenpaw/utils/telemetry.py` — `_upload_telemetry_sync` 改为 no-op（return False），删除 `TELEMETRY_ENDPOINT`（`qwenpawelemetry-*.fcapp.run` 上报地址）
- [修改] `src/qwenpaw/app/_app.py` — 移除启动时的自动上报调用
- [修改] `src/qwenpaw/cli/init_cmd.py` — 移除遥测代码块 + `TELEMETRY_INFO` 文案 + `_echo_telemetry_info_box`
- [确认] 前端 console 无遥测（grep 无 analytics/posthog/sentry 依赖与上报端点）
- 结果：hanbao 不再向 QwenPaw 官方上报任何数据，全链路零上报

---

<a id="i-007"></a>
## I-007 · Web Console 默认无认证

**严重度**：🟠 中 &nbsp;|&nbsp; **状态**：🟡 方案已明确（上游认证系统完整，仅默认关闭，FPK 阶段默认开启） &nbsp;|&nbsp; **必须处理时机**：阶段 5 FPK 打包

### 现象
QwenPaw Web Console（8088）默认不开启认证，设计假设是"个人本地使用"。

### 为什么必须处理
飞牛 NAS 常有公网映射 / 内网多用户场景。若用户把 8088 暴露到公网，**任何人都能直接操作其 AI 助手、读写其文件、消耗其 API 额度**。

### 处理方案
- 阶段 2：确认上游是否已有认证开关，能开则默认开启
- FPK 向导：强制要求用户设置访问密码，或明确警告"仅限内网访问"

### 调研结论（2026-08-17）：认证系统已完整存在，I-007 实为「默认关闭」而非「缺失」

经代码核查，上游 QwenPaw **已内置完整 Web 登录认证**，hanbao 原样继承、未破坏：

- **后端**：`src/qwenpaw/app/auth.py` — 盐化 SHA-256 口令哈希 + HMAC-SHA256 自签 token（无额外依赖）；`AuthMiddleware`（`BaseHTTPMiddleware`）在 `_app.py:603` 挂载；启动时 `_app.py:111` 调用 `auto_register_from_env()` 从环境变量建管理员。
- **开关**：`is_auth_enabled()` 读 `QWENPAW_AUTH_ENABLED`（true/1/yes 即开）。关时中间件放行（当前默认行为）。
- **前端**：`console/src/pages/Login/index.tsx` 真实登录/注册页；`api/request.ts` 收到 401 自动跳 `/login`；token 存 `localStorage["hanbao_auth_token"]`（即 I-013 改名后的 key）。后端 + 前端双重拦截。
- **单用户**：仅允许注册一个账号，契合「单用户私人豆包」定位；忘密码删 `SECRET_DIR/auth.json` 重启即可重注册。
- **渠道不受影响**：中间件仅对 `/api/` 路径鉴权（`not path.startswith("/api/")` 即跳过），微信/OneBot 等渠道走独立连接，登录认证不干预。

**结论 / 处理方向**：I-007 不是「造认证」，而是「FPK 打包时默认开启 + 向导注入凭据」：
1. FPK 阶段（`阶段 5`）在默认 env / docker-compose 设 `QWENPAW_AUTH_ENABLED=true`；
2. FPK 安装向导收集管理员账号密码 → 以 `QWENPAW_AUTH_USERNAME`/`QWENPAW_AUTH_PASSWORD` 注入，首次启动 `auto_register_from_env()` 自动建账号（上游专为 Docker/面板自动化部署设计）；
3. 保留 entrypoint.sh 的 SECURITY NOTICE 警告（auth 关闭时提示），并保留 `security.allow_no_auth_hosts` 回环免登（NAS 本机访问便利）。
4. ⚠️ 阶段 5 实施前需确认 `security.allow_no_auth_hosts` 默认值不误放行 LAN 访问（应为仅 loopback）。

### 关联改动（2026-08-14，非本项解决）
- **OneBot 反向 WS 服务端**获独立加固（上游 v2.1.0 #6676，P0-2）：`ws_host` 默认改 loopback，非 loopback 绑定强制 `access_token`（常量时间比较，拒绝 query-param token）。见 `CHANGES-FROM-UPSTREAM.md` 阶段 3 对应条目。
- ⚠️ 上述加固**只覆盖 OneBot 渠道的 WS 服务端**，本 I-007 专指 **Web Console 8088 本身无认证**，二者是不同攻击面。Console 8088 认证**仍待处理**，未因 #6676 而解决。

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
## I-012 · 品牌名残留：JS 命名空间 `window.QwenPaw`

**严重度**：🟡 低 &nbsp;|&nbsp; **状态**：🔴 待处理 &nbsp;|&nbsp; **必须处理时机**：阶段 3 删减定制

- `window.QwenPaw` 是前端插件系统的宿主 API 命名空间，所有外部插件通过它获取 React/antd 等依赖。
- **不能直接改名**：改了会让所有已安装插件失效。需要在阶段 3 评估兼容方案（如同时暴露 `window.hanbao` 别名 + 保留 `window.QwenPaw` 过渡期）。

<a id="i-013"></a>
## I-013 · 品牌名残留：localStorage keys (`qwenpaw_*`)

**严重度**：🟡 低 &nbsp;|&nbsp; **状态**：🔴 待处理 &nbsp;|&nbsp; **必须处理时机**：阶段 3 删减定制

- 5 个 localStorage key 使用 `qwenpaw_` 前缀（auth_token、agent-storage、theme、sidebar_mode 等）。
- **不能直接改名**：会导致所有用户丢失登录态和偏好设置。需要迁移逻辑：读旧 key → 写新 key → 删旧 key。

<a id="i-014"></a>
## I-014 · 品牌名残留：CSS 前缀 `qwenpaw` (Ant Design ConfigProvider)

**严重度**：🟡 低 &nbsp;|&nbsp; **状态**：🔴 待处理 &nbsp;|&nbsp; **必须处理时机**：阶段 3 删减定制

- `App.tsx` 中 `ConfigProvider prefix="qwenpaw" prefixCls="qwenpaw"` 控制所有 Ant Design 组件的 CSS 类名前缀。
- **不能直接改名**：改了会让所有样式失效。需同步更新所有 `.less` 文件中的 `&:global(.qwenpaw-*)` 选择器。

<a id="i-015"></a>
## I-015 · 品牌名残留：测试/e2e/website 中的 QwenPaw

**严重度**：🟢 极低 &nbsp;|&nbsp; **状态**：🔴 待处理 &nbsp;|&nbsp; **必须处理时机**：无阻塞

- `tests/`、`e2e/`、`website/` 目录包含大量 QwenPaw 引用（测试 fixture、文档、博客等）。
- 不影响容器镜像和用户体验。纯内部文件，后续闲暇时批量替换即可。

<a id="i-016"></a>
## I-016 · 品牌名残留：插件 plugin.json author 字段

**严重度**：🟢 极低 &nbsp;|&nbsp; **状态**：🔴 待处理 &nbsp;|&nbsp; **必须处理时机**：无阻塞

- `plugins/*/plugin.json` 中 `author: "QwenPaw Team"` 等字段。
- 用户看不到这些元数据，不影响功能。后续批量替换。

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

**严重度**：🔥 高 &nbsp;|&nbsp; **状态**：🟡 处理中 &nbsp;|&nbsp; **必须处理时机**：阶段 3 完成前

### 现象
在阶段 3 删减定制过程中，多次出现执行 `git checkout HEAD -- <path>` 恢复文件后，`console/src/api/` 和 `src/qwenpaw/app/routers/` 等目录下的文件从磁盘消失。具体表现为：

1. **第一次**（2026-08-11）：`git checkout` 后 `console/src/api/modules/` 目录整个变空，Docker 构建阶段 `tsc` 报 200+ 个 `TS2307: Cannot find module`。
2. **第二次**（2026-08-12）：`src/qwenpaw/app/routers/__init__.py` 被清空，容器启动后 `ImportError: cannot import name 'create_agent_scoped_router'`。
3. **第三次**（2026-08-12）：`routers/` 下 5 个 `.py` 文件（`_backup_helpers.py`, `tool_calls.py`, `tools.py`, `voice.py`, `workspace.py`）同时消失。

### 根因
这些文件在上游 tarball 中存在，但被 `.gitignore` 规则（主要是 `dist/`、`*.md` 的变体影响）匹配。初始建仓时虽然 `git add -f` 强制纳入了，但后续的 `git rm --cached` 或 check-ignore 路径匹配导致它们从 staging area 丢失。一旦文件不在 git index 中，`git checkout` 无法恢复它们。

### 临时方案
- 从上游本地源码（`E:\浏览器下载\QwenPaw-2.0.1\`）用 `cp -r` 恢复缺失文件
- 或用 `git checkout HEAD -- <path>` 恢复（仅对仍在 index 中的文件有效）

### 根本修复方向
1. 彻底审核 `.gitignore` 中所有可能误伤的规则（已做：`dist/` → `/dist/`，`console/package-lock.json` 取消忽略）
2. 建立验证脚本：每次 git 操作后运行 `git ls-files | wc -l` 对比基线 2846
3. 优先用 `cp -r` 从上游恢复而非依赖 `git checkout`

---

## I-019 · 文档处理能力降级：Anthropic 技能侵权，只能读不能改/创建

**严重度**：🔥 高 &nbsp;|&nbsp; **状态**：🟡 处理中 &nbsp;|&nbsp; **必须处理时机**：上架前

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
| 读 docx/pdf/pptx/xlsx 内容 | 🟡 markitdown 待接入（当前 file_io 只读文本） |
| 改 docx/xlsx 样式/内容 | ❌ 不可（无 python-docx/openpyxl 库 + 无技能指引） |
| 创建 docx/xlsx/pptx | ❌ 不可（已放弃） |

### 待办
1. [x] 删除 4 个 Anthropic 专有技能目录（docx/pdf/pptx/xlsx 的中英双语 + LICENSE.txt + scripts）—— ✅ 已删除（2026-08-13）
2. [x] 接入 `markitdown`（加依赖 `markitdown[pdf,docx,pptx,xlsx]>=0.1.0` + 新增 `document_reader` 技能中英双语）—— ✅ 已完成（2026-08-13，构建验证通过 hanbao:0.0.12）
3. [ ] 后续评估是否需要补「改文档」能力（自研简化版）

---

## I-020 · html2text 为 GPL-3.0 传染性依赖，违反 R5 红线

**严重度**：🔥 高 &nbsp;|&nbsp; **状态**：🟢 已解决 &nbsp;|&nbsp; **必须处理时机**：上架前

### 现象
工具依赖审计发现 `pyproject.toml` 中的 `html2text>=2024.2.26`（用于 `web_search.py` 的 `web_fetch` 把 HTML 转 Markdown）为 **GPL-3.0** 许可（Aaron Swartz 原作，PyPI 明确 "distributed under the GPLv3"）。

GPL 是 copyleft 传染性许可，与 Apache-2.0 闭源分发目标冲突，违反合规规范 **R5 红线**（禁止引入 GPL/AGPL/SSPL 依赖）。

### 处置
- [修改] `pyproject.toml` — `html2text>=2024.2.26` → `markdownify>=1.0.0`（MIT 许可）
- [修改] `src/qwenpaw/agents/tools/web_search.py` — `import html2text` → `from markdownify import markdownify as md`；`_html_to_text` 改用 `md(html, heading_style="ATX", strip=["img","script","style"])`
- 删除 `_new_html2text()` 函数（原 html2text 转换器）

### 教训
上游 QwenPaw 虽然整体 Apache-2.0，但**依赖树里可能藏 GPL 库**（html2text 是 Aaron Swartz 的老牌 GPL 项目）。fork 项目必须做一次**全依赖 license 审计**，不能只看顶层许可证。

---

## I-021 · 依赖审计：4 个 LGPL 弱传染依赖

**严重度**：🟠 中 &nbsp;|&nbsp; **状态**：🟡 处理中 &nbsp;|&nbsp; **必须处理时机**：上架前备案

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

---

## I-022 · web_search 用 Tavily keyless（免费限速），重度使用会撞限速

**严重度**：🟡 低 &nbsp;|&nbsp; **状态**：🔴 待处理 &nbsp;|&nbsp; **必须处理时机**：上架后可优化（非阻塞）

### 现象
`web_search` 工具用 Tavily **keyless** 模式（`X-Tavily-Access-Mode: keyless`），免费、无密钥、开箱即用，但 **Tavily 官方定位是"探索/轻量使用"**，明确说"生产环境换 API key"。keyless 有严格速率限制。

### 风险（非侵权，是服务条款/体验层面）
- 函包上架后用户多了 → 集体触发 Tavily keyless 限流
- Tavily 可能视函包为"第三方产品滥用免费额度"，甚至封禁
- 重度用户（天天让 Agent 联网搜）体验差

### 现状
- `web_search` 工具：默认用 keyless，无需任何配置
- `config.py` 已预留 `tavily_search` MCP 配置（`enabled=False` + `TAVILY_API_KEY=""`），填了 key 才启用

### 待办（上架后优化）
1. [ ] 设置页加"搜索 API key"可选入口，支持用户填 Tavily key（免费 1000 credits/月），keyless 作为 fallback
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
