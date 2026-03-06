# Bocha Search Skill for OpenClaw

🔍 博查AI搜索技能 - 专为 OpenClaw 设计的智能搜索工具

## 功能特点

- ✅ **中文优化**: 针对中文搜索内容特别优化
- ✅ **简单易用**: 仅需提供 API Key 和搜索语句
- ✅ **快速响应**: 通常 1-2 秒内返回结果
- ✅ **灵活配置**: 支持环境变量或配置文件设置

## 安装方法

### 方法一：直接克隆到工作区（推荐）

```bash
# 进入你的 OpenClaw 工作区
cd ~/.openclaw/workspace/skills

# 克隆 skill
git clone https://github.com/your-username/bocha-search-skill.git bocha-search

# 或者手动复制本文件夹到 ~/.openclaw/workspace/skills/bocha-search/
```

### 方法二：使用 ClawdHub 安装（发布后）

```bash
# 安装 clawdhub CLI
npm install -g clawdhub

# 搜索并安装
clawdhub search bocha
clawdhub install bocha-search
```

## 配置

### 获取 API Key

1. 访问 [博查AI官网](https://bocha-ai.com/)
2. 注册账号并创建应用
3. 获取 API Key

### 配置方式一：环境变量（推荐）

```bash
export BOCHA_API_KEY="your-api-key-here"
```

添加到 `~/.bashrc` 或 `~/.zshrc` 使其永久生效。

### 配置方式二：OpenClaw 配置文件

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "skills": {
    "entries": {
      "bocha-search": {
        "enabled": true,
        "apiKey": "your-api-key-here",
        "env": {
          "BOCHA_API_KEY": "your-api-key-here"
        }
      }
    }
  }
}
```

## 使用方法

配置完成后，在 OpenClaw 中直接使用：

```
"搜索北京今天的天气"
"用博查查一下量子计算的最新进展"
"bocha search: 人工智能发展趋势"
```

## 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| query | string | 是 | - | 搜索关键词（支持中英文） |
| count | number | 否 | 10 | 返回结果数量（1-50） |
| freshness | string | 否 | noLimit | 时间筛选：oneDay, oneWeek, oneMonth, oneYear, noLimit |

## 技术实现

### 项目结构

```
bocha-search/
├── SKILL.md              # Skill 定义文件（必需）
├── README.md             # 说明文档
└── scripts/
    ├── package.json      # Node.js 项目配置
    ├── tool.json         # OpenClaw 工具定义
    └── bocha_search.js   # 核心搜索脚本
```

### API 调用流程

1. 用户输入搜索请求
2. OpenClaw 识别并路由到 bocha-search skill
3. 脚本读取 `BOCHA_API_KEY` 环境变量
4. 调用博查 API: `POST https://api.bocha-ai.com/v1/web-search`
5. 格式化结果为 Markdown 输出

## 发布到 ClawdHub

如果你想让更多人使用这个 skill，可以发布到 [ClawdHub](https://clawdhub.com)：

### 步骤 1：准备发布

确保包含以下文件：
- ✅ `SKILL.md` - 带有 YAML frontmatter 的技能定义
- ✅ `README.md` - 使用说明
- ✅ `scripts/` - 可执行脚本

### 步骤 2：登录 ClawdHub

```bash
# 安装 clawdhub CLI
npm install -g clawdhub

# 登录
clawdhub login
```

### 步骤 3：发布

```bash
# 进入 skill 目录
cd ~/.openclaw/workspace/skills/bocha-search

# 发布到 ClawdHub
clawdhub publish . \
  --slug bocha-search \
  --name "Bocha Search" \
  --version 1.0.0 \
  --tags "search,chinese,web,bocha,latest"
```

### 步骤 4：更新版本

当需要更新时：

```bash
# 修改代码后，更新版本号
clawdhub publish . \
  --slug bocha-search \
  --version 1.0.1 \
  --changelog "修复了 XXX 问题"
```

## 开发调试

### 本地测试脚本

```bash
# 设置 API Key
export BOCHA_API_KEY="your-key"

# 测试搜索
cd scripts
echo '{"query": "人工智能", "count": 5}' | node bocha_search.js

# 或者直接传参
node bocha_search.js '{"query": "北京天气", "freshness": "oneDay"}'
```

### 检查 Skill 状态

```bash
openclaw skills info bocha-search
```

## 故障排除

### 问题：API Key 错误

**症状**: 提示 `BOCHA_API_KEY environment variable is required`

**解决**:
1. 确认已正确设置环境变量：`echo $BOCHA_API_KEY`
2. 检查 OpenClaw 配置：`cat ~/.openclaw/openclaw.json | grep bocha`
3. 重启 OpenClaw 会话以加载新配置

### 问题：搜索结果为空

**症状**: 返回 "未找到相关结果"

**解决**:
1. 尝试更换关键词
2. 调整 `freshness` 参数扩大时间范围
3. 增加 `count` 参数获取更多结果

### 问题：网络连接失败

**症状**: 提示连接超时或无法访问 API

**解决**:
1. 检查网络连接
2. 确认 API 端点可访问：`curl https://api.bocha-ai.com/v1/web-search`
3. 检查防火墙设置

## 许可证

MIT License - 详见 LICENSE 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [博查AI官网](https://bocha-ai.com/)
- [OpenClaw 文档](https://docs.openclaw.ai)
- [ClawdHub](https://clawdhub.com)
- [smart-search-skill](https://github.com/QLBQLB/smart-search-skill) - 智能路由搜索技能