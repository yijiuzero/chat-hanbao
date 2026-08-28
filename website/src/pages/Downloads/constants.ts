import { Laptop, Monitor, type LucideIcon } from "lucide-react";

// [hanbao modification] Upstream CDN `download.qwenpaw.agentscope.io` replaced
// with a hanbao-owned GitHub base. hanbao has no hosted download metadata yet,
// so the Downloads page shows its empty state until `metadata/index.json` is
// published at this base (see docs/known-issues.md I-038).
export const CDN_BASE = "https://raw.githubusercontent.com/yijiuzero/chat-hanbao/main";

export const DOWNLOADS_HEADER_BG_URL =
  "https://img.alicdn.com/imgextra/i2/O1CN01DAtS4T1FJTi3kRSot_!!6000000000466-2-tps-2880-554.png";

export const PLATFORM_ICONS: Record<string, LucideIcon> = {
  win: Monitor,
  mac: Laptop,
  linux: Monitor,
};

export const KNOWN_PLUGIN_PLATFORM_KINDS = ["bundle", "tool"] as const;
