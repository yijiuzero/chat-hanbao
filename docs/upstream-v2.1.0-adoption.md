# 上游 QwenPaw v2.1.0 改动采纳指南（函包动工清单）

> 本文件供**另一个会话 / 协作者**直接照做。读完即可知道：我们要从上游 v2.1.0 移植哪些改动、为什么、具体怎么动手。
> 数据来源：QwenPaw 官方 release notes（https://qwenpaw.agentscope.io/release-notes/）+ GitHub compare `v2.0.1...v2.1.0`（212 commits / 3330 files）。
> 生成日期：2026-08-14。基线：函包当前停在 `upstream/v2.0.1`（= 上游 v2.0.1）。

---

## 0. 最终敲定结论（2026-08-14，泽零拍板）

> 在动工前，结合函包定位（微信渠道为主、渠道全开、云 API 走 OpenAI 兼容、审批/备份已砍、沙箱硬开、MCP/多智能体保留）逐项判定做/不做。

**P0（11 项）→ 做 10 项 + 已做 1 项 + 跳过 1 项**

| 判定 | 项 |
|---|---|
| ✅ 已做 | P0-2 OneBot 安全（#6676，已落地 commit `0ae826a`） |
| ✅ 做 | P0-1 渠道完整性、P0-4 日志隐私、P0-5/6 沙箱、P0-7 导入安全、P0-8 配置健壮性、P0-9 微信语音、P0-10 视频、P0-11 中文路径 |
| ❌ 跳过 | P0-3 备份恢复（函包已砍备份 UI，数据保护交 NAS 快照） |

**P1（30 项）→ 做大部分 + 跳过 2 项 Provider 特定**

| 判定 | 项 |
|---|---|
| ✅✅ 优先做 | P1-9 中文召回（微信中文核心）、P1-26 token 统计（云 API 成本）、P1-28 MCP 会话恢复 |
| ✅ 做 | P1-12~16 渠道增强（渠道全开）、P1-2~5 记忆、P1-6~8 Scroll 压缩、P1-17 Provider 通用、P1-20~27 Console、P1-29~30 |
| ⚠️ 可选 | P1-1 工作区检查点（NAS 有快照）、P1-10~11 后台任务/工具流 |
| ❌ 跳过 | P1-18 OpenRouter、P1-19 MiniMax（函包走 OpenAI 兼容，不用这些 Provider） |

**执行顺序**：P0-1 渠道完整性 → P0-9/10/11 微信多模态/中文路径 → P0-4/5/6/7/8 安全健壮性 → P1-9/26/28 重点 → 其余 P1。

---

## 1. 背景与目标

- 函包 = QwenPaw 的 fork，定位：**飞牛 NAS 上的个人 AI 聊天应用**，单用户、本地数据主权、**渠道（微信等）聊天为主**。
- 已拍板的方向：**只改品牌展示层**（Web 标题/图标/文档），Python 包名 `qwenpaw` 与 `QWENPAW_*` 环境变量**保持不动**；**保留**多智能体(ACP)、渠道、MCP；**已砍掉**审批(governance 主路径 ASK→ALLOW)；**只用云 API**，不做本地模型。
- v2.1.0 是一次大版本。经评估：**大部分新功能对函包是膨胀（不采纳），但一大批"渠道正确性 / 安全 / 数据完整性 / 记忆·Scroll"修复咱们现在就有同样的坑，必须或应该移植。**

本文只收录 **P0（必做）** 与 **P1（建议做）**。P2（不采纳）见第 6 节，避免走偏。

---

## 2. 动工前必须遵守的硬约束（违反即违规/出事）

1. **开源许可合规**（最高优先级，详见 `docs/license-compliance.md` §4，每动一块前先过检查项）：
   - 任何改动文件加 `[hanbao modification]` 标注；同步记到 `docs/CHANGES-FROM-UPSTREAM.md`。
   - **红线 R2**：绝不能用 `sed -i 's/QwenPaw/hanbao/g'` 之类批量替换波及 `LICENSE` / `NOTICE` / `docs/license-compliance.md` / `docs/CHANGES-FROM-UPSTREAM.md`。
   - 二进制/镜像分发也要带 LICENSE（阶段3 容器化时补 `COPY LICENSE NOTICE`）。
