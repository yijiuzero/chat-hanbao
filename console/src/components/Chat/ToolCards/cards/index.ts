/**
 * Builtin tool card registry.
 *
 * Each tool name maps to a React component that receives
 * { content: ToolCallContent, isStreaming?: boolean }.
 *
 * The mapping is consumed by:
 *  - ToolCallBlock (ChatV2) via CardRegistry
 *  - ChatV1 via v1Adapter + PluginSystem
 */

// [hanbao modification] AppendFileCard & DelegateExternalAgentCard removed
// (their underlying tools append_file / delegate_external_agent were deleted).
// [hanbao modification] BrowserUseCard & DesktopScreenshotCard removed
// (their underlying tools browser_use / desktop_screenshot were deleted).
import type React from "react";
import type { ToolCallContent } from "../shared/types";

// ── Card imports ──────────────────────────────────────────────────────
export { default as ReadFileCard } from "./ReadFileCard";
export { default as WriteFileCard } from "./WriteFileCard";
export { default as EditFileCard } from "./EditFileCard";
export { default as GrepSearchCard } from "./GrepSearchCard";
export { default as GlobSearchCard } from "./GlobSearchCard";
export { default as ViewImageCard } from "./ViewImageCard";
export { default as ViewVideoCard } from "./ViewVideoCard";
export { default as SendFileCard } from "./SendFileCard";
export { default as GetCurrentTimeCard } from "./GetCurrentTimeCard";
export { default as SetTimezoneCard } from "./SetTimezoneCard";
export { default as TokenUsageCard } from "./TokenUsageCard";
export { default as MemorySearchCard } from "./MemorySearchCard";
export { default as ListAgentsCard } from "./ListAgentsCard";
export { default as ChatWithAgentCard } from "./ChatWithAgentCard";
export { default as SubmitToAgentCard } from "./SubmitToAgentCard";
export { default as CheckAgentTaskCard } from "./CheckAgentTaskCard";
export { default as MaterializeSkillCard } from "./MaterializeSkillCard";
export { default as ShellCard } from "./ShellCard";
export { default as GenericToolCard } from "./GenericToolCard";

// ── Re-import for registry ────────────────────────────────────────────
import ReadFileCard from "./ReadFileCard";
import WriteFileCard from "./WriteFileCard";
import EditFileCard from "./EditFileCard";
import GrepSearchCard from "./GrepSearchCard";
import GlobSearchCard from "./GlobSearchCard";
import ViewImageCard from "./ViewImageCard";
import ViewVideoCard from "./ViewVideoCard";
import SendFileCard from "./SendFileCard";
import GetCurrentTimeCard from "./GetCurrentTimeCard";
import SetTimezoneCard from "./SetTimezoneCard";
import TokenUsageCard from "./TokenUsageCard";
import MemorySearchCard from "./MemorySearchCard";
import ListAgentsCard from "./ListAgentsCard";
import ChatWithAgentCard from "./ChatWithAgentCard";
import SubmitToAgentCard from "./SubmitToAgentCard";
import CheckAgentTaskCard from "./CheckAgentTaskCard";
import MaterializeSkillCard from "./MaterializeSkillCard";
import ShellCard from "./ShellCard";

// ── Common props type ─────────────────────────────────────────────────
export interface BuiltinCardProps {
  content: ToolCallContent;
  isStreaming?: boolean;
}

export type BuiltinCardComponent = React.FC<BuiltinCardProps>;

// ── Tool-name → component registry ───────────────────────────────────

export const BUILTIN_CARD_REGISTRY: Record<string, BuiltinCardComponent> = {
  // File I/O
  read_file: ReadFileCard,
  write_file: WriteFileCard,
  edit_file: EditFileCard,

  // Search
  grep_search: GrepSearchCard,
  glob_search: GlobSearchCard,

  // Media
  view_image: ViewImageCard,
  view_video: ViewVideoCard,
  send_file_to_user: SendFileCard,

  // Time
  get_current_time: GetCurrentTimeCard,
  set_user_timezone: SetTimezoneCard,

  // Token usage
  get_token_usage: TokenUsageCard,

  // Memory
  memory_search: MemorySearchCard,

  // Agent management
  list_agents: ListAgentsCard,
  chat_with_agent: ChatWithAgentCard,
  submit_to_agent: SubmitToAgentCard,
  check_agent_task: CheckAgentTaskCard,

  // Skills
  materialize_skill: MaterializeSkillCard,

  // Shell
  execute_shell_command: ShellCard,
  shell: ShellCard,
  bash: ShellCard,
  terminal: ShellCard,
  run_command: ShellCard,
};
