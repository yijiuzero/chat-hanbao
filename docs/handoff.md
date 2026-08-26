# hanbao 项目续跑基准（会话交接）

> 本文档是当前会话交付给后续会话的**唯一权威基准**。新会话须严格遵循，不重复返工已确认内容；与原设计冲突的技术决策，须先说明原因并征得确认后再实施。
> 最后更新：2026-08-26 收尾 · 状态：阶段0~6 主体全部完成、包名全量改名落地、桌面端整条线已砍除、10 个频道已砍除仅留 8 个、I-019 文档改/创建自研工具落地、I-022 Tavily key 方案落地、前端两轮水墨化已重建验收；I-027~I-033 全部 🟢 已解决（运行配置页下线、append_file/delegate_external_agent 删除、前端导航收敛 6.aa/6.ab）；**hanbao:latest 已瘦身至 1.23GB（2026-08-25 前端收敛构建部署验收全绿、数据卷保留）**；**待办：阶段5 真正 `fnpack build` + fnOS 实测上架**。

---

## 〇、当前环境实况（2026-08-24 深夜交接时刻，新会话必读）

**Git**
- HEAD = `5ed0391`（ChannelDrawer 死代码清理）；工作树干净；所有改动均已提交（未推送 origin/main）
- 08-21~08-24 提交链（重大减法 + 美化 + 收尾）：`f8fdce0`(砍 10 频道) → `e9c6d08`(砍桌面端整条线) → `d9a9875`(桌面线收尾) → `59220ad`(前端全面水墨化第二轮) → `039fa49`(auth.py 死条目+remeLightMemory TAB 隐藏) → `5ed0391`(ChannelDrawer 死代码清理)
- I-019(文档改/创建自研) / I-022(Tavily key) / 前端第一轮水墨美化(a87fb07) 也已提交

**Docker 实况**
- daemon 在跑；**`hanbao:latest` 已瘦身至 1.23GB**（2026-08-25 前端收敛构建部署验收全绿：含 6.aa/6.ab + I-029/I-030/I-033 收尾；`<title>hanbao Console</title>`、auth/status `{"enabled":true,"has_users":true}`、err.log 零 traceback；数据卷 `hanbao-data`/`hanbao-secrets`/`hanbao-backups` 全部保留）
- **✅ 用户日常部署的 `hanbao` 容器（8088）已切到 `hanbao:latest`（1.23GB，2026-08-25 前端收敛重建后按用户拍板「先停旧再起新」切换，数据卷 `hanbao-data`/`hanbao-secrets`/`hanbao-backups` 全部保留，`has_users:true` 确认账号数据未丢）**。部署铁律：重建后先 `docker stop hanbao && docker rm hanbao` 再挂同名卷起重容器，AI 已获授权自动执行此流程。
- **⚠️ 验证容器 `hanbao_verify2`（8091，`531ecf90e1ff`）可能仍在运行** → http://localhost:8091 可预览；`docker rm -f hanbao_verify2` 停。
- **🔴 构建铁律（2026-08-24 实测 + 2026-08-26 修正）：构建必须走代理**——宿主若有死 Clash（`HTTP_PROXY=127.0.0.1:7897`）会被注入构建容器致 npm/pip 假死；但**当前 Docker Desktop 已配 daemon 代理 `http.docker.internal:3128`**，且 `deploy/Dockerfile` 已声明 `ARG HTTP_PROXY/HTTPS_PROXY`（构建期注入 RUN，否则 apt 报 "no Release file"）。正确命令（经 daemon 代理）：
  `docker build -f deploy/Dockerfile --build-arg NODE_IMAGE=node:20-slim --build-arg UV_IMAGE=uv:local --build-arg HTTP_PROXY=http.docker.internal:3128 --build-arg HTTPS_PROXY=http.docker.internal:3128 --build-arg http_proxy=http.docker.internal:3128 --build-arg https_proxy=http.docker.internal:3128 -t hanbao:latest .`
  （`node:20-slim` 替代默认 ACR 的 `agentscope/node:slim`，后者因 Clash 对 aliyuncs 授权 EOF 拉不动；`uv:local` 用本地缓存省一次拉取。无代理环境（如飞牛 fnpack build）省略 proxy 四个 build-arg 即可走直连。）

**待办（下轮优先）**
1. **阶段5 真正 `fnpack build` + fnOS 实测上架**——脚手架已按官方规范建好（docker-project 形态），剩封装+飞牛实测
2. 浏览器预览新界面（8091 或替换 8088 后）

