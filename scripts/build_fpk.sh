#!/bin/bash
# Chat Hanbao - FPK 打包脚本
# 用法: ./scripts/build_fpk.sh [版本号]

set -e

VERSION=${1:-1.0.0}
FPK_NAME="chat-hanbao-${VERSION}.fpk"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FPK_DIR="${PROJECT_DIR}/fpk"
BUILD_DIR="${PROJECT_DIR}/build"

echo "========================================="
echo "  Chat Hanbao FPK 打包"
echo "  版本: ${VERSION}"
echo "========================================="

# 检查 fnpack 工具
if ! command -v fnpack &> /dev/null; then
    echo "[WARN] fnpack 未找到，请从以下地址下载:"
    echo "  https://developer.fnnas.com/"
    echo "  并确保 fnpack 在 PATH 中"
    exit 1
fi

# 清理并创建构建目录
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

# 复制 FPK 目录内容
echo "[1/4] 复制文件..."
cp -r "${FPK_DIR}"/* "${BUILD_DIR}/"

# 更新 manifest 中的版本号
echo "[2/4] 更新版本号..."
sed -i "s/^version=.*/version=${VERSION}/" "${BUILD_DIR}/manifest"

# 创建图标（如果不存在）
echo "[3/4] 检查图标..."
if [ ! -f "${BUILD_DIR}/app/ui/images/icon.png" ]; then
    echo "  生成图标..."
    python3 "${SCRIPT_DIR}/gen_icons.py"
    cp "${PROJECT_DIR}/fpk/app/ui/images/icon.png" "${BUILD_DIR}/app/ui/images/"
    cp "${PROJECT_DIR}/fpk/app/ui/images/icon_256.png" "${BUILD_DIR}/app/ui/images/"
fi

# 打包 FPK
echo "[4/4] 打包 FPK..."
cd "${BUILD_DIR}"
fnpack create "${FPK_NAME}" .

echo ""
echo "========================================="
echo "  打包完成！"
echo "  文件: ${BUILD_DIR}/${FPK_NAME}"
echo "========================================="
echo ""
echo "安装到飞牛 NAS:"
echo "  1. 将 ${FPK_NAME} 上传到飞牛 NAS"
echo "  2. 飞牛桌面 → 应用中心 → 右上角设置 → 手动安装应用"
echo "  3. 选择 ${FPK_NAME} 文件"
echo "  4. 安装完成后点击图标启动"
