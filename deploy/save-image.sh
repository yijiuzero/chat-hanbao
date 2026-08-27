#!/usr/bin/env bash
# ============================================================
#  [hanbao modification] 导出 hanbao 镜像为 tar，随 FPK 应用包分发
#
#  飞牛 FPK「docker-project 形态」自带镜像模式（上架飞牛官方应用中心）：
#    镜像 tar 随 FPK 内置，由 FPK 内的 install_callback 在安装时 `docker load`
#    （见 deploy/fpk/cmd/install_callback），随后飞牛按 config/resource 的 docker-project
#    声明接管容器生命周期；compose 设 pull_policy: never，全程不向外部仓库拉取。
#    更新时发布新 FPK 包（内含新镜像 tar）覆盖即可，更新也走 FPK。
#
#  用法:
#    ./deploy/save-image.sh                              # 导出当前 hanbao:latest -> deploy/fpk/app/docker/hanbao-amd64.tar
#    ./deploy/save-image.sh output/my.tar                # 指定输出路径
#    BUILD=0 ./deploy/save-image.sh                      # 跳过构建，只导出已存在的镜像
#
#  前置条件:
#    - Docker daemon 已启动
#    - 如需构建：agentscope 构建镜像(node/uv)本机已缓存；
#      python:3.12-slim(Docker Hub) 国内或需代理/镜像源
#    - 必须在仓库根目录执行（Dockerfile 用相对路径 COPY）
# ============================================================
set -euo pipefail

IMAGE="${HANBAO_IMAGE:-hanbao:latest}"
OUT="${1:-deploy/fpk/app/docker/hanbao-amd64.tar}"
BUILD="${BUILD:-1}"

if [[ "$BUILD" != "0" ]]; then
  echo ">>> 构建 ${IMAGE} (DOCKER_BUILDKIT=0，规避 buildx 拉取死代理)"
  DOCKER_BUILDKIT=0 docker build -f deploy/Dockerfile -t "${IMAGE}" .
fi

echo ">>> 导出 ${IMAGE} -> ${OUT}"
mkdir -p "$(dirname "$OUT")"
docker save "${IMAGE}" -o "${OUT}"
echo "完成: ${OUT} ($(du -h "$OUT" | cut -f1))"
echo "该 tar 默认落在 deploy/fpk/app/docker/hanbao-amd64.tar，随 FPK 打包；install_callback 在安装时 docker load。"
