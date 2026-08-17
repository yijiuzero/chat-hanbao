export * from "./types";

export { request } from "./request";

export { getApiUrl, getApiToken } from "./config";

import { rootApi } from "./modules/root";
import { channelApi } from "./modules/channel";
import { cronJobApi } from "./modules/cronjob";
import { chatApi, sessionApi } from "./modules/chat";
import { envApi } from "./modules/env";
import { providerApi } from "./modules/provider";
import { marketApi } from "./modules/market";
import { skillApi } from "./modules/skill";
import { agentApi } from "./modules/agent";
import { agentsApi } from "./modules/agents";
import { workspaceApi } from "./modules/workspace";
import { mcpApi } from "./modules/mcp";
import { tokenUsageApi } from "./modules/tokenUsage";
import { agentStatsApi } from "./modules/agentStats";
import { toolsApi } from "./modules/tools";
import { userTimezoneApi } from "./modules/userTimezone";
import { languageApi } from "./modules/language";
import { consoleApi } from "./modules/console";
import { accessControlApi } from "./modules/accessControl";

export const api = {
  // Root
  ...rootApi,


  // Channels
  ...channelApi,


  // Cron Jobs
  ...cronJobApi,

  // Chats
  ...chatApi,

  // Sessions（Legacy aliases）
  ...sessionApi,

  // Environment Variables
  ...envApi,

  // Providers
  ...providerApi,

  // Agent
  ...agentApi,

  // Skills
  ...skillApi,

  // Skill Market
  ...marketApi,

  // Workspace
  ...workspaceApi,

  // MCP Clients
  ...mcpApi,

  // Token Usage
  ...tokenUsageApi,
  // Agent Statistics
  ...agentStatsApi,
  // Tools
  ...toolsApi,


  // User Timezone
  ...userTimezoneApi,

  // Language
  ...languageApi,


  // Console
  ...consoleApi,

  // Access Control
  ...accessControlApi,
};

export default api;

// Export individual APIs for direct access
export { agentsApi };
