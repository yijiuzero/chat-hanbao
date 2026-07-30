FROM postgres:16-alpine

# 健康检查
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD pg_isready -U chatuser -d chatdb

EXPOSE 5432
