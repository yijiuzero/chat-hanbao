import {
  Drawer,
  Form,
  Input,
  InputNumber,
  Switch,
  Button,
  Select,
} from "@agentscope-ai/design";
import { useAppMessage } from "../../../../hooks/useAppMessage";
import { Alert, ConfigProvider } from "antd";
import { useTranslation } from "react-i18next";
import type { FormInstance } from "antd";
import { getChannelLabel, type ChannelKey } from "./constants";
import { QrcodeAuthBlock } from "./QrcodeAuthBlock";
import type { ChannelSchema } from "../../../../api/modules/channel";
import styles from "../index.module.less";
import { useAgentStore } from "../../../../stores/agentStore";

// [hanbao modification] removed discord/telegram/mattermost/matrix/onebot/
// mqtt/yuanbao/slack from access-control list
const CHANNELS_WITH_ACCESS_CONTROL: ChannelKey[] = [
  "dingtalk",
  "feishu",
  "wecom",
  "wechat",
  "imessage",
  "qq",
  "xiaoyi",
];

const BASE_FIELDS = [
  "enabled",
  "bot_prefix",
  "show_tool_calls",
  "show_tool_results",
  "tool_call_max_length",
  "tool_result_max_length",
  "show_thinking",
  "isBuiltin",
];

// Resolve a plugin-provided localized text (a plain string or a
// locale->string dict) against the given UI language, with graceful
// fallback so a missing locale never renders blank. Long codes ("zh-CN")
// and short codes ("zh") are matched on either side via prefix matching.
// Priority: exact locale -> short code -> prefix match (short<->long) ->
// English -> Chinese -> first non-empty value.
function resolveLocalized(value: unknown, lang: string): string {
  if (value == null) return "";
  if (typeof value === "string") return value;
  if (typeof value !== "object") return String(value);

  const dict = value as Record<string, string>;
  const locale = lang || "en";
  const short = locale.split("-")[0].toLowerCase();
  // Prefix match so UI short code "zh" hits dict long key "zh-CN"
  // (and vice versa), regardless of which style the plugin used.
  const prefixKey = Object.keys(dict).find(
    (k) => k.split("-")[0].toLowerCase() === short && !!dict[k],
  );

  const exactMatch = dict[locale];
  const shortMatch = dict[short];
  const prefixMatch = prefixKey ? dict[prefixKey] : undefined;
  const englishFallback = dict["en-US"] || dict["en"];
  const chineseFallback = dict["zh-CN"] || dict["zh"];
  const anyNonEmpty = Object.values(dict).find((v) => !!v);

  return (
    exactMatch ||
    shortMatch ||
    prefixMatch ||
    englishFallback ||
    chineseFallback ||
    anyNonEmpty ||
    ""
  );
}

interface ChannelDrawerProps {
  open: boolean;
  activeKey: ChannelKey | null;
  activeLabel: string;
  form: FormInstance<Record<string, unknown>>;
  saving: boolean;
  initialValues: Record<string, unknown> | undefined;
  isBuiltin: boolean;
  channelSchema?: ChannelSchema;
  onClose: () => void;
  onSubmit: (values: Record<string, unknown>) => void;
}

