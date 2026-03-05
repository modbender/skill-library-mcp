# 快速测试方案

当需要快速评估模型时，使用此精简测试方案。

## 精简测试项 (10项)

### 文生图 (5项)

| 测试 | 提示词 | 评估要点 |
|------|--------|----------|
| 横版16:9 | 壮丽的雪山风景，云雾缭绕，金色阳光 | 构图比例、细节质量 |
| 竖版9:16 | 优雅的年轻女子全身像，站立姿态，自然光，专业摄影 | 人物比例、面部细节 |
| 文字生成 | 咖啡店招牌，上面写着"COFFEE TIME"，复古风格 | 文字清晰度、拼写正确 |
| 油画风格 | 梵高风格的星空夜景，漩涡笔触，油画质感 | 风格还原度 |
| 多人场景 | 三个朋友在咖啡厅聊天，每人表情不同 | 多人物处理、表情差异 |

### 人物一致性测试 (5项)

**核心测试目标**：测试模型能否在大幅度改变场景、姿态的同时保持人物特征一致。

先用竖版全身人像作为基准图（需要清晰的面部特征），然后测试：

| 测试 | 场景变化 | 姿态变化 | 编辑指令 |
|------|----------|----------|----------|
| 海边奔跑 | 室内→海滩 | 站立→奔跑 | Transform this person to be running joyfully on a sunny beach, waves splashing, dynamic action pose, same person same face |
| 咖啡厅阅读 | 室外→室内 | 站立→坐着 | Place this person sitting in a cozy cafe, reading a book, relaxed pose, warm lighting, same person same face |
| 雪山徒步 | 城市→雪山 | 静止→行走 | Transform this person hiking in snowy mountains, wearing winter gear, walking pose with backpack, same person same face |
| 健身运动 | 日常→健身房 | 休闲→运动 | Show this person doing yoga in a modern gym, stretching pose, athletic wear, same person same face |
| 正装演讲 | 休闲→正式 | 放松→演讲 | Transform this person giving a speech on stage, wearing formal business suit, confident gesture, same person same face |

**评估标准**：
- 面部特征保持度（眼睛、鼻子、脸型）
- 体型比例一致性
- 发型发色一致性
- 整体辨识度（是否还能认出是同一人）

## 预估费用

| 模型 | 单价 | 快速测试费用 |
|------|------|-------------|
| nano-banana | 0.018元 | 0.18元 |
| jimeng-4.5 | 0.018元 | 0.18元 |
| nano-banana-pro-2k | 0.054元 | 0.54元 |
| fal-ai/flux-2/flash | 50积分 | 500积分 |

## 快速测试流程

```
1. 并行执行 5 个文生图测试
   ↓
2. 选择全身人像作为基准图（确保面部清晰）
   ↓
3. 并行执行 5 个人物一致性测试（大幅度场景+姿态变化）
   ↓
4. 生成测试报告（含一致性评分）
```

预计耗时：3-5 分钟

## 人物一致性评分标准

| 评分 | 说明 | 判断依据 |
|------|------|----------|
| 优秀 (90-100%) | 完全认出是同一人 | 面部、体型、发型全部一致 |
| 良好 (70-89%) | 基本认出是同一人 | 面部相似，细节有变化 |
| 一般 (50-69%) | 勉强认出是同一人 | 部分特征保持，明显变化 |
| 较差 (0-49%) | 无法认出是同一人 | 人物特征丢失 |

## 基准图要求

为了更好测试人物一致性，基准图应满足：
- **全身像**：方便测试不同姿态
- **清晰面部**：五官清晰可辨
- **简单背景**：避免复杂背景干扰
- **自然姿态**：站立或轻松姿态
