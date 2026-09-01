import { useTranslation } from "react-i18next";
import {
  Alert,
  Button,
  Card,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
  Badge,
} from "antd";
import type { TableColumnsType } from "antd";
import dayjs from "dayjs";
import { PageHeader } from "@/components/PageHeader";
import { useChannelHealth } from "./useChannelHealth";
import type { ChannelStatus } from "../../../api/modules/channelHealth";
import styles from "./index.module.less";

const { Text } = Typography;

function statusColor(status: string): string {
  switch (status) {
    case "healthy":
      return "green";
    case "unhealthy":
    case "error":
    case "disconnected":
      return "red";
    case "reconnecting":
      return "orange";
    default:
      return "default";
  }
}

function fmt(ts: number | null): string {
  if (!ts) return "—";
  return dayjs(ts * 1000).format("YYYY-MM-DD HH:mm:ss");
}

function ChannelStatusBadge({ online }: { online: boolean }) {
  return online ? (
    <Badge status="success" text="online" />
  ) : (
    <Badge status="error" text="offline" />
  );
}

export default function ChannelHealthPage() {
  const { t } = useTranslation();
  const {
    channels,
    monitoring,
    loading,
    autoRefresh,
    setAutoRefresh,
    refresh,
    reconnect,
  } = useChannelHealth();

  const columns: TableColumnsType<ChannelStatus> = [
    {
      title: t("channelHealth.colChannel", "Channel"),
      dataIndex: "channel",
      key: "channel",
      render: (c: string) => <Text strong>{c}</Text>,
    },
    {
      title: t("channelHealth.colStatus", "Status"),
      dataIndex: "status",
      key: "status",
      render: (s: string) => <Tag color={statusColor(s)}>{s}</Tag>,
    },
    {
      title: t("channelHealth.colOnline", "Online"),
      dataIndex: "online",
      key: "online",
      width: 110,
      render: (online: boolean) => <ChannelStatusBadge online={online} />,
    },
    {
      title: t("channelHealth.colLastHeartbeat", "Last heartbeat"),
      dataIndex: "last_ok_at",
      key: "last_ok_at",
      width: 180,
      render: (v: number | null) => <Text type="secondary">{fmt(v)}</Text>,
    },
    {
      title: t("channelHealth.colFailures", "Failures"),
      dataIndex: "consecutive_failures",
      key: "consecutive_failures",
      width: 90,
    },
    {
      title: t("channelHealth.colReconnects", "Reconnects"),
      dataIndex: "reconnect_count",
      key: "reconnect_count",
      width: 100,
    },
    {
      title: t("channelHealth.colError", "Last error"),
      dataIndex: "last_error",
      key: "last_error",
      ellipsis: true,
      render: (e: string | null) =>
        e ? (
          <Text type="danger" className={styles.errorText}>
            {e}
          </Text>
        ) : (
          <Text type="secondary">—</Text>
        ),
    },
    {
      title: t("channelHealth.colActions", "Actions"),
      key: "actions",
      width: 130,
      render: (_: unknown, entry: ChannelStatus) => (
        <Button
          size="small"
          loading={entry.status === "reconnecting"}
          onClick={() => void reconnect(entry.channel)}
        >
          {t("channelHealth.reconnect", "Reconnect")}
        </Button>
      ),
    },
  ];

  return (
    <div className={styles.page}>
      <PageHeader
        parent={t("nav.control")}
        current={t("nav.channelHealth", "Channel Health")}
      />
      <div className={styles.content}>
        <Alert
          type="info"
          showIcon
          className={styles.tip}
          message={t(
            "channelHealth.desc",
            "Live online/offline status for every channel. The monitor actively reconnects dropped channels; you can also force a reconnect here. Token and secrets are never exposed.",
          )}
        />

        <Card>
          <Space wrap>
            <Tag color={monitoring ? "green" : "default"}>
              {monitoring
                ? t("channelHealth.monitoringOn", "Monitor running")
                : t("channelHealth.monitoringOff", "Monitor off")}
            </Tag>
            <Space>
              <Text type="secondary">
                {t("channelHealth.autoRefresh", "Auto refresh")}
              </Text>
              <Switch checked={autoRefresh} onChange={setAutoRefresh} />
            </Space>
            <Button onClick={() => void refresh()}>
              {t("common.refresh")}
            </Button>
          </Space>
        </Card>

        <Card title={t("channelHealth.title", "Channel status")}>
          <Table
            rowKey={(e) => e.channel}
            loading={loading}
            columns={columns}
            dataSource={channels}
            pagination={false}
            size="small"
          />
        </Card>
      </div>
    </div>
  );
}
