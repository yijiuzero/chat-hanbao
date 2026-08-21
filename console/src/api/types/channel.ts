export interface BaseChannelConfig {
  enabled: boolean;
  bot_prefix: string;
  show_tool_calls?: boolean;
  show_tool_results?: boolean;
  tool_call_max_length?: number;
  tool_result_max_length?: number;
  show_thinking?: boolean;
  dm_policy?: "open" | "allowlist";
  group_policy?: "open" | "allowlist";
  allow_from?: string[];
  require_mention?: boolean;
  no_text_debounce?: boolean;
}

export interface IMessageChannelConfig extends BaseChannelConfig {
  db_path: string;
  poll_sec: number;
}

export interface DingTalkConfig extends BaseChannelConfig {
  client_id: string;
  client_secret: string;
  message_type: string;
  cron_message_type: string;
  card_template_id: string;
  card_template_key: string;
  robot_code: string;
  at_sender_on_reply?: boolean;
  streaming_enabled?: boolean;
  endpoint?: string;
}

export interface FeishuConfig extends BaseChannelConfig {
  app_id: string;
  app_secret: string;
  encrypt_key: string;
  verification_token: string;
  media_dir: string;
  domain?: "feishu" | "lark";
  streaming_enabled?: boolean;
  share_session_in_group?: boolean;
}

export interface QQConfig extends BaseChannelConfig {
  app_id: string;
  client_secret: string;
  ack_message?: string;
  user_openid?: string;
}

export interface WecomConfig extends BaseChannelConfig {
  bot_id: string;
  secret: string;
  media_dir?: string;
  welcome_text?: string;
  share_session_in_group?: boolean;
  max_reconnect_attempts?: number;
  streaming_enabled?: boolean;
}

export type ConsoleConfig = BaseChannelConfig;

export interface XiaoYiConfig extends BaseChannelConfig {
  ak: string;
  sk: string;
  agent_id: string;
  task_timeout_ms?: number;
}

export interface WeChatConfig extends BaseChannelConfig {
  bot_token: string;
  bot_token_file: string;
  base_url: string;
  media_dir?: string;
  message_merge_enabled?: boolean;
  message_merge_delay_ms?: number;
}

// [hanbao modification] removed channel config types for
// discord/telegram/slack/mqtt/matrix/mattermost/voice/sip/yuanbao/onebot
export interface ChannelConfig {
  imessage: IMessageChannelConfig;
  dingtalk: DingTalkConfig;
  feishu: FeishuConfig;
  qq: QQConfig;
  wecom: WecomConfig;
  console: ConsoleConfig;
  xiaoyi: XiaoYiConfig;
  wechat: WeChatConfig;
}

export type SingleChannelConfig =
  | IMessageChannelConfig
  | DingTalkConfig
  | FeishuConfig
  | QQConfig
  | ConsoleConfig
  | WecomConfig
  | WeChatConfig
  | XiaoYiConfig;