export function ChannelDrawer({
  open,
  activeKey,
  activeLabel,
  form,
  saving,
  initialValues,
  isBuiltin,
  channelSchema,
  onClose,
  onSubmit,
}: ChannelDrawerProps) {
  const { t, i18n } = useTranslation();
  const { selectedAgent, agents } = useAgentStore();
  const currentAgent = agents.find((a) => a.id === selectedAgent);
  const defaultMediaDir = currentAgent?.workspace_dir
    ? `${currentAgent.workspace_dir}/media`
    : "~/.hanbao/media";
  const label = activeKey ? getChannelLabel(activeKey, t) : activeLabel;
  const { message } = useAppMessage();
  const feishuDomain = (Form.useWatch("domain", form) as string) || "feishu";
  const showToolCalls = Form.useWatch("show_tool_calls", form) ?? true;
  const showToolResults = Form.useWatch("show_tool_results", form) ?? true;


  // ── Access control fields (shared across multiple channels) ──────────────

  const renderAccessControlFields = () => (
    <>
      <Form.Item
        name="access_control_dm"
        label={t("channels.accessControlDm")}
        valuePropName="checked"
        tooltip={t("channels.accessControlDmTooltip")}
      >
        <Switch />
      </Form.Item>
      <Form.Item
        name="access_control_group"
        label={t("channels.accessControlGroup")}
        valuePropName="checked"
        tooltip={t("channels.accessControlGroupTooltip")}
      >
        <Switch />
      </Form.Item>
      <Form.Item
        name="require_mention"
        label={t("channels.requireMention")}
        valuePropName="checked"
        tooltip={t("channels.requireMentionTooltip")}
      >
        <Switch />
      </Form.Item>
    </>
  );

  // ── Builtin channel-specific fields ─────────────────────────────────────

  const renderBuiltinExtraFields = (key: ChannelKey) => {
    switch (key) {

      case "imessage":
        return (
          <>
            <Form.Item
              name="db_path"
              label="DB Path"
              rules={[{ required: true, message: "Please input DB path" }]}
            >
              <Input placeholder="~/Library/Messages/chat.db" />
            </Form.Item>
            <Form.Item
              name="poll_sec"
              label="Poll Interval (sec)"
              rules={[
                { required: true, message: "Please input poll interval" },
              ]}
            >
              <InputNumber min={0.1} step={0.1} style={{ width: "100%" }} />
            </Form.Item>
          </>
        );


      case "dingtalk":
        return (
          <>
            <ConfigProvider prefixCls="ant">
              <Alert
                type="info"
                showIcon
                message={t("channels.dingtalkSetupGuide")}
                style={{ marginBottom: 16 }}
              />
            </ConfigProvider>
            <QrcodeAuthBlock
              label={t("channels.dingtalkScanAuth")}
              buttonText={t("channels.dingtalkGetQrcode")}
              imageAlt="DingTalk QR Code"
              hintText={t("channels.dingtalkScanHint")}
              channel="dingtalk"
              successStatus="success"
              successCredentialKey="client_id"
              pollInterval={5000}
              onSuccess={(credentials) => {
                form.setFieldsValue({
                  client_id: credentials.client_id,
                  client_secret: credentials.client_secret,
                });
                message.success(t("channels.dingtalkAuthSuccess"));
              }}
              onError={(type) => {
                if (type === "expired") {
                  message.warning(t("channels.dingtalkQrcodeExpired"));
                } else {
                  message.error(t("channels.dingtalkQrcodeFailed"));
                }
              }}
            />
            <Form.Item
              name="client_id"
              label="Client ID"
              rules={[{ required: true }]}
            >
              <Input placeholder="dingxxxxx" />
            </Form.Item>
            <Form.Item
              name="client_secret"
              label="Client Secret"
              rules={[{ required: true }]}
            >
              <Input.Password />
            </Form.Item>
            <Form.Item
              name="message_type"
              label="Message Type"
              tooltip="markdown: regular messages; card: AI interactive card"
            >
              <Select
                options={[
                  { label: "markdown", value: "markdown" },
                  { label: "card", value: "card" },
                ]}
              />
            </Form.Item>
            <Form.Item
              name="cron_message_type"
              label="Cron Message Type"
              tooltip="Message type for cron/scheduled task sends. Independent from the chat message type above."
            >
              <Select
                options={[
                  { label: "markdown", value: "markdown" },
                  { label: "card", value: "card" },
                ]}
              />
            </Form.Item>
            <Form.Item
              noStyle
              shouldUpdate={(prev, cur) =>
                prev.message_type !== cur.message_type ||
                prev.cron_message_type !== cur.cron_message_type
              }
            >
              {({ getFieldValue }) => {
                const needsCard =
                  getFieldValue("message_type") === "card" ||
                  getFieldValue("cron_message_type") === "card";
                if (!needsCard) return null;
                return (
                  <>
                    <Form.Item
                      name="card_template_id"
                      label="Card Template ID"
                      rules={[
                        {
                          required: true,
                          message:
                            "Please input card template id when message_type=card",
                        },
                      ]}
                    >
                      <Input placeholder="dt_card_template_xxx" />
                    </Form.Item>
                    <Form.Item
                      name="card_template_key"
                      label="Card Template Key"
                      tooltip="Must exactly match the template variable name"
                    >
                      <Input placeholder="content" />
                    </Form.Item>
                    <Form.Item
                      name="robot_code"
                      label="Robot Code"
                      tooltip="Recommended to configure explicitly for group chats"
                    >
                      <Input placeholder="robot code (default client_id)" />
                    </Form.Item>
                  </>
                );
              }}
            </Form.Item>
            <Form.Item
              name="endpoint"
              label={t("channels.dingtalkEndpoint")}
              tooltip={t("channels.dingtalkEndpointTooltip")}
            >
              <Input placeholder="https://api.dingtalk.com" />
            </Form.Item>
            <Form.Item
              name="at_sender_on_reply"
              label={t("channels.atSenderOnReply")}
              tooltip={t("channels.atSenderOnReplyTooltip")}
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>
          </>
        );

      case "feishu":
        return (
          <>
            <Form.Item
              name="domain"
              label={t("channels.feishuRegion")}
              initialValue="feishu"
              tooltip={t("channels.feishuRegionTooltip")}
            >
              <Select>
                <Select.Option value="feishu">
                  {t("channels.feishuChina")}
                </Select.Option>
                <Select.Option value="lark">
                  {t("channels.feishuInternational")}
                </Select.Option>
              </Select>
            </Form.Item>
            <ConfigProvider prefixCls="ant">
              <Alert
                type="info"
                showIcon
                message={t("channels.feishuScanGuide")}
                style={{ marginBottom: 16 }}
              />
            </ConfigProvider>
            <QrcodeAuthBlock
              label={t("channels.feishuScanLogin")}
              buttonText={t("channels.feishuGetQrcode")}
              imageAlt="Feishu QR Code"
              hintText={t("channels.feishuScanHint")}
              channel="feishu"
              successStatus="success"
              successCredentialKey="app_id"
              pollInterval={2000}
              params={{ domain: feishuDomain }}
              onSuccess={(credentials) => {
                form.setFieldsValue({
                  app_id: credentials.app_id,
                  app_secret: credentials.app_secret,
                });
                message.success(t("channels.feishuAuthSuccess"));
              }}
              onError={(type) => {
                if (type === "expired") {
                  message.warning(t("channels.feishuQrcodeExpired"));
                } else {
                  message.error(t("channels.feishuQrcodeFailed"));
                }
              }}
            />
            <Form.Item
              name="app_id"
              label="App ID"
              rules={[{ required: true }]}
            >
              <Input placeholder="cli_xxx" />
            </Form.Item>
            <Form.Item
              name="app_secret"
              label="App Secret"
              rules={[{ required: true }]}
            >
              <Input.Password placeholder="App Secret" />
            </Form.Item>
            <Form.Item name="encrypt_key" label="Encrypt Key">
              <Input placeholder="Optional, for event encryption" />
            </Form.Item>
            <Form.Item name="verification_token" label="Verification Token">
              <Input placeholder="Optional" />
            </Form.Item>
            <Form.Item name="media_dir" label={t("channels.wechatMediaDir")}>
              <Input placeholder={defaultMediaDir} />
            </Form.Item>
            <Form.Item
              name="share_session_in_group"
              label={t("channels.shareSessionInGroup")}
              valuePropName="checked"
              tooltip={t("channels.shareSessionInGroupTooltip")}
            >
              <Switch />
            </Form.Item>
          </>
        );

      case "qq":
        return (
          <>
            <ConfigProvider prefixCls="ant">
              <Alert
                type="info"
                showIcon
                message={t("channels.qqSetupGuide")}
                style={{ marginBottom: 16 }}
              />
            </ConfigProvider>
            <QrcodeAuthBlock
              label={t("channels.qqScanAuth")}
              buttonText={t("channels.qqGetQrcode")}
              imageAlt="QQ QR Code"
              hintText={t("channels.qqScanHint")}
              channel="qq"
              successStatus="success"
              successCredentialKey="app_id"
              pollInterval={2000}
              pollTimeout={300000}
              maxPollCount={180}
              onSuccess={(credentials) => {
                form.setFieldsValue({
                  app_id: credentials.app_id,
                  client_secret: credentials.client_secret,
                  user_openid: credentials.user_openid,
                });
                message.success(t("channels.qqAuthSuccess"));
              }}
              onError={(type) => {
                if (type === "expired") {
                  message.warning(t("channels.qqQrcodeExpired"));
                } else {
                  message.error(t("channels.qqQrcodeFailed"));
                }
              }}
            />
            <Form.Item
              name="app_id"
              label="App ID"
              rules={[{ required: true }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="client_secret"
              label="Client Secret"
              rules={[{ required: true }]}
            >
              <Input.Password />
            </Form.Item>
            <Form.Item name="user_openid" hidden>
              <Input />
            </Form.Item>
            <Form.Item
              name="ack_message"
              label={t("channels.ackMessage")}
              tooltip={t("channels.ackMessageTooltip")}
            >
              <Input placeholder={t("channels.ackMessagePlaceholder")} />
            </Form.Item>
          </>
        );


      case "wecom":
        return (
          <>
            <ConfigProvider prefixCls="ant">
              <Alert
                type="warning"
                showIcon
                message={t("channels.wecomSetupGuide")}
                style={{ marginBottom: 16 }}
              />
            </ConfigProvider>
            <QrcodeAuthBlock
              label={t("channels.wecomScanAuth")}
              buttonText={t("channels.loginWeCom")}
              imageAlt="WeCom QR Code"
              hintText={t("channels.wecomAuthHint")}
              channel="wecom"
              successStatus="success"
              successCredentialKey="bot_id"
              pollInterval={3000}
              onSuccess={(credentials) => {
                form.setFieldsValue({
                  bot_id: credentials.bot_id,
                  secret: credentials.secret,
                });
                message.success(t("channels.wecomAuthSuccess"));
              }}
              onError={() => {
                message.error(t("channels.wecomQrcodeFailed"));
              }}
            />
            <Form.Item
              name="bot_id"
              label="Bot ID"
              rules={[{ required: true, message: "Please input Bot ID" }]}
            >
              <Input placeholder="Bot ID from WeCom backend" />
            </Form.Item>
            <Form.Item
              name="secret"
              label="Secret"
              rules={[{ required: true, message: "Please input Secret" }]}
            >
              <Input.Password placeholder="Secret from WeCom backend" />
            </Form.Item>
            <Form.Item name="media_dir" label={t("channels.wechatMediaDir")}>
              <Input placeholder={defaultMediaDir} />
            </Form.Item>
            <Form.Item
              name="welcome_text"
              label={t("channels.welcomeText")}
              tooltip={t("channels.welcomeTextTooltip")}
            >
              <Input placeholder={t("channels.welcomeTextPlaceholder")} />
            </Form.Item>
            <Form.Item
              name="share_session_in_group"
              label={t("channels.shareSessionInGroup")}
              valuePropName="checked"
              tooltip={t("channels.shareSessionInGroupTooltip")}
            >
              <Switch />
            </Form.Item>
          </>
        );

      case "xiaoyi":
        return (
          <>
            <ConfigProvider prefixCls="ant">
              <Alert
                type="info"
                showIcon
                message={t("channels.xiaoyiSetupGuide")}
                style={{ marginBottom: 16 }}
              />
            </ConfigProvider>
            <Form.Item
              name="ak"
              label="Access Key (AK)"
              rules={[{ required: true, message: "Please input Access Key" }]}
            >
              <Input placeholder="Access Key from Huawei Developer Platform" />
            </Form.Item>
            <Form.Item
              name="sk"
              label="Secret Key (SK)"
              rules={[{ required: true, message: "Please input Secret Key" }]}
            >
              <Input.Password placeholder="Secret Key from Huawei Developer Platform" />
            </Form.Item>
            <Form.Item
              name="agent_id"
              label="Agent ID"
              rules={[{ required: true, message: "Please input Agent ID" }]}
            >
              <Input placeholder="Agent ID from XiaoYi platform" />
            </Form.Item>
          </>
        );

      case "wechat":
        return (
          <>
            <ConfigProvider prefixCls="ant">
              <Alert
                type="info"
                showIcon
                message={t("channels.wechatSetupGuide")}
                style={{ marginBottom: 16 }}
              />
              <Alert
                type="warning"
                showIcon
                message={t("channels.wechatContextTokenLimit")}
                style={{ marginBottom: 16 }}
              />
            </ConfigProvider>
            <QrcodeAuthBlock
              label={t("channels.wechatScanLogin")}
              buttonText={t("channels.wechatGetQrcode")}
              imageAlt="WeChat QR Code"
              hintText={t("channels.wechatScanHint")}
              channel="wechat"
              successStatus="confirmed"
              successCredentialKey="bot_token"
              pollInterval={2000}
              onSuccess={(credentials) => {
                form.setFieldsValue({ bot_token: credentials.bot_token });
                message.success(t("channels.wechatLoginSuccess"));
              }}
              onError={(type) => {
                if (type === "expired") {
                  message.warning(t("channels.wechatQrcodeExpired"));
                } else {
                  message.error(t("channels.wechatQrcodeFailed"));
                }
              }}
            />
            <Form.Item
              name="bot_token"
              label={t("channels.wechatBotToken")}
              tooltip={t("channels.wechatBotTokenTooltip")}
            >
              <Input.Password
                placeholder={t("channels.wechatBotTokenPlaceholder")}
              />
            </Form.Item>
            <Form.Item
              name="bot_token_file"
              label={t("channels.wechatBotTokenFile")}
              tooltip={t("channels.wechatBotTokenFileTooltip")}
            >
              <Input placeholder="~/.hanbao/wechat_bot_token" />
            </Form.Item>
            <Form.Item name="media_dir" label={t("channels.wechatMediaDir")}>
              <Input placeholder={defaultMediaDir} />
            </Form.Item>
            <Form.Item
              name="message_merge_enabled"
              label={t("channels.wechatMessageMerge")}
              valuePropName="checked"
              tooltip={t("channels.wechatMessageMergeTooltip")}
            >
              <Switch />
            </Form.Item>
            <Form.Item
              noStyle
              shouldUpdate={(prev, cur) =>
                prev.message_merge_enabled !== cur.message_merge_enabled
              }
            >
              {({ getFieldValue }) =>
                getFieldValue("message_merge_enabled") ? (
                  <Form.Item
                    name="message_merge_delay_ms"
                    label={t("channels.wechatMessageMergeDelayMs")}
                    tooltip={t("channels.wechatMessageMergeDelayMsTooltip")}
                    initialValue={0}
                    rules={[
                      {
                        validator: (_: unknown, value: unknown) => {
                          if (
                            value === null ||
                            value === undefined ||
                            value === ""
                          ) {
                            return Promise.resolve();
                          }
                          const num = Number(value);
                          if (!Number.isInteger(num) || num < 0) {
                            return Promise.reject(
                              new Error(
                                t(
                                  "channels.wechatMessageMergeDelayMsValidation",
                                ),
                              ),
                            );
                          }
                          return Promise.resolve();
                        },
                      },
                    ]}
                  >
                    <InputNumber
                      min={0}
                      step={100}
                      style={{ width: "100%" }}
                      placeholder="0"
                    />
                  </Form.Item>
                ) : null
              }
            </Form.Item>
          </>
        );


      default:
        return null;
    }
  };

  // ── Custom channel fields (key-value editor) ─────────────────────────────

  const renderCustomExtraFields = (
    values: Record<string, unknown> | undefined,
  ) => {
    // If we have a schema from the plugin system, render based on it
    if (channelSchema && channelSchema.config_fields.length > 0) {
      return (
        <>
          {channelSchema.description && (
            <div className={styles.schemaDescription}>
              {channelSchema.description}
            </div>
          )}
          {channelSchema.config_fields.map((field) => {
            const fieldLabel = resolveLocalized(field.label, i18n.language);
            const fieldHelp =
              resolveLocalized(field.help, i18n.language) || undefined;
            const fieldPlaceholder = resolveLocalized(
              field.placeholder,
              i18n.language,
            );
            const rules = field.required
              ? [{ required: true, message: `Please enter ${fieldLabel}` }]
              : undefined;

            switch (field.type) {
              case "password":
                return (
                  <Form.Item
                    key={field.name}
                    name={field.name}
                    label={fieldLabel}
                    rules={rules}
                    tooltip={fieldHelp}
                    initialValue={field.default}
                  >
                    <Input.Password placeholder={fieldPlaceholder} />
                  </Form.Item>
                );
              case "number":
                return (
                  <Form.Item
                    key={field.name}
                    name={field.name}
                    label={fieldLabel}
                    rules={rules}
                    tooltip={fieldHelp}
                    initialValue={field.default}
                  >
                    <InputNumber
                      style={{ width: "100%" }}
                      placeholder={fieldPlaceholder}
                    />
                  </Form.Item>
                );
              case "switch":
                return (
                  <Form.Item
                    key={field.name}
                    name={field.name}
                    label={fieldLabel}
                    valuePropName="checked"
                    tooltip={fieldHelp}
                    initialValue={field.default}
                  >
                    <Switch />
                  </Form.Item>
                );
              case "select":
                return (
                  <Form.Item
                    key={field.name}
                    name={field.name}
                    label={fieldLabel}
                    rules={rules}
                    tooltip={fieldHelp}
                    initialValue={field.default}
                  >
                    <Select
                      placeholder={fieldPlaceholder}
                      options={(field.options || []).map((opt) => ({
                        label: opt,
                        value: opt,
                      }))}
                    />
                  </Form.Item>
                );
              default:
                return (
                  <Form.Item
                    key={field.name}
                    name={field.name}
                    label={fieldLabel}
                    rules={rules}
                    tooltip={fieldHelp}
                    initialValue={field.default}
                  >
                    <Input placeholder={fieldPlaceholder} />
                  </Form.Item>
                );
            }
          })}
        </>
      );
    }

    // Fallback: infer field types from existing values (legacy behavior)
    if (!values) return null;
    const extraKeys = Object.keys(values).filter(
      (k) => !BASE_FIELDS.includes(k),
    );
    if (extraKeys.length === 0) return null;

    return (
      <>
        <div style={{ marginBottom: 8, fontWeight: 500 }}>Custom Fields</div>
        {extraKeys.map((fieldKey) => {
          const value = values[fieldKey];
          return (
            <Form.Item key={fieldKey} name={fieldKey} label={fieldKey}>
              {typeof value === "boolean" ? (
                <Switch />
              ) : typeof value === "number" ? (
                <InputNumber style={{ width: "100%" }} />
              ) : (
                <Input />
              )}
            </Form.Item>
          );
        })}
      </>
    );
  };

  // ── Drawer title ─────────────────────────────────────────────────────────
  // [hanbao modification] removed the per-channel "Doc" buttons (built-in doc
  // URLs, plugin schema.doc_url, and the voice/Twilio link) that jumped to
  // upstream QwenPaw doc pages.

  const drawerTitle = (
    <div className={styles.drawerTitle}>
      <span>
        {label
          ? `${label} ${t("channels.settings")}`
          : t("channels.channelSettings")}
      </span>
    </div>
  );

  // ── Render ───────────────────────────────────────────────────────────────

  const drawerFooter = (
    <div className={styles.formActions}>
      <Button onClick={onClose}>{t("common.cancel")}</Button>
      <Button type="primary" loading={saving} onClick={() => form.submit()}>
        {t("common.save")}
      </Button>
    </div>
  );

  return (
    <Drawer
      width={420}
      placement="right"
      title={drawerTitle}
      open={open}
      onClose={onClose}
      destroyOnHidden
      footer={drawerFooter}
      key={activeKey} // Force remount when switching channels
    >
      {activeKey && (
        <Form
          form={form}
          layout="vertical"
          initialValues={initialValues}
          onFinish={(values) => onSubmit(values)}
        >
          <Form.Item
            name="enabled"
            label={t("common.enabled")}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          {activeKey !== "voice" && (
            <Form.Item name="bot_prefix" label="Bot Prefix">
              <Input placeholder="@bot" />
            </Form.Item>
          )}

          <>
            <Form.Item
              name="show_tool_calls"
              label={t("channels.showToolCalls")}
              valuePropName="checked"
              tooltip={t("channels.showToolCallsTooltip")}
            >
              <Switch />
            </Form.Item>
            {showToolCalls && (
              <Form.Item
                name="tool_call_max_length"
                label={t("channels.toolCallMaxLength")}
                tooltip={t("channels.toolMaxLengthTooltip")}
              >
                <InputNumber min={0} style={{ width: "100%" }} />
              </Form.Item>
            )}
            <Form.Item
              name="show_tool_results"
              label={t("channels.showToolResults")}
              valuePropName="checked"
              tooltip={t("channels.showToolResultsTooltip")}
            >
              <Switch />
            </Form.Item>
            {showToolResults && (
              <Form.Item
                name="tool_result_max_length"
                label={t("channels.toolResultMaxLength")}
                tooltip={t("channels.toolMaxLengthTooltip")}
              >
                <InputNumber min={0} style={{ width: "100%" }} />
              </Form.Item>
            )}
            {activeKey !== "console" && (
              <Form.Item
                name="show_thinking"
                label={t("channels.showThinking")}
                valuePropName="checked"
                tooltip={t("channels.showThinkingTooltip")}
              >
                <Switch />
              </Form.Item>
            )}
          </>

          {(activeKey === "wecom" ||
            activeKey === "telegram" ||
            activeKey === "dingtalk" ||
            activeKey === "feishu" ||
            activeKey === "discord" ||
            activeKey === "slack" ||
            activeKey === "matrix") && (
            <Form.Item
              name="streaming_enabled"
              label={t("channels.streamingEnabled")}
              valuePropName="checked"
              tooltip={
                activeKey === "dingtalk"
                  ? t("channels.streamingEnabledDingtalkHint")
                  : activeKey === "feishu"
                  ? t("channels.streamingEnabledFeishuHint")
                  : undefined
              }
            >
              <Switch />
            </Form.Item>
          )}

          {isBuiltin
            ? renderBuiltinExtraFields(activeKey)
            : renderCustomExtraFields(initialValues)}

          {CHANNELS_WITH_ACCESS_CONTROL.includes(activeKey) &&
            renderAccessControlFields()}

          {activeKey !== "console" && (
            <Form.Item
              name="no_text_debounce"
              label={t("channels.noTextDebounce")}
              valuePropName="checked"
              tooltip={t("channels.noTextDebounceTooltip")}
              initialValue={true}
            >
              <Switch />
            </Form.Item>
          )}
        </Form>
      )}
    </Drawer>
  );
}
