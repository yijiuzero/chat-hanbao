FROM redis:7-alpine

# 健康检查
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD redis-cli ping || exit 1

EXPOSE 6379
