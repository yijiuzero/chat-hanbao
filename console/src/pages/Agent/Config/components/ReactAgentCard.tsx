import { Form, Select, Card } from "@agentscope-ai/design";
import { useTranslation } from "react-i18next";
import { useTimezoneOptions } from "../../../../hooks/useTimezoneOptions";
import styles from "../index.module.less";

// [hanbao modification] Simplified reactAgent tab: only the user timezone is
// exposed. All other fields keep their existing defaults and are no longer
// shown in the UI (per "运行配置" simplification request). Preserved on save
// via the `...original` fallback in useAgentConfig.handleSave.
interface ReactAgentCardProps {
  timezone: string;
  savingTimezone: boolean;
  onTimezoneChange: (value: string) => void;
}

export function ReactAgentCard({
  timezone,
  savingTimezone,
  onTimezoneChange,
}: ReactAgentCardProps) {
  const { t } = useTranslation();

  return (
    <Card className={styles.formCard} title={t("agentConfig.reactAgentTitle")}>
      <Form.Item
        label={t("agentConfig.timezone")}
        tooltip={t("agentConfig.timezoneTooltip")}
      >
        <Select
          showSearch
          value={timezone}
          placeholder={t("agentConfig.selectTimezone")}
          filterOption={(input, option) =>
            (option?.label?.toString() || "")
              .toLowerCase()
              .includes(input.toLowerCase())
          }
          options={useTimezoneOptions()}
          onChange={onTimezoneChange}
          loading={savingTimezone}
          disabled={savingTimezone}
          style={{ width: "100%" }}
        />
      </Form.Item>
    </Card>
  );
}
