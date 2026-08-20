# hanbao 项目续跑基准（会话交接）

> 本文档是当前会话交付给后续会话的**唯一权威基准**。新会话须严格遵循，不重复返工已确认内容；与原设计冲突的技术决策，须先说明原因并征得确认后再实施。
> 最后更新：2026-08-20 · 状态：阶段0~4 全清（容器化 1.78GB 验收全绿）、包名全量改名落地、阶段5 FPK 脚手架按官方规范建好（剩 `fnpack build` + fnOS 实测）；阶段6 界面品牌化（T5/T5b/T6/T7 水墨古风）+ 时间感知（T8/T9）已实现，T1 镜像重建验收全绿；待 fnOS 实测 → 上架

---

## 一、项目定位（一句话）

hanbao（中文"函包"）是 fork 自 **QwenPaw v2.0.1（Apache-2.0）** 的个人 AI 聊天软件二次开发，目标是打包成**飞牛 NAS FPK 应用包**上架应用中心。单用户、本地数据主权、**渠道（微信等）聊天为主**（2026-08-13 泽零明确修正）。

- 上游：QwenPaw v2.0.1（2026-07-24），基于 AgentScope 2.0（`agentscope==2.0.4.post1`）
- 技术栈：Python 包 `hanbao` + uvicorn(ASGI) + React console，Web Console 端口 **8088**
- 源码本地路径：`E:\浏览器下载\Hanbao-2.0.1\Hanbao-2.0.1`（用户已下载，**勿自行从网络拉取**）

---

## 二、已交付设计文档索引（docs/，均为阶段 1 已对齐版）

| 文档 | 用途 | 新会话如何使用 |
|---|---|---|
| `docs/feasibility-analysis.md` | 可行性分析 | 需求与可行性基准；模型仅云 API |
| `docs/project-plan.md` | 项目规划 | **8 阶段路线 + 版本 + MVP 范围**基准 |
| `docs/lifecycle-management.md` | 全生命周期管理 | 版本号 / 阶段准出标准基准 |
| `docs/license-compliance.md` | 开源许可合规规范 | **每阶段开工前必读 §4 检查项**，未过不进下一阶段 |
| `docs/CHANGES-FROM-UPSTREAM.md` | 与上游差异记录 | 改动证据；每次改动须同步追加 |
| `docs/known-issues.md` | 已知问题追踪 | **I-001~I-024**，每个阶段逐条清 |
| `README_zh.md`（顶部派生说明块） | 项目门面 | 上游正文原样保留，阶段 2 品牌改造再替换 |
| `LICENSE` / `NOTICE` | 许可文件 | **永不动**，Apache-2.0 合规红线 |

---

## 三、关键决策清单（用户拍板，不推翻）

1. **展示名** hanbao（函包）；**版本号从 v0.0.1 起**（非 1.0.0）。
2. **模型策略：仅云 API**，不做本地模型；测试用 OpenAI 兼容 Key（DeepSeek / Kimi / 智谱 / 硅基流动）。
3. **包名策略 = 只改品牌展示层**（Web 标题 / 图标 / 文档）；Python 包名 `hanbao` 与 `HANBAO_*` 环境变量**保持不动**（避免上千处 import 改动与上游同步冲突）。
4. **策略**：先完完整整移植跑通原版，再按需一点点改；不提前裁剪、不提前改名（用户原话）。
5. **8 阶段路线**（阶段 1 已完成，后续依次推进）：
   - 阶段 0 准备 ✅ → **阶段 1 构建跑通原版 ✅** → 阶段 2 品牌改造（主体 ✅）→ 阶段 3 删减定制（主体 ✅，收尾：I-024 Monaco 已清）→ **v2.1.0 修复移植 ✅（P0/P1 重点全清）** → 阶段 4 容器化（自建瘦身镜像）→ 阶段 5 FPK 打包 → 阶段 6 飞牛实测 → 阶段 7 上架
6. **目标架构 linux/amd64**（飞牛为 x86_64），与本机 Docker Desktop 一致，无需 buildx 交叉编译。
7. **构建路径**：本机 Docker Desktop 构建+测试 → 全流程跑通 → 打 FPK → 上传飞牛。
8. **基础镜像**：先用上游默认阿里云 ACR 源，拉不动再 `--build-arg` 换 Docker Hub。
9. **Apache-2.0 合规硬约束**（永不遗忘）：①分发物随附 LICENSE ②原样保留上游版权行 ③改过的文件加 `[hanbao modification]` 标注 ④NOTICE 已主动创建。二进制分发（镜像 / .fpk）同样要带 LICENSE。

---

## 四、当前可运行产物（阶段 1 成果）

- 镜像 `hanbao:0.0.1-upstream`（4.02GB，8GB WSL 下构建成功）
- 容器 `hanbao-test` 运行中；本机访问 **http://localhost:8088** 返回 Hanbao Console 首页
- 基线 commit `9b86a976fffdc37b871fe31a7b689a8b6463c5b4`（`9b86a97`），tag `upstream/v2.0.1`（纯净上游 2846 文件）
- 查看 hanbao 全部改动：`git diff upstream/v2.0.1..HEAD`

