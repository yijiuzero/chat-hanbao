/**
 * [hanbao modification] Stripped down builtin routes — Coding, Heartbeat,
 * ACP, Environments, Security, VoiceTranscription, AppCenter removed.
 */
import { Suspense } from "react";
import { Navigate } from "react-router-dom";
import { lazyImportWithRetry } from "../../utils/lazyWithRetry";
import { routeRegistry } from "../../plugins/registry/store";
import type { Route } from "../../plugins/registry/types";

// Eager pages
import Chat from "../../pages/Chat";

// Lazy pages
const ChannelsPage = lazyImportWithRetry("../../pages/Control/Channels");
const SessionsPage = lazyImportWithRetry("../../pages/Control/Sessions");
const InboxPage = lazyImportWithRetry("../../pages/Inbox");
const CronJobsPage = lazyImportWithRetry("../../pages/Control/CronJobs");
const AgentConfigPage = lazyImportWithRetry("../../pages/Agent/Config");
const SkillsPage = lazyImportWithRetry("../../pages/Agent/Skills");
const SkillPoolPage = lazyImportWithRetry("../../pages/Settings/SkillPool");
const ToolsPage = lazyImportWithRetry("../../pages/Agent/Tools");
const WorkspacePage = lazyImportWithRetry("../../pages/Agent/Workspace");
const MCPPage = lazyImportWithRetry("../../pages/Agent/MCP");
const ModelsPage = lazyImportWithRetry("../../pages/Settings/Models");
const TokenUsagePage = lazyImportWithRetry("../../pages/Settings/TokenUsage");
const AgentStatsPage = lazyImportWithRetry("../../pages/Settings/AgentStats");
const AgentsPage = lazyImportWithRetry("../../pages/Settings/Agents");
const DebugPage = lazyImportWithRetry("../../pages/Settings/Debug");

// ── Default redirect ────────────────────────────────────────────────

function DefaultRedirect() {
  // [hanbao modification] Coding removed. Always redirect to /chat.
  return <Navigate to="/chat" replace />;
}

// ── Builtin routes ──────────────────────────────────────────────────

export const BUILTIN_ROUTES: Route[] = [
  { id: "core.root", path: "/", component: DefaultRedirect },
  { id: "core.chat", path: "/chat/*", component: Chat },
  { id: "core.channels", path: "/channels", component: ChannelsPage },
  { id: "core.sessions", path: "/sessions", component: SessionsPage },
  { id: "core.inbox", path: "/inbox", component: InboxPage },
  { id: "core.cron-jobs", path: "/cron-jobs", component: CronJobsPage },
  { id: "core.skills", path: "/skills", component: SkillsPage },
  { id: "core.skill-pool", path: "/skill-pool", component: SkillPoolPage },
  { id: "core.tools", path: "/tools", component: ToolsPage },
  { id: "core.mcp", path: "/mcp", component: MCPPage },
  { id: "core.workspace", path: "/workspace", component: WorkspacePage },
  { id: "core.agents", path: "/agents", component: AgentsPage },
  { id: "core.models", path: "/models", component: ModelsPage },
  {
    id: "core.agent-config",
    path: "/agent-config",
    component: AgentConfigPage,
  },
  { id: "core.token-usage", path: "/token-usage", component: TokenUsagePage },
  { id: "core.agent-stats", path: "/agent-stats", component: AgentStatsPage },
  { id: "core.debug", path: "/debug", component: DebugPage },
];

routeRegistry.addBuiltin(BUILTIN_ROUTES);

// Suspense imported above is used by lazyImportWithRetry consumers; ref keeps
// TS from tree-shaking the import in older bundler configs.
void Suspense;
