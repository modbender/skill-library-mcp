# Performance Profiler

分析代码性能，识别瓶颈并提供优化建议。

## 功能

- 循环性能分析
- 重复计算检测
- 同步阻塞识别
- 复杂度计算
- 优化建议生成

## 触发词

- "性能分析"
- "性能瓶颈"
- "performance"
- "优化建议"

## 检测问题

- 循环内数组操作
- 重复的函数调用
- 同步阻塞操作
- 内存泄漏风险

## 输出示例

```json
{
  "issues": [
    {
      "type": "loop_push",
      "location": "line 42",
      "suggestion": "使用数组推导式或预先分配"
    }
  ],
  "complexity": "O(n²)",
  "score": 75
}
```
