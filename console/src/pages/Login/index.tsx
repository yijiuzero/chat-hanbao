import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Button, Form, Input } from "antd";
import { useAppMessage } from "../../hooks/useAppMessage";
import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { authApi } from "../../api/modules/auth";
import { setAuthToken } from "../../api/config";
import { useTheme } from "../../contexts/ThemeContext";

export default function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { isDark } = useTheme();
  const [loading, setLoading] = useState(false);
  const [isRegister, setIsRegister] = useState(false);
  const [hasUsers, setHasUsers] = useState(true);
  const { message } = useAppMessage();

  useEffect(() => {
    authApi
      .getStatus()
      .then((res) => {
        if (!res.enabled) {
          navigate("/chat", { replace: true });
          return;
        }
        setHasUsers(res.has_users);
        if (!res.has_users) {
          setIsRegister(true);
        }
      })
      .catch(() => {});
  }, [navigate]);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const raw = searchParams.get("redirect") || "/chat";
      const redirect =
        raw.startsWith("/") && !raw.startsWith("//") ? raw : "/chat";

      if (isRegister) {
        const res = await authApi.register(values.username, values.password);
        if (res.token) {
          setAuthToken(res.token);
          message.success(t("login.registerSuccess"));
          navigate(redirect, { replace: true });
        }
      } else {
        const res = await authApi.login(values.username, values.password);
        if (res.token) {
          setAuthToken(res.token);
          navigate(redirect, { replace: true });
        } else {
          message.info(t("login.authNotEnabled"));
          navigate(redirect, { replace: true });
        }
      }
    } catch (err) {
      let errorMsg = t("login.failed");

      // Check if it's an Error object and use the backend message directly
      if (err instanceof Error) {
        // Use the backend message directly without complex parsing
        errorMsg = err.message;
      } else if (isRegister) {
        errorMsg = t("login.registerFailed");
      }

      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: isDark
          ? "radial-gradient(circle at 25% 25%, rgba(255,255,255,0.04) 0, transparent 45%), linear-gradient(160deg, #161616 0%, #1f1f1f 100%)"
          : "radial-gradient(circle at 20% 20%, rgba(31,31,31,0.05) 0, transparent 45%), radial-gradient(circle at 80% 80%, rgba(31,31,31,0.04) 0, transparent 50%), linear-gradient(160deg, #F7F4ED 0%, #EFE9DC 100%)",
      }}
    >
      <div
        style={{
          width: 400,
          padding: 32,
          borderRadius: 12,
          background: isDark
            ? "#242424"
            : "linear-gradient(180deg, #FFFFFF 0%, #FBF8F1 100%)", // [hanbao modification] 亮色微宣纸渐变
          border: isDark
            ? "1px solid rgba(255,255,255,0.10)"
            : "1px solid rgba(31,31,31,0.10)",
          boxShadow: isDark
            ? "0 4px 24px rgba(0,0,0,0.4)"
            : "0 8px 32px rgba(31,31,31,0.08)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* [hanbao modification] 朱砂闲章（函）：落于卡片右上角，立水墨文人气质，呼应「函包」品牌 */}
        <span
          aria-hidden
          style={{
            position: "absolute",
            top: 16,
            right: 16,
            width: 34,
            height: 34,
            borderRadius: 6,
            border: `1.5px solid ${isDark ? "rgba(192,57,43,0.55)" : "rgba(158,43,37,0.55)"}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: isDark ? "rgba(192,57,43,0.6)" : "rgba(158,43,37,0.6)",
            fontFamily: "var(--font-serif)",
            fontSize: 16,
            fontWeight: 600,
            opacity: 0.85,
            transform: "rotate(-5deg)",
            pointerEvents: "none",
            userSelect: "none",
          }}
        >
          函
        </span>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <img
            src={isDark ? "/logo-dark.svg" : "/logo-light.svg"}
            alt="hanbao"
            style={{
              height: 48,
              marginBottom: 12,
              filter: "drop-shadow(0 2px 6px rgba(31,31,31,0.15))", // [hanbao modification] 白底肖像卡片在亮背景上立体化
            }}
          />
          <h2 className="ink-title" style={{ margin: 0, fontWeight: 600, fontSize: 20 }}>
            {isRegister ? t("login.registerTitle") : t("login.title")}
          </h2>
          {!hasUsers && (
            <p
              style={{
                margin: "8px 0 0",
                color: isDark ? "rgba(255,255,255,0.45)" : "#666",
                fontSize: 13,
              }}
            >
              {t("login.firstUserHint")}
            </p>
          )}
        </div>

        <Form
          layout="vertical"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: t("login.usernameRequired") }]}
          >
            <Input
              prefix={
                <UserOutlined
                  style={{
                    color: isDark ? "rgba(255,255,255,0.45)" : undefined,
                  }}
                />
              }
              placeholder={t("login.usernamePlaceholder")}
              autoFocus
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: t("login.passwordRequired") }]}
          >
            <Input.Password
              prefix={
                <LockOutlined
                  style={{
                    color: isDark ? "rgba(255,255,255,0.45)" : undefined,
                  }}
                />
              }
              placeholder={t("login.passwordPlaceholder")}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, marginTop: 8 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              style={{ height: 44, borderRadius: 8, fontWeight: 500 }}
            >
              {isRegister ? t("login.register") : t("login.submit")}
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
}
