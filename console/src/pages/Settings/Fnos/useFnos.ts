import { useCallback, useEffect, useState } from "react";
import { App } from "antd";
import { useTranslation } from "react-i18next";
import {
  fnosApi,
  type FnOSListResponse,
  type FnOSStatus,
} from "../../../api/modules/fnos";

export function useFnos() {
  const { t } = useTranslation();
  const { message: messageApi } = App.useApp();

  const [status, setStatus] = useState<FnOSStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [media, setMedia] = useState<FnOSListResponse | null>(null);
  const [files, setFiles] = useState<FnOSListResponse | null>(null);
  const [downloads, setDownloads] = useState<FnOSListResponse | null>(null);
  const [query, setQuery] = useState("");
  const [path, setPath] = useState("/");

  const loadStatus = useCallback(async () => {
    try {
      const res = await fnosApi.status();
      setStatus(res);
    } catch (error) {
      messageApi.error(
        error instanceof Error
          ? error.message
          : t("fnos.loadFailed", "Failed to load fnOS status"),
      );
    } finally {
      setLoading(false);
    }
  }, [messageApi, t]);

  useEffect(() => {
    void loadStatus();
  }, [loadStatus]);

  const saveConfig = useCallback(
    async (body: {
      enabled?: boolean;
      host?: string;
      token?: string;
      timeout?: number;
    }) => {
      try {
        const res = await fnosApi.updateConfig(body);
        setStatus((s) => (s ? { ...s, ...res } : s));
        await loadStatus();
        messageApi.success(t("fnos.saved", "Saved"));
      } catch (error) {
        messageApi.error(
          error instanceof Error
            ? error.message
            : t("fnos.saveFailed", "Save failed"),
        );
      }
    },
    [loadStatus, messageApi, t],
  );

  const loadMedia = useCallback(
    async (q: string) => {
      try {
        const res = await fnosApi.media(q);
        setMedia(res);
      } catch (error) {
        messageApi.error(
          error instanceof Error
            ? error.message
            : t("fnos.mediaFailed", "Failed to load media"),
        );
      }
    },
    [messageApi, t],
  );

  const loadFiles = useCallback(
    async (p: string) => {
      try {
        const res = await fnosApi.files(p);
        setFiles(res);
      } catch (error) {
        messageApi.error(
          error instanceof Error
            ? error.message
            : t("fnos.filesFailed", "Failed to load files"),
        );
      }
    },
    [messageApi, t],
  );

  const loadDownloads = useCallback(async () => {
    try {
      const res = await fnosApi.downloads();
      setDownloads(res);
    } catch (error) {
      messageApi.error(
        error instanceof Error
          ? error.message
          : t("fnos.downloadsFailed", "Failed to load downloads"),
      );
    }
  }, [messageApi, t]);

  return {
    status,
    loading,
    media,
    files,
    downloads,
    query,
    setQuery,
    path,
    setPath,
    loadStatus,
    saveConfig,
    loadMedia,
    loadFiles,
    loadDownloads,
  };
}