2. **包名不动**：源码里 `import qwenpaw`、环境变量 `QWENPAW_*` 一律保留。只改展示层文案/图标。
3. **审批相关不要碰**：函包已砍审批。凡是只服务于 approval 的改动（如 #6508 子 agent 继承审批级别、#6833 渠道审批路由字段）**直接跳过**；只有与审批无关的子项（如 #6595 空 batch 不把单任务变批处理）才做。
4. **外网策略**：本环境基本不碰 GitHub。若要拉取 v2.1.0 源码/标签，**先停手并告知用户开代理**，不要静默重试。
5. **一次一处、可验证**：单用户逐个验，不一次性大改（见 `docs/` 协作约定）。改完记入 `docs/known-issues.md` 若发现新问题。

---

## 3. 如何取得 v2.1.0 的改动（来源与提取方法）

有两个素材，按需选：

- **A. 已下载的整包 patch**（本机已有，无需联网）：
  `F:\work\chat-hanbao\qwenpaw_v201_v210.patch`（约 32MB，git-format-patch，212 个提交，含提交元信息）。
  用它**只读**地查"某个 PR 到底改了哪些文件/行"：用 Grep 工具搜 `Subject:` 或 PR 号，再定位 `diff --git` 块。**不要直接 `git am` 整个文件**（会把 212 个上游提交全打进来，与函包已有改动大规模冲突）。

- **B. 上游 v2.1.0 源码/标签**（需联网，推荐用于实际移植对照）：
  方式一：`git fetch` 上游后 `git diff upstream/v2.0.1 upstream/v2.1.0 -- <路径>` 看增量；
  方式二：下载 v2.1.0 release tarball 解到临时目录，与函包当前文件逐文件比对。
  取得源码前**先按 §2.4 与用户确认开代理**。

**通用移植步骤（每个 P0/P1 项都遵循）**：
1. 用素材 A 或 B 定位该项涉及的**具体文件路径与 hunk**（先 `git log v2.0.1..v2.1.0 -- <路径>` 找提交，或 grep patch）。
2. 在函包对应文件上**手工移植**该 hunk（不要整文件覆盖，避免冲掉函包已有改动）。
3. 加 `[hanbao modification]` 标注；若改的是从上游来的文件，同步 `docs/CHANGES-FROM-UPSTREAM.md`。
4. 跑对应模块测试 / 在 Docker(`hanbao-test`) 里手动验证；有问题记 `known-issues.md`。

---

## 4. P0 —— 必做（安全 / 数据完整性 / 渠道正确性）

> 这些直接戳中"飞牛 NAS 部署 + 单用户 + 渠道聊天"的命门，建议优先。

