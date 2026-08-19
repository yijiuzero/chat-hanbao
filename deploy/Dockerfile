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
# desktop_screenshot) was removed. build-essential is installed only to
# compile any source wheels during `uv pip install` and purged afterwards.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    supervisor \
    gettext-base \
    libssl-dev \
    build-essential \
    python3 \
    python3-venv \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get clean

# Indicate running in container (used by telemetry/secret-store guards).
ENV HANBAO_RUNNING_IN_CONTAINER=1

WORKDIR ${WORKSPACE_DIR}

RUN python3 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# [hanbao modification] Reorder for layer caching: install Python deps first.
# A minimal package stub (__init__.py + __version__.py) lets uv resolve
# dependencies without requiring the full source tree; PYTHONPATH makes
# the stub discoverable by setuptools.
COPY pyproject.toml setup.py README.md ./
COPY --from=uv-src /uv /bin/uv
ENV PYTHONPATH=/app/src
RUN mkdir -p src/hanbao && \
    echo '' > src/hanbao/__init__.py && \
    echo '__version__ = "0.0.1"' > src/hanbao/__version__.py && \
    uv pip install --no-cache-dir . && \
    rm -rf ./build && rm -rf src/hanbao

# Copy real source and reinstall (dependencies already in venv from above).
COPY src ./src
COPY website/public/docs/ ./src/hanbao/docs/
# Inject console dist from build stage (repo does not commit dist).
COPY --from=console-builder /app/console/dist/ ./src/hanbao/console/
RUN uv pip install --no-cache-dir --no-deps . && rm -rf ./build

# [hanbao modification] Apache-2.0 compliance: ship license & attribution files
# inside the image. As a redistributor (derivative work) we MUST include these
# even when only the image (not the source) is distributed. See known-issues I-002 / I-003.
COPY LICENSE NOTICE /app/
COPY docs/CHANGES-FROM-UPSTREAM.md /app/docs/

LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.source="https://github.com/agentscope-ai/QwenPaw"
LABEL org.opencontainers.image.description="hanbao (函包), derived from Hanbao v2.0.1"

# [hanbao modification] Brand display name in comment
# hanbao app port (default 8088). Override at runtime with -e HANBAO_PORT=3000.
ENV HANBAO_PORT=8088
# [hanbao modification] I-007: 上架飞牛默认开启 Web Console 认证（可被 -e HANBAO_AUTH_ENABLED=false 覆盖）
ENV HANBAO_AUTH_ENABLED=true

# [hanbao modification] I-004: remove the build toolchain from the final image.
RUN apt-get purge -y build-essential gcc g++ make && \
    rm -rf /var/lib/apt/lists/* && apt-get clean

COPY deploy/config/supervisord.conf.template /etc/supervisor/conf.d/supervisord.conf.template
# [hanbao modification] I-004: DOCKER_BUILDKIT=0 (legacy builder, no --chmod) compatibility
COPY deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8088

CMD ["/entrypoint.sh"]
