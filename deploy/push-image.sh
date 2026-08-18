#!/usr/bin/env bash
set -euo pipefail

# ============================================================
#  hanbao 镜像 构建 + 推送到自有仓库
#  （FPK 不构建模式的镜像分发：本机构建 -> 自有仓库 -> 飞牛 docker pull）
#
#  用法:
#    ./push-image.sh docker.io/<你的用户名>            # 推到 Docker Hub
#    ./push-image.sh registry.cn-xxx.aliyuncs.com/<ns> # 推到阿里云 ACR
#
#  可选参数:
#    --no-build   跳过本地构建，直接推送已存在的 hanbao:latest
#    --tag <tag>  指定标签（默认 latest）
#
#  前置条件:
#    - 已在目标仓库 docker login
#    - Docker daemon 已启动
#    - 构建时需能拉取基础镜像：
#        · agentscope 构建镜像(node/uv) 本机已缓存，无网络依赖
#        · python:3.12-slim(Docker Hub) 国内可能需代理，或用镜像源
#    - 必须在仓库根目录执行（Dockerfile 用相对路径 COPY）
# ============================================================

REGISTRY=""
TAG="latest"
NO_BUILD=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-build) NO_BUILD=1; shift ;;
    --tag)      TAG="$2"; shift 2 ;;
    -*)         echo "未知参数: $1" >&2; exit 1 ;;
    *)          REGISTRY="$1"; shift ;;
  esac
done

if [[ -z "$REGISTRY" ]]; then
  echo "用法: $0 <registry-prefix> [--no-build] [--tag <tag>]" >&2
  echo "示例: $0 docker.io/myuser" >&2
  exit 1
fi

IMAGE_LOCAL="hanbao:latest"
IMAGE_REMOTE="${REGISTRY}/hanbao:${TAG}"

if [[ "$NO_BUILD" -eq 0 ]]; then
  echo ">>> 构建 ${IMAGE_LOCAL} (DOCKER_BUILDKIT=0 旧构建器，规避 buildx 拉取死代理)"
  DOCKER_BUILDKIT=0 docker build -f deploy/Dockerfile -t "${IMAGE_LOCAL}" .
fi

echo ">>> 打标签 ${IMAGE_LOCAL} -> ${IMAGE_REMOTE}"
docker tag "${IMAGE_LOCAL}" "${IMAGE_REMOTE}"

echo ">>> 推送 ${IMAGE_REMOTE}"
docker push "${IMAGE_REMOTE}"

echo ""
echo ">>> 完成。飞牛 FPK 安装时设置 HANBAO_IMAGE=${IMAGE_REMOTE} 即可拉取该镜像。"
