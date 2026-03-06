#!/bin/bash
# Export portable packages for deployment - 优化版

set -e

# 可通过环境变量自定义路径
: "${PORTABLE_DIR:=$(cd "$(dirname "${BASH_SOURCE[0]}")/../portable" && pwd)}"
: "${OUTPUT_DIR:=$(cd "$(dirname "${BASH_SOURCE[0]}")/../export" && pwd)}"

echo "=========================================="
echo "Exporting OpenClaw Portable Packages"
echo "=========================================="

# 检查源目录
if [ ! -d "$PORTABLE_DIR" ]; then
    echo "❌ 错误: 便携版目录不存在: $PORTABLE_DIR"
    echo "   请先运行 build-portable.sh"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Create clean package
echo ""
echo "📦 Packaging clean version..."
if [ -d "$PORTABLE_DIR/clean" ]; then
    tar -czf "$OUTPUT_DIR/openclaw-clean-portable.tar.gz" -C "$PORTABLE_DIR" clean/
    echo "✅ Clean: openclaw-clean-portable.tar.gz ($(du -h $OUTPUT_DIR/openclaw-clean-portable.tar.gz | cut -f1))"
else
    echo "⚠️  Clean version not found, skipping"
fi

# Create full package
echo ""
echo "📦 Packaging full version..."
if [ -d "$PORTABLE_DIR/full" ]; then
    tar -czf "$OUTPUT_DIR/openclaw-full-portable.tar.gz" -C "$PORTABLE_DIR" full/
    echo "✅ Full: openclaw-full-portable.tar.gz ($(du -h $OUTPUT_DIR/openclaw-full-portable.tar.gz | cut -f1))"
else
    echo "⚠️  Full version not found, skipping"
fi

# Create deployment script
cat > "$OUTPUT_DIR/deploy.sh" <>>> "$OUTPUT_DIR/README.md" << 'EOF'
# OpenClaw 部署包

## 文件说明

- `openclaw-clean-portable.tar.gz` - 纯净版
- `openclaw-full-portable.tar.gz` - 完整版含配置
- `install-node.sh` - Node.js 安装脚本
- `deploy.sh` - 远程部署脚本

## 部署步骤

### 1. 在目标服务器安装 Node.js
```bash
./install-node.sh
```

### 2. 解压并启动
```bash
# 纯净版
tar -xzf openclaw-clean-portable.tar.gz
cd clean
./start.sh

# 完整版
tar -xzf openclaw-full-portable.tar.gz
cd full
./start.sh
```

### 3. 或使用部署脚本
```bash
./deploy.sh user@remote-server clean /opt/openclaw
./deploy.sh user@remote-server full /opt/openclaw
```

## 访问服务
- WebUI: http://localhost:18789

## 版本信息
- 版本: v1.0.1
- 作者: zfanmy-梦月儿
EOF

echo ""
echo "=========================================="
echo "Export completed!"
echo ""
echo "Files in: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR" 2>/dev/null || echo "No files exported"
echo ""
echo "Deploy example:"
echo "  cd $OUTPUT_DIR"
echo "  ./deploy.sh user@remote clean /opt/openclaw"
echo "=========================================="
