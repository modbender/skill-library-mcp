# String Search - 高效字符串搜索

**Version**: 1.0.0  
**Author**: Claw  
**License**: MIT

---

## Description / 功能说明

High-performance string search algorithm with adaptive strategies and multi-level pruning. Optimized for large-scale text processing.

高性能字符串搜索算法，支持自适应策略和多层次剪枝。适用于大规模文本处理。

### Core Features / 核心功能
- Adaptive algorithm selection / 自适应算法选择
- Multi-level pruning / 多层次剪枝
- Statistical awareness / 统计感知
- Redundancy detection / 重复度检测

### Use Cases / 适用场景
- Large text search / 大文本搜索
- Pattern matching / 模式匹配
- Log analysis / 日志分析
- Data deduplication / 数据去重

---

## Usage / 使用示例

```c
#include "code.c"

int main() {
    const char* text = "This is a sample text for searching...";
    const char* pattern = "sample";
    
    int pos = string_search(text, strlen(text), pattern, strlen(pattern));
    
    if (pos >= 0) {
        printf("Found at position: %d\n", pos);
    }
    
    return 0;
}
```

---

## Impact / 效果

| Metric | Naive Search | Optimized | Improvement |
|:---|:---:|:---|:---:|
| Avg Time | O(n*m) | O(n) | Up to 10x faster |
| Redundancy Handling | None | Adaptive | Significant boost |
| Memory Usage | O(1) | O(1) | Same footprint |

---

## Changelog / 变更日志

### 1.0.0
- Initial release / 初始版本
- Adaptive string search / 自适应字符串搜索
- Multi-level pruning / 多层次剪枝
- Statistical optimization / 统计优化
