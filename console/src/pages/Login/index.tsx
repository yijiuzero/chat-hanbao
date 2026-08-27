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
      className="hanbao-login-ink"
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        /* [hanbao modification] 水墨晕染底：亮色宣纸+双角墨晕，暗色墨空 */
        background: isDark
          ? "radial-gradient(circle at 22% 18%, rgba(255,255,255,0.05) 0, transparent 46%), linear-gradient(155deg, #141414 0%, #1d1d1d 60%, #161616 100%)"
          : "radial-gradient(circle at 18% 16%, rgba(31,31,31,0.06) 0, transparent 44%), radial-gradient(circle at 85% 88%, rgba(158,43,37,0.05) 0, transparent 46%), linear-gradient(155deg, #F7F4ED 0%, #EFE9DC 100%)",
      }}
    >
      <div
        className="hanbao-login-split"
        style={{
          width: "min(880px, 92vw)",
          display: "flex",
          borderRadius: 18,
          overflow: "hidden",
          boxShadow: isDark
            ? "0 20px 60px rgba(0,0,0,0.55)"
            : "0 24px 70px rgba(31,31,31,0.16)",
          border: isDark
            ? "1px solid rgba(255,255,255,0.10)"
            : "1px solid rgba(31,31,31,0.10)",
        }}
      >
        {/* [hanbao modification] 左：墨黑品牌立轴（宽屏可见），朱砂圆晕+衬线 wordmark+闲章 */}
        <aside
          className="hanbao-login-brand"
          style={{
            flex: "0 0 300px",
            background: isDark
              ? "linear-gradient(160deg, #20120f 0%, #1a1413 100%)"
              : "linear-gradient(160deg, #2a1f1c 0%, #3a2420 100%)",
            color: "#F2EEE4",
            padding: "40px 32px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            position: "relative",
            overflow: "hidden",
          }}
        >
          <span
            aria-hidden
            style={{
              position: "absolute",
              top: -40,
              right: -40,
              width: 160,
              height: 160,
              borderRadius: "50%",
              background:
                "radial-gradient(circle at 50% 50%, rgba(192,57,43,0.35), transparent 70%)",
            }}
          />
          <div style={{ position: "relative" }}>
            <span
              aria-hidden
              style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                width: 44,
                height: 44,
                borderRadius: 8,
                border: "1.5px solid rgba(242,238,228,0.55)",
                transform: "rotate(-5deg)",
              }}
            />
          </div>
          <div style={{ position: "relative" }}>
            <h1
              style={{
                fontFamily: "var(--font-serif)",
                fontSize: 46,
                fontWeight: 600,
                letterSpacing: "0.08em",
                margin: "0 0 10px",
                color: "#F2EEE4",
              }}
            >
              hanbao
            </h1>
          </div>
          <p
            style={{
              position: "relative",
              margin: 0,
              fontSize: 12,
              color: "rgba(242,238,228,0.45)",
            }}
          >
            家庭本地 · 私人 AI 聊天助手
          </p>
        </aside>

        {/* [hanbao modification] 右：宣纸登录卡 */}
        <main
          style={{
            flex: 1,
            padding: "40px 36px",
            background: isDark
              ? "#1f1f1f"
              : "linear-gradient(180deg, #FFFFFF 0%, #FBF8F1 100%)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            position: "relative",
            overflow: "hidden",
          }}
        >
          {/* [hanbao modification] 朱砂闲章：落于卡片右上角，纯装饰水墨印记 */}
          <span
            aria-hidden
            style={{
              position: "absolute",
              top: 20,
              right: 20,
              width: 34,
              height: 34,
              borderRadius: 6,
              border: `1.5px solid ${isDark ? "rgba(192,57,43,0.55)" : "rgba(158,43,37,0.55)"}`,
              transform: "rotate(-5deg)",
              pointerEvents: "none",
              userSelect: "none",
            }}
          />
          <div style={{ marginBottom: 28 }}>
            <img
              src={isDark ? "/logo-dark.svg" : "/logo-light.svg"}
              alt="hanbao"
              style={{
                height: 40,
                marginBottom: 14,
                filter: "drop-shadow(0 2px 6px rgba(31,31,31,0.15))", // [hanbao modification] 白底肖像卡片在亮背景上立体化
              }}
            />
            <h2
              className="ink-title"
              style={{ margin: 0, fontWeight: 600, fontSize: 20 }}
            >
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
        </main>
      </div>
    </div>
  );
}
