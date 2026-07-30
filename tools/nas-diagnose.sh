#!/bin/bash
# chat-hanbao 飞牛 NAS 安装诊断脚本
# 用法：在飞牛 SSH 里执行  bash nas-diagnose.sh
# 会一次性输出所有排查所需信息，把输出整段贴回来即可定位问题。

echo "########## chat-hanbao 安装诊断 ##########"
echo "时间: $(date)"
echo

echo "===== 1. 系统与 Docker ====="
uname -a
docker --version 2>&1
docker compose version 2>&1 || docker-compose --version 2>&1
echo

echo "===== 2. 已加载的 chat-hanbao 镜像（关键！应有 4 个）====="
docker images | grep -E "REPOSITORY|chat-hanbao" || echo ">>> 没有任何 chat-hanbao 镜像，说明离线镜像未加载成功"
echo

echo "===== 3. 容器状态 ====="
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAMES|chat-hanbao" || echo ">>> 没有 chat-hanbao 容器"
echo

echo "===== 4. 应用安装目录 ====="
for d in /var/apps/chat-hanbao /var/packages/chat-hanbao; do
    if [ -d "$d" ]; then
        echo "--- $d ---"
        find "$d" -maxdepth 4 -type d 2>/dev/null | head -20
        echo "--- 内嵌镜像包 ---"
        find "$d" -name "*.tar.gz" -o -name "*.tar" 2>/dev/null | head -5 | while read -r f; do
            echo "  $f  ($(du -h "$f" | cut -f1))"
        done
    else
        echo "$d 不存在"
    fi
done
echo

echo "===== 5. cmd 脚本权限（应为 -rwxr-xr-x）====="
find /var/apps/chat-hanbao /var/packages/chat-hanbao -path '*cmd*' -maxdepth 4 -type f 2>/dev/null | head -12 | while read -r f; do
    ls -l "$f"
    head -c 20 "$f" | od -c | head -1
done
echo

echo "===== 6. 安装日志 ====="
for L in /var/log/chat-hanbao-install.log /tmp/chat-hanbao-install.log; do
    if [ -f "$L" ]; then
        echo "--- $L (最后 60 行) ---"
        tail -60 "$L"
    else
        echo "$L 不存在"
    fi
done
echo

echo "===== 7. compose 文件 ====="
CF=$(find /var/apps/chat-hanbao /var/packages/chat-hanbao -name "docker-compose.y*ml" 2>/dev/null | head -1)
if [ -n "$CF" ]; then
    echo "路径: $CF"
    cat "$CF"
else
    echo ">>> 未找到 compose 文件"
fi
echo

echo "===== 8. 容器日志（各取最后 30 行）====="
for c in chat-hanbao-postgres chat-hanbao-redis chat-hanbao-backend chat-hanbao-frontend; do
    echo "--- $c ---"
    docker logs --tail 30 "$c" 2>&1 || echo "(容器不存在)"
    echo
done

echo "===== 9. 端口 8373 占用情况 ====="
(ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null) | grep -E "8373|Local" || echo "8373 未监听"
echo

echo "===== 10. 访问自测 ====="
curl -s -o /dev/null -w "前端 http://127.0.0.1:8373  -> HTTP %{http_code}\n" --max-time 5 http://127.0.0.1:8373 2>&1
curl -s -o /dev/null -w "健康 http://127.0.0.1:8373/health -> HTTP %{http_code}\n" --max-time 5 http://127.0.0.1:8373/health 2>&1
curl -s -o /dev/null -w "接口 http://127.0.0.1:8373/api/health -> HTTP %{http_code}\n" --max-time 5 http://127.0.0.1:8373/api/health 2>&1
echo
echo "########## 诊断结束 ##########"
