# 实验设计指南

## 实验类型

### 1. 主实验（Main Results）

复现论文的核心实验结果，用于验证方法有效性。

**设计要点：**
- 使用与论文相同的数据集划分
- 使用与论文相同的评估指标
- 报告平均值±标准差（多次运行）
- 与论文报告的基线方法对比

**输出格式：**
```markdown
| 方法 | 准确率 (%) | F1 Score | AUC |
|------|-----------|----------|-----|
| Baseline 1 | 85.2 | 83.1 | 0.89 |
| Baseline 2 | 87.5 | 85.4 | 0.91 |
| **Ours** | **89.3** | **87.2** | **0.93** |
```

### 2. 消融实验（Ablation Study）

分析各组件对整体性能的贡献。

**常见类型：**
- **组件移除：** 逐个移除模型组件
- **组件替换：** 用替代方案替换关键组件
- **超参数敏感性：** 测试关键超参数的影响

**设计示例：**
```markdown
| 变体 | 准确率 (%) | 说明 |
|------|-----------|------|
| Full Model | 89.3 | 完整模型 |
| -Component A | 86.1 | 移除组件 A |
| -Component B | 87.5 | 移除组件 B |
| Replace X with Y | 85.8 | 替换组件 X |
```

### 3. 对比实验（Comparative Study）

与 SOTA 方法进行公平对比。

**注意事项：**
- 确保实验设置一致（数据预处理、增强等）
- 使用相同的训练/测试划分
- 报告统计显著性检验（如 t-test）

### 4. 定性分析（Qualitative Analysis）

可视化展示方法效果。

**常见形式：**
- 注意力可视化
- 特征空间 t-SNE 图
- 成功/失败案例分析
- 生成结果展示

## 实验记录模板

### 实验日志

```markdown
## 实验 ID: exp_001

**日期：** 2024-01-15

**目的：** 复现论文 Table 1 主实验

**配置：**
- 模型：PaperModel
- 数据集：CIFAR-10
- 批次大小：32
- 学习率：0.001

**结果：**
- 训练损失：0.342
- 验证准确率：87.5%
- 测试准确率：86.8%

**与论文对比：**
- 论文报告：89.3%
- 差距：-2.5%

**分析：**
可能原因：
1. 数据预处理差异
2. 超参数未完全调优
3. 随机种子影响

**下一步：**
- [ ] 检查数据预处理流程
- [ ] 尝试学习率调优
- [ ] 多次运行取平均
```

## 超参数搜索空间

### 网格搜索示例

```yaml
hyperparameter_search:
  learning_rate:
    - 0.0001
    - 0.001
    - 0.01
  batch_size:
    - 16
    - 32
    - 64
  hidden_dim:
    - 256
    - 512
    - 1024
  dropout:
    - 0.1
    - 0.3
    - 0.5
```

### 贝叶斯优化配置

```python
from optuna import Trial

def suggest_hyperparams(trial: Trial):
    return {
        'lr': trial.suggest_float('lr', 1e-5, 1e-2, log=True),
        'batch_size': trial.suggest_categorical('batch_size', [16, 32, 64]),
        'hidden_dim': trial.suggest_int('hidden_dim', 128, 1024, step=128),
        'dropout': trial.suggest_float('dropout', 0.1, 0.5),
    }
```

## 统计显著性检验

```python
from scipy import stats

def t_test(results_a, results_b):
    """
    执行配对 t 检验。
    
    Args:
        results_a: 方法 A 的多次运行结果
        results_b: 方法 B 的多次运行结果
        
    Returns:
        t_statistic, p_value
    """
    t, p = stats.ttest_rel(results_a, results_b)
    return t, p

# 示例
ours = [89.1, 89.5, 88.9, 89.3, 89.0]
baseline = [87.2, 87.5, 87.0, 87.8, 87.3]
t, p = t_test(ours, baseline)
print(f"t={t:.3f}, p={p:.4f}")
# p < 0.05 表示差异显著
```

## 计算资源估算

### GPU 内存估算

```python
def estimate_gpu_memory(model, batch_size, input_shape):
    """
    估算 GPU 内存需求（近似）。
    
    Args:
        model: PyTorch 模型
        batch_size: 批次大小
        input_shape: 输入形状
        
    Returns:
        estimated_memory_mb: 估算内存 (MB)
    """
    # 模型参数
    param_memory = sum(p.numel() * p.element_size() for p in model.parameters())
    
    # 梯度
    grad_memory = param_memory
    
    # 激活（粗略估算）
    # 需要根据具体模型架构计算
    
    total = param_memory + grad_memory
    return total / (1024 * 1024)  # MB
```

### 训练时间估算

```
训练时间 ≈ (数据集大小 / 批次大小) × 每批次时间 × 训练轮数

示例：
- 数据集：50,000 样本
- 批次大小：32
- 每批次时间：0.1 秒
- 训练轮数：100

训练时间 ≈ (50000/32) × 0.1 × 100 ≈ 15,625 秒 ≈ 4.3 小时
```

## 实验检查清单

### 实验前

- [ ] 确认数据集已正确下载和预处理
- [ ] 确认环境配置与论文一致
- [ ] 确认随机种子已设置
- [ ] 确认基线方法可正常运行

### 实验中

- [ ] 记录所有超参数配置
- [ ] 保存训练日志和 checkpoints
- [ ] 监控训练曲线（损失、准确率）
- [ ] 记录异常情况和解决方案

### 实验后

- [ ] 整理实验结果表格
- [ ] 生成可视化图表
- [ ] 与论文结果对比分析
- [ ] 撰写实验报告

---

*参考：https://www.cs.cmu.edu/~aarti/Class/10701/experiment_design.pdf*
