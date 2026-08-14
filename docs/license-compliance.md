# hanbao 开源许可合规规范（强制约束）

> 上游基线：QwenPaw v2.0.1 · Apache License 2.0
> 版权方：`Copyright 2025 The QwenPaw Authors`
> 本文档为**项目硬约束**，优先级高于任何开发便利性考虑。任何阶段的准出都必须通过本文档 §4 的检查项。

---

## 1. 已核实的上游许可事实

以下事实经本地源码 `E:\浏览器下载\QwenPaw-2.0.1\QwenPaw-2.0.1` 实际核实，非推测：

| 项目 | 核实结果 | 对 hanbao 的含义 |
|---|---|---|
| 许可证文件 | 根目录存在 `LICENSE`（10768 字节，Apache 2.0 全文） | **必须原样保留并随分发物一起提供** |
| 版权声明 | LICENSE 尾部为 `Copyright 2025 The QwenPaw Authors` | **不得删除、不得替换为 hanbao 的版权** |
| NOTICE 文件 | **上游不存在 NOTICE** | 严格意义上无"转发 NOTICE"义务；但 hanbao 已主动创建 `NOTICE` 声明派生关系（最佳实践 + 上架审核凭据） |
| 逐文件版权头 | 源码 `.py` 文件**无**版权头（仅 `# -*- coding: utf-8 -*-` 与 docstring） | 无需逐文件保留版权头；但 hanbao 修改过的文件**必须加修改标注** |
| 项目元数据 | `pyproject.toml` 中 `name = "qwenpaw"` | 改包名属"显著修改"，须在 CHANGES 中记录 |
| 商标 | "QwenPaw"、"AgentScope"、通义/Qwen 相关标识 | Apache-2.0 **§6 明确不授予商标许可**，见 §5 红线 |

---

## 2. Apache-2.0 授予我们什么（可以放心做）

Apache License 2.0 是**宽松许可（permissive）**，明确授权：

- ✅ **使用**：商用、私用均可
- ✅ **修改**：任意删减、重写、重构
- ✅ **再分发**：源码或二进制形式
- ✅ **闭源分发**：衍生作品**不必**开源（这是与 GPL 的根本区别）
- ✅ **收费**：可对分发物收费
- ✅ **专利授权**：上游贡献者授予专利使用权

> **结论：把 QwenPaw 改造成 hanbao 并上架飞牛应用中心，法律上完全可行。**
> 我们不是在"钻空子"，这正是 Apache-2.0 鼓励的用法。

---

## 3. Apache-2.0 要求我们做什么（四项强制义务）

分发 hanbao（无论源码、Docker 镜像还是 `.fpk` 包）时，**必须同时满足**：

### 义务 1 — 提供 LICENSE 副本
分发物中必须包含 Apache 2.0 许可证全文。
- 仓库根：`LICENSE` ✅ 已落地
- Docker 镜像内：必须 `COPY` 进镜像（建议 `/app/LICENSE`）
- FPK 包内：必须包含，且应在应用详情/关于页可访问

### 义务 2 — 保留版权、专利、商标、归属声明
上游 `LICENSE` 中的 `Copyright 2025 The QwenPaw Authors` **原样保留**。
- ❌ 不得删除
- ❌ 不得改成 `Copyright 2026 hanbao`
- ✅ hanbao 自己的版权在 `NOTICE` 中**追加**声明，与上游版权**并存**

### 义务 3 — 标注修改（Apache-2.0 §4(b)）
> "You must cause any modified files to carry prominent notices stating that You changed the files."

所有被 hanbao 修改的文件**必须携带显著修改标注**。规范见 §6。

### 义务 4 — 随附 NOTICE（若上游有）
上游无 NOTICE，本义务在技术上不触发。hanbao 仍主动提供 `NOTICE` ✅ 已落地。

---

## 4. 各阶段合规准出检查项（Definition of Done）

**任何阶段未通过对应检查项，不得进入下一阶段。**

### 阶段 0 · 源码就位 + 建仓库
- [x] 上游 `LICENSE` 原样复制到 hanbao 仓库根，字节一致
- [x] 创建 `NOTICE`，声明派生自 QwenPaw v2.0.1 及其版权方
- [x] 创建 `docs/CHANGES-FROM-UPSTREAM.md`，记录基线版本与 commit/发布号
- [x] Git 首个 commit 为**未经修改的上游原始代码**（_commit `9b86a97`，tag `upstream/v2.0.1`_，形成干净的 diff 基线，这是证明"我们改了什么"最有力的证据）
- [x] 第二个 commit 起才是 hanbao 的改动

