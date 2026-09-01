import { request } from "../request";

export type MemorySource =
  | "user_stated"
  | "AI_inferred"
  | "AI_creative"
  | "unknown";

export interface MemoryEntry {
  id: string;
  file: string;
  line: number;
  text: string;
  source: MemorySource;
  deprecated: boolean;
  date: string | null;
  transient: boolean;
  /** "deprecated" | "likely-stale" | null */
  hint: string | null;
  editable: boolean;
}

export interface MemoryStats {
  total: number;
  by_source: Record<string, number>;
  files: number;
  deprecated: number;
  stale: number;
  truncated: boolean;
}

export type MemoryEntryListParams = {
  q?: string;
  source?: string;
  file?: string;
  include_deprecated?: boolean;
  limit?: number;
};

function buildQuery(params?: MemoryEntryListParams): string {
  if (!params) return "";
  const usp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") usp.set(k, String(v));
  });
  const s = usp.toString();
  return s ? `?${s}` : "";
}

export const memoryApi = {
  listEntries: (params?: MemoryEntryListParams) =>
    request<{ entries: MemoryEntry[]; count: number }>(
      `/memory-admin/entries${buildQuery(params)}`,
    ),
  stats: () => request<MemoryStats>("/memory-admin/stats"),
  files: () => request<{ files: string[] }>("/memory-admin/files"),
  deleteEntry: (body: { file: string; line: number; text?: string }) =>
    request<{
      ok: boolean;
      action: string;
      file: string;
      line: number;
      previous: string;
      current: string;
    }>("/memory-admin/entries/delete", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  updateEntry: (body: {
    file: string;
    line: number;
    new_text: string;
    text?: string;
    source?: MemorySource;
  }) =>
    request<{
      ok: boolean;
      action: string;
      file: string;
      line: number;
      previous: string;
      current: string;
    }>("/memory-admin/entries/update", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};
