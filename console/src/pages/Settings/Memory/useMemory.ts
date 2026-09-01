import { useCallback, useEffect, useState } from "react";
import { App } from "antd";
import { useTranslation } from "react-i18next";
import {
  memoryApi,
  type MemoryEntry,
  type MemoryStats,
  type MemorySource,
} from "../../../api/modules/memory";

export function useMemory() {
  const { t } = useTranslation();
  const { message: messageApi } = App.useApp();

  const [entries, setEntries] = useState<MemoryEntry[]>([]);
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [files, setFiles] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [source, setSource] = useState<string>("");
  const [includeDeprecated, setIncludeDeprecated] = useState(true);
  const [selectedFile, setSelectedFile] = useState<string>("");

  const loadEntries = useCallback(async () => {
    try {
      const res = await memoryApi.listEntries({
        q: query || undefined,
        source: source || undefined,
        file: selectedFile || undefined,
        include_deprecated: includeDeprecated,
        limit: 500,
      });
      setEntries(res.entries);
    } catch (error) {
      messageApi.error(
        error instanceof Error
          ? error.message
          : t("memory.loadFailed", "Failed to load memory"),
      );
    } finally {
      setLoading(false);
    }
  }, [query, source, selectedFile, includeDeprecated, messageApi, t]);

  const loadStats = useCallback(async () => {
    try {
      const res = await memoryApi.stats();
      setStats(res);
    } catch {
      /* non-fatal */
    }
  }, []);

  const loadFiles = useCallback(async () => {
    try {
      const res = await memoryApi.files();
      setFiles(res.files);
    } catch {
      /* non-fatal */
    }
  }, []);

  useEffect(() => {
    void loadStats();
    void loadFiles();
  }, [loadStats, loadFiles]);

  useEffect(() => {
    void loadEntries();
  }, [loadEntries]);

  const deleteEntry = useCallback(
    async (file: string, line: number, text: string) => {
      try {
        await memoryApi.deleteEntry({ file, line, text });
        messageApi.success(t("memory.deleted", "Entry deleted"));
        await loadEntries();
        await loadStats();
      } catch (error) {
        messageApi.error(
          error instanceof Error
            ? error.message
            : t("memory.deleteFailed", "Delete failed"),
        );
      }
    },
    [loadEntries, loadStats, messageApi, t],
  );

  const updateEntry = useCallback(
    async (
      file: string,
      line: number,
      newText: string,
      text: string,
      src?: MemorySource,
    ) => {
      try {
        await memoryApi.updateEntry({
          file,
          line,
          new_text: newText,
          text,
          source: src,
        });
        messageApi.success(t("memory.updated", "Entry updated"));
        await loadEntries();
      } catch (error) {
        messageApi.error(
          error instanceof Error
            ? error.message
            : t("memory.updateFailed", "Update failed"),
        );
        throw error;
      }
    },
    [loadEntries, messageApi, t],
  );

  return {
    entries,
    stats,
    files,
    loading,
    query,
    setQuery,
    source,
    setSource,
    includeDeprecated,
    setIncludeDeprecated,
    selectedFile,
    setSelectedFile,
    refresh: loadEntries,
    deleteEntry,
    updateEntry,
  };
}
