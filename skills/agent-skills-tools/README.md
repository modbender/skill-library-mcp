# Agent Skills Tools 🔧

为Agent Skills生态系统开发的实用工具。

## 工具列表

### 1. 技能安全审计（skill-security-audit）

扫描技能包中的安全隐患。

**检查项目**：
- 凭据泄露（API key, password, secret, token）
- 危险的文件操作（~/.ssh, ~/.aws, ~/.config）
- 外部网络请求
- 环境变量使用（推荐做法）
- 文件权限检查
- Git历史记录检查

**使用方法**：
```bash
./skill-security-audit.sh path/to/skill
```

## 原因

eudaemon_0在286个技能中发现了1个凭据窃取器。技能包需要安全审计。

## 未来的工具

- [ ] 技能包验证工具（基于skills-ref）
- [ ] 批量验证脚本
- [ ] 技能评分系统

## License

MIT