**铁律速查**（详见 .workbuddy/memory/MEMORY.md）
- 仅用户说「测一下/构建验证」才构建；改完即 commit
- 验证容器**绝不挂宿主 src**；看 body `<title>` 不看 HTTP 状态码
- 删 tracked 用 `rm` + `git add -u`，绝不用 `git rm`；批量替换脚本二进制读写
- 合规 R2：LICENSE/NOTICE/README 出处完好已核实；品牌替换禁波及 LICENSE/NOTICE/license-compliance/CHANGES
- **构建清代理 env**（见上「Docker 实况」）

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
| `docs/known-issues.md` | 已知问题追踪 | **I-001~I-033**，全部已解决/已确认（无未闭合代码项） |
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

## 四、当前可运行产物（截至 2026-08-24）

- 镜像 **`hanbao:latest` 已瘦身至 1.23GB**（2026-08-25 回测重建，含 6.aa/6.ab + I-029/I-030/I-033 收尾；验收全绿）
- 用户日常容器 `hanbao`（8088，带数据）仍跑旧镜像 `4b9b782c5d9b`；验证容器 `hanbao_verify2`（8091，`531ecf90e1ff`）可预览
- 基线 commit `9b86a976fffdc37b871fe31a7b689a8b6463c5b4`（`9b86a97`），tag `upstream/v2.0.1`（纯净上游 2846 文件）
- 查看 hanbao 全部改动：`git diff upstream/v2.0.1..HEAD`

> 注：上游 XFCE4 桌面 + Chromium + 桌面端整条线 + 10 个频道 SDK 已全部砍除（阶段4 瘦身 + 08-21 减法），镜像从 4.02GB 降到 1.23GB。

---

## 五、接口 / 架构约定

- **对外接口以 QwenPaw v2.0.1 上游架构为准**：Web Console 端口 8088（uvicorn/ASGI）、`hanbao` Python 包结构、三个数据 volume（working / working.secret / working.backups）。
- 阶段 1 为原版未改，**无自定义接口文档**。
- 若新会话需新增功能 / 定义新接口：须在理解上游架构基础上进行；**与原设计冲突时先说明原因并征得确认**，不擅自推翻。

---

## 六、已知问题（known-issues.md，I-001~I-028 全部 🟢 已解决/已确认）

**全部已解决 ✅**（截至 2026-08-26）：I-001~I-031 历史项全部闭环；I-027（桌面线收尾，2026-08-21 `d9a9875`）、I-028（前端两轮水墨化，2026-08-24 已重建验收）、I-029（ChannelDrawer 死代码清理，2026-08-24 `5ed0391`）、I-030（运行配置页清理，2026-08-24 `039fa49`）、I-031（header 占位修复，2026-08-24 `e27acfa`）、I-032（运行配置页下线，2026-08-25）、I-033（删除 append_file/delegate_external_agent 及对应前端卡片/测试，2026-08-25）。I-029~I-033 已随 2026-08-25 前端收敛构建部署验收全绿。

**重要变更（本交接时刻已落地，新会话勿重复）**：
- **桌面端整条线已砍除**（2026-08-21 `e9c6d08` + 2026-08-24 收尾 `d9a9875`）：Header/App 桌面死代码、pywebview/tauri mock、`scripts/pack-tauri/`、7 个桌面 GitHub Actions、`@tauri-apps/*` 依赖（package-lock 残留 43 处待 npm 自动清）全部清除。
- **10 个频道已砍除仅留 8 个**（2026-08-21 `f8fdce0`）：Discord/Telegram/元宝/Matrix/SIP/Mattermost/MQTT/Slack/语音/OneBot 移除，保留 imessage/dingtalk/feishu/qq/console/wecom/xiaoyi/wechat；对应 pyproject SDK（python-telegram-bot 等）已移除，LGPL 直接依赖清零。
- **I-019 文档改/创建已自研补齐**（2026-08-24）：`document_edit.py` 4 工具（create/edit docx/xlsx），python-docx/openpyxl MIT，pptx 维持放弃。
- **I-022 Tavily 已 env 化**（2026-08-24）：`TAVILY_API_KEY` 可选，无 key 回退 keyless。
- **I-029 ChannelDrawer 死代码清理（2026-08-24 `5ed0391`）**：删 10 频道 `case` 块(667 行)+3 const+useEffect（noUnusedLocals 须连带删），活频道逻辑不受影响。
- **I-030 运行配置页清理（2026-08-24 `039fa49`）**：`auth.py` `_PUBLIC_PATHS` 删漏清的 `/api/desktop/shutdown`；运行配置页隐藏记忆后端 TAB，仅留 reactAgent（时区）。

**唯一未闭合的对外事项**：阶段5 真正 `fnpack build` + fnOS 实测上架（脚手架已建，代码层面无阻塞；2026-08-26 上线前全检收尾：清 browser_use 悬空引用、修 e2e 缩进、升级 cryptography、删 LspError 孤儿类、前端卡片去注册）。

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
