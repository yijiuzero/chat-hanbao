#!/bin/bash
# Chat Hanbao - 构建并推送 Docker 镜像到 Docker Hub
# 用法: ./scripts/build_and_push.sh

set -e

VERSION="1.0.0"
DOCKERHUB_USER="yijiuzero"

echo "========================================="
echo "  Chat Hanbao - 构建 & 推送镜像"
echo "  用户: ${DOCKERHUB_USER}"
echo "  版本: ${VERSION}"
echo "========================================="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker 未安装"
    exit 1
fi

# 检查是否已登录
if ! docker info 2>/dev/null | grep -q "Username"; then
    echo "[INFO] 请先登录 Docker Hub:"
    echo "  docker login"
    exit 1
fi

echo ""
echo "[1/8] 构建 PostgreSQL 镜像..."
docker build -t ${DOCKERHUB_USER}/chat-hanbao-postgres:${VERSION} ./backend/postgres/
docker tag ${DOCKERHUB_USER}/chat-hanbao-postgres:${VERSION} ${DOCKERHUB_USER}/chat-hanbao-postgres:latest

echo ""
echo "[2/8] 构建 Redis 镜像..."
docker build -t ${DOCKERHUB_USER}/chat-hanbao-redis:${VERSION} ./backend/redis/
docker tag ${DOCKERHUB_USER}/chat-hanbao-redis:${VERSION} ${DOCKERHUB_USER}/chat-hanbao-redis:latest

echo ""
echo "[3/8] 构建后端镜像..."
docker build -t ${DOCKERHUB_USER}/chat-hanbao-backend:${VERSION} ./backend/
docker tag ${DOCKERHUB_USER}/chat-hanbao-backend:${VERSION} ${DOCKERHUB_USER}/chat-hanbao-backend:latest

echo ""
echo "[4/8] 构建前端镜像..."
docker build -t ${DOCKERHUB_USER}/chat-hanbao-frontend:${VERSION} ./frontend/
docker tag ${DOCKERHUB_USER}/chat-hanbao-frontend:${VERSION} ${DOCKERHUB_USER}/chat-hanbao-frontend:latest

echo ""
echo "[5/8] 推送 PostgreSQL..."
docker push ${DOCKERHUB_USER}/chat-hanbao-postgres:${VERSION}
docker push ${DOCKERHUB_USER}/chat-hanbao-postgres:latest

echo ""
echo "[6/8] 推送 Redis..."
docker push ${DOCKERHUB_USER}/chat-hanbao-redis:${VERSION}
docker push ${DOCKERHUB_USER}/chat-hanbao-redis:latest

echo ""
echo "[7/8] 推送后端..."
docker push ${DOCKERHUB_USER}/chat-hanbao-backend:${VERSION}
docker push ${DOCKERHUB_USER}/chat-hanbao-backend:latest

echo ""
echo "[8/8] 推送前端..."
docker push ${DOCKERHUB_USER}/chat-hanbao-frontend:${VERSION}
docker push ${DOCKERHUB_USER}/chat-hanbao-frontend:latest

echo ""
echo "========================================="
echo "  全部完成！"
echo "========================================="
echo ""
echo "镜像列表:"
docker images | grep "${DOCKERHUB_USER}/chat-hanbao"
echo ""
echo "下一步: 打包 FPK"
echo "  ./scripts/build_fpk.sh ${VERSION}"