| # | 改动 | PR | 文件线索 | 动工要点 |
|---|---|---|---|---|
| P0-1 | 重连/切 Agent 不再恢复错聊天、陈旧渠道、重复待发消息 | #6602 #6546 #6382 | `console/src/pages/Chat/*`、`sessionApi/*` | 渠道是核心。**最高优先**。对照 patch 里 `fix(chat): prevent stale channel identity leaking` 等提交，移植会话/渠道身份重置逻辑，重点测"切换 Agent 后首条消息是否带旧渠道"。 |
| P0-2 | OneBot 默认只监听本地，暴露网络需 token | #6676 | `qwenpaw/channels/onebot/*`、`entrypoint`/配置 | **安全红线**，对应已知问题 I-007（容器无认证）。把"默认 bind 127.0.0.1 + 暴露须 token"的校验逻辑移植；验证对外只暴露时需 token。 |
| P0-3 | 备份恢复等待后台完成 + 接受零字节锁文件 | #6735 #6703 | `qwenpaw` 备份/恢复核心（对应 backups volume） | 防数据损坏。移植"restore 等待后台任务结束"与"零字节锁文件可接受"的判断；验证中断恢复不丢数据。 |
| P0-4 | 对话命令参数不再写入日志 | #6692 | 日志配置 / 命令执行日志点 | 隐私。定位打印 command args 的日志行，改为脱敏或不打印；grep 确认无明文参数落盘。 |
| P0-5 | 沙箱子进程不再继承 `PYTHONHOME` | #6902 | `qwenpaw/sandbox/*` | 防工具执行跑到错误 Python。移植"启动沙箱子进程时清理 `PYTHONHOME` 环境变量"的逻辑。 |
| P0-6 | 沙箱中断清理 / 无效配置降级不崩 + 告警 | #6600 #6582 #6747 #6857 | `qwenpaw/sandbox/*` | 健壮性。移植清理与降级分支，确认异常配置只告警不崩溃。 |
| P0-7 | 项目导入仅读批准路径、上报敏感目录 | #6487 #6713 | 项目导入 / 文件读取模块 | 安全。移植"白名单路径 + 跳过敏感目录并上报"的逻辑；测越界路径被拒。 |
| P0-8 | 损坏 Agent 配置 / 非法 JSON → 可恢复错误而非崩溃 | #6615 | `qwenpaw` Agent 配置加载 | 单人 NAS 上配置坏了不至于整站起不来。移植"try/except → 可恢复配置错误"分支。 |
| P0-9 | 微信语音 / 渠道音频重新转写 | #6573 | 渠道媒体/音频处理 | **微信核心**：语音消息能识别。移植音频转写调用（确认走云 API ASR）；测微信语音进来能出文字。 |
| P0-10 | 视频转发给支持视频的模型 | #6495 | 渠道媒体 / 模型能力判断 | 多模态。移植"按模型 video 能力转发视频"的分支。 |
| P0-11 | 本地路径媒体重新加载（中文/百分号编码路径） | #6873 | 媒体/附件加载、URL 编解码 | 中文路径、微信文件名常带特殊字符。移植 legacy 会话本地路径媒体的解码（含 UNC / 百分号编码）。 |

---

## 5. P1 —— 建议做（体验 / 质量 / 能力，对齐目标）

