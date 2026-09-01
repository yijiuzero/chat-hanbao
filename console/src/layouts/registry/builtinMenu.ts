/**
 * builtinMenu.ts — host's built-in sidebar menu entries as data.
 *
 * Importing this module self-registers all builtins into menuRegistry, so the
 * Sidebar's `useMenuItems()` snapshot returns them on first render. Plugins
 * register via `Hanbao.menu.add(...)` which lands in the same registry, so
 * Sidebar treats core + plugin items uniformly.
 *
 * ── Naming convention ──────────────────────────────────────────────────────
 *  Group ids: `core.<name>-group` (e.g. core.control-group)
 *  Item ids:  `core.<key>`        (e.g. core.workspace)
 *  Plugin items use their own prefix (e.g. cloudpaw.a2a) — no clash possible.
 *
 * ── Sticky chat button carve-out ───────────────────────────────────────────
 *  `core.chat` is NOT in this data. The sticky chat button lives outside the
 *  antd <Menu> (rendered next to AgentSelector with bespoke styling); see
 *  Sidebar.tsx. We don't model it as menu data because it has zero antd-Menu
 *  semantics in common with the rest of the sidebar entries.
 *
 * ── Order convention ───────────────────────────────────────────────────────
 *  Within each group, items use order = 10/20/30/… in their natural sequence
 *  so plugins can insert with order 15/25 without colliding.
 */
import {
  SparkAgentLine,
  SparkBarChartLine,
  SparkDataLine,
  SparkDateLine,
  SparkDebugLine,
  SparkEmailLine,
  SparkLocalFileLine,
  SparkMagicWandLine,
  SparkMcpMcpLine,
  SparkModePlazaLine,
  SparkToolLine,
  SparkUserGroupLine,
  SparkWifiLine,
} from "@agentscope-ai/icons";
import i18next from "i18next";
import { menuRegistry } from "../../plugins/registry/store";
import type { MenuItem } from "../../plugins/registry/types";

/** Translate a nav key. Falls back to defaultValue when i18n hasn't loaded. */
const navLabel = (key: string, defaultValue?: string) => (): string =>
  i18next.t(key, defaultValue ?? key);

