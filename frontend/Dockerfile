# 构建阶段
FROM node:22-alpine AS builder

WORKDIR /app

# 安装依赖
COPY package.json .
RUN npm install

# 复制源码
COPY . .

# 构建（API 请求通过 nginx 代理到后端）
ENV VITE_API_BASE=/api
RUN npm run build

# 运行阶段 - 使用 nginx
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 健康检查
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
