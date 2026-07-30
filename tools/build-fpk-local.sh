#!/bin/bash
# ============================================================
# 本地一键打包离线 fpk（Windows / Git Bash）
#
# 用途：改完 fpk/ 下的脚本或配置后，无需 Docker、无需推 GitHub，
#       本地 30 秒直接出可安装的 fpk。
#
# 前置条件（只需满足一次）：
#   1. tools/fnpack.exe            —— 飞牛官方打包工具
#   2. fpk/app/docker/images/chat-hanbao-images.tar.gz
#      —— 内嵌的 4 个 Docker 镜像（约 276MB，已缓存，不入 git）
#
# 什么时候必须回到 GitHub Actions：
#   仅当修改了 backend/ 或 frontend/ 的源码或 Dockerfile —— 那需要
#   重新 docker build 生成镜像，本机没装 Docker 做不到。
#   只改 fpk/cmd/*、docker-compose.yaml、config/* 时，用本脚本即可。
#
# 用法：  bash tools/build-fpk-local.sh
# ============================================================
set -euo pipefail

cd "$(dirname "$0")/.."
ROOT="$(pwd)"
# manifest 为 key = value 格式，取 version 行
VERSION="$(grep -E '^version' fpk/manifest | head -1 | sed 's/.*=[[:space:]]*//' | tr -d '[:space:]')"
[ -n "$VERSION" ] || VERSION="1.0.0"
OUT="build/chat-hanbao-${VERSION}.fpk"
IMAGES="fpk/app/docker/images/chat-hanbao-images.tar.gz"

echo "=========================================="
echo " 本地打包离线 fpk  v${VERSION}"
echo "=========================================="

# ---------- 1. 前置检查 ----------
[ -f tools/fnpack.exe ] || { echo "ERROR: 缺少 tools/fnpack.exe"; exit 1; }
if [ ! -f "$IMAGES" ]; then
  echo "ERROR: 缺少内嵌镜像包 $IMAGES"
  echo "  这是离线安装的核心，本机无 Docker 无法生成。"
  echo "  恢复办法：从已有 fpk 中提取 ——"
  echo "    tar -xzf build/chat-hanbao-*.fpk -C /tmp app.tgz"
  echo "    tar -xzf /tmp/app.tgz -C fpk/app/docker/images --strip-components=2 docker/images/chat-hanbao-images.tar.gz"
  exit 1
fi
IMG_SIZE=$(stat -c%s "$IMAGES")
echo "[1/6] 镜像缓存 OK  ($((IMG_SIZE/1024/1024)) MB)"

# ---------- 2. 归一化行尾 ----------
# Windows 的 CRLF 会让 Linux 报 bad interpreter: /bin/bash^M
for f in fpk/cmd/* fpk/manifest fpk/config/*; do
  [ -f "$f" ] && sed -i 's/\r$//' "$f"
done
echo "[2/6] 行尾归一化为 LF  OK"

# ---------- 3. 语法检查 ----------
for s in fpk/cmd/*; do
  bash -n "$s" || { echo "SYNTAX ERROR: $s"; exit 1; }
done
echo "[3/6] shell 语法检查通过  ($(ls fpk/cmd | wc -l) 个脚本)"

# ---------- 4. fnpack 打包 ----------
rm -f "$ROOT"/*.fpk
./tools/fnpack.exe build fpk >/dev/null 2>&1 || { echo "ERROR: fnpack 打包失败"; ./tools/fnpack.exe build fpk; exit 1; }
RAW=$(ls -1 "$ROOT"/*.fpk 2>/dev/null | head -1)
[ -n "$RAW" ] || { echo "ERROR: 未生成 fpk"; exit 1; }
echo "[4/6] fnpack 打包完成  ($(( $(stat -c%s "$RAW") /1024/1024 )) MB)"

# ---------- 5. 修复执行权限并重打包 ----------
# Windows 文件系统无 Unix 执行位，fnpack.exe 会把 cmd/* 写成 0666，
# 装到飞牛上一律 Permission denied —— 必须用 GNU tar 重打包修正。
rm -rf build/_repack && mkdir -p build/_repack build
tar -xzf "$RAW" -C build/_repack
chmod +x build/_repack/cmd/*
mkdir -p "$(dirname "$OUT")"
rm -f "$OUT"
( cd build/_repack && tar -I 'gzip -1' --owner=0 --group=0 --numeric-owner \
    -cf "../../$OUT" app.tgz cmd config ICON.PNG ICON_256.PNG manifest wizard )
rm -rf build/_repack "$RAW"
echo "[5/6] 执行权限修复完成  (cmd/* -> 0755)"

# ---------- 6. 产物自检 ----------
SIZE=$(stat -c%s "$OUT")
if [ "$SIZE" -lt 52428800 ]; then
  echo "ERROR: fpk 仅 $((SIZE/1024/1024))MB，内嵌镜像未打包成功"; exit 1
fi
BAD=$(tar -tzvf "$OUT" | grep '^-' | grep 'cmd/' | grep -cv '^-rwx' || true)
if [ "$BAD" != "0" ]; then
  echo "ERROR: 仍有 $BAD 个 cmd 脚本没有执行权限"; exit 1
fi
echo "[6/6] 自检通过"
echo ""
echo "=========================================="
echo " 产物: $OUT"
echo " 大小: $((SIZE/1024/1024)) MB  ($SIZE bytes)"
echo " 权限: cmd/* 全部 -rwxr-xr-x"
echo "=========================================="
echo ""
echo "下一步：上传到飞牛 -> 应用中心 -> 手动安装"
