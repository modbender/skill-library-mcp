# Progress Tracking System

## File Structure in ~/gaokao/

### profile.md
```markdown
# Student Profile

## Basic Info
- Name: [学生姓名]
- Province: [省份]
- School: [学校]
- Exam Date: 2025-06-07

## Subject Combination
- Core: 语文, 数学, 英语
- Choice 1: [物理/历史]
- Choice 2: [科目], [科目]

## Targets
- Goal Score: [目标分数]
- Dream University: [大学]
- Backup Universities: [备选]
- Major: [专业]

## Current Status
- Latest Mock Score: [分数]
- Estimated Rank: [位次]
- Days Until Exam: [倒计时]
```

### subjects/{subject}.md
```markdown
# 数学 Progress

## Current Status
- Latest Score: 125/150
- Mastery: 78%
- Trend: ↑ improving

## Weak Areas (sorted by ROI)
| Topic | Mastery | Points at Stake | Priority |
|-------|---------|-----------------|----------|
| 圆锥曲线 | 45% | 12 | ★★★★★ |
| 导数压轴 | 50% | 12 | ★★★★★ |
| 概率综合 | 60% | 10 | ★★★★ |

## Strong Areas
- 三角函数: 92%
- 数列基础: 88%

## Error Log (last 10)
| Date | Topic | Error Type | Fixed? |
|------|-------|------------|--------|
| 02-13 | 椭圆焦点 | Concept | ✓ |
| 02-12 | 导数单调性 | Careless | ✓ |

## Study Hours This Week
- Target: 15h
- Actual: 12h
- Efficiency: 80%
```

### sessions/{date}.md
```markdown
# Study Session: 2025-02-13

## Morning (08:00-12:00)
- 数学: 2.5h — 导数专项练习
- 英语: 1.5h — 阅读理解 x4

## Afternoon (14:00-18:00)
- 物理: 2h — 电磁感应复习
- 语文: 2h — 文言文训练

## Evening (19:00-22:00)
- 数学: 1.5h — 错题回顾
- 英语: 1.5h — 听力练习

## Metrics
- Total: 11h
- Focus Rating: 7/10
- Energy: Started strong, tired by evening
- Key Win: Finally understood 楞次定律
```

### mocks/{date}-{exam_name}.md
```markdown
# Mock Exam: 2025-02-10 省统考

## Scores
| Subject | Score | vs Last | vs Target |
|---------|-------|---------|-----------|
| 语文 | 118/150 | +3 | -7 |
| 数学 | 125/150 | +5 | -5 |
| 英语 | 132/150 | +2 | +2 |
| 物理 | 85/100 | +0 | -5 |
| 化学 | 78/100 | -2 | -7 |
| 生物 | 82/100 | +4 | +2 |
| **Total** | **620/750** | **+12** | **-20** |

## Error Analysis
### 数学
- Q19: 圆锥曲线 — 忘了第二定义
- Q21: 导数压轴 — 时间不够，只拿6/12分

### 语文
- 作文: 审题偏差 — 论点不够鲜明

## Action Items
1. 圆锥曲线第二定义 — 今晚复习
2. 导数压轴时间分配 — 练习20分钟内完成
3. 作文审题 — 下周专项训练
```

## Update Triggers

| Event | Action |
|-------|--------|
| Study session ends | Update sessions/{date}.md |
| Mock exam taken | Create mocks/{date}.md, update subjects/* |
| Weak area improved | Move from weak to neutral in subject file |
| Weekly | Summarize week's progress, adjust next week's plan |

## Metrics to Track

### Daily
- Hours studied per subject
- Problems completed
- Error count and types

### Weekly
- Total study hours vs target
- Score trends by subject
- Weak areas addressed
- Flashcard review completion

### Monthly
- Mock exam score trajectory
- University target feasibility
- Burnout risk indicators
