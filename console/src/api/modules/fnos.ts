import { request } from "../request";

export interface FnOSStatus {
  enabled: boolean;
  host: string;
  timeout: number;
  token_set: boolean;
  connected: boolean;
  error: string | null;
}

export type FnOSItem = Record<string, unknown>;

export interface FnOSListResponse {
  available: boolean;
  reason?: string;
  items: FnOSItem[];
}

export const fnosApi = {
  status: () => request<FnOSStatus>("/fnos/status"),
  updateConfig: (body: {
    enabled?: boolean;
    host?: string;
    token?: string;
    timeout?: number;
  }) =>
    request<{ enabled: boolean; host: string; timeout: number; token_set: boolean }>(
      "/fnos/config",
      { method: "PUT", body: JSON.stringify(body) },
    ),
  media: (query = "") =>
    request<FnOSListResponse>(
      `/fnos/media${query ? `?query=${encodeURIComponent(query)}` : ""}`,
    ),
  files: (path = "/") =>
    request<FnOSListResponse>(
      `/fnos/files?path=${encodeURIComponent(path)}`,
    ),
  downloads: () => request<FnOSListResponse>("/fnos/downloads"),
};
