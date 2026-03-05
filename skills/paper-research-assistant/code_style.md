# 复现代码规范

## 目录结构

```
paper-implementation/
├── README.md           # 项目说明
├── requirements.txt    # 依赖列表
├── setup.py           # 安装脚本（可选）
│
├── configs/           # 配置文件
│   ├── default.yaml
│   └── experiment_*.yaml
│
├── src/               # 源代码
│   ├── __init__.py
│   ├── model.py       # 模型定义
│   ├── layers.py      # 自定义层
│   ├── losses.py      # 损失函数
│   └── utils.py       # 工具函数
│
├── datasets/          # 数据加载
│   ├── __init__.py
│   ├── base.py        # 基类
│   └── custom.py      # 自定义数据集
│
├── scripts/           # 脚本
│   ├── train.py       # 训练脚本
│   ├── evaluate.py    # 评估脚本
│   └── visualize.py   # 可视化脚本
│
├── checkpoints/       # 模型权重（.gitignore）
├── logs/              # 训练日志（.gitignore）
└── results/           # 实验结果（可选）
```

## 代码规范

### 1. 模型定义

```python
import torch
import torch.nn as nn


class PaperModel(nn.Module):
    """
    论文方法的核心模型实现。
    
    Reference:
        [论文标题](论文链接)
    
    Args:
        config: 配置字典，包含模型超参数
        **kwargs: 其他参数
    
    Examples:
        >>> model = PaperModel(config)
        >>> output = model(input_tensor)
    """
    
    def __init__(self, config, **kwargs):
        super().__init__()
        self.config = config
        
        # 明确标注每个组件对应的论文章节/公式
        # Example: "对应论文公式 (3)"
        self.encoder = nn.Linear(config.input_dim, config.hidden_dim)
        
    def forward(self, x):
        """
        前向传播。
        
        Args:
            x: 输入张量 [batch_size, input_dim]
            
        Returns:
            output: 输出张量 [batch_size, output_dim]
        """
        # 添加注释说明每步对应的算法步骤
        x = self.encoder(x)  # 公式 (3): 编码
        return x
```

### 2. 配置管理

```yaml
# configs/default.yaml

# 模型配置
model:
  name: "PaperModel"
  input_dim: 784
  hidden_dim: 512
  output_dim: 10
  
# 训练配置
training:
  epochs: 100
  batch_size: 32
  learning_rate: 0.001
  weight_decay: 1e-5
  
# 数据配置
data:
  name: "mnist"
  data_dir: "./data"
  num_workers: 4
  
# 实验配置
experiment:
  seed: 42
  log_interval: 10
  save_dir: "./checkpoints"
```

### 3. 训练循环

```python
def train_epoch(model, dataloader, optimizer, criterion, device, epoch):
    """
    单个训练 epoch。
    
    Args:
        model: 模型
        dataloader: 数据加载器
        optimizer: 优化器
        criterion: 损失函数
        device: 计算设备
        epoch: 当前 epoch 编号
        
    Returns:
        avg_loss: 平均损失
    """
    model.train()
    total_loss = 0
    
    for batch_idx, (data, target) in enumerate(dataloader):
        data, target = data.to(device), target.to(device)
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        
        if batch_idx % args.log_interval == 0:
            print(f'Epoch {epoch} [{batch_idx}/{len(dataloader)}] Loss: {loss.item():.4f}')
    
    return total_loss / len(dataloader)
```

### 4. 评估函数

```python
@torch.no_grad()
def evaluate(model, dataloader, criterion, device):
    """
    评估模型性能。
    
    Args:
        model: 模型
        dataloader: 数据加载器
        criterion: 损失函数
        device: 计算设备
        
    Returns:
        metrics: 评估指标字典
    """
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    
    for data, target in dataloader:
        data, target = data.to(device), target.to(device)
        output = model(data)
        
        total_loss += criterion(output, target).item()
        pred = output.argmax(dim=1)
        correct += pred.eq(target).sum().item()
        total += target.size(0)
    
    metrics = {
        'loss': total_loss / len(dataloader),
        'accuracy': correct / total
    }
    
    return metrics
```

## 注释规范

1. **关键公式引用：** 在实现论文公式的代码处添加注释
   ```python
   # 公式 (5): 注意力权重计算
   attention = softmax(q @ k.transpose(-2, -1) / sqrt(d_k))
   ```

2. **超参数说明：** 说明关键超参数的选择依据
   ```python
   # 论文 Section 4.2: hidden_dim=512 在大多数任务上表现最佳
   self.hidden_dim = 512
   ```

3. **与官方实现差异：** 如有不同，明确标注
   ```python
   # 注意：官方代码使用 LayerNorm，这里用 BatchNorm 替代
   # 原因：小 batch size 下 LayerNorm 更稳定
   ```

## Git 规范

### .gitignore
```
__pycache__/
*.pyc
checkpoints/
logs/
*.log
.env
.DS_Store
```

### Commit Message
```
feat: 实现论文核心注意力机制
fix: 修复梯度计算错误
docs: 添加 API 文档
test: 添加单元测试
```

## 文档规范

### README.md 必含内容

1. 论文信息（标题、作者、链接）
2. 环境要求
3. 快速开始
4. 复现结果对比
5. 与官方实现的差异说明

---

*参考：https://github.com/ossu/computer-science*
