import { createGlobalStyle } from "antd-style";
import {
  ConfigProvider,
  bailianDarkTheme,
  bailianTheme,
} from "@agentscope-ai/design";
import { App as AntdApp } from "antd";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import zhCN from "antd/locale/zh_CN";
import enUS from "antd/locale/en_US";
import jaJP from "antd/locale/ja_JP";
import ruRU from "antd/locale/ru_RU";
import idID from "antd/locale/id_ID";
import type { Locale } from "antd/es/locale";
import { theme as antdTheme } from "antd";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import "dayjs/locale/zh-cn";
import "dayjs/locale/ja";
import "dayjs/locale/ru";
import "dayjs/locale/id";
dayjs.extend(relativeTime);
import MainLayout from "./layouts/MainLayout";
import { ThemeProvider, useTheme } from "./contexts/ThemeContext";
import { PluginProvider, usePlugins } from "./plugins/PluginContext";
import { Suspense } from "react";
import { lazyImportWithRetry } from "./utils/lazyWithRetry";

const LoginPage = lazyImportWithRetry("./pages/Login/index");
import { authApi } from "./api/modules/auth";
import { languageApi } from "./api/modules/language";
import { useUploadLimitStore } from "./stores/uploadLimitStore";
import { getApiUrl, getApiToken, clearAuthToken } from "./api/config";
import "./styles/layout.css";
import "./styles/form-override.css";

const antdLocaleMap: Record<string, Locale> = {
  zh: zhCN,
  en: enUS,
  ja: jaJP,
  ru: ruRU,
  id: idID,
};

const dayjsLocaleMap: Record<string, string> = {
  zh: "zh-cn",
  en: "en",
  ja: "ja",
  ru: "ru",
  id: "id",
};

const GlobalStyle = createGlobalStyle`
* {
  margin: 0;
  box-sizing: border-box;
}
`;

