---
name: openclaw-reportstudio-community
description: Generate polished, read-only business reports from CSV/XLSX into static deliverables (xlsx+pdf+pptx) using ReportStudio Community. Use when a user says things like “用这个表生成月报/周报/经营分析/PPT+PDF汇报材料”, provides a file path, asks for trends (day/week/month), TopN breakdowns by a dimension/metric, or wants professional exports without hallucinated claims.
---

# openclaw-reportstudio-community

将用户的自然语言需求 + 本地 CSV/XLSX 文件，转成可交付的 **XLSX + PDF + PPTX**（社区版：只读、安全、保守洞察）。

## 工作流（自然语言触发）

### 1) 先把“人话”解析成参数

从用户话里抽取（缺省就用默认）：

- `file`: 输入文件路径（必填）
- `prompt`: 用户意图（必填，原话或等价改写）
- `out_dir`: 输出目录（默认 `./artifacts`）
- `formats`: 默认 `xlsx,pdf,pptx`
- `grain`: `day|week|month`（默认 `month`）
- `dim`: 拆解维度（可选；默认用第一个维度列）
- `measure`: 拆解指标（可选；默认用第一个数值列）
- `topn`: 默认 10
- `time_range`: `YYYY-MM-DD..YYYY-MM-DD`（可选）

如果用户没有给文件路径：先追问“文件在哪里/发我路径”。

### 2) 执行 ReportStudio（不改源文件）

优先用当前 python 环境直接运行：

```bash
python -m reportstudio.cli.main \
  --file <PATH> \
  --prompt "<PROMPT>" \
  --out-dir <OUT_DIR> \
  --formats xlsx,pdf,pptx \
  --topn 10 \
  --grain month
```

需要指定拆解维度/指标时：

```bash
  --dim <DIM_COL> \
  --measure <MEASURE_COL>
```

> 可选：使用 `scripts/run_reportstudio.py` 做一层薄包装，方便做 artifacts 存在性校验与 JSON 捕获。

### 3) 回传“可验收”的结果

- 把 stdout 的 JSON 作为主输出（包含 `artifacts/warnings/tables/meta`）。
- 同时给用户一句人话总结：产物有哪些、是否有 warnings（历史不足/截断/字段未识别等）。

### 4) 保守原则（必须遵守）

- 不编造因果；只输出数据支持的、可量化的结论。
- 历史不足就写 warning，不硬算 DoD/WoW/MoM/YoY。
- 社区版只读：不写 DB、不改源文件、不默认外网。

## 验收

需要验收清单时，读取：`references/acceptance.md`