export const BUILTIN_MENU: MenuItem[] = [
  // ── Agent-scoped (Sidebar Menu #1) ───────────────────────────────────────
  {
    id: "core.inbox",
    location: "primary.agentScoped",
    label: navLabel("nav.inbox"),
    icon: SparkEmailLine,
    route: "core.inbox",
    order: 10,
  },

  // control-group
  {
    id: "core.control-group",
    location: "primary.agentScoped",
    label: navLabel("nav.control"),
    isGroup: true,
    order: 20,
  },
  {
    id: "core.channels",
    location: "primary.agentScoped",
    parentId: "core.control-group",
    label: navLabel("nav.channels"),
    icon: SparkWifiLine,
    route: "core.channels",
    order: 10,
  },
  {
    id: "core.sessions",
    location: "primary.agentScoped",
    parentId: "core.control-group",
    label: navLabel("nav.sessions"),
    icon: SparkUserGroupLine,
    route: "core.sessions",
    order: 20,
  },
  {
    id: "core.cron-jobs",
    location: "primary.agentScoped",
    parentId: "core.control-group",
    label: navLabel("nav.cronJobs"),
    icon: SparkDateLine,
    route: "core.cron-jobs",
    order: 30,
  },
  // [hanbao modification] 2026-09-01: 渠道在线状态/健康页（P0-②）
  {
    id: "core.channel-health",
    location: "primary.agentScoped",
    parentId: "core.control-group",
    label: navLabel("nav.channelHealth", "Channel Health"),
    icon: SparkWifiLine,
    route: "core.channel-health",
    order: 40,
  },
  {

  // agent-group
    id: "core.agent-group",
    location: "primary.agentScoped",
    label: navLabel("nav.agent"),
    isGroup: true,
    order: 30,
  },
  {
    id: "core.workspace",
    location: "primary.agentScoped",
    parentId: "core.agent-group",
    label: navLabel("nav.workspace"),
    icon: SparkLocalFileLine,
    route: "core.workspace",
    order: 10,
  },
  {
    id: "core.skills",
    location: "primary.agentScoped",
    parentId: "core.agent-group",
    label: navLabel("nav.skills"),
    icon: SparkMagicWandLine,
    route: "core.skills",
    order: 20,
  },
  {
    id: "core.tools",
    location: "primary.agentScoped",
    parentId: "core.agent-group",
    label: navLabel("nav.tools"),
    icon: SparkToolLine,
    route: "core.tools",
    order: 30,
  },
  {
    id: "core.mcp",
    location: "primary.agentScoped",
    parentId: "core.agent-group",
    label: navLabel("nav.mcp"),
    icon: SparkMcpMcpLine,
    route: "core.mcp",
    order: 40,
  },
  {
    id: "core.agent-stats",
    location: "primary.agentScoped",
    parentId: "core.agent-group",
    label: navLabel("nav.agentStats"),
    icon: SparkBarChartLine,
    route: "core.agent-stats",
    order: 70,
  },

  // ── Settings (Sidebar Menu #2) ───────────────────────────────────────────
  {
    id: "core.settings-group",
    location: "primary.settings",
    label: navLabel("nav.settings"),
    isGroup: true,
    order: 10,
  },
  {
    id: "core.agents",
    location: "primary.settings",
    parentId: "core.settings-group",
    label: navLabel("nav.agents"),
    icon: SparkAgentLine,
    route: "core.agents",
    order: 10,
  },
  {
    id: "core.models",
    location: "primary.settings",
    parentId: "core.settings-group",
    label: navLabel("nav.models"),
    icon: SparkModePlazaLine,
    route: "core.models",
    order: 20,
  },
  // [hanbao modification] 2026-08-25: 单用户场景移除独立「技能池」导航入口；
  // 技能管理统一收敛到 /skills（Agent 技能）页，底层 SkillPoolService 保留。
  // {
  //   id: "core.skill-pool",
  //   location: "primary.settings",
  //   parentId: "core.settings-group",
  //   label: navLabel("nav.skillPool", "Skill Pool"),
  //   icon: SparkOtherLine,
  //   route: "core.skill-pool",
  //   order: 30,
  // },
  {
    id: "core.token-usage",
    location: "primary.settings",
    parentId: "core.settings-group",
    label: navLabel("nav.tokenUsage"),
    icon: SparkDataLine,
    route: "core.token-usage",
    order: 70,
  },
  {
    id: "core.debug",
    location: "primary.settings",
    parentId: "core.settings-group",
    label: navLabel("nav.debug", "Debug"),
    icon: SparkDebugLine,
    route: "core.debug",
    order: 100,
  },
  // [hanbao modification] 2026-09-01: 记忆档案面板 / 本地知识库 / 飞牛联动（P0-① / P1-③ / P1-④）
  {
    id: "core.memory",
    location: "primary.settings",
    parentId: "core.settings-group",
    label: navLabel("nav.memory", "Memory & Profile"),
    icon: SparkDataLine,
    route: "core.memory",
    order: 40,
  },
  {
    id: "core.knowledge",
    location: "primary.settings",
    parentId: "core.settings-group",
    label: navLabel("nav.knowledge", "Knowledge Base"),
    icon: SparkMagicWandLine,
    route: "core.knowledge",
    order: 50,
  },
  {
    id: "core.fnos",
    location: "primary.settings",
    parentId: "core.settings-group",
    label: navLabel("nav.fnos", "fnOS Integration"),
    icon: SparkLocalFileLine,
    route: "core.fnos",
    order: 60,
  },
];

// Self-register at module load. main.tsx imports this file as a side-effect.
menuRegistry.addBuiltin(BUILTIN_MENU);
