# hanbao 已知问题与踩坑追踪

> 本文件记录移植 QwenPaw 过程中发现的**必须处理但当前阶段尚未处理**的问题。
> 每项都有明确的「必须处理时机」，到达对应阶段时**必须逐项核对**，未处理不得进入下一阶段。
>
> 状态取值：`🔴 待处理` / `🟡 处理中` / `🟢 已解决` / `⚪ 已确认无需处理`

## 索引

| 编号 | 问题 | 严重度 | 必须处理时机 | 状态 |
|---|---|---|---|---|
| [I-001](#i-001) | 上游 `.gitignore` 静默吞掉运行时必需文件 | 🔥 高 | 阶段 0（已完成） | 🟢 已解决 |
| [I-002](#i-002) | Dockerfile 缺 `COPY LICENSE NOTICE`（合规缺口） | 🔥 高（法务） | 阶段 3 容器化 | 🔴 待处理 |
| [I-003](#i-003) | `.dockerignore` 的 `*.md` 会排除合规文档 | 🔥 高（法务） | 阶段 3 容器化 | 🔴 待处理 |
| [I-004](#i-004) | 镜像含完整 XFCE4 桌面 + Chromium，体积巨大 | 🟠 中 | 阶段 2 删减定制 | 🔴 待处理 |
| [I-005](#i-005) | 基础镜像写死阿里云 ACR 新加坡节点 | 🟡 低 | 阶段 1 构建时 | 🔴 待观察 |
| [I-006](#i-006) | 上游自带遥测上报 | 🟠 中 | 阶段 2 删减定制 | 🔴 待处理 |
| [I-007](#i-007) | Web Console 默认无认证 | 🟠 中 | 阶段 2 / FPK 向导 | 🔴 待处理 |

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

**严重度**：🔥 高（法务风险） &nbsp;|&nbsp; **状态**：🔴 待处理 &nbsp;|&nbsp; **必须处理时机**：阶段 3 容器化

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

**严重度**：🔥 高（法务风险） &nbsp;|&nbsp; **状态**：🔴 待处理 &nbsp;|&nbsp; **必须处理时机**：阶段 3 容器化（与 I-002 同批）

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

**严重度**：🟠 中 &nbsp;|&nbsp; **状态**：🔴 待处理 &nbsp;|&nbsp; **必须处理时机**：阶段 2 删减定制

### 现象
`deploy/Dockerfile` 的 runtime 阶段安装了：
- **XFCE4 完整桌面环境** + **Xvfb** 虚拟显示服务器
- **Chromium** 浏览器（用于浏览器自动化 / 网页操作能力）
- **build-essential** 编译工具链

预估镜像 **2–4GB**。飞牛 NAS 通常内存 4–8GB、存储也不宽裕，这是实打实的负担。

### 当前决策
按用户策略 **先完整移植跑通，不提前裁剪**。本阶段原样构建，仅记录不处理。

### 处理方案（阶段 2 执行）
确认 hanbao 定位为「Web 聊天为主」后，评估砍掉：
- XFCE4 + Xvfb（若不需要 GUI 自动化）
- Chromium（若不需要浏览器工具）
- build-essential（改为多阶段构建，只在 builder 阶段保留）

> 这是**全项目瘦身收益最大的一块**，预计可省 50%+ 体积。
> ⚠️ 砍之前必须先确认哪些 Skill / Plugin 依赖它们，否则会静默失去能力。

---

<a id="i-005"></a>
## I-005 · 基础镜像写死阿里云 ACR 新加坡节点

**严重度**：🟡 低 &nbsp;|&nbsp; **状态**：🔴 待观察 &nbsp;|&nbsp; **必须处理时机**：阶段 1 首次构建时

### 现象
`deploy/Dockerfile` 默认基础镜像指向
`agentscope-registry.ap-southeast-1.cr.aliyuncs.com`（新加坡节点），国内拉取速度不确定。

### 好消息
上游留了 `--build-arg` 口子，可覆盖：
```bash
docker build \
  --build-arg NODE_IMAGE=node:22-slim \
  --build-arg UV_IMAGE=ghcr.io/astral-sh/uv:latest \
  -f deploy/Dockerfile -t hanbao:0.0.1 .
```

### 当前决策
用户选择 **先试原版，拉不动再换源**（贴近上游原始状态，符合完整移植要求）。

---

<a id="i-006"></a>
## I-006 · 上游自带遥测上报

**严重度**：🟠 中 &nbsp;|&nbsp; **状态**：🔴 待处理 &nbsp;|&nbsp; **必须处理时机**：阶段 2 删减定制

### 现象
`qwenpaw init` 等命令会向上游上报使用数据。

### 为什么必须处理
hanbao 将**分发给第三方用户**（飞牛应用中心下载）。让用户的数据在不知情的情况下上报给上游第三方，既不符合"本地数据主权"的产品定位，也存在隐私合规风险。

### 处理方案（阶段 2 执行）
定位遥测代码 → 默认关闭或彻底移除 → 在 CHANGES-FROM-UPSTREAM.md 记录该修改。
若保留任何形式的数据上报，必须在 FPK 安装向导中明确告知用户并提供开关。

---

<a id="i-007"></a>
## I-007 · Web Console 默认无认证

**严重度**：🟠 中 &nbsp;|&nbsp; **状态**：🔴 待处理 &nbsp;|&nbsp; **必须处理时机**：阶段 2 / FPK 向导设计

### 现象
QwenPaw Web Console（8088）默认不开启认证，设计假设是"个人本地使用"。

### 为什么必须处理
飞牛 NAS 常有公网映射 / 内网多用户场景。若用户把 8088 暴露到公网，**任何人都能直接操作其 AI 助手、读写其文件、消耗其 API 额度**。

### 处理方案
- 阶段 2：确认上游是否已有认证开关，能开则默认开启
- FPK 向导：强制要求用户设置访问密码，或明确警告"仅限内网访问"

---

## 变更历史

| 日期 | 变更 |
|---|---|
| 2026-08-10 | 创建，登记 I-001 ~ I-007；I-001 已解决 |
