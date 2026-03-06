# 安装与运行（通用版）

## 1. 环境准备
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 单案一键运行（非门禁执行）
```bash
python auto_recognize_and_generate.py   --evidence-dir "/path/to/证据目录"   --xlsx-template "./nonuse_casebook_v4_增强识别.xlsx"   --xlsx-out "/path/to/out/nonuse_casebook_自动识别.xlsx"   --ocr-cache "/path/to/out/ocr_cache"   --generator "./generate_suite_v2.py"   --out-dir "/path/to/out/最终输出"   --scan-mode fast --max-pages 2 --notice-max-pages 6 --dpi 320 --notice-dpi 340
```

### 2.1 目录分流模式（推荐）
```bash
python run_nonuse_case.py \
  --evidence-dir-fast "/path/to/fast目录" \
  --evidence-dir-full "/path/to/full目录" \
  --out-dir "/path/to/输出目录"
```
- `fast目录`：现场图、包装、环境、无需严格时间锚点证据
- `full目录`：合同发票、网店页面、客户评价、交易履约等需要时间节点分析证据

### 2.2 不扫描直接装订（直装材料）
```bash
python run_nonuse_case.py \
  --evidence-dir-fast "/path/to/fast目录" \
  --evidence-dir-full "/path/to/full目录" \
  --direct-bind-config "/path/to/direct_bind_manifest.json" \
  --out-dir "/path/to/输出目录"
```

`direct_bind_manifest.json` 示例：
```json
{
  "items": [
    {"label": "答辩通知书", "path": "/path/A.pdf"},
    {"label": "主体资格证明", "path": "/path/主体目录"},
    {"label": "委托书", "path": "/path/委托书.pdf"},
    {"label": "照片", "path": "/path/工厂照片目录"},
    {"label": "其他-补强", "path": "/path/其他目录", "name": "补充材料"}
  ]
}
```

### 2.3 扫描后人工核验再输出（仅生成文书）
```bash
python run_nonuse_case.py \
  --only-generate-xlsx "/path/to/nonuse_casebook_自动识别.xlsx" \
  --out-dir "/path/to/输出目录"
```

## 3. 高亮参数说明
- 当前版本已停用证据高亮，相关 `--precise-highlight*` 参数仅保留兼容，不影响输出。

## 4. 主要产物
- `答辩理由_自动识别.docx`
- `证据目录_自动识别.docx`
- `风险报告_自动识别.docx`
- `证据内容_重排合并.pdf`
- `caseinfo_validation.json`
- `time_quality_validation.json`
- `name_quality_validation.json`
- `page_map_validation.json`


## 5. Windows 一键运行
双击 `一键运行_windows.bat`，按提示输入：
- 证据目录绝对路径
- 输出目录绝对路径

默认非门禁执行：若失败直接退出并保留诊断文件，便于人工核验。

## 6. Windows 图形应用（GUI）
双击 `启动应用_windows.bat`，在界面中选择目录并运行。

## 7. Windows 打包 EXE
双击 `build_windows_exe.bat`：
- 自动安装 `pyinstaller`
- 输出 `dist\\撤三证据智审系统\\撤三证据智审系统.exe`
- 可将该目录整体复制到其他 Windows 电脑运行

## 8. macOS 图形应用（GUI）
双击 `启动应用_macos.command`，将自动打开中文蓝白主题网页界面，在页面中选择目录并运行。

## 9. macOS 打包 APP
在终端执行：
```bash
bash build_macos_app.sh
```
输出：
- `dist_macos_app/撤三证据智审系统.app`
- `dist_macos_app/使用说明.txt`
- 该 `.app` 为无终端模式，自动打开本地网页界面并后台执行主流程

## 10. macOS 打包自包含 APP（推荐分发）
在终端执行：
```bash
bash build_macos_app_selfcontained.sh
```
输出：
- `dist_macos_app_selfcontained/撤三证据智审系统-自包含.app`
- 根目录 zip：`撤三证据智审系统-自包含_YYYYMMDD-HHMMSS.zip`
- 该 `.app` 可独立拷贝运行，不依赖当前工程目录

注意：
- OCR 仍依赖系统安装 `tesseract/pdftoppm`，若缺失会影响扫描能力。


> 启动器说明：不再自动重试阈值；如执行失败，请根据诊断 JSON 修正材料后重跑。
