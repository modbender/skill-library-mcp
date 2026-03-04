---
name: weixin-xlog-analyzer
description: 解析和分析微信Xlog日志文件，提取关键信息并生成诊断报告；当用户需要分析微信日志、排查故障或统计日志数据时使用
---

# 微信Xlog分析工具

## 任务目标
- 本Skill用于:分析微信Xlog调试日志文件，提取关键信息并辅助问题诊断
- 能力包含:日志解析、错误提取、统计分析、问题诊断报告生成
- 触发条件:用户需要分析微信日志、排查故障、统计日志数据或定位问题时

## 前置准备
- Xlog文件准备:用户需提供微信Xlog文件（如已加密，需先使用外部工具解密）
- 外部解密工具:如需解密Xlog，用户需自行准备QXLog等解密工具（本Skill不包含解密功能）
- 依赖说明:scripts脚本仅使用Python标准库，无需额外安装依赖包

## 操作步骤
- 标准流程:
  1. 准备阶段
     - 确认Xlog文件路径（相对路径或绝对路径）
     - 如文件为加密格式，使用外部工具解密得到明文日志
  2. 日志解析
     - 调用 `scripts/xlog_parser.py <log_file_path>` 解析日志文件
     - 脚本会返回结构化的日志数据（JSON格式）
  3. 统计分析
     - 调用 `scripts/log_analyzer.py <parsed_data_file>` 进行统计分析
     - 脚本会返回统计结果（各级别日志数量、错误信息、模块分布等）
  4. 问题诊断
     - 根据统计结果和日志内容，智能体分析问题模式
     - 参考 `references/analysis_guide.md` 中的分析要点
     - 生成诊断报告和改进建议

- 可选分支:
  - 当仅需提取错误信息:在步骤2后，使用正则表达式过滤ERROR级别日志
  - 当仅需统计特定模块:在步骤3中指定模块名称进行过滤统计

## 资源索引
- 必要脚本:
  - [scripts/xlog_parser.py](scripts/xlog_parser.py):解析日志文件，提取时间戳、级别、模块、消息等结构化数据
  - [scripts/log_analyzer.py](scripts/log_analyzer.py):统计分析日志数据，生成统计报告
- 领域参考:
  - [references/xlog_format.md](references/xlog_format.md):Xlog文件格式说明和常见日志模式
  - [references/analysis_guide.md](references/analysis_guide.md):日志分析方法论和诊断要点

## 注意事项
- Xlog文件可能为加密格式，解密需要外部工具支持
- 日志解析依赖特定的格式模式，如遇格式变化可能需要调整正则表达式
- 统计分析基于日志级别和模块标签，确保日志输出包含这些信息
- 大文件处理时注意内存使用，建议分批处理

## 使用示例

### 示例1:基本日志分析
```bash
# 解析日志文件
python scripts/xlog_parser.py ./input/xlog.txt -o ./parsed_data.json

# 统计分析
python scripts/log_analyzer.py ./parsed_data.json -o ./analysis_result.json
```

### 示例2:仅提取错误信息
```bash
# 解析日志文件并过滤ERROR级别
python scripts/xlog_parser.py ./input/xlog.txt --level ERROR -o ./errors.json
```

### 示例3:特定模块分析
```bash
# 统计特定模块的日志
python scripts/log_analyzer.py ./parsed_data.json --module Network -o ./network_analysis.json
```