### 阶段 1 · 构建跑通原版
- [x] 本机 Docker 完整构建上游原版 QwenPaw（镜像 `hanbao:0.0.1-upstream`，4.02GB）
- [x] 容器验证 8088 可访问（返回 QwenPaw Console 首页）
- [ ] 此阶段未改动任何上游代码（仅 `deploy/Dockerfile` 加 NODE 构建堆参数，见 CHANGES），合规检查重点在后续阶段

### 阶段 2 · 品牌改造
- [ ] 每个改动文件加修改标注（§6 规范）
- [ ] `CHANGES-FROM-UPSTREAM.md` 同步更新改动条目
- [ ] 品牌替换**未误伤** `LICENSE` / `NOTICE` 中的 `QwenPaw` 字样（批量替换的高危点，见 §5）
- [ ] 关于页/README 保留"基于 QwenPaw 开发"的出处说明

### 阶段 3 · 删减定制
- [ ] 删除的功能模块不影响 LICENSE/NOTICE 完整性
- [ ] 删除动作记入 CHANGES
- [ ] 若引入新的第三方依赖，核对其许可是否与 Apache-2.0 兼容（禁止引入 GPL/AGPL，见 §5）
- [ ] **全依赖树 license 审计**：不能只看顶层 Apache-2.0，依赖树里可能藏 GPL 库（html2text 教训，I-020）或第三方专有内容（Anthropic 技能教训，I-019）
- [ ] **内置技能/内容的 license 检查**：`agents/skills/` 等内置内容可能带独立 LICENSE（上游 QwenPaw 的 docx/pdf/pptx/xlsx 技能即 Anthropic 专有），逐一核对 source/许可后再决定保留或替换

