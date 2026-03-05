#!/bin/bash
# 准备发布到 ClawHub 的脚本

set -e

echo "=========================================="
echo "准备发布 Brand Monitor Skill"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查必需文件
echo -e "\n${YELLOW}1. 检查必需文件...${NC}"

required_files=(
    "SKILL.md"
    "README.md"
    "LICENSE"
    "CHANGELOG.md"
    "config.example.json"
    "install.sh"
    "prompts/monitor.md"
    "prompts/alert.md"
    "prompts/analyze-trend.md"
    "crawler/search_crawler_serpapi.py"
    "crawler/requirements.txt"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
        echo -e "${RED}  ✗ 缺失: $file${NC}"
    else
        echo -e "${GREEN}  ✓ $file${NC}"
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo -e "\n${RED}错误: 缺少必需文件，请先创建这些文件${NC}"
    exit 1
fi

# 读取版本号
echo -e "\n${YELLOW}2. 读取版本号...${NC}"
version=$(grep "^version:" SKILL.md | head -1 | awk '{print $2}')
echo -e "${GREEN}  当前版本: $version${NC}"

# 清理不必要的文件
echo -e "\n${YELLOW}3. 清理不必要的文件...${NC}"

# 创建临时目录
temp_dir="brand-monitor-skill-release"
rm -rf "$temp_dir"
mkdir -p "$temp_dir"

# 复制必需文件
echo "  复制文件到临时目录..."
cp -r \
    SKILL.md \
    README.md \
    LICENSE \
    CHANGELOG.md \
    config.example.json \
    install.sh \
    prompts/ \
    crawler/ \
    快速参考.md \
    使用指南-SerpAPI版.md \
    如何使用Skill.md \
    获取飞书Webhook指南.md \
    "$temp_dir/"

# 清理临时文件
echo "  清理临时文件..."
find "$temp_dir" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$temp_dir" -name "*.pyc" -delete 2>/dev/null || true
find "$temp_dir" -name "*.pyo" -delete 2>/dev/null || true
find "$temp_dir" -name ".DS_Store" -delete 2>/dev/null || true
find "$temp_dir" -name "Thumbs.db" -delete 2>/dev/null || true
find "$temp_dir" -name "*.log" -delete 2>/dev/null || true
find "$temp_dir" -name "test_*.py" -delete 2>/dev/null || true

echo -e "${GREEN}  ✓ 清理完成${NC}"

# 创建发布包
echo -e "\n${YELLOW}4. 创建发布包...${NC}"

package_name="brand-monitor-skill-v${version}"

# 创建 tar.gz
echo "  创建 ${package_name}.tar.gz..."
tar -czf "${package_name}.tar.gz" -C "$temp_dir" .
echo -e "${GREEN}  ✓ ${package_name}.tar.gz 创建成功${NC}"

# 创建 zip
echo "  创建 ${package_name}.zip..."
(cd "$temp_dir" && zip -r "../${package_name}.zip" . -q)
echo -e "${GREEN}  ✓ ${package_name}.zip 创建成功${NC}"

# 计算文件大小
tar_size=$(du -h "${package_name}.tar.gz" | cut -f1)
zip_size=$(du -h "${package_name}.zip" | cut -f1)

echo -e "\n${GREEN}发布包创建成功:${NC}"
echo "  - ${package_name}.tar.gz (${tar_size})"
echo "  - ${package_name}.zip (${zip_size})"

# 清理临时目录
rm -rf "$temp_dir"

# 生成发布说明
echo -e "\n${YELLOW}5. 生成发布说明...${NC}"

cat > "RELEASE_NOTES_v${version}.md" << EOF
# Brand Monitor Skill v${version}

## 🎉 发布说明

新能源汽车品牌舆情监控 Skill，专为汽车品牌打造的零代码舆情监控解决方案。

## ✨ 主要特性

- 🔍 多平台监控 - 覆盖 9+ 国内主流平台
- 😊 情感分析 - 自动分析正面/中性/负面情感
- 🚨 实时警报 - 及时发现负面提及和病毒式传播
- 📊 趋势分析 - 生成品牌趋势报告
- 🎭 官方账号过滤 - 关注第三方真实声音
- ⚡ 稳定可靠 - 使用 SerpAPI 专业搜索服务

## 📦 安装

\`\`\`bash
cd ~/.openclaw/workspace/skills/
wget https://github.com/你的用户名/brand-monitor-skill/releases/download/v${version}/${package_name}.tar.gz
tar -xzf ${package_name}.tar.gz
cd brand-monitor-skill
./install.sh
\`\`\`

## 🚀 快速开始

1. 获取 SerpAPI Key: https://serpapi.com/
2. 配置环境变量: \`export SERPAPI_KEY='your_key'\`
3. 配置 config.json
4. 执行监控: \`openclaw agent --message "执行品牌监控"\`

## 📚 文档

- [README.md](README.md) - 完整文档
- [快速参考.md](快速参考.md) - 快速参考
- [如何使用Skill.md](如何使用Skill.md) - 使用指南
- [CHANGELOG.md](CHANGELOG.md) - 更新日志

## 🔄 更新内容

详见 [CHANGELOG.md](CHANGELOG.md)

## 🐛 已知问题

- 数据完整度约 50-70%（SerpAPI 限制）
- 小红书搜索结果有限
- 需要手动使用 web_fetch 补充重要内容

## 🙏 致谢

感谢所有贡献者和用户的支持！

---

**Made with ❤️ for New Energy Vehicle Brands**
EOF

echo -e "${GREEN}  ✓ RELEASE_NOTES_v${version}.md 创建成功${NC}"

# 生成 Git 命令
echo -e "\n${YELLOW}6. 下一步操作...${NC}"

cat << EOF

${GREEN}发布准备完成！${NC}

${YELLOW}下一步操作:${NC}

1. 检查发布包:
   tar -tzf ${package_name}.tar.gz | head -20

2. 初始化 Git 仓库（如果还没有）:
   git init
   git add .
   git commit -m "Release v${version}"

3. 创建 GitHub 仓库并推送:
   git remote add origin https://github.com/你的用户名/brand-monitor-skill.git
   git branch -M main
   git push -u origin main

4. 创建 Git Tag:
   git tag -a v${version} -m "Release v${version}"
   git push origin v${version}

5. 在 GitHub 上创建 Release:
   - 访问: https://github.com/你的用户名/brand-monitor-skill/releases/new
   - Tag: v${version}
   - Title: Brand Monitor Skill v${version}
   - 描述: 复制 RELEASE_NOTES_v${version}.md 的内容
   - 上传: ${package_name}.tar.gz 和 ${package_name}.zip

6. 提交到 ClawHub:
   - 访问 ClawHub 网站
   - 提交 Skill
   - Git URL: https://github.com/你的用户名/brand-monitor-skill.git

${YELLOW}详细步骤请查看: 发布到ClawHub指南.md${NC}

EOF

echo "=========================================="
echo "准备完成！"
echo "=========================================="
