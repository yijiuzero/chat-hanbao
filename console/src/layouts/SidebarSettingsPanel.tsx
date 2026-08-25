import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

import { SunMoon } from "lucide-react";
import {
  SparkSunLine,
  SparkMoonLine,
  SparkChinese02Line,
  SparkEnglish02Line,
  SparkFullscreenLine,
  SparkExitFullscreenLine,
} from "@agentscope-ai/icons";
import { Select } from "@agentscope-ai/design";
import api from "../api";
import { useAppMessage } from "../hooks/useAppMessage";
import { useTimezoneOptions } from "../hooks/useTimezoneOptions";
import { languageApi } from "../api/modules/language";
import { useTheme, type ThemeMode } from "../contexts/ThemeContext";
import { useSidebarModeStore } from "../stores/sidebarModeStore";
import styles from "./sidebarSettingsPanel.module.less";

// ── Language config ────────────────────────────────────────────────────────

const LANGS = [
  { key: "zh", label: "简体中文", icon: <SparkChinese02Line size={14} /> },
  { key: "en", label: "English", icon: <SparkEnglish02Line size={14} /> },
];
const KNOWN_KEYS = new Set(LANGS.map((l) => l.key));

// ── Timezone quick-setting (moved from the removed "运行配置" page) ──────────
function TimezoneRow() {
  const { t } = useTranslation();
  const { message } = useAppMessage();
  const [timezone, setTimezone] = useState<string>("UTC");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const timezoneOptions = useTimezoneOptions();

  useEffect(() => {
    let active = true;
    api
      .getUserTimezone()
      .then((resp) => {
        if (active) setTimezone(resp.timezone || "UTC");
      })
      .catch(() => {})
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const handleChange = async (value: string) => {
    if (value === timezone) return;
    setSaving(true);
    try {
      await api.updateUserTimezone(value);
      setTimezone(value);
      message.success(t("agentConfig.timezoneSaveSuccess"));
    } catch (err) {
      const errMsg =
        err instanceof Error
          ? err.message
          : t("agentConfig.timezoneSaveFailed");
      message.error(errMsg);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className={styles.row}>
      <span className={styles.label}>
        {t("agentConfig.timezone", "Timezone")}
      </span>
      <Select
        showSearch
        value={timezone}
        placeholder={t("agentConfig.selectTimezone", "Select timezone")}
        filterOption={(input, option) =>
          (option?.label?.toString() || "")
            .toLowerCase()
            .includes(input.toLowerCase())
        }
        options={timezoneOptions}
        onChange={handleChange}
        loading={loading || saving}
        disabled={saving}
        size="small"
        style={{ width: "100%" }}
      />
    </div>
  );
}

// ── Component ─────────────────────────────────────────────────────────────

interface SidebarSettingsPanelProps {
  onClose?: () => void;
}

export default function SidebarSettingsPanel({
  onClose,
}: SidebarSettingsPanelProps) {
  const { t, i18n } = useTranslation();
  const { themeMode, setThemeMode } = useTheme();
  const { mode: sidebarMode, toggleMode: toggleSidebarMode } =
    useSidebarModeStore();

  const raw = i18n.resolvedLanguage || i18n.language;
  const currentLang = KNOWN_KEYS.has(raw) ? raw : raw.split("-")[0];

  const changeLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
    localStorage.setItem("language", lang);
    languageApi.updateLanguage(lang).catch(() => {});
  };

  const themeOptions: {
    key: ThemeMode;
    label: string;
    icon: React.ReactNode;
  }[] = [
    {
      key: "light",
      label: t("theme.light", "Light"),
      icon: <SparkSunLine size={14} />,
    },
    {
      key: "dark",
      label: t("theme.dark", "Dark"),
      icon: <SparkMoonLine size={14} />,
    },
    {
      key: "system",
      label: t("theme.system", "System"),
      icon: <SunMoon size={14} />,
    },
  ];

  return (
    <div className={styles.panel}>
      {/* ── Language ─────────────────────────────────────── */}
      <div className={styles.row}>
        <span className={styles.label}>
          {t("sidebar.settings.language", "Language")}
        </span>
        <div className={styles.options}>
          {LANGS.map(({ key, label, icon }) => (
            <button
              key={key}
              title={label}
              className={`${styles.optBtn} ${
                currentLang === key ? styles.optBtnActive : ""
              }`}
              onClick={() => changeLanguage(key)}
            >
              {icon}
            </button>
          ))}
        </div>
      </div>

      {/* ── Theme ────────────────────────────────────────── */}
      <div className={styles.row}>
        <span className={styles.label}>
          {t("sidebar.settings.theme", "Theme")}
        </span>
        <div className={styles.options}>
          {themeOptions.map(({ key, label, icon }) => (
            <button
              key={key}
              title={label}
              className={`${styles.optBtn} ${
                themeMode === key ? styles.optBtnActive : ""
              }`}
              onClick={() => setThemeMode(key)}
            >
              {icon}
              <span className={styles.optLabel}>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ── Mode ─────────────────────────────────────────── */}
      <div className={styles.row}>
        <span className={styles.label}>
          {t("sidebar.settings.mode", "Mode")}
        </span>
        <button
          className={`${styles.optBtn} ${styles.optBtnBlock}`}
          onClick={() => {
            toggleSidebarMode();
            onClose?.();
          }}
        >
          {sidebarMode === "simple" ? (
            <>
              <SparkFullscreenLine size={14} />
              <span className={styles.optLabel}>
                {t("sidebar.fullMode", "Full Mode")}
              </span>
            </>
          ) : (
            <>
              <SparkExitFullscreenLine size={14} />
              <span className={styles.optLabel}>
                {t("sidebar.simpleMode", "Simple Mode")}
              </span>
            </>
          )}
        </button>
      </div>

      {/* ── Timezone ───────────────────────────────────── */}
      <TimezoneRow />
    </div>
  );
}
