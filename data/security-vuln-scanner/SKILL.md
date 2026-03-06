---
name: Security Vulnerability Scanner
description: 扫描代码中的安全漏洞，提供修复建议。
---

# Security Vulnerability Scanner

扫描代码中的安全漏洞，提供修复建议。

## 功能

- SQL 注入检测
- XSS 跨站脚本检测
- 硬编码密码/密钥检测
- 不安全随机数检测
- 命令注入检测
- 敏感信息泄露检测
- 安全评分

## 触发词

- "安全扫描"
- "漏洞检测"
- "security scan"
- "vulnerability"

## 检测模式

```javascript
const patterns = {
  sqlInjection: /query\s*\(\s*['"`].*\$\{/,
  xss: /innerHTML\s*=|document\.write/,
  hardcodedSecret: /password\s*=\s*['"][^'"]+['"]/,
  insecureRandom: /Math\.random\(\)/,
  commandInjection: /exec\s*\(\s*\$\{/
};
```

## 输出示例

```json
{
  "vulnerabilities": [
    {
      "type": "sql_injection",
      "line": 42,
      "severity": "high",
      "message": "检测到SQL注入风险"
    }
  ],
  "score": 65
}
```
