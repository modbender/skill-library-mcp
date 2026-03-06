# Claw-Ethics-Checker 使用示例

## 🎯 实际应用场景

### 示例1：电商价格监控任务

```python
from claw_ethics_checker import EthicsChecker

# 创建检查器
checker = EthicsChecker()

# 任务描述：监控竞争对手价格
task = {
    'description': '每日监控竞争对手网站商品价格',
    'client': '电商公司',
    'methods': ['web_scraping', 'api_calls'],
    'data_source': '竞争对手公开网站',
    'frequency': '每日一次',
    'data_storage': '本地数据库，不存储用户个人信息'
}

# 分析伦理合规性
result = checker.analyze_task('价格监控', task)

print('📊 分析结果:')
print(f'风险等级: {result.risk_level.value}')
print(f'是否合规: {result.is_compliant}')
print(f'需要人工审核: {result.needs_human_review}')

if result.warnings:
    print(f'警告: {result.warnings}')

if result.recommendations:
    print(f'建议:')
    for rec in result.recommendations:
        print(f'  • {rec}')

# 输出:
# 风险等级: low
# 是否合规: True
# 需要人工审核: True
# 建议: 任务基本合规, 建议简单审核
```

### 示例2：社交媒体情感分析

```python
from claw_ethics_checker import EthicsChecker

checker = EthicsChecker()

task = {
    'description': '分析社交媒体上关于品牌的用户情感',
    'client': '营销公司',
    'methods': ['sentiment_analysis', 'natural_language_processing'],
    'data_source': '公开社交媒体帖子',
    'data_scope': '仅分析公开帖子，不访问私人信息',
    'anonymization': '用户数据匿名化处理'
}

result = checker.analyze_task('社交媒体分析', task)

print('📊 分析结果:')
print(f'风险等级: {result.risk_level.value}')  # medium
print(f'是否合规: {result.is_compliant}')      # False
print(f'需要人工审核: {result.needs_human_review}')  # True

print(f'警告: {result.warnings}')  # ['可能涉及隐私侵犯']
print(f'建议: {result.recommendations[:2]}')  # ['进行数据匿名化处理', '获取用户明确同意']
```

### 示例3：求职者背景调查

```python
from claw_ethics_checker import EthicsChecker

checker = EthicsChecker(config={'risk_threshold': 'low'})

task = {
    'description': '自动化调查求职者社交媒体背景',
    'client': '招聘公司',
    'methods': ['data_collection', 'profile_analysis'],
    'data_source': '求职者社交媒体公开资料',
    'consent': '求职者已签署背景调查同意书',
    'data_usage': '仅用于招聘评估，评估后删除'
}

result = checker.analyze_task('背景调查', task)

print('📊 分析结果:')
print(f'风险等级: {result.risk_level.value}')  # high
print(f'是否合规: {result.is_compliant}')      # False
print(f'需要人工审核: {result.needs_human_review}')  # True

print(f'法律问题: {result.legal_issues}')  # ['可能违反隐私法规']
print(f'伦理问题: {result.ethical_concerns}')  # ['隐私保护问题']
print(f'建议: {result.recommendations}')  # ['建议拒绝此任务', '必须进行人工审核', '咨询法律专家']
```

## 🔧 集成到工作流

### 在OpenClaw技能中集成

```python
# my_skill.py
from claw_ethics_checker import EthicsChecker, RiskLevel

class MySkill:
    def __init__(self):
        self.ethics_checker = EthicsChecker()
    
    def handle_request(self, task_request):
        # 1. 先进行伦理检查
        ethics_result = self.ethics_checker.analyze_task(
            task_request['description'],
            task_request
        )
        
        # 2. 根据风险等级决定
        if ethics_result.risk_level == RiskLevel.HIGH:
            return {
                'status': 'rejected',
                'reason': '高风险任务，基于伦理检查拒绝',
                'ethics_check': ethics_result.to_dict(),
                'suggestion': '请修改任务方案或联系人工审核'
            }
        
        elif ethics_result.risk_level == RiskLevel.MEDIUM:
            return {
                'status': 'needs_review',
                'reason': '中等风险任务，需要人工审核',
                'ethics_check': ethics_result.to_dict(),
                'recommendations': ethics_result.recommendations
            }
        
        else:  # LOW risk
            # 3. 如果合规，继续处理任务
            task_result = self.process_task(task_request)
            
            return {
                'status': 'approved',
                'ethics_check': ethics_result.to_dict(),
                'task_result': task_result
            }
    
    def process_task(self, task_request):
        # 实际处理任务的逻辑
        return {'result': '任务处理完成'}
```

### 在自动化脚本中集成

