# PDF Compressor 技能引擎

一个简易的 OpenClaw 技能，用于压缩指定的 PDF 文件，并返回压缩比率与结果。内部默认采用 `PyMuPDF` 处理。

## 输入格式

本技能接受 JSON 格式输入，或者命令行显式参数：
- `pdf_path`: (必填) 原始 PDF 绝对路径
- `compression_level`: (选填) 压缩等级 (1=Low, 2=Medium, 3=High)，默认为 2

## 输出

返回标准 JSON：
```json
{
  "status": "success",
  "data": {
    "original_size": 1048576,
    "compressed_size": 204800,
    "output_path": "/path/to/output.pdf"
  },
  "message": "Compression applied successfully."
}
```

## 打包与发布 (Packaging & Publishing)

为了在 OpenClaw 中发布此技能，请按照以下步骤对其进行打包：

### 1. 源码压缩包方式（推荐）
这是最简单的方式，您只需要将核心代码和清单文件打包为一个 `.zip` 文件即可。
我们提供了一个自动打包脚本：
```bash
# 运行打包脚本
./build.sh
```
这会在当前目录下生成一个 `pdf_compressor_skill.zip`。

在 OpenClaw (或 ClawHub) 的技能管理面板中：
1. 点击 **"上传技能包 / Upload Skill"**
2. 选中刚才生成的 `pdf_compressor_skill.zip`
3. 平台会自动读取 `pyproject.toml` / `uv.lock` 并通过 `uv` 安装依赖。

### 2. 使用 PyInstaller 构建独立可执行文件（高阶）
如果希望降低目标环境对 Python 环境及依赖派发的处理成本，可以打包为单独的二进制文件。
1. 安装并在虚拟环境中通过 uv 运行: `uv run pyinstaller --onefile src/main.py -n pdf_compressor`
2. 修改 `SKILL.md` 的 metadata:
   ```yaml
   runtime: executable
   ```
3. 将 `dist/pdf_compressor` 和 `SKILL.md` 打包发布。

## 开发者本地运行
本项目使用 [`uv`](https://github.com/astral-sh/uv) 进行 Python 依赖管理和环境隔离。

```bash
# 安装依赖并同步环境
uv sync

# 本地运行测试
uv run src/main.py --pdf_path "/path/to/test.pdf" --compression_level 2
```
