#!/bin/sh
# Substitute QWENPAW_PORT in supervisord template and start supervisord.
# Default port 8088; override at runtime with -e QWENPAW_PORT=3000.
set -e

# [hanbao modification] I-007: 上架飞牛默认开启 Web Console 认证。
# 用户若需关闭，显式传入 -e QWENPAW_AUTH_ENABLED=false 即可。
export QWENPAW_AUTH_ENABLED="${QWENPAW_AUTH_ENABLED:-true}"

is_auth_enabled() {
  if [ "${QWENPAW_AUTH_ENABLED+x}" ]; then
    flag="${QWENPAW_AUTH_ENABLED}"
  else
    flag="${QWENPAW_AUTH_ENABLED:-}"
  fi
  flag="$(printf '%s' "$flag" | tr '[:upper:]' '[:lower:]')"
  [ "$flag" = "true" ] || [ "$flag" = "1" ] || [ "$flag" = "yes" ]
}

warn_if_auth_off_container_bind() {
  if is_auth_enabled; then
    return
  fi

  cat >&2 <<EOF
============================================================
# [hanbao modification] Brand display name: QwenPaw → hanbao
SECURITY NOTICE: hanbao is running in Docker without authentication.

hanbao cannot verify whether access to the service is limited to a trusted
network. Anyone who can reach the service may access hanbao APIs without login.

Recommended:
  - Restrict access to a trusted network or protected environment.
  - Enable authentication with QWENPAW_AUTH_ENABLED=true if untrusted users or
    processes may reach the service.
============================================================
EOF
}

# [hanbao modification] I-007: 认证开启时的启动引导
print_auth_banner() {
  if ! is_auth_enabled; then
    warn_if_auth_off_container_bind
    return
  fi
  if [ -n "${QWENPAW_AUTH_USERNAME:-}" ] && [ -n "${QWENPAW_AUTH_PASSWORD:-}" ]; then
    echo "Web Console 认证已启用：首次启动将从环境变量自动创建管理员账号。"
  else
    echo "Web Console 认证已启用：首次打开页面将进入注册页，请设置管理员密码。"
    echo "  （建议装好后立即设置，避免局域网内他人抢先注册）"
  fi
}

# Auto-initialize if config.json is missing (bind mount with empty directory).
if [ ! -f "${QWENPAW_WORKING_DIR}/config.json" ]; then
  echo "⚠️  No config.json found in ${QWENPAW_WORKING_DIR}"
  echo "📦 Running initialization..."
  qwenpaw init --defaults --accept-security
  echo "✅ Initialization complete!"
else
  echo "✓ Config found in ${QWENPAW_WORKING_DIR}, skipping initialization."
fi

export QWENPAW_PORT="${QWENPAW_PORT:-8088}"
print_auth_banner
envsubst '${QWENPAW_PORT}' \
  < /etc/supervisor/conf.d/supervisord.conf.template \
  > /etc/supervisor/conf.d/supervisord.conf
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
