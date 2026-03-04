# 飞书文档技能安装和配置指南

## 1. 获取飞书应用凭证

### 步骤1：创建飞书应用
1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 点击"创建企业自建应用"
3. 填写应用名称和描述
4. 记录应用ID（格式：`cli_xxxxxx`）

### 步骤2：获取应用密钥
1. 在应用详情页面，点击"凭证与基础信息"
2. 在"应用凭证"部分，点击"重置App Secret"
3. 复制生成的App Secret

### 步骤3：配置API权限
1. 点击"权限管理"
2. 添加以下权限：
   - `drive:drive:readonly` - 读取云文档
   - `drive:drive:write` - 写入云文档
   - `drive:file:readonly` - 读取文件
   - `drive:file:write` - 写入文件

### 步骤4：发布应用
1. 点击"版本管理与发布"
2. 创建版本
3. 申请发布
4. 等待审核通过（企业自建应用通常自动通过）

## 2. 安装技能

### 方法A：从GitHub克隆
```bash
# 克隆技能到Clawdbot技能目录
cd /Users/steven/openclaw/skills
git clone <repository-url> feishu-docs
cd feishu-docs
npm install
```

### 方法B：手动安装
```bash
# 创建技能目录
mkdir -p /Users/steven/openclaw/skills/feishu-docs
cd /Users/steven/openclaw/skills/feishu-docs

# 复制所有文件到目录
# ... 复制文件 ...

# 安装依赖
npm install
```

## 3. 配置环境变量

### 方法A：使用.env文件（推荐）
```bash
cd skills/feishu-docs
cp .env.example .env
# 编辑.env文件，填入你的凭证
```

`.env` 文件内容：
```env
FEISHU_APP_ID=cli_xxxxxx
FEISHU_APP_SECRET=your_app_secret
```

### 方法B：设置系统环境变量
```bash
# 在~/.zshrc或~/.bashrc中添加
export FEISHU_APP_ID=cli_xxxxxx
export FEISHU_APP_SECRET=your_app_secret

# 重新加载配置
source ~/.zshrc
```

### 方法C：在Clawdbot配置中设置
编辑Clawdbot配置文件（通常位于 `~/.clawdbot/clawdbot.json`）：
```json
{
  "env": {
    "FEISHU_APP_ID": "cli_xxxxxx",
    "FEISHU_APP_SECRET": "your_app_secret"
  }
}
```

## 4. 测试安装

### 测试本地功能
```bash
cd skills/feishu-docs
node test-basic.js
```

### 测试CLI工具
```bash
# 显示帮助
node bin/cli.js --help

# 测试创建命令（使用--help查看参数）
node bin/cli.js create --help
```

## 5. 获取必要的参数

### 获取文件夹Token
1. 在飞书中打开目标文件夹
2. 复制浏览器地址栏中的URL
3. 提取文件夹Token（URL中的 `fldxxxxxx` 部分）

示例URL：`https://example.feishu.cn/drive/folder/fldabc123`
文件夹Token：`fldabc123`

### 获取用户ID
1. 在飞书中点击用户头像
2. 查看用户详情
3. 用户ID格式：`ou_xxxxxx`

## 6. 使用示例

### 创建文档
```bash
node bin/cli.js create \
  --folder-token fldabc123 \
  --title "项目计划" \
  --content-file examples/create-project-doc.md
```

### 搜索文档
```bash
node bin/cli.js search \
  --query "项目" \
  --folder-token fldabc123
```

### 导出文档
```bash
node bin/cli.js export \
  --document-id dcnxyz789 \
  --output my-document.md
```

## 7. 在Clawdbot中使用

### 配置Clawdbot识别此技能
确保技能目录结构正确，Clawdbot会自动检测 `skills/` 目录下的技能。

### 示例对话
**用户**: "帮我在飞书创建一个会议纪要"
**Clawdbot**: 
```bash
# Clawdbot会自动调用技能
node skills/feishu-docs/bin/cli.js create \
  --folder-token fldmeetings \
  --title "2024年1月会议纪要" \
  --content "# 会议纪要\n\n## 参会人员\n- 张三\n- 李四\n\n## 讨论内容\n1. 项目进度\n2. 下一步计划"
```

## 8. 故障排除

### 常见问题

#### 问题1：认证失败
```
错误: 获取访问令牌失败: app_id or app_secret invalid
```
**解决方案**：
- 检查 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 是否正确
- 确保应用已发布
- 检查应用权限是否已配置

#### 问题2：权限不足
```
错误: API请求失败: No permission. (code: 99991663)
```
**解决方案**：
- 检查应用是否已获得必要的API权限
- 确保应用已发布并生效

#### 问题3：文件夹不存在
```
错误: API请求失败: folder not found
```
**解决方案**：
- 检查文件夹Token是否正确
- 确认有访问该文件夹的权限

#### 问题4：网络错误
```
错误: 网络请求错误: connect ETIMEDOUT
```
**解决方案**：
- 检查网络连接
- 确认可以访问飞书API（`https://open.feishu.cn`）

### 调试模式
启用调试模式查看详细日志：
```bash
DEBUG=true node bin/cli.js create --help
```

## 9. 安全注意事项

1. **保护应用凭证**：不要将 `.env` 文件提交到版本控制系统
2. **使用环境变量**：在生产环境中使用环境变量而非硬编码
3. **限制权限**：只授予应用必要的最小权限
4. **定期轮换密钥**：定期重置App Secret增强安全性

## 10. 获取帮助

- 查看技能文档：`README.md` 和 `SKILL.md`
- 查看飞书官方文档：https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/overview
- 查看命令行帮助：`node bin/cli.js --help`
- 运行测试：`node test-basic.js`