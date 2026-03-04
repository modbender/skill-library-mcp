# 阿里云百炼图像生成、编辑与翻译 Skill

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://clawhub.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![ClawHub](https://img.shields.io/badge/ClawHub-Synced-green.svg)](https://clawhub.com/skill/aliyun-image)

阿里云百炼平台提供的图像生成、编辑与翻译能力，包含千问-文生图(Qwen-Image)、千问-图像编辑(Qwen-Image-Edit)和千问-图像翻译(Qwen-MT-Image)三个模型。

## 🔄 同步更新

本项目在 **GitHub** 和 **ClawHub** 同步发布更新：

- **GitHub 仓库**: https://github.com/StanleyChanH/aliyun-image-skill
- **ClawHub 页面**: https://clawhub.com/skill/aliyun-image
- **GitHub Actions**: 自动同步 ✅

### 自动同步机制
- ✅ 使用 GitHub Actions 自动同步到 ClawHub
- ✅ 每次推送到 `main` 分支自动触发
- ✅ 版本号和更新日志保持一致
- ✅ GitHub Release 自动创建

### 配置自动同步
查看 [.github/SETUP.md](.github/SETUP.md) 了解如何配置 GitHub Actions 自动同步。

## 更新日志

### v1.1.0 (2026-02-13)
- 新增图像翻译功能（Qwen-MT-Image）
- 支持11种源语言和14种目标语言
- 提供术语定义、敏感词过滤、领域提示等高级功能
- 更新客户端脚本支持翻译命令

### v1.0.4 (2026-02-13)
- 修复 GitHub Actions 权限问题
- 添加 `permissions: contents: write` 以支持自动创建 Release
- 完整测试自动同步流程

### v1.0.3 (2026-02-13)
- 测试 GitHub Actions 自动同步到 ClawHub
- 验证自动发布流程

### v1.0.2 (2026-02-13)
- 作者改为 StanleyChanH
- 添加 GitHub Actions 自动同步到 ClawHub
- 更新文档说明 GitHub 和 ClawHub 同步更新机制
- 添加配置文档 .github/SETUP.md

### v1.0.1 (2026-02-13)
- 更新 API 文档和示例代码
- 优化技能说明和触发词
- 完善参考文档结构

## 功能特性

### 🎨 文生图 (Qwen-Image)
- 根据文本描述生成图像
- 支持复杂文字渲染
- 多种分辨率选择
- 智能提示词改写

### ✏️ 图像编辑 (Qwen-Image-Edit)
- 单图编辑：修改文字、增删物体、改变动作
- 多图融合：人物换装、姿势迁移
- 风格迁移：艺术风格转换
- 细节增强：图像质量提升

### 🌐 图像翻译 (Qwen-MT-Image)
- 精准翻译图像中的文字
- 保留原始排版与内容信息
- 支持11种源语言（中/英/日/韩/俄/西/法/葡/意/德/越）
- 支持14种目标语言（含马来/泰/印尼/阿拉伯）
- 领域提示：电商、客服等场景优化
- 敏感词过滤：屏蔽指定内容
- 术语定义：自定义专业术语翻译

## 支持的模型

### 文生图模型
- `qwen-image-max` - 高质量，真实感强
- `qwen-image-plus` - 性价比高，多样化风格
- `qwen-image` - 基础版

### 图像编辑模型
- `qwen-image-edit-max` - 高质量编辑
- `qwen-image-edit-plus` - 性价比高
- `qwen-image-edit` - 基础版

### 图像翻译模型
- `qwen-mt-image` - 图像文字翻译，保留排版

## 安装要求

### 环境变量
```bash
export DASHSCOPE_API_KEY="your_api_key_here"
```

### 获取 API Key
1. 访问 [阿里云百炼控制台](https://bailian.console.aliyun.com/)
2. 创建并获取 API Key
3. 配置到环境变量

### 依赖安装（可选）
```bash
pip install requests
```

## 使用示例

### 文生图
```python
import requests

response = requests.post(
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
    headers={
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}"
    },
    json={
        "model": "qwen-image-plus",
        "input": {
            "messages": [{
                "role": "user",
                "content": [{"text": "一只可爱的橘猫"}]
            }]
        },
        "parameters": {
            "size": "1024*1024"
        }
    }
)
```

### 图像编辑
```python
response = requests.post(
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
    headers={"Authorization": f"Bearer {DASHSCOPE_API_KEY}"},
    json={
        "model": "qwen-image-edit-plus",
        "input": {
            "messages": [{
                "role": "user",
                "content": [
                    {"image": "https://example.com/input.jpg"},
                    {"text": "把背景改成星空"}
                ]
            }]
        }
    }
)
```

### 图像翻译
```python
import time

# 1. 创建翻译任务
response = requests.post(
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis",
    headers={
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "X-DashScope-Async": "enable"
    },
    json={
        "model": "qwen-mt-image",
        "input": {
            "image_url": "https://example.com/english-poster.jpg",
            "source_lang": "en",
            "target_lang": "zh"
        }
    }
)
task_id = response.json()["output"]["task_id"]

# 2. 轮询获取结果
while True:
    time.sleep(3)
    result = requests.get(
        f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {DASHSCOPE_API_KEY}"}
    ).json()
    if result["output"]["task_status"] == "SUCCEEDED":
        print(result["output"]["image_url"])
        break
```

### 使用客户端脚本
```bash
# 文生图
python scripts/client.py generate "一只橘猫在阳光下打盹" --size 1920*1080

# 图像编辑
python scripts/client.py edit "https://example.com/photo.jpg" "把背景换成星空" -n 2

# 图像翻译
python scripts/client.py translate "https://example.com/english.jpg" --source en --target zh

# 带高级选项的翻译
python scripts/client.py translate "https://example.com/ad.jpg" \
    --source auto --target zh \
    --domain "E-commerce product description" \
    --sensitives "促销,折扣" \
    --terms "API:应用程序接口,ML:机器学习"
```

## 特点

✅ 国内网络友好（阿里云服务）
✅ 支持中文提示词
✅ 多种分辨率选择
✅ 智能提示词优化
✅ 图像文字翻译，保留排版
✅ 24小时图像存储

## 适用场景

- 小红书封面生成
- 产品宣传图制作
- 社交媒体内容创作
- 艺术风格迁移
- 图像修复与增强
- 海报/说明书多语言翻译
- 跨境电商图片本地化

## 许可证

MIT

## 作者

StanleyChanH

## 同步更新

本项目在 **GitHub** 和 **ClawHub** 同步发布更新：

- **GitHub**: https://github.com/StanleyChanH/aliyun-image-skill
- **ClawHub**: https://clawhub.com/skill/aliyun-image

每次发布新版本时，会同时推送到两个平台，确保用户可以从任一渠道获取最新版本。

### 版本同步策略
- 所有版本更新优先发布到 GitHub
- 通过自动化流程同步到 ClawHub
- 两个平台保持版本号一致

---

**注意**：使用本 skill 需要 [阿里云百炼](https://bailian.console.aliyun.com/) 账号和 API Key。
