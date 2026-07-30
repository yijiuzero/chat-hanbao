FROM redis:7-alpine

# 自定义 Redis 配置
COPY ./redis.conf /usr/local/etc/redis/redis.conf

# 健康检查
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD redis-cli ping || exit 1

EXPOSE 6379

CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
