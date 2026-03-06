---
name: character-profile
description: "Novel Character Profile Builder (小说人物档案创建工具) — A bilingual CN/EN skill for creating structured, detailed character profiles for fiction writing. Generates complete markdown profiles including backstory, personality, relationships, character arcs, and consistency checks. Supports protagonist, antagonist, and supporting character templates with built-in conflict detection and relationship matrix tools. Ideal for web novel (网文), fantasy, romance, and literary fiction authors."
---

# 小说人物档案创建工具

## 概述

本skill帮助小说作者创建结构化的人物角色档案，以markdown格式输出。适用于小说创作前期的人物设定阶段，确保角色设定完整、一致，为故事创作奠定基础。

## 快速开始

当用户需要创建人物档案时：

0. **设置工作目录**：访问用户工作目录，并切换到该目录
1. **收集角色信息**：询问用户角色的核心信息
2. **选择模板类型**：根据角色类型选择合适的模板
3. **填充详细信息**：逐步引导用户完善各个字段
4. **生成markdown档案**：输出格式化的markdown文档

## 核心工作流程

### 1. 确定角色类型

首先识别角色在故事中的定位：
- **主角**：故事核心，需要最详细的档案
- **重要配角**：关键支持角色，需要较详细档案
- **次要角色**：功能性角色，需要基本档案
- **反派**：对立角色，需要动机和背景深度分析

### 2. 信息收集顺序

按照以下逻辑顺序收集信息：

1. **基础身份**：姓名、年龄、性别、职业等
2. **外在特征**：外貌、着装、举止
3. **内在特质**：性格、价值观、信仰
4. **背景故事**：过去经历、关键事件
5. **关系网络**：与其他角色的联系
6. **故事功能**：角色弧线、目标、冲突

### 3. 档案结构

所有档案都包含以下核心部分：

```markdown
# [角色姓名] - 角色档案

## 基本信息
- **姓名**：
- **年龄**：
- **性别**：
- **职业/身份**：
- **故事中的角色**：

## 外貌特征
- **整体印象**：
- **面部特征**：
- **身材体型**：
- **着装风格**：
- **标志性特征**：

## 性格特点
- **核心性格**：
- **优点**：
- **缺点**：
- **价值观**：
- **恐惧**：
- **渴望**：

## 背景故事
- **出身背景**：
- **关键经历**：
- **转折点**：
- **未解之谜**：

## 人物关系
- **与主角关系**：
- **重要关系人**：
- **敌对关系**：
- **情感羁绊**：

## 故事发展
- **角色目标**：
- **内在冲突**：
- **外在冲突**：
- **发展弧线**：
- **可能的结局**：

## 创作笔记
- **灵感来源**：
- **象征意义**：
- **潜在发展**：
```

## 详细指南

### 针对不同角色类型的调整

#### 主角模板
- 需要最完整的背景故事和内心冲突
- 详细的发展弧线规划
- 复杂的动机层次
- 参考：[主角详细指南](references/protagonist.md)

#### 反派模板
- 重点刻画动机的合理性
- 详细的对立逻辑
- 潜在的救赎可能性
- 参考：[反派塑造指南](references/antagonist.md)

#### 配角模板
- 突出功能性特点
- 简化的背景故事
- 明确的故事作用
- 参考：[配角设计指南](references/supporting.md)

### 高级技巧

#### 角色一致性检查
创建档案后，进行以下检查：
1. **动机一致性**：行为是否与动机匹配
2. **发展合理性**：变化是否有合理铺垫
3. **关系逻辑性**：人物关系是否自然
4. **冲突有效性**：冲突是否推动故事

#### 角色关系矩阵
对于多个角色，创建关系矩阵：
- 情感强度
- 冲突程度
- 信任等级
- 依赖关系

## 使用示例

### 示例1：创建奇幻小说主角
```
用户：我需要创建一个奇幻小说的主角，年轻法师，出身平凡但有特殊血统

步骤：
1. 识别为"主角"类型
2. 使用主角模板
3. 重点询问：特殊血统的设定、法师能力的限制、成长路径
4. 生成完整档案，强调魔法系统和成长弧线
```

### 示例2：创建都市情感故事配角
```
用户：需要一个都市故事的女主角闺蜜，性格开朗但有自己的秘密

步骤：
1. 识别为"重要配角"类型
2. 使用配角模板，调整情感深度
3. 重点询问：秘密的内容、与女主的关系、独立故事线
4. 生成档案，平衡功能性和深度
```

## 输出文件处理

生成的markdown档案可以：
1. 直接保存为`.md`文件
2. 集成到小说写作软件
3. 作为角色卡片打印使用
4. 后续更新和迭代

## 常见问题

### Q: 如何避免角色模板化？
A: 在每个部分加入独特细节，寻找角色的矛盾点和非常规特征。

### Q: 档案应该多详细？
A: 根据角色重要性调整，主角可能需要5000+字，配角500-1000字。

### Q: 如何处理角色发展？
A: 在"故事发展"部分规划多个阶段的状态变化。

