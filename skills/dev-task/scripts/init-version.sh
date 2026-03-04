#!/bin/bash
# 初始化新版本目录结构
# 用法: ./init-version.sh <项目路径> <版本号>

PROJECT_PATH=$1
VERSION=$2

if [ -z "$PROJECT_PATH" ] || [ -z "$VERSION" ]; then
    echo "Usage: $0 <项目路径> <版本号>"
    echo "Example: $0 ./my-project v1.1.0"
    exit 1
fi

if [ ! -d "$PROJECT_PATH" ]; then
    echo "Error: Project path does not exist: $PROJECT_PATH"
    exit 1
fi

cd "$PROJECT_PATH"

# 创建版本目录
echo "Creating version directory: versions/$VERSION"
mkdir -p "versions/$VERSION"/{docs,src,release}

# 获取 skill 模板路径
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="$SKILL_DIR/references"

# 复制文档模板
echo "Creating documentation..."
cp "$TEMPLATE_DIR/CHANGELOG.template.md" "versions/$VERSION/docs/CHANGELOG.md"
cp "$TEMPLATE_DIR/REQUIREMENTS.template.md" "versions/$VERSION/docs/REQUIREMENTS.md"
cp "$TEMPLATE_DIR/DEPLOY.template.md" "versions/$VERSION/docs/DEPLOY.md"

# 替换版本号占位符
sed -i "s/vX.Y.Z/$VERSION/g" "versions/$VERSION/docs/"*.md

# 备份当前代码
echo "Backing up current code..."
# 根据项目类型备份不同文件
if [ -f "package.json" ]; then
    # Node.js 项目
    cp package.json "versions/$VERSION/src/"
    [ -f "server.js" ] && cp server.js "versions/$VERSION/src/"
    [ -f "app.js" ] && cp app.js "versions/$VERSION/src/"
    [ -d "public" ] && cp -r public "versions/$VERSION/src/"
    [ -d "src" ] && cp -r src "versions/$VERSION/src/source"
fi

echo "✅ Version $VERSION initialized successfully!"
echo ""
echo "Next steps:"
echo "1. Edit versions/$VERSION/docs/REQUIREMENTS.md - Define requirements"
echo "2. Start development"
echo "3. Update versions/$VERSION/docs/CHANGELOG.md - Track changes"
echo "4. Complete versions/$VERSION/docs/DEPLOY.md - Deployment guide"