### 阶段 4 · 容器化
- [ ] Dockerfile 中 `COPY LICENSE NOTICE /app/` —— 详见 [known-issues.md I-002](./known-issues.md#i-002)
- [ ] `.dockerignore` 的 `*.md` 已加白名单例外，否则上一项构建必然失败 —— 详见 [I-003](./known-issues.md#i-003)
- [ ] 镜像 label 标注上游出处：
  `LABEL org.opencontainers.image.source` / `.licenses="Apache-2.0"`
- [ ] 实测验收：`docker run --rm <image> sh -c "ls -l /app/LICENSE /app/NOTICE"` 两文件均存在且非空

> ⚠️ I-002 与 I-003 是**连体问题**，必须同批修复。只加 `COPY` 不改 `.dockerignore` 会直接构建失败。

### 阶段 5 · FPK 打包
- [ ] `.fpk` 包内含 `LICENSE` 与 `NOTICE`
- [ ] 应用详情页/关于页可查看许可信息与上游出处
- [ ] `manifest` 中 license 字段填 `Apache-2.0`

### 阶段 6 · 飞牛实测
- [ ] 安装后在 UI 中能实际访问到许可信息（不是只躺在文件里）

### 阶段 7 · 上架
- [ ] 上架资料中如实说明"基于开源项目 QwenPaw（Apache-2.0）二次开发"
- [ ] 不声称 hanbao 为完全原创
- [ ] 应用图标/名称不含 QwenPaw、AgentScope、Qwen、通义 等商标元素

---

## 5. 红线（绝对禁止）

| # | 禁止行为 | 原因 |
|---|---|---|
| R1 | 删除或篡改 `LICENSE` 中的 `Copyright 2025 The QwenPaw Authors` | 直接违反 §4(c)，是最典型的许可违约 |
| R2 | 批量替换品牌时把 `LICENSE`/`NOTICE` 里的 `QwenPaw` 一并替换掉 | **本项目最可能踩的坑**：`sed -i 's/QwenPaw/hanbao/g'` 全仓库执行即触发 R1。品牌替换脚本必须显式排除 `LICENSE`、`NOTICE`、`docs/license-compliance.md` |
| R3 | 声称 hanbao 为完全自主原创 / 隐瞒派生关系 | 违反归属义务，且上架审核存在欺诈风险 |
| R4 | 在 hanbao 名称、Logo、宣传中使用 "QwenPaw"/"AgentScope"/"Qwen"/"通义" 等商标暗示官方背书 | Apache-2.0 **§6 不授予商标许可**，属独立的商标法问题 |
| R5 | 引入 GPL / AGPL / SSPL 等**强传染**许可的依赖 | 会污染整个分发物，强制 hanbao 开源，与闭源分发目标冲突 |
| R6 | 修改文件却不加修改标注 | 违反 §4(b) |
| R7 | 保留上游遥测上报却不告知用户 | 非许可问题，但属隐私合规风险；改造时必须移除或改向（见项目规划） |
| R8 | 引入**第三方专有许可**的内容/技能（如 Anthropic 文档技能） | 专有许可通常明令禁止「分发/复制/衍生」，再分发即著作权侵权，比商标红线更严重（见 I-019） |

> **LGPL 补充说明（弱传染，不属 R5）**：LGPL（Lesser GPL）是**弱 copyleft**，允许闭源软件**动态链接**（Python `import` 即动态链接）且不修改库本身，仅需在分发物中附 LGPL license 文本 + 版权声明 + 允许用户替换库。与 GPL/AGPL/SSPL（强传染，链接即强制开源）有本质区别。函包已审计出的 LGPL 依赖见 I-021，NOTICE 已补声明。

> **R2 单独强调**：这是"技术操作导致法律违约"的典型场景。阶段 2（品牌改造）执行任何批量替换前，必须先确认排除清单。

---

## 6. 修改标注规范（义务 3 的落地写法）

### Python 文件
在文件顶部 `# -*- coding: utf-8 -*-` 之后插入：

```python
# -*- coding: utf-8 -*-
#
# This file was modified for the hanbao project.
# Original source: QwenPaw v2.0.1 (https://github.com/agentscope-ai/QwenPaw)
# Copyright 2025 The QwenPaw Authors — licensed under Apache License 2.0
# Modifications Copyright 2026 hanbao contributors
#
"""原有 docstring 保持不变。"""
```

### TypeScript / JavaScript 文件
```typescript
/*
 * This file was modified for the hanbao project.
 * Original source: QwenPaw v2.0.1 (https://github.com/agentscope-ai/QwenPaw)
 * Copyright 2025 The QwenPaw Authors — licensed under Apache License 2.0
 * Modifications Copyright 2026 hanbao contributors
 */
```

### 新建的原创文件
无需上游版权，仅标 hanbao 自己的版权即可：
```python
# Copyright 2026 hanbao contributors
# Licensed under the Apache License, Version 2.0
```

### 简化策略（推荐）
逐文件加头部工作量大且易漏。**允许采用替代方案**：
1. 保持 Git 首个 commit 为纯净上游代码 → `git diff` 天然构成完整修改记录；
2. 在 `docs/CHANGES-FROM-UPSTREAM.md` 中维护结构化改动清单；
3. **仅对改动量大的核心文件**加头部标注。

> 该替代方案在实践中被广泛接受（"prominent notices" 未强制要求逐文件头部），但**前提是 CHANGES 文档必须真实、完整、随分发物提供**。

---

## 7. 常见误区澄清

| 误区 | 事实 |
|---|---|
| "Apache-2.0 要求衍生作品也开源" | ❌ 错。那是 GPL。Apache-2.0 允许闭源分发 |
| "改了名字就不算派生了" | ❌ 错。改名不改变派生事实，义务照旧 |
| "只分发 Docker 镜像 / FPK，不发源码，就不用带 LICENSE" | ❌ 错。**二进制形式分发同样需要提供 LICENSE 与归属声明** |
| "上游没有 NOTICE，所以我什么都不用做" | ⚠️ 部分对。NOTICE 义务确实不触发，但 LICENSE 保留、版权保留、修改标注三项义务**照常生效** |
| "保留了 LICENSE 就可以用 QwenPaw 的名字宣传" | ❌ 错。商标权独立于著作权，§6 明确排除 |
| "个人项目不商用就不用管" | ⚠️ 只要**分发**给他人（上架应用中心就是分发），义务即触发 |

---

## 8. 上架飞牛应用中心的合规材料清单

- [ ] `.fpk` 内含 `LICENSE`、`NOTICE`、`CHANGES-FROM-UPSTREAM.md`
- [ ] 应用"关于"页展示：版本号、基于 QwenPaw v2.0.1 (Apache-2.0)、上游仓库链接、许可证全文入口
- [ ] 应用描述中如实标注开源派生关系
- [ ] 应用名称与图标不含上游商标元素
- [ ] 隐私说明：明确 hanbao 是否上报任何数据（遥测移除后应声明"不上报"）

---

## 9. 维护约定

- 本文档随项目长期有效，**每阶段开工前重读 §4 对应检查项**
- 若上游升级基线版本（如 QwenPaw v2.1.x），须同步更新 §1 事实表与 `NOTICE` 中的版本号
- 若引入任何新的第三方依赖，须在合并前核对许可兼容性（禁止 R5 类许可）