function AuthGuard({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<"loading" | "auth-required" | "ok">(
    "loading",
  );

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await authApi.getStatus();
        if (cancelled) return;
        if (!res.enabled) {
          setStatus("ok");
          return;
        }
        const token = getApiToken();
        if (!token) {
          setStatus("auth-required");
          return;
        }
        try {
          const r = await fetch(getApiUrl("/auth/verify"), {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (cancelled) return;
          if (r.ok) {
            setStatus("ok");
          } else {
            clearAuthToken();
            setStatus("auth-required");
          }
        } catch {
          if (!cancelled) {
            clearAuthToken();
            setStatus("auth-required");
          }
        }
      } catch {
        if (!cancelled) setStatus("ok");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (status === "loading") return null;
  if (status === "auth-required")
    return (
      <Navigate
        to={`/login?redirect=${encodeURIComponent(window.location.pathname)}`}
        replace
      />
    );
  return <>{children}</>;
}

function getRouterBasename(pathname: string): string | undefined {
  return /^\/console(?:\/|$)/.test(pathname) ? "/console" : undefined;
}

function AppInner() {
  const basename = getRouterBasename(window.location.pathname);
  const { i18n } = useTranslation();
  const { isDark } = useTheme();
  const { loading: pluginsLoading } = usePlugins();
  const selectedTheme = isDark ? bailianDarkTheme : bailianTheme;
  const lang = i18n.resolvedLanguage || i18n.language || "en";
  const [antdLocale, setAntdLocale] = useState<Locale>(
    antdLocaleMap[lang] ?? enUS,
  );

  useEffect(() => {
    if (!localStorage.getItem("language")) {
      languageApi
        .getLanguage()
        .then(({ language }) => {
          if (language && language !== i18n.language) {
            i18n.changeLanguage(language);
            localStorage.setItem("language", language);
          }
        })
        .catch((err) =>
          console.error("Failed to fetch language preference:", err),
        );
    }
    useUploadLimitStore.getState().fetch();
  }, []);

  useEffect(() => {
    const handleLanguageChanged = (lng: string) => {
      const shortLng = lng.split("-")[0];
      setAntdLocale(antdLocaleMap[shortLng] ?? enUS);
      dayjs.locale(dayjsLocaleMap[shortLng] ?? "en");
    };

    // Set initial dayjs locale
    dayjs.locale(dayjsLocaleMap[lang.split("-")[0]] ?? "en");

    i18n.on("languageChanged", handleLanguageChanged);
    return () => {
      i18n.off("languageChanged", handleLanguageChanged);
    };
  }, [i18n]);

  // Wait for plugins to load before rendering routes that might be patched
  if (pluginsLoading) {
    return null;
  }

  return (
    <BrowserRouter basename={basename}>
      <GlobalStyle />
      <ConfigProvider
        {...selectedTheme}
        prefix="hanbao"
        prefixCls="hanbao"
        locale={antdLocale}
        theme={{
          ...(selectedTheme as any)?.theme,
          algorithm: isDark
            ? antdTheme.darkAlgorithm
            : antdTheme.defaultAlgorithm,
          token: {
            // [hanbao modification] 水墨风品牌：墨黑文字 + 朱砂红印章 + 宣纸底（原暖橘已弃用，logo 保留暖橘点缀）
            // 全量化覆盖 bailianTheme（Spark Design）默认 token，让 antd/Spark 组件形态全面脱离 qwenpaw 上游味道
            colorPrimary: isDark ? "#C0392B" : "#9E2B25",
            colorPrimaryHover: isDark ? "#D9574B" : "#B03A2E",
            colorPrimaryActive: isDark ? "#A92B23" : "#7E211C",
            colorPrimaryText: isDark ? "#D9574B" : "#9E2B25",
            colorPrimaryTextHover: isDark ? "#E57368" : "#B03A2E",
            colorPrimaryTextActive: isDark ? "#A92B23" : "#7E211C",
            // [hanbao modification] 全站无衬线行书字体统一（含中文 PingFang/雅黑/Noto），与 .ink-title 衬线立骨形成反差
            fontFamily: "var(--font-sans)",
            colorLink: isDark ? "#D9574B" : "#9E2B25",
            colorLinkHover: "#B03A2E",
            colorLinkActive: "#7E211C",
            colorTextBase: isDark ? "#ECE9E3" : "#1F1F1F",
            colorText: isDark ? "rgba(236,233,227,0.88)" : "rgba(31,31,31,0.88)",
            colorTextSecondary: isDark ? "rgba(236,233,227,0.65)" : "rgba(31,31,31,0.65)",
            colorTextTertiary: isDark ? "rgba(236,233,227,0.45)" : "rgba(31,31,31,0.45)",
            colorTextQuaternary: isDark ? "rgba(236,233,227,0.25)" : "rgba(31,31,31,0.25)",
            colorBgBase: isDark ? "#1A1A1A" : "#F7F4ED",
            colorBgLayout: isDark ? "#161616" : "#F2EEE4",
            colorBgContainer: isDark ? "#242424" : "#FFFFFF",
            colorBgElevated: isDark ? "#2A2A2A" : "#FFFFFF",
            colorBgSpotlight: isDark ? "#3A3A3A" : "#2B2B2B",
            colorBgMask: "rgba(0,0,0,0.45)",
            colorBorder: isDark ? "rgba(255,255,255,0.14)" : "rgba(31,31,31,0.12)",
            colorBorderSecondary: isDark ? "rgba(255,255,255,0.09)" : "rgba(31,31,31,0.08)",
            colorFill: isDark ? "rgba(255,255,255,0.12)" : "rgba(31,31,31,0.10)",
            colorFillSecondary: isDark ? "rgba(255,255,255,0.08)" : "rgba(31,31,31,0.06)",
            colorFillTertiary: isDark ? "rgba(255,255,255,0.05)" : "rgba(31,31,31,0.04)",
            colorFillQuaternary: isDark ? "rgba(255,255,255,0.03)" : "rgba(31,31,31,0.02)",
            colorInfo: isDark ? "#D9574B" : "#9E2B25",
            colorInfoBg: isDark ? "rgba(192,57,43,0.16)" : "#F7E9E7",
            colorInfoBorder: isDark ? "rgba(192,57,43,0.45)" : "#E3C4BF",
            colorSuccess: isDark ? "#5E9E6F" : "#3E7A4E",
            colorSuccessBg: isDark ? "rgba(62,122,78,0.16)" : "#EAF3EC",
            colorSuccessBorder: isDark ? "rgba(62,122,78,0.45)" : "#C4DCCB",
            colorWarning: isDark ? "#C99A3C" : "#9A7B2D",
            colorWarningBg: isDark ? "rgba(154,123,45,0.16)" : "#F6F0E0",
            colorWarningBorder: isDark ? "rgba(154,123,45,0.45)" : "#E4D8B4",
            colorError: isDark ? "#E57368" : "#C0392B",
            colorErrorBg: isDark ? "rgba(229,115,104,0.16)" : "#F9E9E7",
            colorErrorBorder: isDark ? "rgba(229,115,104,0.45)" : "#ECC9C4",
            borderRadius: 8,
            borderRadiusLG: 12,
            borderRadiusSM: 6,
            colorPrimaryBg: isDark ? "rgba(192,57,43,0.16)" : "#F7E9E7",
            colorPrimaryBgHover: isDark ? "rgba(192,57,43,0.26)" : "#F0DCD9",
            colorPrimaryBorder: isDark ? "rgba(192,57,43,0.45)" : "#E3C4BF",
            colorPrimaryBorderHover: isDark ? "rgba(217,87,75,0.60)" : "#D3A9A3",
            boxShadow: "0 1px 2px rgba(31,31,31,0.06), 0 1px 6px rgba(31,31,31,0.04)",
            boxShadowSecondary: "0 4px 16px rgba(31,31,31,0.10)",
            boxShadowTertiary: "0 1px 2px rgba(31,31,31,0.04)",
            boxShadowTertiaryLeft: "-2px 0 8px rgba(31,31,31,0.08)",
            boxShadowInput: isDark ? "0 0 0 2px rgba(217,87,75,0.10)" : "0 0 0 2px rgba(158,43,37,0.08)",
          },
        }}
      >
        <AntdApp>
                <Routes>
                  <Route
                    path="/login"
                    element={
                      <Suspense fallback={null}>
                        <LoginPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/*"
                    element={
                      <AuthGuard>
                        <MainLayout />
                      </AuthGuard>
                    }
                  />
                </Routes>
        </AntdApp>
      </ConfigProvider>
    </BrowserRouter>
  );
}

function App() {
  return (
    <ThemeProvider>
      <PluginProvider>
        <AppInner />
      </PluginProvider>
    </ThemeProvider>
  );
}

export default App;
