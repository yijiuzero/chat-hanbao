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

_（待执行；品牌替换脚本必须显式排除 `LICENSE` / `NOTICE` / `docs/license-compliance.md`，见 license-compliance §5 R2）_

- [删除] `README_ja.md`、`README_ru.md`、`README_vi.md` — 上游多语言 README（ja/ru/vi）。产品定位：函包仅做**中英双语**（英文 `README.md` + 中文 `README_zh.md`），其他语言不维护。技术零风险：README 纯文档不被代码依赖，且 `deploy/Dockerfile` 仅 `COPY README.md` 进镜像，ja/ru/vi 从未进镜像。合规允许：保留 `LICENSE`/`NOTICE`/`README.md`/`README_zh.md` 即可（Apache-2.0 不要求保留所有语言 README）。关联 commit `a5fcbc9`。

## 阶段 3 · 删减定制

_（待执行）_

## 阶段 4 · 容器化

_（待执行；须同批修复 I-002 `COPY LICENSE NOTICE` 与 I-003 `.dockerignore` 白名单）_

## 阶段 5 · FPK 打包

_（待执行）_

---

## 未修改声明

除本文件记录的改动外，hanbao 中其余代码均来自上游 QwenPaw v2.0.1，其著作权归 The QwenPaw Authors 所有，按 Apache License 2.0 条款授权使用。
