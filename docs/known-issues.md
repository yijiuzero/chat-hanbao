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
| [I-005](#i-005) | 基础镜像拉取失败（buildkit 并发鉴权 EOF） | 🟠 中 | 阶段 1 构建时 | 🟢 已解决（预拉规避） |
| [I-006](#i-006) | 上游自带遥测上报 | 🟠 中 | 阶段 2 删减定制 | 🔴 待处理 |
| [I-007](#i-007) | Web Console 默认无认证 | 🟠 中 | 阶段 2 / FPK 向导 | 🔴 待处理 |
| [I-008](#i-008) | console 前端构建 OOM，4GB WSL 内存不足 | 🔥 高（阻塞） | 阶段 1 构建时 | 🟡 处理中 |
| [I-009](#i-009) | 构建机 C 盘 0GB 可用，Docker 无法写入 | 🔥 高（阻塞） | 阶段 1 构建时 | 🟢 已解决（迁 F 盘 Junction） |
| [I-010](#i-010) | WSL 崩溃转储吞噬 18.58GB 磁盘 | 🔥 高 | 阶段 1 构建前 | 🟢 已解决（crashDumpCount=0） |
| [I-011](#i-011) | Docker DataFolder 键对 WSL2 后端无效 | 🟠 中 | 阶段 1 构建前 | 🟢 已解决（Junction 重定向） |

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

<a id="i-008"></a>
## I-008 · console 前端构建 OOM，4GB WSL 内存不足

**严重度**：🔥 高（**阻塞构建**） &nbsp;|&nbsp; **状态**：🟡 处理中 &nbsp;|&nbsp; **必须处理时机**：阶段 1 构建时

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

## 变更历史

| 日期 | 变更 |
|---|---|
| 2026-08-10 | 创建，登记 I-001 ~ I-007；I-001 已解决 |
| 2026-08-10 | I-005 实测解决（预拉规避 buildkit 并发鉴权）；新增 I-008 构建 OOM |
| 2026-08-10 | I-009 结案（迁 F 盘 Junction）；新增 I-010（WSL 崩溃转储 18.58GB）、I-011（DataFolder 无效 / Junction 方案）；C 盘回收站仍压 8.19GB 本轮 vhdx 待用户手动清 |
