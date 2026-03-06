# 公众号配图生成脚本使用说明

## 配置

配置文件：`scripts/image.env`

当前配置：
- 模型：GLM-Image
- 尺寸：900×383 像素（头条封面图推荐）
- API密钥：已配置

### 获取/更新API密钥

访问 [智谱AI开放平台](https://open.bigmodel.cn/) 获取新密钥。

## 安装依赖

```bash
pip install zhipuai
```

## 使用方法

### 1. 准备提示词文件

创建 `prompts.jsonl`：

```json
{"id": "cover", "size": "900x383", "prompt": "A 900x383 pixel infographic with warm cream paper texture, Chinese title about time management"}
{"id": "info1", "size": "900x383", "prompt": "A 900x383 pixel infographic showing a 3-step process, hand-drawn icons, warm colors"}
{"id": "cta", "size": "900x383", "prompt": "A 900x383 pixel infographic with heart icon, Chinese text for call to action"}
```

### 2. 运行脚本

```bash
# 基础用法
python scripts/generate_images.py --input prompts.jsonl

# 指定输出目录
python scripts/generate_images.py --input prompts.jsonl --out ./my_images

# 切换模型
python scripts/generate_images.py --input prompts.jsonl --model cogview-4
```

### 3. 查看结果

图片保存在指定输出目录。

## 图片尺寸规则

| 类型 | 尺寸 | 说明 |
|---|---|---|
| **头条封面图** | 900×383 | 推荐尺寸 |
| **核心内容区** | 中心383×383 | 防止信息丢失 |

**重要提示**：所有核心内容必须集中在图片中心约383×383像素范围内，以防止在头条展示时被裁剪。

## 支持的模型

| 模型 | 说明 |
|---|---|
| glm-image | 标准图片生成模型（默认） |
| cogview-4 | 高级图片生成模型 |

## API调用示例

```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="your-api-key")
response = client.images.generations(
    model="glm-image",
    prompt="A 900x383 pixel infographic with warm cream paper texture",
    size="900*383",
)
print(response.data[0].url)  # 图片URL
```

## 提示词模板参考

### 封面图
```
A 900x383 pixel infographic with warm cream paper texture background.
In the center, a large bold Chinese title "文章标题" in hand-drawn colored pencil style.
Important: keep all core content within the center 383x383 pixel area to prevent cropping.
Around the title, 2-3 small playful doodle icons related to the topic.
Colored pencil line art with light watercolor wash, warm colors, clean and cute.
Chinese text must be clear and readable.
```

### 信息图
```
A 900x383 pixel infographic on warm cream paper texture.
Title at top in hand-drawn colored pencil text.
Below, 3-4 horizontal cards, each with an icon and short Chinese text.
Important: keep core content within center 383x383 pixel area.
Colored pencil line art with light watercolor wash.
Warm color palette, clean layout with arrows between cards.
Ample white space, Chinese text clear and readable.
```

## 参数说明

| 参数 | 说明 | 默认值 |
|---|---|---|
| --config | 配置文件路径 | scripts/image.env |
| --input | 输入文件路径（必需） | - |
| --out | 输出目录 | outputs/images-时间戳 |
| --model | 模型名称 | glm-image |

## 注意事项

- 图片尺寸：默认 900×383 像素
- 核心内容区：中心 383×383 像素范围
- 提示词建议使用英文，效果更稳定
- 调用有频率限制，批量时注意控制节奏
- 生成时间约5-15秒/张
- API密钥请妥善保管，不要泄露
