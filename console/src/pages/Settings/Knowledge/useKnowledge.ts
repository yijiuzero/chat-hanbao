import { useCallback, useEffect, useState } from "react";
import { App } from "antd";
import { useTranslation } from "react-i18next";
import {
  knowledgeApi,
  type KnowledgeConfig,
  type KnowledgeSearchHit,
  type KnowledgeSource,
  type KnowledgeStatus,
} from "../../../api/modules/knowledge";

export function useKnowledge() {
  const { t } = useTranslation();
  const { message: messageApi } = App.useApp();

  const [config, setConfig] = useState<KnowledgeConfig | null>(null);
  const [status, setStatus] = useState<KnowledgeStatus | null>(null);
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [building, setBuilding] = useState(false);
  const [searchResults, setSearchResults] = useState<KnowledgeSearchHit[]>([]);
  const [searching, setSearching] = useState(false);

  const refreshStatus = useCallback(async () => {
    try {
      const res = await knowledgeApi.status();
      setStatus(res);
      setConfig(res.config);
    } catch (error) {
      messageApi.error(
        error instanceof Error
          ? error.message
          : t("knowledge.loadFailed", "Failed to load knowledge base"),
      );
    } finally {
      setLoading(false);
    }
  }, [messageApi, t]);

  const loadSources = useCallback(async () => {
    try {
      const res = await knowledgeApi.sources();
      setSources(res.sources);
    } catch {
      /* non-fatal */
    }
  }, []);

  useEffect(() => {
    void refreshStatus();
  }, [refreshStatus]);
  useEffect(() => {
    void loadSources();
  }, [loadSources]);

  const updateConfig = useCallback(
    async (body: Partial<KnowledgeConfig>) => {
      try {
        const res = await knowledgeApi.updateConfig(body);
        setConfig(res);
        messageApi.success(t("knowledge.saved", "Saved"));
      } catch (error) {
        messageApi.error(
          error instanceof Error
            ? error.message
            : t("knowledge.saveFailed", "Save failed"),
        );
      }
    },
    [messageApi, t],
  );

  const build = useCallback(
    async (rebuild: boolean) => {
      setBuilding(true);
      try {
        const res = await knowledgeApi.build(rebuild);
        if (res && res.ok === false) {
          messageApi.warning(
            (res.error as string) || t("knowledge.buildFailed", "Build failed"),
          );
        } else {
          messageApi.success(t("knowledge.buildStarted", "Build started"));
        }
        await refreshStatus();
        await loadSources();
        return res;
      } catch (error) {
        messageApi.error(
          error instanceof Error
            ? error.message
            : t("knowledge.buildFailed", "Build failed"),
        );
      } finally {
        setBuilding(false);
      }
    },
    [messageApi, t, refreshStatus, loadSources],
  );

  const search = useCallback(
    async (query: string, topK?: number) => {
      if (!query.trim()) return;
      setSearching(true);
      try {
        const res = await knowledgeApi.search(query, topK);
        setSearchResults(res.results);
      } catch (error) {
        messageApi.error(
          error instanceof Error
            ? error.message
            : t("knowledge.searchFailed", "Search failed"),
        );
      } finally {
        setSearching(false);
      }
    },
    [messageApi, t],
  );

  const clear = useCallback(async () => {
    try {
      await knowledgeApi.clear();
      messageApi.success(t("knowledge.cleared", "Index cleared"));
      await refreshStatus();
      setSources([]);
      setSearchResults([]);
    } catch (error) {
      messageApi.error(
        error instanceof Error
          ? error.message
          : t("knowledge.clearFailed", "Clear failed"),
      );
    }
  }, [messageApi, t, refreshStatus]);

  return {
    config,
    status,
    sources,
    loading,
    building,
    searchResults,
    searching,
    refreshStatus,
    updateConfig,
    build,
    search,
    clear,
  };
}
