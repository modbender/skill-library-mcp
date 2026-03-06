---
name: Test Case Generator
description: 根据代码自动生成单元测试用例。
---

# Test Case Generator

根据代码自动生成单元测试用例。

## 功能

- 从代码提取函数签名
- 自动生成测试框架代码
- 支持 Jest、Mocha、Pytest
- 智能生成测试参数

## 触发词

- "生成测试"
- "测试用例"
- "unit test"
- "generate test"

## 支持框架

```javascript
// Jest
test('functionName should work', () => {
  expect(result).toBe(expected);
});

// Mocha
it('functionName', () => {
  assert(result === expected);
});

// Python Pytest
def test_function_name():
    assert result is not None
```

## 输出

返回完整的测试文件代码，包含：
- 导入语句
- 测试用例
- Mock 数据
- 断言
