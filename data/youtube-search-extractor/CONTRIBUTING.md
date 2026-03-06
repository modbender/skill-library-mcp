# Contributing to YouTube Search Extractor

我们欢迎您为YouTube Search Extractor做出贡献！这是一个开源项目，旨在帮助用户从YouTube搜索结果中自动提取视频链接。

## 代码规范

### Python规范

- 使用PEP 8风格指南
- 使用4个空格进行缩进
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串

### 代码结构

```python
# 函数应该有明确的功能
def function_name(parameters):
    """
    文档字符串应该包含：
    - 功能描述
    - 参数说明
    - 返回值说明
    - 异常说明（如果有）
    """
    # 代码实现
```

### 提交规范

我们使用语义化提交信息：

```
feat: 添加新功能
fix: 修复bug
docs: 文档更新
style: 代码风格改进（不改变功能）
refactor: 重构（既不添加新功能也不修复bug）
perf: 性能优化
test: 添加或更新测试
chore: 其他变更（构建系统、依赖等）
```

## 开发流程

### 1. Fork仓库

点击GitHub页面上的"Fork"按钮将仓库复制到您的账户下。

### 2. 克隆到本地

```bash
git clone https://github.com/您的用户名/skills.git
cd skills/youtube-search-extractor
```

### 3. 创建分支

```bash
git checkout -b feature/your-feature-name
```

### 4. 开发和测试

```bash
# 安装依赖
npm install

# 运行测试
npm run test

# 测试功能
python3 youtube_search_extractor.py "测试关键词" test_output
```

### 5. 提交代码

```bash
git add .
git commit -m "feat: 添加新功能"
git push origin feature/your-feature-name
```

### 6. 创建Pull Request

到GitHub页面上创建Pull Request，描述您的变更。

## 问题报告

### Bug报告

当报告bug时，请包含：

1. **完整的错误信息** - 包括堆栈跟踪
2. **环境信息** - 操作系统、Python版本、agent-browser版本
3. **复现步骤** - 如何重现问题
4. **预期行为** - 应该发生什么
5. **实际行为** - 实际发生了什么

### 功能请求

当请求新功能时，请包含：

1. **功能描述** - 您想要的功能是什么
2. **使用场景** - 您将在什么情况下使用这个功能
3. **预期接口** - 您希望如何使用这个功能
4. **其他考虑** - 任何相关的信息

## 开发资源

### 文档

- [YouTube Search Extractor - SKILL.md](SKILL.md) - 技能文档
- [agent-browser官方文档](https://github.com/vercel-labs/agent-browser)
- [npm package.json文档](https://docs.npmjs.com/files/package.json)

### 测试资源

- [pytest官方文档](https://docs.pytest.org/)
- [unittest官方文档](https://docs.python.org/3/library/unittest.html)

### 调试工具

- 使用`--debug`参数启用详细输出
- 查看`*.html`和`*_links.txt`输出文件
- 使用浏览器开发者工具分析YouTube页面结构

## 社区准则

### 行为准则

我们遵循开放源代码行为准则，请保持：

- 尊重他人
- 友好和专业
- 建设性的反馈
- 有帮助的态度

### 交流方式

- **GitHub Issues** - 问题报告和功能请求
- **Pull Requests** - 代码贡献
- **Discussions** - 技术讨论和建议

## 许可证

本项目使用MIT许可证。通过贡献代码，您同意您的贡献将根据MIT许可证进行授权。

## 联系我们

如果您有任何问题或建议，欢迎通过以下方式联系我们：

- 创建GitHub Issue
- 发送邮件到contact@openclaw.com
- 在Discord社区中提问

感谢您的贡献！
