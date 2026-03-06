---
name: Dockerfile Generator
description: 根据应用类型自动生成优化的 Dockerfile。
---

# Dockerfile Generator

根据应用类型自动生成优化的 Dockerfile。

## 功能

- 多语言支持 (Node.js, Python, Go, Java等)
- 多阶段构建优化
- 最佳实践自动应用
- 性能优化

## 触发词

- "生成Dockerfile"
- "docker配置"
- "containerize"

## 支持模板

```dockerfile
# Node.js
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]

# Python
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]

# Go (多阶段构建)
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o main .
FROM alpine
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
```
