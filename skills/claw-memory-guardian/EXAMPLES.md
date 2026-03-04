# Claw Memory Guardian - 使用示例

## 🎯 快速开始示例

### 1. 基本安装和初始化
```bash
# 通过ClawdHub安装
clawdhub install claw-memory-guardian

# 初始化记忆系统
memory-guardian init

# 检查系统状态
memory-guardian status
```

### 2. 日常使用流程
```bash
# 开始新的一天
memory-guardian init  # 如果还没初始化

# 工作时定期保存
memory-guardian save "完成项目需求分析"
memory-guardian save "与客户确认需求"
memory-guardian save "开始编码实现"

# 搜索之前的记忆
memory-guardian search "项目需求"
memory-guardian search "客户确认"

# 创建备份
memory-guardian backup

# 结束工作时
memory-guardian save "今日工作完成，明日继续"
```

## 📝 实际使用场景示例

### 场景1：项目管理
```bash
# 项目启动
memory-guardian save "项目启动：AI助手开发平台"
memory-guardian save "目标：3个月内完成MVP"
memory-guardian save "团队：3名开发者，1名产品经理"

# 项目进展
memory-guardian save "第一周：完成需求分析和架构设计"
memory-guardian save "第二周：开发核心功能模块"
memory-guardian save "遇到技术难点：记忆系统实现"

# 问题解决
memory-guardian search "技术难点"
# 找到相关记忆，回顾解决方案

# 项目总结
memory-guardian save "项目完成，发布v1.0版本"
memory-guardian save "学习经验：需要更好的测试覆盖"
```

### 场景2：学习记录
```bash
# 学习新技能
memory-guardian save "开始学习OpenClaw技能开发"
memory-guardian save "学习重点：SKILL.md结构、package.json配置"
memory-guardian save "难点：记忆系统架构设计"

# 学习笔记
memory-guardian save "重要概念：实时保存、多重备份、自动索引"
memory-guardian save "最佳实践：每完成重要步骤就保存"
memory-guardian save "工具推荐：fs-extra、simple-git、date-fns"

# 知识应用
memory-guardian search "最佳实践"
# 快速找到之前的学习笔记

# 学习总结
memory-guardian save "完成OpenClaw技能开发学习"
memory-guardian save "下一步：实践开发一个完整skill"
```

### 场景3：客户服务
```bash
# 客户咨询记录
memory-guardian save "客户A咨询：需要AI助手定制开发"
memory-guardian save "需求：自动化客服系统，支持多语言"
memory-guardian save "预算：$5000，时间：2周"

# 方案讨论
memory-guardian save "提供方案：基于OpenClaw的客服skill"
memory-guardian save "技术栈：Node.js + OpenAI API + 数据库"
memory-guardian save "报价：$4500，时间：10个工作日"

# 跟进记录
memory-guardian save "客户A确认方案，签订合同"
memory-guardian save "开始开发，每日进度汇报"
memory-guardian save "客户反馈：满意，请求额外功能"

# 项目完成
memory-guardian save "项目交付，客户支付尾款"
memory-guardian save "客户评价：专业、高效、质量好"
```

## 🔧 高级功能示例

### 1. 自动保存配置
```bash
# 查看当前配置
cat ~/.openclaw/workspace/config.json

# 修改配置（示例）
{
  "memoryGuardian": {
    "autoSaveInterval": 60,       # 每60秒自动保存
    "autoCommitInterval": 900,    # 每15分钟自动git提交
    "backupRetention": 30,        # 保留30天备份
    "enableSemanticSearch": true,
    "enableTimeline": true
  }
}
```

### 2. 崩溃恢复示例
```bash
# 模拟崩溃场景
# 1. 正在工作时系统突然重启
# 2. 重新启动OpenClaw

# 恢复工作
memory-guardian status
# 显示：今日记忆文件存在，2小时前更新

memory-guardian search "最后工作"
# 找到：最后保存的是"完成用户登录模块开发"

# 继续工作
memory-guardian save "系统重启后恢复工作"
memory-guardian save "继续开发用户权限模块"
```

### 3. 团队协作示例
```bash
# 团队共享记忆
# 开发者A：
memory-guardian save "完成API接口设计"
memory-guardian save "接口文档：https://docs.example.com/api"

# 开发者B：
memory-guardian search "API接口"
# 找到开发者A的工作记录

memory-guardian save "基于API文档开始前端开发"
memory-guardian save "遇到问题：接口返回格式不一致"

# 开发者A：
memory-guardian search "接口问题"
# 找到开发者B的反馈

memory-guardian save "修复API返回格式问题"
memory-guardian save "通知开发者B：问题已修复"
```

## 🚀 生产力提升示例

