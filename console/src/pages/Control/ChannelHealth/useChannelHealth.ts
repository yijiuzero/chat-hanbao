import { useCallback, useEffect, useState } from "react";
import { App } from "antd";
import { useTranslation } from "react-i18next";
import {
  channelHealthApi,
  type ChannelStatus,
  type ChannelStatusList,
} from "../../../api/modules/channelHealth";

const REFRESH_MS = 15000;

export function useChannelHealth() {
  const { t } = useTranslation();
  const { message: messageApi } = App.useApp();

  const [data, setData] = useState<ChannelStatusList | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const load = useCallback(
    async (refresh = false) => {
      try {
        const res = await channelHealthApi.list(refresh);
        setData(res);
      } catch (error) {
        messageApi.error(
          error instanceof Error
            ? error.message
            : t("channelHealth.loadFailed", "Failed to load channel status"),
        );
      } finally {
        setLoading(false);
      }
    },
    [messageApi, t],
  );

  useEffect(() => {
    void load(false);
  }, [load]);

  useEffect(() => {
    if (!autoRefresh) return;
    let cancelled = false;
    const id = window.setInterval(() => {
      if (!cancelled) void load(true);
    }, REFRESH_MS);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [autoRefresh, load]);

  const reconnect = useCallback(
    async (channel: string) => {
      try {
        await channelHealthApi.reconnect(channel, true);
        messageApi.success(
          t("channelHealth.reconnectStarted", "Reconnect requested"),
        );
        await load(true);
      } catch (error) {
        messageApi.error(
          error instanceof Error
            ? error.message
            : t("channelHealth.reconnectFailed", "Reconnect failed"),
        );
      }
    },
    [load, messageApi, t],
  );

  const channels: ChannelStatus[] = data?.channels ?? [];
  const monitoring = data?.monitoring ?? false;

  return {
    channels,
    monitoring,
    loading,
    autoRefresh,
    setAutoRefresh,
    refresh: () => void load(true),
    reconnect,
  };
}