| # | 改动 | PR | 文件线索 | 动工要点 |
|---|---|---|---|---|
| P1-1 | 工作区检查点 snapshot/restore | #6269 | `qwenpaw` workspace / checkpoint | 本地数据主权增强。移植快照保存/恢复（不改动项目 Git 历史）；与 P0-3 备份机制协调，避免重复。 |
| P1-2 | ReMe 记忆 reranker（OpenAI 兼容端点） | #6398 | `qwenpaw/memory`（ReMe Light 检索） | 咱们用云 API 可直接用。移植 reranker 调用 + 不可用时优雅降级。 |
| P1-3 | ReMe embedding 热更新 / Daily / 手动重建 / 状态 | #6772 | `qwenpaw/memory` | 移植 embedding 热更新、Daily Paper、per-Agent 状态、手动 reindex 开关。 |
| P1-4 | 记忆 & 检查点保存修复（上下文迁移/Web 恢复） | #6592 #6597 | `qwenpaw/memory`、`workspace` | 与 P1-1/P1-3 配套，先移植保存逻辑修复。 |
| P1-5 | auto-memory 跨上下文压缩/恢复保留 + 失败可重试 | #6830 | `qwenpaw/memory` | 防自动记忆在压缩/恢复时丢状态或污染聊天。 |
| P1-6 | Scroll 上下文溢出自动压缩 + 重试 | #6267 | `qwenpaw/scroll` | 长对话不崩。移植"上下文超限→压缩→重试一次"。 |
| P1-7 | 长对话任务驻留 + 可搜索历史索引 | #6323 | `qwenpaw/scroll`、历史检索 | 长聊天体验。 |
| P1-8 | Visual Compact（长上下文压缩输入） | #6456 | `qwenpaw/scroll`、多模态处理 | 省 token，对云 API 成本友好；确认支持多模态时保留源可恢复。 |
| P1-9 | Scroll 中文(CJK) 召回修复 | #6824 | `qwenpaw/scroll` 检索 | **中文用户关键**。移植完整 CJK turn 召回 + 拒绝反向扩展范围。✅ 已落地（含前置依赖 PATCH 066 #6068 + #6237，见 known-issues I-023） |
| P1-10 | 后台长任务工具（进度/取消） | #6151 | `qwenpaw` 工具执行 | 长工具不阻塞。 |
| P1-11 | 工具流复用/分支/循环/并行 | #5698 | `qwenpaw` 工具编排 | Agent 能力增强。 |
| P1-12 | 渠道自定义网关端点（飞书/QQ/WeCom/等） | #6907 | `qwenpaw/channels/*` | opt-in，不改默认。按需移植网关端点配置项。 |
| P1-13 | 机器人冲突告警（同 bot 被多 Agent 占用） | #6909 | `qwenpaw/channels/*` 保存逻辑 | 防误配置。 |
| P1-14 | OneBot 文本/媒体顺序 + 引用/转发展开 | #6543 #6769 | `qwenpaw/channels/onebot` | 渠道消息保真。 |
| P1-15 | 钉钉组织审批自动填充凭据 | #6709 | `qwenpaw/channels/dingtalk` | 若用钉钉则移植。 |
| P1-16 | Matrix 支持 Python 3.12 | #6486 | `qwenpaw/channels/matrix` | 若用 Matrix 则移植（注意上游 .python-version=3.11，函包跑 3.13，需验证）。 |
| P1-17 | Provider：流式/历史/压缩中工具字段不丢 | #6759 | `qwenpaw/providers`、消息存储 | 工具调用可靠性。 |
| P1-18 | OpenRouter 多模态保留 + 可恢复错误重试 | #6733 #6714 #6721 | `qwenpaw/providers/openrouter` | 若用 OpenRouter 则移植。 |
| P1-19 | MiniMax 上下文窗口更新 | #6479 #6554 | `qwenpaw/providers/minimax` | 若用 MiniMax 则移植。 |
| P1-20 | 生产 console 构建不再漏依赖 CSS | #6639 | `console/` 构建配置 | 咱们也构建 console，可能踩同样坑；验证生产包不缺样式。 |
| P1-21 | 大工具输出有界预览（防卡死） | #6637 #6677 | `console/src/**` 工具输出组件 | 体验/稳定性。 |
| P1-22 | 图片 base64 不再算进 token 环 | #6968 | `console` token 统计 / 上传 | **云 API 算费准确**。 |
| P1-23 | 富消息进发送队列 + 多文件预览换行 | #6798 #6662 | `console/src/pages/Chat` | 渠道富媒体体验。 |
| P1-24 | 聊天输入回退 textarea（兼容 contenteditable） | #6934 | `console/src/pages/Chat` 输入框 | 输入健壮性。 |
| P1-25 | 长多行输出保留换行、宽代码块/表格滚动 | #6890 | `console/src/**` 消息渲染 | 渲染体验。 |
| P1-26 | Agent 统计显示 token 用量（收窄到当前 Agent） | #6503 #6402 #6862 | `console` Agent Statistics 页 + `qwenpaw` token 统计 | **云 API 成本核算**，单用户也想知道花多少。 |
| P1-27 | 代码块响应式 + LaTeX/Mermaid 预览 | #6911 | `console/src/**` 代码块组件 | 渲染体验。 |
| P1-28 | MCP 终止会话恢复不丢工具 | #6894 | `qwenpaw/mcp` | 咱们保留 MCP；移植会话恢复逻辑。 |
| P1-29 | 每日记忆按路径日期分组排序 | #6941 | `qwenpaw/memory` | 记忆可读性。 |
| P1-30 | 普通非流式回复也能生成聊天标题 | #6816 | `qwenpaw` 标题生成 | 小体验。 |

---

## 6. 范围外（不要做，避免走偏）

以下属膨胀或与定位不符，**本清单不要求移植**（若后续策略变化再单独评估）：
- QwenPaw OS Shell 桌面窗口/启动器/任务栏（#6645 #6718）—— NAS 是 web 控制台，不需要"桌面 OS"。
- QwenPaw Creator 视频生成（#6284）—— 重且与私人聊天无关。
- Cross-harness Codex / Qoder（#6397）—— 需外部 CLI。
- Browser-use（#6276）、Computer-use 桌面 GUI 自动化（#6424）—— 桌面自动化非 web 聊天核心。
- Unified Files Workspace（#6504）—— 与 OS Shell 耦合，可选低优先。
- App Center 重设计底层依赖上述 App，仅前端可酌情取（#6553）。

**审批相关修复整体跳过**（函包已砍审批），仅 #6595（空 batch 不把单任务变批处理）属通用正确性，保留。

---

## 7. 建议执行顺序

