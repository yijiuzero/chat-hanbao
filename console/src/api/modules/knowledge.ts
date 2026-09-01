import { request } from "../request";

export interface KnowledgeConfig {
  enabled: boolean;
  source_dirs: string[];
  include_globs: string[];
  exclude_globs: string[];
  max_file_mb: number;
  chunk_size: number;
  chunk_overlap: number;
  top_k: number;
  min_score: number;
}

export interface KnowledgeStatus {
  config: KnowledgeConfig;
  index: {
    built: boolean;
    built_at: number | null;
    files: number;
    chunks: number;
    by_root: Record<string, number>;
    modes: Record<string, number>;
    index_dir: string;
  };
  building: boolean;
  last_build: Record<string, unknown> | null;
}

export interface KnowledgeSearchHit {
  score: number;
  path: string;
  root: string;
  source: string;
  order: number;
  text: string;
}

export interface KnowledgeSource {
  path: string;
  root: string;
  chunks: number;
  size: number;
  mtime: number;
  mode: string;
  source: string;
}

export const knowledgeApi = {
  status: () => request<KnowledgeStatus>("/knowledge/status"),
  getConfig: () => request<KnowledgeConfig>("/knowledge/config"),
  updateConfig: (body: Partial<KnowledgeConfig>) =>
    request<KnowledgeConfig>("/knowledge/config", {
      method: "PUT",
      body: JSON.stringify(body),
    }),
  build: (rebuild = false) =>
    request<Record<string, unknown>>(
      `/knowledge/build${rebuild ? "?rebuild=true" : ""}`,
      { method: "POST" },
    ),
  search: (query: string, top_k?: number) =>
    request<{ query: string; count: number; results: KnowledgeSearchHit[] }>(
      "/knowledge/search",
      { method: "POST", body: JSON.stringify({ query, top_k }) },
    ),
  sources: () =>
    request<{ sources: KnowledgeSource[] }>("/knowledge/sources"),
  clear: () => request<{ ok: boolean }>("/knowledge/index", { method: "DELETE" }),
};
