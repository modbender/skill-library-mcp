# CI/CD 说明与使用指南

## CI (Continuous Integration) 是什么？

CI 是**持续集成**，用于自动化测试代码质量，**不是**用来运行实际的数据提取任务。

### CI 的作用

| CI 能做的 | CI 不能做的 |
|-----------|------------|
| ✅ 检查 Python 语法错误 | ❌ 提取真实的科学数据 |
| ✅ 验证文件结构完整 | ❌ 替代本地安装使用 |
| ✅ 运行安全扫描 | ❌ 使用你的 API key |
| ✅ 测试导入是否成功 | ❌ 处理你的 PDF 文件 |

### 工作流程

```
你推送代码到 GitHub
    ↓
GitHub Actions 自动运行 CI 测试
    ↓
测试通过 ✓ → 代码健康，其他人可以放心使用
测试失败 ✗ → 收到通知，需要修复问题
```

## 实际使用方法

### 方法 1: 作为 Claude Code Skill 使用（推荐）

#### 安装

```bash
# 安装到 Claude Code
npx skills add https://github.com/JackKuo666/sci-data-extractor.git

# 或手动克隆
git clone https://github.com/JackKuo666/sci-data-extractor.git ~/.claude/skills/sci-data-extractor
```

#### 使用

在 Claude Code 对话中：

```
/extract-data 从 paper.pdf 中提取酶动力学数据
```

### 方法 2: 作为命令行工具使用

#### 安装依赖

```bash
cd sci-data-extractor
pip install -r requirements.txt
```

#### 配置环境变量

```bash
# 创建 .env 文件
cp .env.example .env

# 编辑 .env，添加你的 API key
# EXTRACTOR_API_KEY=your-api-key-here
```

#### 运行示例

```bash
# 使用内置模板
python extractor.py examples/sample.pdf --template enzyme -o output.md

# 查看结果
cat output.md
```

## CI 工作流说明

### 1. `ci.yml` - 持续集成测试

触发条件：
- 推送代码到 `main` 或 `dev` 分支
- 创建 Pull Request

测试内容：
- Python 3.11 和 3.12 兼容性测试
- 代码语法检查
- 类型检查
- 导入验证
- 文档完整性检查
- 安全漏洞扫描

### 2. `release.yml` - 自动发布

触发条件：
- 推送版本标签（如 `v1.0.0`）

功能：
- 自动创建 GitHub Release
- 生成版本说明

### 3. `example.yml` - 示例演示

触发条件：
- 手动触发（在 GitHub Actions 页面点击运行）

功能：
- 展示基本用法
- 验证 PyMuPDF 文本提取功能
- 显示安装和使用说明

## 本地测试建议

在提交代码前，建议本地运行以下测试：

### 1. 语法检查

```bash
python -m py_compile extractor.py
python -m py_compile batch_extract.py
```

### 2. 导入测试

```bash
python -c "import extractor; print('✓ extractor.py')"
python -c "import fitz; print('✓ PyMuPDF')"
```

### 3. 功能测试

```bash
# 测试 PDF 文本提取（不需要 API key）
python -c "
import fitz
doc = fitz.open('examples/sample.pdf')
print(f'PDF pages: {doc.page_count}')
text = doc.load_page(0).get_text('text')
print(f'Text length: {len(text)} chars')
"
```

### 4. 完整测试（需要 API key）

```bash
export EXTRACTOR_API_KEY="your-api-key"
python extractor.py examples/sample.pdf --template enzyme -o test_output.md
```

## 常见问题

### Q: CI 测试失败了怎么办？

A:
1. 查看 GitHub Actions 的错误日志
2. 本地复现问题
3. 修复后重新提交

### Q: 如何跳过 CI 测试？

A: 不建议跳过。如果必须，可以在 commit message 中加入 `[skip ci]`。

### Q: CI 会使用我的 API key 吗？

A: 不会。CI 只测试代码语法和结构，不会调用实际的 LLM API。

### Q: 我可以在 CI 中运行完整的数据提取吗？

A: 可以，但需要：
1. 在 GitHub Settings 中添加 Secrets（API key）
2. 修改 `ci.yml` 添加实际的提取步骤
3. 注意：每次运行都会消耗 API 配额

## 相关资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [CI/CD 最佳实践](https://www.github.com/features/actions)
- [项目 README](README.md) - 英文文档
- [项目 README_ZH](README_ZH.md) - 中文文档
