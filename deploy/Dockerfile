# Base images — override with --build-arg for environments without ACR access.
ARG NODE_IMAGE=agentscope-registry.ap-southeast-1.cr.aliyuncs.com/agentscope/node:slim
ARG UV_IMAGE=agentscope-registry.ap-southeast-1.cr.aliyuncs.com/agentscope/uv:latest

# -----------------------------------------------------------------------------
# Stage 1: build console frontend (dist not committed in repo).
# -----------------------------------------------------------------------------
# [hanbao modification] Reorder COPY for layer caching: install deps first
# (cached unless package.json changes), then copy source and build.
FROM ${NODE_IMAGE} AS console-builder
WORKDIR /app
# [hanbao modification] Raise Node heap limit for the console build.
# `tsc -b && vite build` exhausts Node's default old-space on machines with
# ~8GB available to the Docker VM, aborting with SIGABRT (exit 134).
# Override with --build-arg NODE_BUILD_HEAP_MB=<mb> if needed.
ARG NODE_BUILD_HEAP_MB=4096
ENV NODE_OPTIONS=--max-old-space-size=${NODE_BUILD_HEAP_MB}
# Install deps first → cached unless package.json / package-lock.json change.
COPY console/package.json console/package-lock.json /app/console/
RUN cd /app/console && npm ci --include=dev
# Copy source and build → only runs when console/ files change.
COPY console /app/console
RUN cd /app/console && npm run build

# Alias for uv binary so COPY --from can reference a build-arg image.
FROM ${UV_IMAGE} AS uv-src

# -----------------------------------------------------------------------------
# Stage 2: runtime image with Python (no Node, no desktop, no Chromium).
# -----------------------------------------------------------------------------
# [hanbao modification] I-004: runtime base is now python:3.12-slim
# (Debian slim, has /bin/sh + apt + python3) instead of node:slim, dropping
# the Node runtime (~200MB+) from the final image. The console is pre-built
# static assets served by FastAPI, so Node is not needed at runtime. The uv
# binary is still sourced from the agentscope/uv image via the uv-src stage.
FROM python:3.12-slim

# ENV variables
ENV NODE_ENV=production
ENV WORKSPACE_DIR=/app
ENV HANBAO_WORKING_DIR=/app/working
ENV HANBAO_SECRET_DIR=/app/working.secret
ENV HANBAO_BACKUP_DIR=/app/working.backups

# Channel filtering: use HANBAO_DISABLED_CHANNELS (exclusion, recommended)
# or HANBAO_ENABLED_CHANNELS (whitelist). Override at runtime with -e.
ARG HANBAO_DISABLED_CHANNELS="imessage"
ENV HANBAO_DISABLED_CHANNELS=${HANBAO_DISABLED_CHANNELS}
ARG HANBAO_ENABLED_CHANNELS=""
ENV HANBAO_ENABLED_CHANNELS=${HANBAO_ENABLED_CHANNELS}

ARG DEBIAN_FRONTEND=noninteractive

# [hanbao modification] I-004: Drop the desktop stack (XFCE4 / Xvfb / dbus)
# and Chromium (~1-2GB). hanbao is a headless chat server: the Web Console
# is static files served by FastAPI, and browser automation (browser_use /
# desktop_screenshot) was removed.
# [hanbao modification] size-opt (2026-08-25): build-only toolchain
# (build-essential / gcc / g++ / make / git / libssl-dev) is NO LONGER
# installed here. It is installed together with the venv build and purged in
# the SAME RUN (see merged install step below) so it never persists in the
# final image layer. ~200MB saved.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    supervisor \
    gettext-base \
    python3 \
    python3-venv \
    fonts-wqy-zenhei \
    # [hanbao modification] fonts-wqy-microhei 已从 Debian 源移除（Unable to locate package），
    # 文泉驿正黑 zenhei 已覆盖中文字体渲染，移除 microhei
  && rm -rf /var/lib/apt/lists/* \
  && apt-get clean

# Indicate running in container (used by telemetry/secret-store guards).
ENV HANBAO_RUNNING_IN_CONTAINER=1

WORKDIR ${WORKSPACE_DIR}

RUN python3 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# [hanbao modification] size-opt (2026-08-25): copy the full source BEFORE the
# build so deps + the local package install in ONE RUN, and the build toolchain
# can be purged in that same RUN. The earlier "stub" trick is no longer needed.
COPY pyproject.toml setup.py README.md ./
COPY --from=uv-src /uv /bin/uv
COPY src ./src
COPY website/public/docs/ ./src/hanbao/docs/
# Inject console dist from build stage (repo does not commit dist).
COPY --from=console-builder /app/console/dist/ ./src/hanbao/console/
ENV PYTHONPATH=/app/src

# [hanbao modification] size-opt (2026-08-25): install build-only toolchain,
# run `uv pip install`, then PURGE it in the same RUN so gcc/g++/make/git/
# libssl-dev/libc6-dev never persist in the final image (~200MB saved).
# apt-mark manual keeps the runtime packages safe from the subsequent autoremove.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential git libssl-dev \
    && uv pip install --no-cache-dir . \
    && rm -rf ./build \
    && apt-mark manual curl supervisor gettext-base python3 python3-venv fonts-wqy-zenhei \
    && apt-get purge -y build-essential gcc g++ make git libssl-dev \
    && apt-get autoremove -y --purge \
    && rm -rf /var/lib/apt/lists/* && apt-get clean

# [hanbao modification] Apache-2.0 compliance: ship license & attribution files
# inside the image. As a redistributor (derivative work) we MUST include these
# even when only the image (not the source) is distributed. See known-issues I-002 / I-003.
COPY LICENSE NOTICE /app/
COPY docs/CHANGES-FROM-UPSTREAM.md /app/docs/

LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.source="https://github.com/agentscope-ai/QwenPaw"
LABEL org.opencontainers.image.description="hanbao (函包), derived from QwenPaw v2.0.1"

# [hanbao modification] Brand display name in comment
# hanbao app port (default 8088). Override at runtime with -e HANBAO_PORT=3000.
ENV HANBAO_PORT=8088
# [hanbao modification] I-007: 上架飞牛默认开启 Web Console 认证（可被 -e HANBAO_AUTH_ENABLED=false 覆盖）
ENV HANBAO_AUTH_ENABLED=true

# [hanbao modification] size-opt (2026-08-25): the build toolchain purge now
# happens inline in the install RUN above (same layer), so no separate purge
# step is needed here.

COPY deploy/config/supervisord.conf.template /etc/supervisor/conf.d/supervisord.conf.template
# [hanbao modification] I-004: DOCKER_BUILDKIT=0 (legacy builder, no --chmod) compatibility
COPY deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8088

CMD ["/entrypoint.sh"]