1. **先打通"取材"**：与用户确认能否联网取 v2.1.0 源码（§3-B）；同时本机 patch 文件已可用于查 diff。
2. **P0 按风险排序**：P0-2(OneBot 安全) → P0-1(渠道完整性) → P0-3(备份) → P0-8(配置健壮性) → P0-9/10/11(渠道多模态/中文路径) → P0-4/5/6/7(日志/沙箱/导入安全)。
3. **P1 按模块分批**：记忆/Scroll 一组（P1-1~9）→ 渠道组（P1-12~16）→ Provider 组（P1-17~19）→ Console/UI 组（P1-20~27）→ MCP/杂项（P1-28~30）。
4. 每批改完在 Docker(`hanbao-test`) 验证后再进下一批；新问题记 `known-issues.md`。

---

## 8. 给后续会话的开放问题（需用户拍板）

- 是否**整体 rebase 到 v2.1.0**（干净但工作量大、需解决函包已有改动冲突），还是**只 cherry-pick 本文清单项**（保守、可控）？当前倾向后者。
- P1 里"若用某渠道/Provider 才做"的项（钉钉 #6709、Matrix #6486、OpenRouter #6733、MiniMax #6479）前提是用户实际启用该渠道/模型，请先确认启用范围再动手。
- 取 v2.1.0 源码需联网 → 是否现在开代理拉取？还是仅用本机 patch 做手工移植？

---

## 9. 移植可行性核验（2026-08-14 抽检 P0-1 / P0-2）

> 目的：验证高优先项能否从 v2.1.0 干净移植，避免"以为能直接打其实会冲突"。

**方法**：从本机 `qwenpaw_v201_v210.patch` 解析 P0-1(#6382/#6546/#6602) 与 P0-2(#6676) 涉及的提交 → 共 **72 个唯一文件**；逐文件跑 `git diff upstream/v2.0.1` 比对函包当前状态。

**结果**：函包已改动其中 **14/72**，其余 **58 个与 v2.0.1 完全一致**（可直接 `git apply` / `git cherry-pick` 单提交，无冲突）。

**14 个已改动文件分类处理**：

| 类别 | 文件 | 处理 |
|---|---|---|
| 跳过（不移植） | `README.md` `README_ja.md` `README_ru.md` `README_vi.md` `README_zh.md`（5）、`src/qwenpaw/__version__.py`（1） | 函包有自有文档/版本策略（v0.0.1），不取上游版本号与多语言 README |
| 特殊（按需合并） | `console/src/locales/en.json` `console/src/locales/zh.json`（2） | 仅当上游新增了 UI 文案字符串才合并，合并时注意品牌层 |
| 需手工 3-way 合并（核心源码 6） | `console/src/pages/Chat/index.tsx`、`console/src/pages/Chat/components/ChatSessionDrawer/index.tsx`、`console/src/pages/Chat/components/ChatSessionInitializer/index.tsx`、`src/qwenpaw/app/chats/utils.py`、`src/qwenpaw/config/config.py`、`src/qwenpaw/constant.py` | 函包这些改动多为品牌/审批移除，非逻辑重写；用 `git apply --3way` 或 cherry-pick 后手动解这 6 个文件的冲突即可 |

**关键结论**：
- **P0-2（OneBot 暴露需 token，#6676）核心文件 `src/qwenpaw/app/channels/onebot/channel.py` 未被函包改动 → 干净**；仅有 `config.py`/`constant.py` 因与 P0-1 共享需合并一次。
- **P0-1（渠道聊天完整性）** 主线在 `console/src/pages/Chat/index.tsx` 与 `sessionApi`、`src/qwenpaw/app/chats/utils.py` 等，其中 Chat 页与 chats/utils.py 已被函包改动 → **必须手工合并**，但改动量可控。
- 整体判断：**P0-1 / P0-2 可移植**，推荐"单提交 cherry-pick + 解 6 个核心文件冲突"的方式，不要整包 `git am`。
- 注意：函包相对 v2.0.1 整体已改 699 文件（含删除 coding mode / tauri 桌面端等约 18.9 万行），移植任何 v2.1.0 改动前都先 `git diff upstream/v2.0.1 -- <目标文件>` 确认该文件未被函包动过。
