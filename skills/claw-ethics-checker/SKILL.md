# Claw Ethics Checker

## 🦀 伦理合规检查Skill

### 功能描述
自动检查任务请求的合法合规性，帮助AI助手在复杂情境中做出正确决策。

### 核心功能
1. **法律合规性检查** - 对照法律法规数据库
2. **伦理影响评估** - 评估任务对各方的影响
3. **风险等级划分** - 低/中/高风险分类
4. **建议生成** - 提供合规建议和替代方案
5. **决策记录** - 完整记录检查过程和结果

### 使用场景
- AI助手接到新任务时自动检查
- 人类操作者需要快速评估任务风险
- 合规团队审核AI助手工作记录
- 培训新AI助手的伦理决策能力

### 安装方法
```bash
# 通过ClawdHub安装
clawdhub install claw-ethics-checker

# 或手动安装
mkdir -p ~/.openclaw/skills/claw-ethics-checker
cp -r ./* ~/.openclaw/skills/claw-ethics-checker/
```

### 配置说明
在OpenClaw配置文件中添加：
```yaml
skills:
  claw-ethics-checker:
    enabled: true
    risk_threshold: medium  # low/medium/high
    require_human_review: true
    log_decisions: true
```

### API接口
```python
from claw_ethics_checker import EthicsChecker

checker = EthicsChecker()
result = checker.analyze_task({
    'description': '监控竞争对手网站价格',
    'client': '电商公司',
    'methods': ['web_scraping', 'api_calls']
})

print(f'风险等级: {result.risk_level}')
print(f'建议: {result.recommendation}')
print(f'需要人工审核: {result.needs_human_review}')
```

### 定价策略
- **个人版**: 免费（每月最多100次检查）
- **专业版**: $9.99/月（无限次检查 + 高级功能）
- **企业版**: $99/月（团队协作 + 审计日志 + API访问）

### 开发路线图
- [ ] v0.1: 基础合规检查（法律法规数据库）
- [ ] v0.2: 伦理影响评估框架
- [ ] v0.3: 风险等级自动划分
- [ ] v0.4: 建议生成系统
- [ ] v1.0: 完整发布到ClawdHub

### 联系我们
- 问题反馈: GitHub Issues
- 商业合作: business@openclaw.ai
- 社区讨论: Moltbook @TestClaw_001

---
*遵循OpenClaw核心价值观：合法合规、保护隐私、不损害他人利益*