### 示例1：会议记录自动化
```bash
# 会议前准备
memory-guardian save "准备项目进度汇报会议"
memory-guardian search "项目进度"
# 快速找到所有相关记录

# 会议中记录
memory-guardian save "会议开始：讨论Q2目标"
memory-guardian save "决策：优先开发用户管理模块"
memory-guardian save "分配任务：A负责前端，B负责后端"

# 会议后跟进
memory-guardian save "会议纪要已发送给团队"
memory-guardian save "下周跟进：检查任务进度"
```

### 示例2：日报/周报自动生成
```bash
# 每日工作记录
memory-guardian save "周一：完成用户注册功能"
memory-guardian save "周二：修复登录bug，优化性能"
memory-guardian save "周三：开发个人资料页面"
memory-guardian save "周四：集成第三方登录"
memory-guardian save "周五：测试和文档编写"

# 生成周报
memory-guardian search "周一 周二 周三 周四 周五"
# 快速汇总一周工作

# 自动生成报告
# （未来版本功能）
```

### 示例3：知识库建设
```bash
# 积累技术知识
memory-guardian save "OpenClaw技能开发技巧：..."
memory-guardian save "Node.js性能优化：..."
memory-guardian save "数据库设计最佳实践：..."

# 积累业务知识
memory-guardian save "客户常见问题解答：..."
memory-guardian save "项目报价策略：..."
memory-guardian save "合同注意事项：..."

# 快速检索
memory-guardian search "性能优化"
memory-guardian search "客户问题"
# 立即找到相关知识
```

## ⚠️ 故障排除示例

### 问题1：记忆文件损坏
```bash
# 症状：无法读取MEMORY.md
memory-guardian status
# 显示：❌ 长期记忆文件

# 解决方案：
# 1. 从备份恢复
ls memory/backup/
# 选择最近的备份

# 2. 手动修复（如果备份不可用）
echo "# MEMORY.md - 修复版本" > memory/MEMORY.md
echo "修复时间：$(date)" >> memory/MEMORY.md
memory-guardian save "修复损坏的记忆文件"
```

### 问题2：搜索功能失效
```bash
# 症状：搜索不到已知内容
memory-guardian search "已知关键词"
# 无结果

# 解决方案：
# 1. 重建索引
# （未来版本功能）

# 2. 手动检查文件
grep -r "关键词" memory/*.md

# 3. 检查文件权限
ls -la memory/
```

### 问题3：自动保存不工作
```bash
# 症状：没有自动创建今日文件
ls memory/*.md
# 没有当天的文件

# 解决方案：
# 1. 手动创建
memory-guardian init

# 2. 检查自动保存脚本
ps aux | grep auto_save

# 3. 重新启动自动保存
bash memory/auto_save.sh &
```

## 💡 最佳实践总结

### 1. 保存频率
- **重要决策**：立即保存
- **任务完成**：每个任务完成后保存
- **定期保存**：每30-60分钟自动保存
- **会话结束**：结束时总结保存

### 2. 记忆组织
- **分类明确**：项目、学习、客户等分类
- **关键词丰富**：便于搜索
- **时间清晰**：包含时间戳
- **结构完整**：问题、方案、结果、学习

### 3. 备份策略
- **本地备份**：每日自动备份
- **版本控制**：git自动提交
- **云端备份**：（可选）定期同步到云
- **定期清理**：删除过期备份

### 4. 搜索技巧
- **具体关键词**：避免太泛的搜索
- **时间范围**：限定搜索时间
- **组合搜索**：多个关键词组合
- **定期搜索**：回顾重要记忆

## 🎮 实战练习

### 练习1：创建一个项目记忆系统
```bash
# 1. 初始化
memory-guardian init

# 2. 记录项目启动
memory-guardian save "项目：个人博客系统"
memory-guardian save "目标：学习全栈开发"
memory-guardian save "技术栈：React + Node.js + MongoDB"

# 3. 记录开发过程
memory-guardian save "第一天：搭建开发环境"
memory-guardian save "第二天：设计数据库模型"
memory-guardian save "第三天：开发用户认证"

# 4. 练习搜索
memory-guardian search "数据库"
memory-guardian search "用户认证"

# 5. 创建备份
memory-guardian backup
```

### 练习2：模拟崩溃恢复
```bash
# 1. 开始工作
memory-guardian save "开始重要工作：数据分析报告"

# 2. 模拟崩溃（删除会话）
# （手动关闭终端）

# 3. 恢复工作
# 重新打开终端
memory-guardian status
memory-guardian search "数据分析"
memory-guardian save "恢复工作，继续数据分析"
```

---

**记住：文本 > 大脑 📝**

通过记忆守护者，你的工作不再会被遗忘，知识可以积累，经验可以传承。开始使用吧！