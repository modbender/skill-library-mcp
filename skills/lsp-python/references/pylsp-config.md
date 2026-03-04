# pylsp 配置指南

## 安装

### 基础安装

```bash
pip install python-lsp-server
```

### 完整安装 (所有插件)

```bash
pip install python-lsp-server[all]
```

### 单独安装插件

```bash
# 代码检查
pip install pylsp-mypy        # mypy 类型检查
pip install pylsp-flake8      # flake8 检查
pip install pylsp-pylint      # pylint 检查

# 格式化
pip install pylsp-black       # black 格式化
pip install pylsp-autopep8    # autopep8 格式化

# 重构
pip install pylsp-rope        # rope 重构支持

# 其他
pip install pylsp-isort       # import 排序
```

## 配置文件

### 项目级配置 (. pylsp.ini 或 setup.cfg)

```ini
# .pylsp.ini
[pylsp]
plugins/pycodestyle/enabled = true
plugins/pycodestyle/maxLineLength = 100
plugins/pyflakes/enabled = true
plugins/mypy/enabled = true
plugins/black/enabled = true
```

### 全局配置 (~/.config/pylsp/config.yml)

```yaml
pylsp:
  configurationSources:
    - pycodestyle
    - pyflakes
  plugins:
    pycodestyle:
      enabled: true
      maxLineLength: 100
    pyflakes:
      enabled: true
    mypy:
      enabled: true
      live_mode: true
      strict: false
    black:
      enabled: true
      line_length: 88
    autopep8:
      enabled: true
    isort:
      enabled: true
```

## 检查器配置

### pycodestyle (PEP8)

```ini
[pycodestyle]
max-line-length = 100
ignore = E501,W503
```

常见错误代码:
- **E402**: 导入不在文件顶部
- **E501**: 行太长
- **E302**: 缺少空行
- **W293**: 空行有空白字符
- **W503**: 运算符在行首 (可忽略)

### pyflakes

无需配置，检测:
- 未使用的导入
- 未定义的变量
- 重复的键
- 无效的字符串格式

### mypy (类型检查)

```ini
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
ignore_missing_imports = True
```

## 编辑器集成

### VS Code

安装 Python 扩展后自动使用 pylsp。

配置 (`settings.json`):

```json
{
  "python.languageServer": "Pylance",
  "python.linting.pylspEnabled": true,
  "python.linting.pycodestyleEnabled": true,
  "python.linting.pyflakesEnabled": true,
  "python.formatting.provider": "black"
}
```

### Neovim (nvim-lspconfig)

```lua
require'lspconfig'.pylsp.setup{
  settings = {
    pylsp = {
      plugins = {
        pycodestyle = {
          enabled = true,
          maxLineLength = 100
        },
        pyflakes = {
          enabled = true
        },
        black = {
          enabled = true
        }
      }
    }
  }
}
```

### Emacs (eglot)

```elisp
(add-hook 'python-mode-hook 'eglot-ensure)
(add-to-list 'eglot-server-programs '(python-mode . ("pylsp")))
```

## 性能优化

### 禁用不需要的插件

```ini
[pylsp]
plugins/pylint/enabled = false
plugins/pydocstyle/enabled = false
plugins/yapf/enabled = false
```

### 增量检查

```yaml
pylsp:
  plugins:
    mypy:
      live_mode: false  # 保存时检查而非实时
```

### 缓存

```bash
# mypy 缓存
export MYPY_CACHE_DIR=~/.cache/mypy
```

## 故障排除

### pylsp 无法启动

```bash
# 检查安装
which pylsp
pylsp --version

# 查看日志
pylsp --log-file pylsp.log
```

### 插件冲突

```bash
# 列出已安装插件
pip list | grep pylsp

# 禁用冲突插件
# 在配置文件中设置 enabled = false
```

### 性能问题

```bash
# 使用 --check-parent-process 自动退出
pylsp --check-parent-process

# 限制检查范围
# 在配置中设置 exclude 模式
```

## 最佳实践

1. **项目级配置优先**: 将配置放在项目中而非全局
2. **只启用需要的插件**: 减少内存和 CPU 使用
3. **使用 pre-commit**: 在提交前自动检查
4. **CI 集成**: 在 CI 中运行相同检查

## Pre-commit 集成

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/python-lsp/pylsp
    rev: v1.14.0
    hooks:
      - id: pylsp
        args: [--pycodestyle, --pyflakes]
```

## 参考资料

- [pylsp 官方文档](https://github.com/python-lsp/python-lsp-server)
- [pylsp 插件列表](https://github.com/python-lsp/python-lsp-server#plugins)
- [PEP 8 风格指南](https://pep8.org/)
