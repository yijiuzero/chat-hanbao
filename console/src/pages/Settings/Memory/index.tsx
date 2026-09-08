import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Alert,
  Button,
  Card,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
} from "antd";
import type { TableColumnsType } from "antd";
import { PageHeader } from "@/components/PageHeader";
import { useMemory } from "./useMemory";
import type { MemoryEntry, MemorySource } from "../../../api/modules/memory";
import styles from "./index.module.less";

const { Text } = Typography;

const SOURCE_COLORS: Record<string, string> = {
  user_stated: "red",
  AI_inferred: "blue",
  AI_creative: "purple",
  unknown: "default",
};

const SOURCE_OPTIONS = [
  { value: "user_stated", label: "user_stated" },
  { value: "AI_inferred", label: "AI_inferred" },
  { value: "AI_creative", label: "AI_creative" },
  { value: "unknown", label: "unknown" },
];

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <Card size="small" className={styles.statCard}>
      <div className={styles.statValue}>{value}</div>
      <div className={styles.statLabel}>{label}</div>
    </Card>
  );
}

function EntryText({ entry }: { entry: MemoryEntry }) {
  return (
    <span>
      {entry.text}
      {entry.deprecated && (
        <Tag color="default" className={styles.inlineTag}>
          已废弃
        </Tag>
      )}
      {entry.hint === "likely-stale" && (
        <Tag color="gold" className={styles.inlineTag}>
          可能过期
        </Tag>
      )}
    </span>
  );
}

