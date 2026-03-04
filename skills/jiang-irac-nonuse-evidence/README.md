# 撤三证据智审系统（通用发布包）

软件介绍：面向商标撤销连续三年不使用（撤三）案件的本地化工具，支持证据识别、组证编排、文书生成与风险检查。  
作者：`@jiangzhongling`

本发布包已包含：
- 增强识别主流程（OCR、时间锚点、要件映射、排序重建、页码回填）
- 文书生成（答辩理由 / 证据目录 / 风险报告）
- Office 文件直读识别（DOC/DOCX/XLS/XLSX/PPT/PPTX）+ 归档转PDF
- 本地 Web 页面（全中文、蓝白基调、无终端独立运行）

请按 `INSTALL.md` 运行。

## 程序入口（推荐）
可直接使用统一入口脚本：

```bash
python run_nonuse_case.py \
  --evidence-dir "/path/to/证据目录" \
  --out-dir "/path/to/最终输出"
```

默认策略：非门禁执行（失败时输出诊断文件，不自动改阈值重试）。

## fast/full 目录分流
- `fast目录`：现场拍摄图片、产品包装、环境展示、无需严格时间锚点的佐证材料（轻量扫描）。
- `full目录`：合同、发票、网店页面、客户评价、交易履约等需要时间节点与要件分析的材料（深度扫描）。
- 支持三种输入方式：
1. 仅 `--evidence-dir`（兼容旧模式）
2. `--evidence-dir-fast` + `--evidence-dir-full`（推荐）
3. 三者混合（通用目录 + 分流目录）

## 案件详情手填 + 自动识别并存
- 支持手填字段：注册号、商标名称、商标图样、类别、被撤商品/服务、答辩商品/服务、指定期间、答辩人及地址、代理公司及地址、联系电话。
- 不填写时保持自动识别；填写后按“手填优先”写入 `CaseInfo`。

## 不扫描直接装订（直装材料）
- 支持将以下证据不参与OCR扫描、直接进入装订：
1. 答辩通知书
2. 主体资格证明
3. 委托书
4. 照片
5. 其他（可自定义名称并增加多项）
- CLI 参数：`--direct-bind-config /path/direct_bind_manifest.json`
- 配置格式示例：

```json
{
  "items": [
    {"label": "答辩通知书", "path": "/path/A.pdf"},
    {"label": "主体资格证明", "path": "/path/主体目录"},
    {"label": "委托书", "path": "/path/委托书.pdf"},
    {"label": "照片", "path": "/path/工厂照片目录"},
    {"label": "其他-合同补强", "path": "/path/合同目录", "name": "合同与补充协议"}
  ]
}
```

## 扫描后核验再输出（仅重新生成文书）
- 用于 full 扫描后人工修改 `nonuse_casebook_自动识别.xlsx` 再出文书：

```bash
python run_nonuse_case.py \
  --only-generate-xlsx "/path/nonuse_casebook_自动识别.xlsx" \
  --out-dir "/path/输出目录"
```


## 双击启动（Mac）
可直接双击运行：`一键运行.command`

首次运行会自动：
1. 创建 `.venv`
2. 安装依赖
3. 提示输入证据目录与输出目录
4. 自动执行全流程


## 双击启动（Windows）
可直接双击运行：`一键运行_windows.bat`

首次运行会自动：
1. 创建 `.venv`
2. 安装依赖
3. 提示输入证据目录与输出目录
4. 自动执行全流程

## Windows 应用程序（GUI）
1. 双击 `启动应用_windows.bat`
2. 在界面中选择“证据目录 / 输出目录”
3. 点“开始运行”

如需生成独立 EXE（给其他电脑分发）：
1. 双击 `build_windows_exe.bat`
2. 生成位置：`dist\\撤三证据智审系统\\撤三证据智审系统.exe`

## macOS 应用程序（GUI）
1. 双击 `启动应用_macos.command`
2. 自动打开本地网页界面（中文蓝白主题）
3. 在页面中选择“证据目录 / 输出目录”，点击“开始运行”

如需生成独立 `.app`（给其他 Mac 分发）：
1. 在终端执行：`bash build_macos_app.sh`
2. 生成位置：`dist_macos_app/撤三证据智审系统.app`
3. 该 `.app` 为无终端模式，自动打开本地网页界面运行

## macOS 真正自包含 .app（拷走可运行）
1. 在终端执行：`bash build_macos_app_selfcontained.sh`
2. 生成位置：
- `dist_macos_app_selfcontained/撤三证据智审系统-自包含.app`
- 根目录自动生成：`撤三证据智审系统-自包含_YYYYMMDD-HHMMSS.zip`
3. 该 `.app` 不依赖当前工程目录，拷走后可直接双击运行。
4. 注意：OCR 仍依赖系统可用的 `tesseract/pdftoppm`（无则扫描能力受限）。


> 启动器说明：自动检查证据目录；执行失败时直接退出并提示查看 `caseinfo_validation.json`、`time_quality_validation.json`、`name_quality_validation.json`、`page_map_validation.json`。
