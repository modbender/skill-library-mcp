# Log Anomaly Detector

智能分析日志文件，检测异常模式、错误趋势和性能问题。

## 功能

- 实时日志分析
- 错误模式识别 (ERROR, FATAL, Exception)
- 警告检测 (WARN, Warning)
- 性能瓶颈识别 (slow, timeout, latency)
- 安全威胁检测 (unauthorized, forbidden, injection)
- 智能建议生成

## 触发词

- "分析日志"
- "日志异常"
- "日志错误"
- "log analysis"
- "error detection"

## 实现逻辑

分析日志文件，识别以下模式：
- 错误频率统计
- 异常时间序列
- 性能下降趋势
- 安全告警

## 输出示例

```json
{
  "errors": [{"line": "...", "timestamp": "..."}],
  "warnings": [...],
  "anomalies": [...],
  "recommendations": [
    "错误数量过多，建议设置告警",
    "检测到多次登录失败，建议检查安全"
  ]
}
```
