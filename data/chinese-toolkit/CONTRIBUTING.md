# 贡献指南

感谢您对OpenClaw中文工具包的贡献！我们欢迎各种形式的贡献。

## 如何贡献

### 1. 报告问题
- 使用GitHub Issues报告bug或提出功能建议
- 提供详细的问题描述和复现步骤
- 如果是bug，请提供错误日志和环境信息

### 2. 提交代码
1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 3. 改进文档
- 修复文档错误
- 添加使用示例
- 翻译文档
- 改进文档结构

## 开发规范

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型提示
- 添加适当的注释
- 编写单元测试

### 提交信息规范
使用Conventional Commits格式：
```
<类型>[可选 范围]: <描述>

[可选 正文]

[可选 脚注]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具

### 测试要求
- 新功能需要包含单元测试
- 测试覆盖率不低于80%
- 确保所有测试通过

## 开发环境设置

### 1. 克隆仓库
```bash
git clone https://github.com/yourusername/openclaw-chinese-toolkit.git
cd openclaw-chinese-toolkit
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行测试
```bash
python -m pytest tests/
```

## 行为准则

请遵守我们的行为准则，保持友好和尊重的交流环境。

## 联系方式

- GitHub Issues: 问题讨论
- Discord: 实时交流
- 邮件列表: 更新通知

感谢您的贡献！