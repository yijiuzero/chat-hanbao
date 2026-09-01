import { request } from "../request";

export interface ChannelStatus {
  channel: string;
  status: string;
  online: boolean;
  enabled: boolean;
  detail: string;
  last_check_at: number | null;
  last_ok_at: number | null;
  last_error: string | null;
  consecutive_failures: number;
  reconnect_count: number;
  last_reconnect_at: number | null;
  next_retry_at: number | null;
  last_reconnect_error: string | null;
}

export interface ChannelStatusList {
  agent_id: string;
  monitoring: boolean;
  channels: ChannelStatus[];
}

export const channelHealthApi = {
  list: (refresh = false) =>
    request<ChannelStatusList>(
      `/channels-status${refresh ? "?refresh=true" : ""}`,
    ),
  reconnect: (channel: string, force = true) =>
    request<Record<string, unknown>>(
      `/channels-status/${encodeURIComponent(channel)}/reconnect?force=${force}`,
      { method: "POST" },
    ),
};
