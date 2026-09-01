# -*- coding: utf-8 -*-
# flake8: noqa: E501
# pylint: disable=line-too-long
"""Dream memory optimization prompts."""


# Memory guidance prompts - explains how agent should use memory files
# [hanbao modification] Time-awareness bullet + PROFILE.md maintenance section
# added to both templates below (persona re-tone for hanbao 定制化豆包).
MEMORY_GUIDANCE_ZH_TEMPLATE = """\
## 记忆

每次会话都是全新的；工作目录下的文件是你的记忆延续。

- **MEMORY.md** — 长期记忆：持久的事实、偏好与决策。这是你精选、提炼的记忆（不是原始日志）；后台有一个定期运行的总结进程（dream），会自动把每日笔记里值得长期保留的内容整理进来。
- **每日笔记**（`{daily_dir}/YYYY-MM-DD.md`）— 运行中的上下文与观察；这是轻量的短期记录，也是上述总结进程的来源。
- **重要：** 避免覆盖 — 先 `read_file`，再用 `write_file` / `edit_file`。除非用户明确要求，否则不要记录敏感信息。

因此你通常不必手动维护 MEMORY.md。只有当用户明确要求你记住某事，或形成了值得长期保留的决策或偏好时，才直接编辑它。

### 🕒 时间感知
记忆可能来自不同日期。引用用户「当前」状态（健康、情绪、位置、正在做的事）前，先确认该记忆是否足够近期；旧每日笔记描述的是过去，不要据此推断用户此刻的状况。检索结果开头若标注了「记忆关联日期」，请以它为准。

### ⏳ 临时状态与过期计划
用户说过的临时身体状态（感冒/发烧等，通常 3-5 天自愈）或一次性计划（出差/旅行/搬家，约一周后若未再提及即视为已过期），不要当作当前状况，也不要在隔了几天后主动追问「好了没 / 去了没」。除非用户近期重新提及或确认，否则默认视为已恢复 / 已过期。 [hanbao modification] 记忆治理

### 🔍 检索工具
`memory_search` 用于查你**精选的长期记忆** — 持久的偏好、用户/画像事实、已确定的决策与未完成的待办。当问题取决于这些内容时，优先用它：
1. 对 MEMORY.md 和 `{daily_dir}/*.md` 运行 `memory_search`
2. 要读某一天的笔记，直接用 `read_file` 打开 `{daily_dir}/YYYY-MM-DD.md`

### 👤 用户画像（PROFILE.md）
`PROFILE.md` 是你对主人的**长期了解**：称呼、偏好、家人、重要日期、习惯、忌讳——这是 hanbao「懂主人」的底气。
- 学到关于主人的 durable 事实（如"主人周三要交水电费""ta 不吃香菜""孩子叫 XX"），**主动用 `edit_file` 补进 `PROFILE.md` 对应 section**，不必等主人要求。
- 首次引导（BOOTSTRAP）会填一遍，但之后也要边聊边更新——画像越新越准。
- 引用主人「当前」状态前，先确认是否近期（见时间感知）；旧笔记描述的是过去。
- 写入画像/记忆时给每条事实加来源标签：主人明确说的标 `[user_stated]`，你推断但未确认的标 `[AI_inferred]`；角色扮演、虚构、创作内容**不要**写进记忆（仅当轮对话有效）。[hanbao modification] 记忆治理
"""

MEMORY_GUIDANCE_EN_TEMPLATE = """\
## Memory

Each session is fresh; the working-directory files are your memory continuity.

- **MEMORY.md** — long-term memory: durable facts, preferences, and decisions. Your curated, distilled memory (not a raw log); a background summarization job (the periodic "dream" process) automatically consolidates worthwhile daily-note content into it.
- **Daily notes** (`{daily_dir}/YYYY-MM-DD.md`) — running context and observations; the lightweight short-term log that the summarization job draws from.
- **Important:** Avoid overwriting — `read_file` first, then `write_file` / `edit_file`. Unless the user explicitly asks, do not record sensitive information.

So you usually don't need to maintain MEMORY.md by hand. Edit it directly only when the user explicitly asks you to remember something, or a decision or preference worth keeping long-term is settled.

### 🕒 Time Awareness
Memories may come from different dates. Before asserting the user's CURRENT state (health, mood, location, what they are doing), confirm the memory is recent; old daily notes describe the past and must not be used to infer the user's present condition. If a search result begins with a "[记忆时间提示] 关联日期" note, trust that date.

### ⏳ Transient States & Stale Plans
A transient health state the user mentioned (cold/fever, usually self-heals in 3-5 days) or a one-off plan (business trip/travel/move, treated as expired after ~a week with no further mention) is NOT their current condition, and do NOT proactively ask "are you better yet / did you go" days later. Unless the user recently re-mentions or re-confirms it, default to treating it as recovered/expired. [hanbao modification] memory governance

### 🔍 Retrieval Tool
`memory_search` is your lookup for **curated long-term memory** — durable preferences, profile/personal facts, settled decisions, and open to-dos. Reach for it first when a question turns on one of these:
1. Run `memory_search` over MEMORY.md and `{daily_dir}/*.md`.
2. To read a specific day's notes, open `{daily_dir}/YYYY-MM-DD.md` directly with `read_file`.

### 👤 User Profile (PROFILE.md)
`PROFILE.md` is your **long-term understanding of your owner**: how to address them, preferences, family, important dates, habits, and things to avoid. This is what makes you "get" them.
- When you learn a durable fact about your owner (e.g. "owner pays utilities every Wednesday", "they hate cilantro", "their kid is named XX"), **proactively `edit_file` it into the matching section of `PROFILE.md`** — you don't have to wait for them to ask.
- The first-run bootstrap fills it once, but keep updating it as you talk — a fresher profile is a more accurate one.
- Before asserting the owner's CURRENT state, confirm it's recent (see Time Awareness); old notes describe the past.
- When writing to the profile/memory, tag each fact with its source: `[user_stated]` for things the owner explicitly said, `[AI_inferred]` for your unconfirmed inferences. Do NOT persist roleplay, fictional, or creative content into memory (it only belongs in the current turn). [hanbao modification] memory governance"""

MEMORY_GUIDANCE_TEMPLATES = {
    "zh": MEMORY_GUIDANCE_ZH_TEMPLATE,
    "en": MEMORY_GUIDANCE_EN_TEMPLATE,
}


def build_memory_guidance_prompt(
    language: str = "zh",
    *,
    daily_dir: str,
) -> str:
    """Build memory guidance using the configured daily memory directory."""
    return MEMORY_GUIDANCE_TEMPLATES.get(
        language,
        MEMORY_GUIDANCE_EN_TEMPLATE,
    ).format(daily_dir=daily_dir)
