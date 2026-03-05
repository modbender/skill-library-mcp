#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          AI协作操作系统 - 一键安装                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未检测到Node.js，请先安装Node.js (>= 16.0.0)"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js版本过低，需要 >= 16.0.0，当前: $(node -v)"
    exit 1
fi

echo "✅ Node.js版本: $(node -v)"
echo ""

# 安装依赖
echo "【1/3】安装依赖..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi
echo "✅ 依赖安装完成"
echo ""

# 编译TypeScript
echo "【2/3】编译TypeScript..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ 编译失败"
    exit 1
fi
echo "✅ 编译完成"
echo ""

# 创建记忆目录
echo "【3/3】初始化记忆目录..."
mkdir -p memory/ai_system/{L0_flash,L1_working,L2_experience,L3_knowledge,L4_wisdom,shared,logs}
echo "✅ 记忆目录创建完成"
echo ""

# 验证安装
echo "【验证】运行测试..."
node dist/example.js
if [ $? -ne 0 ]; then
    echo "❌ 测试失败"
    exit 1
fi
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              ✅ 安装完成！                                  ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║  使用方式:                                                 ║"
echo "║                                                            ║"
echo "║  import { AICollaborationSystem } from './dist/index';     ║"
echo "║  const ai = new AICollaborationSystem('my_system');        ║"
echo "║                                                            ║"
echo "║  文档:                                                     ║"
echo "║  • README.md - 快速开始                                    ║"
echo "║  • docs/完整使用手册.md - 详细文档                         ║"
echo "║  • docs/集中部署指南.md - 部署说明                         ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