## 参考文件

- [主角详细指南](references/protagonist.md) - 主角塑造的深入指导
- [反派塑造指南](references/antagonist.md) - 反派角色的创作要点
- [配角设计指南](references/supporting.md) - 配角的功能性和深度平衡
- [关系网络设计](references/relationships.md) - 角色关系矩阵构建方法

## 最佳实践

1. **从核心概念开始**：先确定角色的核心理念
2. **逐步丰富细节**：层层添加具体特征
3. **检查逻辑一致性**：确保所有元素协调
4. **预留发展空间**：为故事发展留有余地
5. **迭代更新**：随着写作进展更新档案

## 增强功能 (v1.1+)

### 概述
从v1.1版本开始，工具增加了LoreBible管理和冲突检测功能，帮助作者维护统一的故事设定宇宙。

### 核心功能

#### 1. LoreBible目录管理
- **工作目录支持**：使用`--workspace`参数指定LoreBible工作目录
- **自动目录创建**：自动创建`00_Prepare`、`02_LoreBible/Characters`等标准目录结构
- **现有角色扫描**：自动扫描和解析现有角色档案，构建角色索引

#### 2. 冲突检测
- **重复角色检测**：检测姓名重复或高度相似的角色
- **常识校验**：检查年龄合理性、时间线一致性等常识错误
- **关系冲突检测**：检测角色关系中的矛盾和不一致
- **冲突报告**：生成详细的冲突报告和建议解决方案

#### 3. 会话管理
- **临时文件系统**：用户确认前在`00_Prepare`目录保存临时档案
- **用户确认流程**：交互式展示冲突，用户确认后移动到最终目录
- **会话状态持久化**：支持断点续传，自动清理过期会话

#### 4. 子代理工作流
- **任务分解**：将角色创建过程分解为原子任务
- **依赖管理**：自动处理任务依赖关系
- **错误恢复**：任务失败时自动重试，提供详细错误报告

### 使用方法

#### 命令行增强模式
```bash
# 基本用法（传统模式）
python scripts/generate_profile.py --name "张三" --age "25" --gender "男"

# 增强模式（推荐）
python scripts/generate_profile.py --name "李四" --age "30" --workspace "/path/to/lorebible"

# 跳过用户确认
python scripts/generate_profile.py --name "王五" --workspace "/path/to/lorebible" --no-confirm

# 指定模板类型
python scripts/generate_profile.py --name "赵六" --type "protagonist" --workspace "/path/to/lorebible"
```

#### 目录结构
```
工作目录/
├── 00_Prepare/           # 临时档案目录
├── 01_Research/          # 研究资料目录（可选）
└── 02_LoreBible/
    ├── Characters/       # 最终角色档案目录
    ├── Locations/        # 地点设定目录（可选）
    ├── Organizations/    # 组织设定目录（可选）
    └── Timeline/         # 时间线目录（可选）
```

#### 子代理工作流
```bash
# 运行完整工作流
python scripts/subagent_orchestrator.py "/path/to/lorebible" "character_creation"

# 运行快速创建模式
python scripts/subagent_orchestrator.py "/path/to/lorebible" "quick_creation"
```

### 配置文件

#### 校验规则配置 (`config/validation_rules.json`)
```json
{
  "rules": [
    {
      "id": "age_realistic",
      "name": "年龄合理性",
      "description": "检查年龄是否在合理范围内",
      "condition": "age.isdigit() and not (0 <= int(age) <= 150)",
      "severity": "warning"
    }
  ]
}
```

#### 工作流配置 (`config/workflow_tasks.json`)
```json
{
  "workflows": {
    "character_creation": {
      "name": "角色创建工作流",
      "tasks": [
        {
          "id": "init_workspace",
          "name": "初始化工作空间",
          "agent_type": "lore_bible_manager"
        }
      ]
    }
  }
}
```

### 新脚本模块

1. **`lore_bible_manager.py`** - LoreBible目录管理和角色扫描
2. **`conflict_detector.py`** - 冲突检测和常识校验
3. **`profile_session.py`** - 会话管理和用户确认流程
4. **`subagent_orchestrator.py`** - 子代理工作流协调

### 向后兼容性

- 传统模式：不指定`--workspace`参数时，使用传统生成模式
- 交互模式：增强模式也支持交互式创建
- 输出文件：传统模式输出到当前目录，增强模式输出到LoreBible目录

### 故障排除

#### 常见问题
1. **导入错误**：确保所有新脚本文件在`scripts/`目录中
2. **目录权限**：确保工作目录有读写权限
3. **配置文件缺失**：`config/`目录需要包含`validation_rules.json`和`workflow_tasks.json`

#### 日志查看
启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 未来计划
- 图形用户界面支持
- 云同步功能
- AI辅助角色生成
- 跨作品角色库管理

---

**版本历史**:
- v1.0 (初始版本): 基础角色档案生成功能
- v1.1 (当前版本): LoreBible管理、冲突检测、会话管理、子代理工作流
