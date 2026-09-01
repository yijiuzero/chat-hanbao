import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Alert,
  Button,
  Card,
  Input,
  InputNumber,
  List,
  Space,
  Spin,
  Switch,
  Tabs,
  Tag,
  Typography,
} from "antd";
import { PageHeader } from "@/components/PageHeader";
import { useFnos } from "./useFnos";
import type { FnOSItem, FnOSListResponse } from "../../../api/modules/fnos";
import styles from "./index.module.less";

const { Text } = Typography;

type Draft = {
  enabled: boolean;
  host: string;
  token: string;
  timeout: number;
};

function itemTitle(item: FnOSItem): string {
  const v =
    item.title ?? item.name ?? item.value ?? item.file_name ?? item.filename;
  if (typeof v === "string" || typeof v === "number") return String(v);
  for (const key of Object.keys(item)) {
    const val = item[key];
    if (typeof val === "string" && val) return val;
  }
  return "未命名";
}

function itemSubtitle(item: FnOSItem): string {
  const skip = new Set([
    "title",
    "name",
    "value",
    "file_name",
    "filename",
  ]);
  const parts: string[] = [];
  for (const key of Object.keys(item)) {
    if (skip.has(key)) continue;
    const val = item[key];
    if (typeof val === "string" || typeof val === "number") {
      parts.push(`${key}=${val}`);
    }
    if (parts.length >= 2) break;
  }
  return parts.join("  ·  ");
}

function ResultList({ data }: { data: FnOSListResponse | null }) {
  if (!data) return null;
  if (!data.available) {
    return <Alert type="warning" showIcon message={data.reason || "不可用"} />;
  }
  if (data.items.length === 0) {
    return <Text type="secondary">（空）</Text>;
  }
  return (
    <List
      size="small"
      className={styles.list}
      dataSource={data.items}
      renderItem={(item) => (
        <List.Item>
          <div className={styles.item}>
            <Text strong>{itemTitle(item)}</Text>
            {itemSubtitle(item) && (
              <Text type="secondary" className={styles.subtitle}>
                {itemSubtitle(item)}
              </Text>
            )}
          </div>
        </List.Item>
      )}
    />
  );
}

export default function FnOsPage() {
  const { t } = useTranslation();
  const {
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
  } = useFnos();

  const [draft, setDraft] = useState<Draft | null>(null);

  useEffect(() => {
    if (status && draft === null) {
      setDraft({
        enabled: status.enabled,
        host: status.host,
        token: "",
        timeout: status.timeout,
      });
    }
  }, [status, draft]);

  if (!draft) {
    return (
      <div className={styles.page}>
        <PageHeader
          parent={t("nav.settings")}
          current={t("nav.fnos", "fnOS Integration")}
        />
        <div className={styles.content}>
          <Spin spinning={loading} />
        </div>
      </div>
    );
  }

  const patch = (p: Partial<Draft>) => setDraft((d) => (d ? { ...d, ...p } : d));

  const onSave = () => {
    const body: {
      enabled?: boolean;
      host?: string;
      token?: string;
      timeout?: number;
    } = {
      enabled: draft.enabled,
      host: draft.host,
      timeout: draft.timeout,
    };
    if (draft.token) body.token = draft.token;
    void saveConfig(body);
  };

  return (
    <div className={styles.page}>
      <PageHeader
        parent={t("nav.settings")}
        current={t("nav.fnos", "fnOS Integration")}
      />
      <div className={styles.content}>
        <Alert
          type="info"
          showIcon
          className={styles.tip}
          message={t(
            "fnos.desc",
            "Connect to your local fnOS on the NAS (media library, files, downloads). All calls stay on your device; the token is stored locally and never leaves it.",
          )}
        />

        <Card title={t("fnos.config", "Connection")}>
          <Space direction="vertical" size="middle" style={{ width: "100%" }}>
            <Space wrap>
              <Text strong>{t("fnos.enabled", "Enabled")}</Text>
              <Switch
                checked={draft.enabled}
                onChange={(v) => patch({ enabled: v })}
              />
              <Button onClick={() => void loadStatus()}>
                {t("fnos.test", "Test connection")}
              </Button>
              <Button type="primary" onClick={onSave}>
                {t("common.save")}
              </Button>
            </Space>
            <Space wrap>
              <div className={styles.field}>
                <Text type="secondary">{t("fnos.host", "Host")}</Text>
                <Input
                  value={draft.host}
                  onChange={(e) => patch({ host: e.target.value })}
                  placeholder="http://localhost:5666"
                  style={{ width: 280 }}
                />
              </div>
              <div className={styles.field}>
                <Text type="secondary">{t("fnos.token", "Token")}</Text>
                <Input.Password
                  value={draft.token}
                  onChange={(e) => patch({ token: e.target.value })}
                  placeholder={t("fnos.tokenPlaceholder", "Leave blank to keep")}
                  style={{ width: 240 }}
                />
              </div>
              <div className={styles.field}>
                <Text type="secondary">{t("fnos.timeout", "Timeout (s)")}</Text>
                <InputNumber
                  value={draft.timeout}
                  min={1}
                  max={30}
                  onChange={(v) =>
                    patch({ timeout: typeof v === "number" ? v : draft.timeout })
                  }
                  style={{ width: 100 }}
                />
              </div>
            </Space>
            <Space>
              <Text type="secondary">{t("fnos.state", "State")}:</Text>
              {status?.connected ? (
                <Tag color="green">{t("fnos.connected", "Connected")}</Tag>
              ) : (
                <Tag color="default">
                  {t("fnos.disconnected", "Not connected")}
                </Tag>
              )}
              {status?.connected === false && status.error && (
                <Text type="danger">{status.error}</Text>
              )}
            </Space>
          </Space>
        </Card>

        <Card title={t("fnos.explorer", "Local resources")}>
          <Tabs
            items={[
              {
                key: "media",
                label: t("fnos.media", "Media library"),
                children: (
                  <Space direction="vertical" style={{ width: "100%" }}>
                    <Space>
                      <Input
                        placeholder={t("fnos.mediaSearch", "Search media...")}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onPressEnter={() => void loadMedia(query)}
                        style={{ width: 280 }}
                        allowClear
                      />
                      <Button onClick={() => void loadMedia(query)}>
                        {t("common.search")}
                      </Button>
                    </Space>
                    <ResultList data={media} />
                  </Space>
                ),
              },
              {
                key: "files",
                label: t("fnos.files", "Files"),
                children: (
                  <Space direction="vertical" style={{ width: "100%" }}>
                    <Space>
                      <Input
                        placeholder={t("fnos.filePath", "Path")}
                        value={path}
                        onChange={(e) => setPath(e.target.value)}
                        onPressEnter={() => void loadFiles(path)}
                        style={{ width: 280 }}
                      />
                      <Button onClick={() => void loadFiles(path)}>
                        {t("fnos.browse", "Browse")}
                      </Button>
                    </Space>
                    <ResultList data={files} />
                  </Space>
                ),
              },
              {
                key: "downloads",
                label: t("fnos.downloads", "Downloads"),
                children: (
                  <Space direction="vertical" style={{ width: "100%" }}>
                    <Button onClick={() => void loadDownloads()}>
                      {t("fnos.refreshDownloads", "Load downloads")}
                    </Button>
                    <ResultList data={downloads} />
                  </Space>
                ),
              },
            ]}
          />
        </Card>
      </div>
    </div>
  );
}
