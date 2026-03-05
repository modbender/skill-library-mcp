## 图片生成API配置（智谱AI CogView-4）

### 环境配置

配置文件：`scripts/image.env`

```bash
# API密钥 - 从 https://open.bigmodel.cn/ 获取
API_KEY=your-api-key-here

# 模型名称
MODEL=cogview-4
```

### 支持的模型

| 模型 | 说明 |
|---|---|
| **cogview-4** | 最新图片生成模型（推荐，默认） |
| glm-image | 标准图片生成模型 |

### 获取API密钥

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册/登录账号
3. 进入「API密钥」页面
4. 创建新的API密钥

### 安装依赖

```bash
pip install zai
```

### API调用示例

```python
from zai import ZhipuAiClient

client = ZhipuAiClient(api_key="your-api-key")
response = client.images.generations(
    model="cogview-4",
    prompt="A 16:9 infographic with warm cream paper texture",
)
print(response.data[0].url)  # 图片URL
```

### 批量生成

```bash
# 1. 准备提示词文件
cat > prompts.jsonl << EOF
{"id": "cover", "prompt": "A 16:9 infographic with warm cream paper texture..."}
{"id": "info1", "prompt": "A 16:9 infographic showing a 3-step process..."}
EOF

# 2. 运行生成脚本
python scripts/generate_images.py --input prompts.jsonl

# 3. 查看结果
# 输出目录: outputs/images-YYYYMMDD-HHMMSS/
```

### 注意事项

- 提示词建议使用英文，效果更稳定
- 调用有频率限制，批量时注意控制节奏
- 生成时间约5-15秒/张
- API密钥请妥善保管
