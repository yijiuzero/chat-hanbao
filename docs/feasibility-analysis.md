# chat-hanbao（hanbao）可行性分析

> 文档版本：v0.1 · 日期：2026-08-07 · 状态：已评审（阶段 1 构建跑通原版已完成）
> 上游基线：Hanbao v2.0.1（2026-07-24，Apache-2.0）

---

## 1. 项目背景与目标

**hanbao** 是 fork 自 [Hanbao](https://github.com/agentscope-ai/QwenPaw) v2.0.1 的个人 AI 聊天软件。Hanbao 是 AgentScope 团队开源的"个人智能体工作站"（Apache-2.0，前身 CoPaw），定位为本地数据主权的个人 AI 助手。

本项目的目标是：**在 Hanbao 基础上按需求删减/定制，做成名为 hanbao 的软件，最终以飞牛 NAS 的 FPK 应用包形式上架飞牛应用中心，供用户一键下载安装。**

核心诉求：
- 单用户、本地数据主权
- Web 聊天为主
- 部署目标 = 飞牛 NAS（fnOS）
- 交付物 = `.fpk` 应用包

---

## 2. 上游软件核实（Hanbao 2.0.1，已本地核实）

源码本地路径：`E:\浏览器下载\Hanbao-2.0.1\Hanbao-2.0.1`（用户已下载，未自行从网络拉取）。

| 维度 | 核实结论（来自 README.md / pyproject.toml / docker-compose.yml） |
| --- | --- |
| 版本 | v2.0.1，2026-07-24 发布；基于 AgentScope 2.0（`agentscope==2.0.4.post1`） |
| 技术栈 | Python 包 `hanbao`（`requires-python >=3.11,<3.14`）；后端 **uvicorn（ASGI）**；前端 React console（构建产物拷至 `src/hanbao/console/`） |
| 运行形态 | CLI `hanbao app`（另有 `copaw` 别名）、Docker（`agentscope/hanbao:latest`）、桌面 App（Tauri Beta）、TUI |
| 访问端口 | Web Console 默认 **8088** |
| 数据存储 | 三个 Docker volume：`working`（配置/记忆/skills）、`working.secret`（密钥）、`working.backups`（备份） |
| 核心能力 | 多智能体、Skills、MCP、多渠道（钉钉/飞书/微信/Discord/Telegram/iMessage/QQ）、Coding Mode、安全四层（Sandbox / Tool Guard / File Guard / Skill Scanner） |
| 遥测 | `hanbao init` 时上报匿名使用数据（版本/安装方式/OS/Python/CPU 架构/GPU） |

---

## 3. 许可与合规可行性 ★

**Apache License 2.0** 明确允许：使用、修改、再分发（含闭源与商用）。

必须满足的义务：
1. 在分发物中保留原始 **LICENSE** 文件（Apache 2.0 全文）与版权声明；
2. 若上游含 **NOTICE** 文件，须一并提供；
3. 对**修改过的文件**，需标注变更说明；
4. 派生作品需声明"基于 Hanbao 修改"，不得移除原作者署名。

**结论：合规可行，且对商业/闭源再分发友好。** 需在仓库根保留 `LICENSE`（Apache 2.0）+ `NOTICE`（如有）+ 原作者版权；hanbao 自身的改动文件头部加 `Modified for hanbao` 注释。建议另附一份 `LICENSE_COMPLIANCE.md` 说明派生关系。

---

## 4. 技术可行性 ★

- 后端已是 ASGI（uvicorn），前端 React，单容器 Docker 部署路径成熟（官方 `docker-compose.yml` 开箱即用）；
- 8088 端口 + 三 volume 持久化，结构清晰，改造集中在**品牌 / 删减 / 打包**三层，不涉及重写内核；
- 数据源、模型 provider 抽象、Skills/MCP 扩展机制均现成。

**结论：高。** 直接复用其运行模型即可。

---

## 5. 资源可行性

- **依赖偏重**：`playwright`、`transformers`、`onnxruntime`、<code>modelscope</code>、<code>huggingface_hub</code>、<code>python-lsp-server</code>、<code>ast-grep-cli</code> 等 → 镜像预估 **2–4 GB**；
- **飞牛 NAS**：通常 x86_64 / arm64，建议内存 **≥4GB**；**基本无独显**，本地大模型（llama.cpp / Ollama）仅能 CPU 跑小模型且较慢；
- 前端需 Node.js 构建链（`npm ci && npm run build`）。

**结论：可行，但有资源门槛。** 模型**仅用云 API**（DashScope / OpenAI 等，飞牛 NAS 无独显，不做本地模型）；镜像需关注飞牛下载体积，建议自建镜像仓库或多阶段构建瘦身。

---

## 6. 部署可行性

- 本地已安装 **Docker Desktop**，容器化验证无障碍；
- 飞牛 **FPK**：官方 `fnpack` CLI 把 Docker 类应用的 `docker-compose.yaml` 包进 `.fpk`，配 `cmd/main` 生命周期、`manifest`、`wizard` 安装向导、`ICON`；
- 飞牛会注入 `TRIM_APPDEST / TRIM_PKGVAR / TRIM_PKGHOME` 等环境变量，可映射到 hanbao 数据卷。

**结论：可行。** FPK 包装本质是把现有 compose 工程化，工作量中等。

---

## 7. 主要风险与对策

| 风险 | 影响 | 对策 |
| --- | --- | --- |
| 遥测上报到 AgentScope 服务器 | 隐私泄露 + 品牌暴露 | 移除或改向 telemetry；`init` 默认 opt-out |
| 品牌改名面大 | 改不干净残留 Hanbao 字样 | 系统扫描包名/CLI/数据目录/前端/文档/telemetry 标识，逐项替换（详见《项目规划》4.1） |
| 镜像体积大 | 飞牛下载慢、存储占用高 | 裁剪无用渠道 SDK；多阶段构建；自建 registry |
| 上游分叉 | 安全补丁/新功能难跟进 | 锁定 v2.0.1，独立 fork，记录改动 delta，按需 cherry-pick |
| 多渠道/桌面/TUI 裁剪耦合 | 砍不干净可能报错 | MVP 优先保留 Web Console；渠道/桌面按需裁剪并跑测试 |
| 认证默认关闭 | 飞牛对外暴露风险 | FPK wizard 强制设管理员账号密码，开启 `HANBAO_AUTH_*` |

---

## 8. 结论

**项目可行。** 推荐路线：

> 锁定 Hanbao v2.0.1 独立 fork → **先完整跑通原版**（阶段 1）→ 最小必要品牌改造 → 按需求删减 → Docker 化（自建瘦身镜像）→ FPK 打包上架飞牛应用中心。模型**仅云 API**（不做本地模型），强制管理员认证。

下一步进入《项目规划》落地。

---

## 9. 待确认事项（决定改造范围）— 已于 2026-08-10 全部确认 ✅

> 以下作为后续改造基线，具体路线见《项目规划》§7（8 阶段）。

1. **展示名**：✅ `hanbao`（中文"函包"）。
2. **保留范围**：✅ MVP 仅保留 Web Console 聊天；TUI / Coding Mode / 多渠道按需求后续裁剪。
3. **默认模型来源**：✅ **仅云 API**（向导填 Key），不做本地模型（飞牛 NAS 无独显）。
4. **版本号起始**：✅ `v0.0.1`（首版标记"移植跑通"阶段，非 1.0.0）。
5. **镜像托管**：⬜ 待定（自建 registry 或 `fnpack` 内嵌构建，阶段 4 容器化时定）。
6. **包名策略**：✅ MVP 仅改"用户可见品牌层"（前端/CLI 别名/数据目录/图标/遥测/文档），Python 包名 `hanbao` 暂保留（避免大规模改 import 引入 bug）；后续版本再彻底改名。