> 注：阶段 1 镜像含完整 XFCE4 桌面 + Chromium（体积大头，I-004），纯 Web 聊天用不到，阶段 4 瘦身。

---

## 五、接口 / 架构约定

- **对外接口以 QwenPaw v2.0.1 上游架构为准**：Web Console 端口 8088（uvicorn/ASGI）、`hanbao` Python 包结构、三个数据 volume（working / working.secret / working.backups）。
- 阶段 1 为原版未改，**无自定义接口文档**。
- 若新会话需新增功能 / 定义新接口：须在理解上游架构基础上进行；**与原设计冲突时先说明原因并征得确认**，不擅自推翻。

---

## 六、已知问题（known-issues.md，I-001~I-024）

**已解决 ✅**：I-001（上游 .gitignore 误伤，已 `git add -f`）、I-005（基础镜像拉取 EOF，预拉规避）、I-006（遥测上报，已禁用+调用移除）、I-008（构建 OOM，WSL 提 8GB 解决）、I-009（C 盘满，Junction 迁 F 盘）、I-010（WSL 崩溃转储吞 18GB，`crashDumpCount=0` 关）、I-011（DataFolder 对 WSL2 无效，Junction 为解）、I-017（sed JS 注释污染 Python）、I-019（Anthropic 专有技能，已删+markitdown 替代）、I-020（html2text GPL，已换 markdownify）、I-023（patch 提交依赖，已澄清——本地基线=官方 v2.0.1，原「基线偏离」为误判）、I-024（Monaco 残留，依赖移除+占位符化）。

**待解决（后续阶段逐条清）**：
- **I-002**：Dockerfile 无 `COPY LICENSE NOTICE` → 镜像不含许可文件，阶段 4 必须补。（再分发者合规硬需）
- **I-003**：`.dockerignore` 第 6 行 `*.md` 会排除 `docs/*.md` → 补 I-002 时需加白名单例外（**I-002/I-003 连体问题，同批修**）。
- **I-004**：镜像含 XFCE4 桌面 + Chromium，体积 4GB → 阶段 4 瘦身去冗余。
- **I-007**：Web Console 默认无认证 → 上飞牛前评估开 `HANBAO_AUTH_ENABLED`。
- **I-012~I-016**：品牌残留（window.QwenPaw / localStorage 14 key / CSS 前缀 151 处 / 测试 / 插件 author）→ 均"不能直接改名"（登录态/样式/插件），收益低，标记低优先级，待评估。
- **I-018**：git checkout 吞文件（处理中）。
- **I-021**：LGPL 依赖（NOTICE 已补声明，rope/pytoolconfig 已随编码工具消除）。
- **I-022**：web_search Tavily keyless 限速 → 上架后加可选 API key。

---

## 七、协作铁律（新会话必须遵守）

1. **发现问题必记录**：任何隐患/坑/待办，立刻写 `docs/known-issues.md`（新增 `## I-xxx` + 索引表补行），不只在对话里。
2. **改动前评估依赖、敢于谏言**：删除功能 = 高危，必做影响分析（谁 import/调用、配置/入口/路由是否引用、删了会否悬空或崩溃）；可基于判断说"不行/必须连带改 X"，不盲从指令。遇合规红线/稳定性/下游完整性风险主动指出并给替代方案。
3. **合规红线 R2 永不触碰**：品牌批量替换禁止波及 `LICENSE` / `NOTICE` / `docs/license-compliance.md` / `docs/CHANGES-FROM-UPSTREAM.md`；全仓库 `sed -i 's/QwenPaw/hanbao/g'` 即违约。
4. **每次改动同步**：加 `[hanbao modification]` 标注 + 更新 `CHANGES-FROM-UPSTREAM.md`。
5. **外网**：基本不需碰 GitHub/外网（源码已本地化）。若某步确需外网被墙，立即停手告知用户开代理，不静默重试。
6. **破坏性文件删除**：本环境禁止程序化永久删除（PowerShell 守卫 / Bash 策略 / COM 拦截三道墙），只能由用户手动清。**`git rm` 也高危**（2026-08-14 触发过整个 `console/` 553 文件消失，`git restore` 可救回）——删文件一律「清空占位 + 留孤儿」，物理删除交用户。

---

## 八、新会话推进要点（用户原话精神）

1. 沿用已确定技术方案与模块划分，**不推翻既有设计**。
2. 从**代码实现 → 单元测试 → 集成验证**三阶段依次推进，优先完成核心功能模块开发与自测。
3. 每完成一个阶段**输出可运行产物 + 验证结果**，便于逐步确认。
4. 如遇与原设计冲突的技术决策，**先说明原因并征得确认后再实施**。

> 当前会话交付的设计文档、接口约定与关键决策记录（本文档 + 第二节索引）为后续工作唯一基准；新会话严格遵循，不再重复返工已确认内容。
