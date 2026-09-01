import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Alert,
  Button,
  Card,
  Collapse,
  Descriptions,
  Empty,
  Input,
  InputNumber,
  List,
  Popconfirm,
  Select,
  Space,
  Spin,
  Switch,
  Tag,
  Typography,
} from "antd";
import dayjs from "dayjs";
import { PageHeader } from "@/components/PageHeader";
import { useKnowledge } from "./useKnowledge";
import type { KnowledgeConfig } from "../../../api/modules/knowledge";
import styles from "./index.module.less";

const { Text, Paragraph } = Typography;

export default function KnowledgePage() {
  const { t } = useTranslation();
  const {
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
  } = useKnowledge();

  const [draft, setDraft] = useState<KnowledgeConfig | null>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    if (config) setDraft(config);
  }, [config]);

  if (!draft) {
    return (
      <div className={styles.page}>
        <PageHeader
          parent={t("nav.settings")}
          current={t("nav.knowledge", "Knowledge Base")}
        />
        <div className={styles.content}>
          <Spin spinning={loading} />
        </div>
      </div>
    );
  }

  const patch = (p: Partial<KnowledgeConfig>) =>
    setDraft((d) => (d ? { ...d, ...p } : d));

  const index = status?.index;

  return (
    <div className={styles.page}>
      <PageHeader
        parent={t("nav.settings")}
        current={t("nav.knowledge", "Knowledge Base")}
      />
      <div className={styles.content}>
        <Alert
          type="info"
          showIcon
          className={styles.tip}
          message={t(
            "knowledge.desc",
            "Index your local family documents, bills and notes. Everything is searched on this device — no file ever leaves the NAS.",
          )}
        />

        {/* Configuration */}
        <Card title={t("knowledge.config", "Configuration")}>
          <Space direction="vertical" size="middle" style={{ width: "100%" }}>
            <Space wrap>
              <Text strong>{t("knowledge.enabled", "Enabled")}</Text>
              <Switch
                checked={draft.enabled}
                onChange={(v) => patch({ enabled: v })}
              />
              <Button
                type="primary"
                onClick={() => void updateConfig(draft)}
              >
                {t("common.save")}
              </Button>
            </Space>
            <div>
              <Text type="secondary">
                {t("knowledge.sourceDirs", "Local directories to index")}
              </Text>
              <Select
                mode="tags"
                style={{ width: "100%", marginTop: 6 }}
                placeholder={t(
                  "knowledge.sourceDirsPlaceholder",
                  "e.g. /volume1/homes/ze/账单, /volume1/家庭相册",
                )}
                value={draft.source_dirs}
                onChange={(v: string[]) => patch({ source_dirs: v })}
                tokenSeparators={[",", "\n"]}
              />
            </div>
            <Space wrap>
              <NumberField
                label={t("knowledge.maxFileMb", "Max file (MB)")}
                value={draft.max_file_mb}
                min={1}
                max={200}
                onChange={(v) => patch({ max_file_mb: v })}
              />
              <NumberField
                label={t("knowledge.chunkSize", "Chunk size")}
                value={draft.chunk_size}
                min={100}
                max={4000}
                onChange={(v) => patch({ chunk_size: v })}
              />
              <NumberField
                label={t("knowledge.chunkOverlap", "Overlap")}
                value={draft.chunk_overlap}
                min={0}
                max={1000}
                onChange={(v) => patch({ chunk_overlap: v })}
              />
              <NumberField
                label={t("knowledge.topK", "Top-K")}
                value={draft.top_k}
                min={1}
                max={50}
                onChange={(v) => patch({ top_k: v })}
              />
              <NumberField
                label={t("knowledge.minScore", "Min score")}
                value={draft.min_score}
                min={0}
                step={0.1}
                onChange={(v) => patch({ min_score: v })}
              />
            </Space>
          </Space>
        </Card>

        {/* Build */}
        <Card title={t("knowledge.indexTitle", "Index")}>
          <Space wrap>
            <Button
              type="primary"
              loading={building}
              disabled={!draft.enabled || draft.source_dirs.length === 0}
              onClick={() => void build(false)}
            >
              {t("knowledge.build", "Build index")}
            </Button>
            <Button
              loading={building}
              disabled={!draft.enabled || draft.source_dirs.length === 0}
              onClick={() => void build(true)}
            >
              {t("knowledge.rebuild", "Rebuild (full)")}
            </Button>
            <Popconfirm
              title={t("knowledge.confirmClear", "Delete the index?")}
              onConfirm={() => void clear()}
            >
              <Button danger>{t("knowledge.clear", "Clear index")}</Button>
            </Popconfirm>
            <Button onClick={() => void refreshStatus()}>
              {t("common.refresh")}
            </Button>
          </Space>
        </Card>

        {/* Status */}
        {index && (
          <Card title={t("knowledge.status", "Status")}>
            <Descriptions column={2} size="small" bordered>
              <Descriptions.Item label={t("knowledge.built", "Built")}>
                {index.built ? (
                  <Tag color="green">{t("common.enabled")}</Tag>
                ) : (
                  <Tag>{t("knowledge.notBuilt", "Not built")}</Tag>
                )}
              </Descriptions.Item>
              <Descriptions.Item label={t("knowledge.files", "Files")}>
                {index.files}
              </Descriptions.Item>
              <Descriptions.Item label={t("knowledge.chunks", "Chunks")}>
                {index.chunks}
              </Descriptions.Item>
              <Descriptions.Item label={t("knowledge.builtAt", "Built at")}>
                {index.built_at
                  ? dayjs(index.built_at * 1000).format("YYYY-MM-DD HH:mm:ss")
                  : "—"}
              </Descriptions.Item>
            </Descriptions>
            {index.by_root && Object.keys(index.by_root).length > 0 && (
              <div className={styles.byRoot}>
                <Text type="secondary">
                  {t("knowledge.byRoot", "Per directory")}:
                </Text>
                {Object.entries(index.by_root).map(([root, count]) => (
                  <Tag key={root} className={styles.rootTag}>
                    {root}: {count}
                  </Tag>
                ))}
              </div>
            )}
          </Card>
        )}

        {/* Search */}
        <Card title={t("knowledge.searchTitle", "Search")}>
          <Space wrap>
            <Input
              placeholder={t("knowledge.searchPlaceholder", "Ask about your files...")}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onPressEnter={() => void search(query)}
              style={{ width: 320 }}
              allowClear
            />
            <Button
              type="primary"
              loading={searching}
              onClick={() => void search(query)}
            >
              {t("common.search")}
            </Button>
          </Space>
          {searchResults.length === 0 && !searching ? (
            <Empty
              className={styles.empty}
              description={t("knowledge.noResults", "No search yet")}
            />
          ) : (
            <List
              className={styles.results}
              loading={searching}
              dataSource={searchResults}
              renderItem={(hit) => (
                <List.Item>
                  <div className={styles.resultItem}>
                    <Space>
                      <Tag color="red">{hit.score}</Tag>
                      <Text code>{hit.path}</Text>
                    </Space>
                    <Paragraph
                      className={styles.resultText}
                      ellipsis={{ rows: 3 }}
                    >
                      {hit.text}
                    </Paragraph>
                  </div>
                </List.Item>
              )}
            />
          )}
        </Card>

        {/* Sources */}
        <Collapse
          className={styles.sources}
          items={[
            {
              key: "sources",
              label: `${t("knowledge.sources", "Indexed files")} (${
                sources.length
              })`,
              children: (
                <List
                  size="small"
                  dataSource={sources}
                  renderItem={(s) => (
                    <List.Item>
                      <Text code className={styles.sourcePath}>
                        {s.path}
                      </Text>
                      <Text type="secondary">· {s.chunks} chunks</Text>
                    </List.Item>
                  )}
                />
              ),
            },
          ]}
        />
      </div>
    </div>
  );
}

function NumberField({
  label,
  value,
  min,
  max,
  step,
  onChange,
}: {
  label: string;
  value: number;
  min?: number;
  max?: number;
  step?: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className={styles.numField}>
      <Text type="secondary">{label}</Text>
      <InputNumber
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(v) => onChange(typeof v === "number" ? v : value)}
        style={{ width: 120 }}
      />
    </div>
  );
}
