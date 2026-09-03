#!/usr/bin/env bash
# ============================================================
# hanbao 一键发版（飞牛 FPK 离线分发）
# [hanbao] 维护脚本，非上游产物
#
# 串联：构建镜像 → 导出离线 tar → 更新 manifest 版本/changelog
#       → fnpack 打包 → 产出 .fpk
#
# 用法:
#   ./deploy/release.sh                         # 仅用现有 tar 重新打包（首发上架用）
#   SKIP_BUILD=1 ./deploy/release.sh            # 同上，显式跳过镜像构建
#   ./deploy/release.sh 0.2.0                   # 新版本：重建镜像 + 改版本号 + 打包
#   ./deploy/release.sh 0.2.0 changelog.txt    # 额外从文件写入 changelog
#   CHANGELOG=$'修复微信重连\n新增XX' ./deploy/release.sh 0.2.0
#
# 前置:
#   - Docker Desktop 已启动（脚本会校验 daemon 可达）
#   - 在仓库根目录执行
#   - Windows 用 Git Bash 运行（fnpack.exe 为 Windows 二进制）
# ============================================================
set -euo pipefail

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

MANIFEST="deploy/fpk/manifest"
DOCKERFILE="deploy/Dockerfile"
TAR="deploy/fpk/app/docker/hanbao-amd64.tar"
FNPACK="./deploy/tools/fnpack.exe"

NEW_VERSION="${1:-}"
CHANGELOG_FILE="${2:-}"
SKIP_BUILD="${SKIP_BUILD:-0}"

# 校验 manifest 存在
if [ ! -f "$MANIFEST" ]; then
  echo "错误: 找不到 $MANIFEST" >&2
  exit 1
fi

CUR_VERSION="$(grep -E '^version=' "$MANIFEST" | head -1 | cut -d= -f2)"
echo ">>> 当前 manifest 版本: ${CUR_VERSION}${NEW_VERSION:+"  ->  新版本: ${NEW_VERSION}"}"

# 0. 校验 docker daemon（除非跳过构建）
if [[ "$SKIP_BUILD" != "1" ]]; then
  if ! docker version >/dev/null 2>&1; then
    echo "错误: 无法连接 Docker daemon，请先启动 Docker Desktop。" >&2
    exit 1
  fi
  echo ">>> 构建 hanbao:latest 并导出离线镜像 tar ..."
  DOCKER_BUILDKIT=0 docker build -f "$DOCKERFILE" -t hanbao:latest .
  mkdir -p "$(dirname "$TAR")"
  docker save hanbao:latest -o "$TAR"
  echo "    镜像 tar: $(du -h "$TAR" | cut -f1)"
else
  echo ">>> 跳过镜像构建，使用现有 tar: $TAR"
fi

# 1. 更新版本号
if [ -n "$NEW_VERSION" ]; then
  sed -i.bak -E "s/^version=.*/version=${NEW_VERSION}/" "$MANIFEST"
  rm -f "${MANIFEST}.bak"
  echo "    manifest version -> $NEW_VERSION"
fi

# 2. 更新 changelog
CHANGELOG="${CHANGELOG:-}"
if [ -n "$CHANGELOG_FILE" ] && [ -f "$CHANGELOG_FILE" ]; then
  CHANGELOG="$(cat "$CHANGELOG_FILE")"
fi
if [ -n "$CHANGELOG" ]; then
  # manifest 的 changelog 用字面量 \n 分隔条目
  CL_ESCAPED="$(printf '%s' "$CHANGELOG" | sed ':a;N;$!ba;s/\n/\\n/g')"
  sed -i.bak -E "@changelog=.*@changelog=${CL_ESCAPED}@" "$MANIFEST"
  rm -f "${MANIFEST}.bak"
  echo "    manifest changelog 已更新"
fi

# 3. fnpack 打包
if [ ! -f "$FNPACK" ]; then
  echo "错误: 找不到 $FNPACK" >&2
  exit 1
fi
echo ">>> fnpack 打包 ..."
"$FNPACK" build -d deploy/fpk

# 4. 定位产物
FPK="$(find . -maxdepth 2 -name 'hanbao.fpk' 2>/dev/null | head -1)"
echo ""
echo "完成! 产物: ${FPK:-<未找到，请检查 deploy/fpk/ 或仓库根目录>}"
if [ -n "$FPK" ]; then
  echo "大小: $(du -h "$FPK" | cut -f1)"
fi
echo ""
echo "下一步（二选一）:"
echo "  A. 飞牛官方应用中心: 去 https://developer.fnnas.com 注册开发者 -> 提交该 .fpk 审核"
echo "  B. 第三方源(FnDepot/2FStore): 上传 .fpk 到源，用户在 fnOS 添加源即可安装"
echo "升级时: 发新 .fpk（含新 tar），用户在应用中心点『升级』，凭据与数据自动保留。"