export default function MemoryPage() {
  const { t } = useTranslation();
  const {
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
    refresh,
    deleteEntry,
    updateEntry,
    reindex,
    reindexing,
  } = useMemory();

  const [editing, setEditing] = useState<MemoryEntry | null>(null);
  const [editText, setEditText] = useState("");
  const [editSource, setEditSource] = useState<MemorySource | "">("");

  const openEdit = (entry: MemoryEntry) => {
    setEditing(entry);
    setEditText(entry.text);
    setEditSource(entry.source === "unknown" ? "" : entry.source);
  };

  const submitEdit = async () => {
    if (!editing) return;
    try {
      await updateEntry(
        editing.file,
        editing.line,
        editText.trim(),
        editing.text,
        editSource || undefined,
      );
      setEditing(null);
    } catch {
      /* error surfaced by hook */
    }
  };

  const columns: TableColumnsType<MemoryEntry> = [
    {
      title: t("memory.colContent", "Content"),
      dataIndex: "text",
      key: "text",
      render: (_: unknown, entry: MemoryEntry) => <EntryText entry={entry} />,
    },
    {
      title: t("memory.colSource", "Source"),
      dataIndex: "source",
      key: "source",
      width: 150,
      render: (s: string) => (
        <Tag color={SOURCE_COLORS[s] || "default"}>{s}</Tag>
      ),
    },
    {
      title: t("memory.colDate", "Date"),
      dataIndex: "date",
      key: "date",
      width: 120,
      render: (d: string | null) =>
        d ? d : <Text type="secondary">—</Text>,
    },
    {
      title: t("memory.colFile", "File"),
      dataIndex: "file",
      key: "file",
      width: 220,
      ellipsis: true,
      render: (f: string) => (
        <Text type="secondary" className={styles.fileText}>
          {f}
        </Text>
      ),
    },
    {
      title: t("memory.colActions", "Actions"),
      key: "actions",
      width: 150,
      render: (_: unknown, entry: MemoryEntry) => (
        <Space>
          <Button size="small" onClick={() => openEdit(entry)}>
            {t("common.edit")}
          </Button>
          <Popconfirm
            title={t("memory.confirmDelete", "Delete this memory entry?")}
            onConfirm={() => void deleteEntry(entry.file, entry.line, entry.text)}
          >
            <Button size="small" danger>
              {t("common.delete")}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className={styles.page}>
      <PageHeader
        parent={t("nav.settings")}
        current={t("nav.memory", "Memory & Profile")}
      />
      <div className={styles.content}>
        <Alert
          type="info"
          showIcon
          className={styles.tip}
          message={t(
            "memory.desc",
            "Browse what the agent remembers. Entries are tagged by source; correct or remove any fact directly. Changes are audited.",
          )}
        />

        <Space className={styles.toolbar}>
          <Popconfirm
            title={t("memory.reindexConfirm", "确认重建记忆索引？")}
            description={t(
              "memory.reindexWarning",
              "此操作会清空并重建记忆搜索索引，期间 CPU 和内存占用可能升高。仅在索引损坏时执行。",
            )}
            onConfirm={() => void reindex()}
            okText={t("common.confirm", "确认")}
            cancelText={t("common.cancel", "取消")}
          >
            <Button loading={reindexing}>
              {t("memory.reindex", "重建索引")}
            </Button>
          </Popconfirm>
        </Space>

        <Space size="middle" wrap className={styles.stats}>
          <StatCard label={t("memory.statTotal", "Total")} value={stats?.total ?? "—"} />
          <StatCard label="user_stated" value={stats?.by_source?.user_stated ?? 0} />
          <StatCard label="AI_inferred" value={stats?.by_source?.AI_inferred ?? 0} />
          <StatCard label="AI_creative" value={stats?.by_source?.AI_creative ?? 0} />
          <StatCard
            label={t("memory.statDeprecated", "Deprecated")}
            value={stats?.deprecated ?? 0}
          />
          <StatCard
            label={t("memory.statStale", "Likely stale")}
            value={stats?.stale ?? 0}
          />
        </Space>

        <Card>
          <Space wrap>
            <Input
              placeholder={t("memory.searchPlaceholder", "Search memory...")}
              allowClear
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ width: 240 }}
            />
            <Select
              allowClear
              placeholder={t("memory.filterSource", "Filter by source")}
              value={source || undefined}
              onChange={(v) => setSource(v ?? "")}
              style={{ width: 160 }}
              options={SOURCE_OPTIONS}
            />
            <Select
              allowClear
              placeholder={t("memory.filterFile", "Filter by file")}
              value={selectedFile || undefined}
              onChange={(v) => setSelectedFile(v ?? "")}
              style={{ width: 240 }}
              options={files.map((f) => ({ value: f, label: f }))}
            />
            <Space>
              <Text type="secondary">
                {t("memory.includeDeprecated", "Include deprecated")}
              </Text>
              <Switch
                checked={includeDeprecated}
                onChange={setIncludeDeprecated}
              />
            </Space>
            <Button onClick={() => void refresh()}>{t("common.refresh")}</Button>
          </Space>
        </Card>

        <Card title={t("memory.entries", "Entries")}>
          <Table
            rowKey={(e) => e.id}
            loading={loading}
            columns={columns}
            dataSource={entries}
            pagination={{ pageSize: 20, showSizeChanger: true }}
            size="small"
          />
        </Card>
      </div>

      <Modal
        title={t("memory.editTitle", "Edit memory entry")}
        open={editing !== null}
        onCancel={() => setEditing(null)}
        onOk={() => void submitEdit()}
        okText={t("common.save")}
        cancelText={t("common.cancel")}
      >
        {editing && (
          <>
            <Text type="secondary">
              {editing.file}:{editing.line}
            </Text>
            <Input.TextArea
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              rows={4}
              style={{ marginTop: 8 }}
            />
            <div className={styles.editSource}>
              <Text type="secondary">{t("memory.source", "Source")}: </Text>
              <Select
                allowClear
                value={editSource || undefined}
                onChange={(v) => setEditSource((v as MemorySource) ?? "")}
                style={{ width: 160 }}
                options={SOURCE_OPTIONS.filter((o) => o.value !== "unknown")}
              />
            </div>
          </>
        )}
      </Modal>
    </div>
  );
}
