import {
  Layout,
  Space,
  Badge,
  Spin,
  Tooltip,
  Dropdown,
} from "antd";
import type { MenuProps } from "antd";
import LanguageSwitcher, {
  LANGUAGE_LIST,
} from "../components/LanguageSwitcher/index";
import ThemeToggleButton from "../components/ThemeToggleButton";
import { useTranslation } from "react-i18next";
import { Button, Modal } from "@agentscope-ai/design";
import styles from "./index.module.less";
import api from "../api";
import { openExternalLink } from "../utils/openExternalLink";
import { ExternalMarkdownLink } from "../components/Markdown/externalLinkComponents";
import {
  GITHUB_URL,
  // [hanbao modification] Disabled — no release channel yet.
  // PYPI_URL,
  // ONE_HOUR_MS,
  UPDATE_MD,
  // isStableVersion,
  // compareVersions,
} from "./constants";
import { useTheme } from "../contexts/ThemeContext";
import { useState, useEffect } from "react";
import { Slot } from "../plugins/registry/Slot";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  CopyOutlined,
  CheckOutlined,
  TagOutlined,
  GithubOutlined,
  InfoCircleOutlined,
} from "@ant-design/icons";

const { Header: AntHeader } = Layout;

// ── Code block with copy button ───────────────────────────────────────────
function UpdateCodeBlock({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };
  return (
    <div className={styles.codeBlock}>
      <code className={styles.codeBlockInner}>{code}</code>
      <button
        className={`${styles.copyBtn} ${
          copied ? styles.copyBtnCopied : styles.copyBtnDefault
        }`}
        onClick={handleCopy}
        title="Copy"
      >
        {copied ? <CheckOutlined /> : <CopyOutlined />}
      </button>
    </div>
  );
}

export default function Header() {
  const { t, i18n } = useTranslation();
  const { isDark, setThemeMode } = useTheme();
  const [version, setVersion] = useState<string>("");
  const [updateModalOpen, setUpdateModalOpen] = useState(false);
  const [updateMarkdown, setUpdateMarkdown] = useState<string>("");

  useEffect(() => {
    api
      .getVersion()
      .then((res) => setVersion(res?.version ?? ""))
      .catch(() => {});
  }, []);

  // [hanbao modification] Web update check disabled — no hanbao release channel
  // yet (e.g. FlyOS app store version check). The update modal is shown from
  // the local UPDATE_MD content instead.

  // The console is browser-served; the desktop install/update flow was removed.
  const hasUpdate = false;

  const mobileMenuItems: MenuProps["items"] = [
    {
      key: "language",
      label: t("sidebar.settings.language"),
      children: LANGUAGE_LIST.map(({ key, label }) => ({
        key,
        label,
        onClick: () => {
          i18n.changeLanguage(key);
          localStorage.setItem("language", key);
        },
      })),
    },
    {
      key: "theme",
      label: t("sidebar.settings.theme"),
      children: [
        {
          key: "light",
          label: t("theme.light"),
          onClick: () => setThemeMode("light"),
        },
        {
          key: "dark",
          label: t("theme.dark"),
          onClick: () => setThemeMode("dark"),
        },
        {
          key: "system",
          label: t("theme.system"),
          onClick: () => setThemeMode("system"),
        },
      ],
    },
  ];

  const handleOpenUpdateModal = () => {
    setUpdateMarkdown("");
    setUpdateModalOpen(true);
    const lang = i18n.language?.startsWith("zh")
      ? "zh"
      : i18n.language?.startsWith("ru")
        ? "ru"
        : "en";

    // [hanbao modification] use local UPDATE_MD instead of fetching the
    // upstream QwenPaw FAQ markdown for update instructions.
    setUpdateMarkdown(UPDATE_MD[lang] ?? UPDATE_MD.en);
  };

  const handleNavClick = (url: string) => {
    openExternalLink(url);
  };

  return (
    <>
      <AntHeader className={styles.header}>
        <div className={styles.logoWrapper}>
          {/*
            Slot lets a plugin replace the brand logo (e.g. a per-agent
            branding override). When no plugin registers a replacement —
            or when the registered render returns null — the host default
            <img> below paints.
          */}
          <Slot name="header.logo" kind="replace">
            <img
              src={isDark ? "/logo-dark.svg" : "/logo-light.svg"}
              alt="hanbao"
              className={styles.logoImg}
            />
          </Slot>
          <div className={styles.logoDivider} />
          {version && (
            <Badge
              dot={!!hasUpdate}
              color="rgba(192, 57, 43, 1)"
              offset={[4, 28]}
            >
              <span
                className={`${styles.versionBadge} ${
                  hasUpdate
                    ? styles.versionBadgeClickable
                    : styles.versionBadgeDefault
                }`}
                onClick={() => {
                  if (hasUpdate) handleOpenUpdateModal();
                }}
              >
                v{version}
              </span>
            </Badge>
          )}
        </div>
        <Slot name="header.left" kind="fill" />
        <Space size="middle">
          <Slot name="header.right" kind="fill" />
          <Tooltip title={t("header.github")}>
            <Button
              type="text"
              icon={<GithubOutlined />}
              onClick={() => handleNavClick(GITHUB_URL)}
              className={styles.hideOnMobile}
            >
              {t("header.github")}
            </Button>
          </Tooltip>
          <div className={styles.headerDivider} />
          <span className={styles.hideOnMobile}>
            <LanguageSwitcher />
          </span>
          <span className={styles.hideOnMobile}>
            <ThemeToggleButton />
          </span>
          <Dropdown menu={{ items: mobileMenuItems }} placement="bottomRight">
            <Button
              type="text"
              icon={<InfoCircleOutlined />}
              className={styles.showOnMobile}
              title={t("header.resources")}
            />
          </Dropdown>
        </Space>
      </AntHeader>

      <Modal
        title={null}
        open={updateModalOpen}
        onCancel={() => setUpdateModalOpen(false)}
        footer={[
          <Button key="close" onClick={() => setUpdateModalOpen(false)}>
            {t("common.close")}
          </Button>,
        ]}
        width={960}
        className={styles.updateModal}
      >
        {/* Banner area */}
        <div className={styles.updateModalBanner}>
          <div className={styles.updateModalBannerLeft}>
            <span className={styles.updateModalVersionTag}>
              <TagOutlined />
              Version {version}
            </span>
            <div className={styles.updateModalBannerTitle}>
              {t("sidebar.updateModal.title", {
                version,
              })}
            </div>
          </div>
        </div>

        {/* Markdown content */}
        <div className={styles.updateModalBody}>
          {updateMarkdown ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                a: ExternalMarkdownLink,
                code({ node, className, children, ...props }: any) {
                  const match = /language-(\w+)/.exec(className || "");
                  const isBlock =
                    node?.position?.start?.line !== node?.position?.end?.line ||
                    match;
                  return isBlock ? (
                    <UpdateCodeBlock
                      code={String(children).replace(/\n$/, "")}
                    />
                  ) : (
                    <code className={styles.codeInline} {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {updateMarkdown}
            </ReactMarkdown>
          ) : (
            <div className={styles.updateModalSpinWrapper}>
              <Spin />
            </div>
          )}
        </div>
      </Modal>
    </>
  );
}