```python
#!/usr/bin/env python3
# automate_with_ethics.py

import sys
from claw_ethics_checker import EthicsChecker

def main():
    # 从命令行读取任务
    if len(sys.argv) < 2:
        print('用法: python automate_with_ethics.py "任务描述"')
        sys.exit(1)
    
    task_description = sys.argv[1]
    
    # 假设从配置文件或数据库读取任务详情
    task_details = {
        'description': task_description,
        'client': '内部使用',
        'methods': ['automation'],
        'data_source': '根据任务确定'
    }
    
    # 伦理检查
    checker = EthicsChecker()
    result = checker.analyze_task(task_description, task_details)
    
    print('🧠 伦理检查结果:')
    print(f'  风险: {result.risk_level.value}')
    print(f'  合规: {result.is_compliant}')
    
    if not result.is_compliant:
        print('❌ 任务被拒绝:')
        for warning in result.warnings:
            print(f'  - {warning}')
        sys.exit(1)
    
    if result.needs_human_review:
        print('⚠️  需要人工审核')
        print('建议:')
        for rec in result.recommendations:
            print(f'  - {rec}')
        # 这里可以发送通知给人类审核员
        sys.exit(2)
    
    # 如果通过检查，执行任务
    print('✅ 任务通过伦理检查，开始执行...')
    execute_task(task_description, task_details)

def execute_task(description, details):
    # 实际执行任务的逻辑
    print(f'执行任务: {description}')
    # ... 任务执行代码 ...

if __name__ == '__main__':
    main()
```

## 📋 实际案例

### 案例1：数据爬虫项目

**场景**: 客户需要爬取竞争对手产品信息

**伦理检查过程**:
1. 检查数据来源合法性
2. 评估隐私影响
3. 确认robots.txt合规性
4. 评估竞争公平性

**结果**: 中等风险，建议：
- 限制爬取频率
- 只爬取公开信息
- 不绕过安全措施
- 人工审核最终方案

### 案例2：用户行为分析

**场景**: 分析应用用户行为以改进产品

**伦理检查过程**:
1. 检查用户同意状态
2. 评估数据匿名化程度
3. 确认数据使用范围
4. 检查数据存储安全

**结果**: 低风险，建议：
- 确保用户明确同意
- 完全匿名化处理
- 定期清理旧数据
- 透明化数据使用政策

### 案例3：自动化营销

**场景**: 自动化发送营销邮件

**伦理检查过程**:
1. 检查收件人同意状态
2. 评估垃圾邮件风险
3. 确认退订机制
4. 检查内容合规性

**结果**: 高风险，建议：
- 只发送给明确同意的用户
- 提供明显退订选项
- 控制发送频率
- 人工审核内容

## 🎓 最佳实践

### 1. 始终先检查后执行
```python
# 好做法
def handle_task(task):
    check_result = ethics_checker.analyze_task(task)
    if not check_result.is_compliant:
        return reject_task(check_result)
    return execute_task(task)

# 坏做法
def handle_task(task):
    result = execute_task(task)  # 先执行，后检查
    check_result = ethics_checker.analyze_task(task)
    # 可能已经违反了伦理规则
```

### 2. 记录所有检查结果
```python
def log_ethics_check(task, result):
    with open('ethics_log.jsonl', 'a') as f:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'task': task,
            'result': result.to_dict(),
            'decision': 'approved' if result.is_compliant else 'rejected'
        }
        f.write(json.dumps(log_entry) + '\\n')
```

### 3. 定期审查和更新规则
```python
# 每月审查一次规则
def review_ethics_rules():
    # 分析历史决策
    # 识别新模式
    # 更新规则库
    # 测试新规则
    pass
```

### 4. 人类监督参与
```python
def escalate_to_human(result, task):
    if result.needs_human_review:
        # 发送通知给人类审核员
        send_notification({
            'task': task,
            'ethics_result': result.to_dict(),
            'urgency': 'high' if result.risk_level == 'high' else 'medium'
        })
        return {'status': 'pending_human_review'}
```

## 🔗 相关资源

- [完整文档](SKILL.md)
- [安装指南](INSTALLATION.md)
- [测试用例](test_ethics_checker.py)
- [GitHub仓库](https://github.com/openclaw/claw-ethics-checker)

## ❓ 常见问题

**Q: 这个工具能保证100%合规吗？**
A: 不能。这是一个辅助工具，最终决策需要人类判断。工具帮助识别风险，但不能替代法律咨询。

**Q: 如何处理自定义规则？**
A: 可以通过配置文件添加自定义规则，或扩展`EthicsChecker`类。

**Q: 性能影响大吗？**
A: 检查通常在毫秒级别，对性能影响很小。

**Q: 支持哪些语言？**
A: 目前主要支持英语和中文任务描述。

---
*使用Claw-Ethics-Checker，让AI助手更安全、更合规* 🦀