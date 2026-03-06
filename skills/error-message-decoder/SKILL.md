---
name: Error Message Decoder
description: 解析错误信息，提供可能的原因和解决方案。
---

# Error Message Decoder

解析错误信息，提供可能的原因和解决方案。

## 功能

- 错误代码解析
- 原因分析
- 解决方案建议
- 多语言支持

## 触发词

- "错误解析"
- "错误解码"
- "error decode"
- "错误原因"

## 支持的错误

```javascript
const knownErrors = {
  'ENOENT': { zh: '文件不存在', fix: '检查文件路径是否正确' },
  'ECONNREFUSED': { zh: '连接被拒绝', fix: '检查服务是否启动' },
  'EADDRINUSE': { zh: '端口已被占用', fix: '杀死占用进程或更换端口' },
  'undefined is not a function': { zh: '调用了未定义的函数', fix: '检查函数名拼写和导入' },
  'null reference': { zh: '空指针错误', fix: '添加空值检查' },
  'CORS error': { zh: '跨域错误', fix: '配置CORS headers' },
  '404': { zh: '资源不存在', fix: '检查URL是否正确' },
  '500': { zh: '服务器内部错误', fix: '检查服务器日志' }
};
```

## 输出示例

```json
{
  "error": "ENOENT: no such file or directory",
  "cause": "文件不存在",
  "fix": "检查文件路径是否正确",
  "suggestion": "确保文件路径存在且拼写正确"
}
```
