# Publish Sanitization Checklist（发布前脱敏）

发布到 EvoMap/外部前，必须满足：

- [ ] 不含任何 token/key/password/secret
- [ ] 不含内外网 IP、域名、主机名
- [ ] 不含本地绝对路径（/home/*, /Users/*）
- [ ] 不含个人身份信息（邮箱、手机号、设备序列）
- [ ] 不含真实 chat_id / open_id

## 建议扫描命令

```bash
grep -riE "(api_key|secret|token|password|/home/[a-z]+|/Users/[a-z]+|[0-9]{1,3}(\.[0-9]{1,3}){3}|open_id|chat_id|@.+\.(com|cn))" <dir>
```

若有命中：先替换为占位符再发布。

## 占位符规范

- 凭据 -> `<gateway-token>` / `<api-key>`
- IP -> `<server-ip>`
- 接口路径/URL -> `<api-endpoint>`
- 用户路径 -> `<local-path>`
- 设备名 -> `<node-name>`
