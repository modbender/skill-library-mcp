# 容器部署指南

## Docker 配置

### Dockerfile.base

```dockerfile
# 切换到root用户
ARG DIR="/home/export/App"

# 创建必要的目录
RUN mkdir -p /export/Data && chmod 777 /export/Data && mkdir -p /home/export/App

RUN node -v && npm -v && npm config set registry=http://registry.m.jd.com

# 修复sharpjnpm镜像过不去的问题
RUN npm config set sharp_binary_host "https://npmmirror.com/mirrors/sharp" && \
npm config set sharp_libvips_binary_host "https://npmmirror.com/mirrors/sharp-libvips"

WORKDIR ${DIR}
COPY . ${DIR}
RUN chmod 777 /home/export/App/ && npm install

# 添加版本管理和部署脚本执行权限
RUN chmod +x /home/export/App/scripts/*.sh && chmod +x /home/export/App/start.sh

# 暴露端口
EXPOSE 80

ENTRYPOINT  /usr/sbin/sshd &&  /usr/sbin/crond && \
  echo '启动自定义start脚本:' &&  /home/export/App/start.sh
```

## 启动脚本

### start.sh

```bash
#!/bin/bash

set -e

# 环境配置 - 优先使用 NODE_ENV 环境变量
ENVIRONMENT=${NODE_ENV:-${1:-production}}

# 工作目录设置
[ -d "/home/export/App" ] && cd /home/export/App

# JDOS 端口配置
export APP_PORT=${PORT:-${APP_PORT:-3000}}
export PORT=${PORT:-${APP_PORT:-3000}}
export HOST=${HOST:-0.0.0.0}
export SERVER_NAME=${SERVER_NAME:-magicbox-node-service}

# 确保 NODE_ENV 环境变量设置正确
export NODE_ENV=$ENVIRONMENT

# 构建应用
npm run build

# 检查构建结果
[ ! -f "dist/app.js" ] && {
    echo "Error: Build failed"
    exit 1
}

# 启动服务
node dist/app.js
```

## 部署脚本

### deploy-manual.sh

```bash
#!/bin/bash

set -e

echo "=== MagicBox Node Service Deployment ==="

# 命令行参数
ENVIRONMENT=${1:-production}

echo "Environment: $ENVIRONMENT"

# 1. 版本管理
echo "=== Step 1: Version Management ==="
chmod +x scripts/version-manager.sh
./scripts/version-manager.sh "$ENVIRONMENT"

# 2. 安装依赖
echo "=== Step 2: Installing Dependencies ==="
npm install --production

# 3. 构建应用
echo "=== Step 3: Building Application ==="
npm run build

if [ $? -ne 0 ]; then
    echo "Build failed, exiting"
    exit 1
fi

if [ ! -d "dist" ] || [ ! -f "dist/app.js" ]; then
    echo "Build artifacts not found, exiting"
    exit 1
fi

echo "Build completed successfully"

# 4. 复制版本信息到 dist
echo "=== Step 4: Copying Version Info ==="
if [ -f "version.json" ]; then
    cp version.json dist/
    echo "Version info copied to dist/version.json"
fi

echo "=== Deployment Completed Successfully ==="
echo "Service is ready for containerization"
```

## 版本管理脚本

### version-manager.sh

```bash
#!/bin/bash

set -e

# 版本文件
VERSION_FILE="version.json"

# 检查版本文件
if [ ! -f "$VERSION_FILE" ]; then
    cat > "$VERSION_FILE" << EOF
{
  "version": "1.0.0",
  "deployTimestamp": "",
  "deployEnvironment": "",
  "deployUser": "",
  "gitCommit": ""
}
EOF
fi

# 读取当前版本
CURRENT_VERSION=$(grep -E '"version":' "$VERSION_FILE" | awk -F'"' '{print $4}' || echo "1.0.0")

# 生成新版本号
NEW_VERSION=$(echo "$CURRENT_VERSION" | awk -F. '{print $1"."$2"."$3+1}')

# 更新版本信息
ENVIRONMENT=${1:-production}
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
USER=$(whoami)
GIT_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "N/A")

# 更新版本文件
cat > "$VERSION_FILE" << EOF
{
  "version": "$NEW_VERSION",
  "deployTimestamp": "$TIMESTAMP",
  "deployEnvironment": "$ENVIRONMENT",
  "deployUser": "$USER",
  "gitCommit": "$GIT_COMMIT"
}
EOF

# 复制到 dist 目录
[ -d "dist" ] && cp "$VERSION_FILE" dist/
```

## Kubernetes 配置

### 部署配置

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: magicbox-node
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: magicbox-node
  template:
    metadata:
      labels:
        app: magicbox-node
    spec:
      containers:
      - name: magicbox-node
        image: magicbox-node:latest
        ports:
        - containerPort: 80
        env:
        - name: NODE_ENV
          value: "production"
        - name: PORT
          value: "80"
        - name: HOST
          value: "0.0.0.0"
        - name: SERVER_NAME
          value: "magicbox-node-service"
        volumeMounts:
        - name: config-volume
          mountPath: /etc/magicbox-node
      volumes:
      - name: config-volume
        configMap:
          name: magicbox-node-config
```

### 配置映射

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: magicbox-node-config
  namespace: default
data:
  env.config.json: |
    {
      "NODE_ENV": "production",
      "PORT": "80",
      "HOST": "0.0.0.0",
      "SERVER_NAME": "magicbox-node-service",
      "DB_HOST": "database-host",
      "DB_PORT": "3306",
      "DB_DATABASE": "magicbox",
      "DB_USERNAME": "username",
      "DB_PASSWORD": "password"
    }
```

### 服务配置

```yaml
apiVersion: v1
kind: Service
metadata:
  name: magicbox-node
  namespace: default
spec:
  selector:
    app: magicbox-node
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

## 部署流程

1. **构建镜像**：`docker build -t magicbox-node:latest -f Dockerfile.base .`
2. **推送镜像**：`docker push magicbox-node:latest`
3. **部署到 Kubernetes**：`kubectl apply -f kubernetes/deployment.yaml`
4. **验证部署**：`kubectl get pods`
5. **检查服务状态**：`kubectl logs magicbox-node-xxx`

## 健康检查

### 健康检查端点

```typescript
router.get('/health', (req, res) => {
  res.json({
    success: true,
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'magicBox-node-service'
  });
});
```

### Kubernetes 健康检查配置

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 80
  initialDelaySeconds: 30
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /health
    port: 80
  initialDelaySeconds: 5
  periodSeconds: 5
```

## 故障排查

### 常见问题

1. **容器启动失败**：检查 `/export/Data` 目录是否存在
2. **数据库连接失败**：检查数据库配置是否正确
3. **配置文件未加载**：检查 `/etc/magicbox-node/env.config.json` 是否存在
4. **端口冲突**：检查容器端口映射是否正确

### 日志查看

```bash
# 查看容器日志
kubectl logs magicbox-node-xxx

# 查看部署状态
kubectl describe deployment magicbox-node

# 查看服务状态
kubectl describe service magicbox-node
```

## 最佳实践

1. **镜像版本管理**：使用语义化版本号
2. **配置分离**：使用 ConfigMap 管理配置
3. **健康检查**：配置适当的健康检查
4. **资源限制**：设置合理的资源限制
5. **滚动更新**：使用滚动更新策略
6. **监控**：配置适当的监控和告警
7. **备份**：定期备份配置和数据