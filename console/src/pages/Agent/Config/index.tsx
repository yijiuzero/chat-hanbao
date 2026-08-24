import { useState, useMemo, useEffect } from "react";
import { Button, Form, Tabs } from "@agentscope-ai/design";
import { useTranslation } from "react-i18next";
import { useSearchParams } from "react-router-dom";
import { useAgentConfig } from "./useAgentConfig.tsx";
import {
  ReactAgentCard,
} from "./components";
import { PageHeader } from "@/components/PageHeader";
import styles from "./index.module.less";

function AgentConfigPage() {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState(
    searchParams.get("tab") || "reactAgent",
  );
  const {
    form,
    loading,
    saving,
    error,
    timezone,
    savingTimezone,
    fetchConfig,
    handleSave,
    handleTimezoneChange,
  } = useAgentConfig();

  const dynamicTabs = useMemo(() => {
    const baseTabs = [
      {
        key: "reactAgent",
        label: (
          <span className={styles.tabLabel}>
            {t("agentConfig.reactAgentTitle")}
          </span>
        ),
        children: (
          <div className={styles.tabContent}>
            <ReactAgentCard
              timezone={timezone}
              savingTimezone={savingTimezone}
              onTimezoneChange={handleTimezoneChange}
            />
          </div>
        ),
      },
    ];

    return baseTabs;
  }, [
    t,
    timezone,
    savingTimezone,
    handleTimezoneChange,
    saving,
  ]);

  useEffect(() => {
    const tabKeys = dynamicTabs.map((t) => t.key);
    if (!tabKeys.includes(activeTab)) {
      setActiveTab(tabKeys[0] ?? "reactAgent");
    }
  }, [dynamicTabs, activeTab]);

  if (loading) {
    return (
      <div className={styles.configPage}>
        <div className={styles.centerState}>
          <span className={styles.stateText}>{t("common.loading")}</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.configPage}>
        <div className={styles.centerState}>
          <span className={styles.stateTextError}>{error}</span>
          <Button size="small" onClick={fetchConfig} style={{ marginTop: 12 }}>
            {t("environments.retry")}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.configPage}>
      <PageHeader parent={t("nav.agent")} current={t("agentConfig.title")} />

      <div className={styles.content}>
        <Form form={form} layout="vertical" className={styles.form}>
          <Tabs
            className={styles.mainTabs}
            activeKey={activeTab}
            onChange={setActiveTab}
            items={dynamicTabs}
            destroyInactiveTabPane={false}
          />
        </Form>
      </div>

      <div className={styles.footerActions}>
        <Button
          onClick={fetchConfig}
          disabled={saving}
          style={{ marginRight: 8 }}
        >
          {t("common.reset")}
        </Button>
        <Button type="primary" onClick={handleSave} loading={saving}>
          {t("common.save")}
        </Button>
      </div>
    </div>
  );
}

export default AgentConfigPage;
