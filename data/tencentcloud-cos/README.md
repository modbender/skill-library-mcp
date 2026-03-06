# 腾讯云COS Clawdbot技能 ☁️

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://clawhub.com)
[![腾讯云COS](https://img.shields.io/badge/腾讯云-COS-green)](https://cloud.tencent.com/product/cos)
[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-orange)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-BSD3-brightgreen)](LICENSE)

基于腾讯云官方 [cos-mcp](https://www.npmjs.com/package/cos-mcp) MCP服务器的Clawdbot技能，提供完整的腾讯云对象存储(COS)和数据万象(CI)能力集成。

## ✨ 特性

### 🗂️ 核心功能
- **文件管理**: 上传、下载、列出、删除COS文件
- **图片处理**: 质量评估、超分辨率、智能抠图、二维码识别
- **智能搜索**: 以图搜图、文本搜图
- **文档处理**: 文档转PDF、视频封面生成
- **批量操作**: 支持批量上传、下载、处理

### 🚀 技术优势
- **官方集成**: 基于腾讯云官方cos-mcp MCP服务器
- **标准协议**: 完全兼容MCP (Model Context Protocol)
- **易于使用**: 简单的配置和直观的命令
- **安全可靠**: 支持环境变量加密和访问控制
- **高性能**: 支持大文件分片上传和并发处理

## 📦 安装

### 快速安装
```bash
# 1. 克隆或下载本技能
git clone <repository-url>
cd tencent-cos

# 2. 运行安装脚本
chmod +x install.sh
./install.sh
```

### 手动安装
```bash
# 1. 安装腾讯云COS MCP服务器
npm install -g cos-mcp@latest

# 2. 配置环境变量
cp config/env.template .env
# 编辑 .env 文件，填入您的腾讯云COS配置

# 3. 配置Clawdbot
# 将 config/clawdbot_config.json 合并到 ~/.openclaw/openclaw.json
```

## ⚙️ 配置

### 环境变量配置
在 `.env` 文件中配置：
```bash
# 腾讯云COS配置
export TENCENT_COS_REGION="ap-guangzhou"
export TENCENT_COS_BUCKET="your-bucket-name-123456"
export TENCENT_COS_SECRET_ID="AKIDxxxxxxxxxxxxxxxxxxxxxxxx"
export TENCENT_COS_SECRET_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TENCENT_COS_DATASET_NAME="your-dataset"  # 可选，用于智能搜索
export TENCENT_COS_DEBUG="false"
```

### Clawdbot配置
在 `~/.openclaw/openclaw.json` 中添加：
```json
{
  "skills": {
    "entries": {
      "tencent-cos": {
        "enabled": true,
        "env": {
          "TENCENT_COS_REGION": "ap-guangzhou",
          "TENCENT_COS_BUCKET": "your-bucket-name-123456",
          "TENCENT_COS_SECRET_ID": "AKIDxxxxxxxxxxxxxxxxxxxxxxxx",
          "TENCENT_COS_SECRET_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        }
      }
    }
  }
}
```

## 📖 使用指南

### 基础命令
在Clawdbot中直接使用自然语言命令：

```
# 文件操作
上传文件到腾讯云COS: /path/to/local/file.jpg
从腾讯云COS下载文件: cos-file-key.jpg
列出腾讯云COS存储桶中的文件
删除COS文件: file-to-delete.jpg

# 图片处理
评估图片质量: image.jpg
提升图片分辨率: low-res-image.jpg
去除图片背景: portrait.jpg
识别二维码: qrcode-image.jpg
添加水印到图片: original.jpg 文字: "公司机密"

# 智能搜索
搜索相关图片: 风景照片
搜索相似图片: reference-image.jpg

# 文档处理
转换文档为PDF: document.docx
生成视频封面: video.mp4
```

### Python API
```python
from scripts.cos_wrapper import TencentCOSWrapper

# 初始化
cos = TencentCOSWrapper()

# 上传文件
result = cos.upload_file('local.jpg', 'remote/key.jpg')

# 下载文件
result = cos.download_file('remote/key.jpg', 'local_copy.jpg')

# 列出文件
result = cos.list_files(prefix='images/')

# 图片处理
result = cos.assess_image_quality('image.jpg')
result = cos.enhance_image_resolution('image.jpg')
result = cos.remove_image_background('portrait.jpg')

# 智能搜索
result = cos.search_by_text('风景照片')
result = cos.search_by_image('reference.jpg')
```

### 命令行工具
```bash
# 上传文件
python3 scripts/cos_wrapper.py --action upload --local-path file.jpg --cos-key remote/key.jpg

# 下载文件
python3 scripts/cos_wrapper.py --action download --cos-key remote/key.jpg --local-path local.jpg

# 列出文件
python3 scripts/cos_wrapper.py --action list --prefix images/

# 搜索图片
python3 scripts/cos_wrapper.py --action search-text --text "风景照片"
```

## 🎯 使用场景

### 场景1: 自动化文件备份
```python
# 自动备份工作目录到COS
import os
from scripts.cos_wrapper import TencentCOSWrapper

cos = TencentCOSWrapper()
backup_dir = '/path/to/backup'

for file in os.listdir(backup_dir):
    if file.endswith('.txt') or file.endswith('.pdf'):
        local_path = os.path.join(backup_dir, file)
        cos_key = f'backups/{file}'
        cos.upload_file(local_path, cos_key)
        print(f"已备份: {file}")
```

### 场景2: 图片处理流水线
```python
# 批量处理产品图片
cos = TencentCOSWrapper()

# 1. 上传原始图片
cos.upload_file('product.jpg', 'raw/product.jpg')

# 2. 评估质量
quality = cos.assess_image_quality('raw/product.jpg')

# 3. 提升分辨率（如果质量较低）
if quality.get('score', 0) < 80:
    cos.enhance_image_resolution('raw/product.jpg')

# 4. 添加水印
cos.add_text_watermark('raw/product.jpg', '品牌名称')

# 5. 存储到最终位置
print("图片处理完成")
```

### 场景3: 智能图片库
```python
# 建立智能图片搜索系统
cos = TencentCOSWrapper()

# 上传新图片
cos.upload_file('new_photo.jpg', 'gallery/photo1.jpg')

# 建立搜索索引（自动通过MCP服务器完成）
# 用户可以通过自然语言搜索
search_results = cos.search_by_text('蓝天白云')
print(f"找到 {len(search_results.get('results', []))} 张相关图片")
```

## 🏗️ 架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Clawdbot      │    │   本技能        │    │ 腾讯云COS MCP   │
│                 │    │                 │    │   服务器        │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │  用户命令  │──┼───▶│  │ Python    │──┼───▶│  │  cos-mcp  │  │
│  │           │  │    │  │ 包装器     │  │    │  │  进程     │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
│                 │    │                 │    │        │        │
└─────────────────┘    └─────────────────┘    └────────┼────────┘
                                                       │
                                                ┌──────▼──────┐
                                                │  腾讯云COS  │
                                                │    API      │
                                                └─────────────┘
```

## 🔧 开发指南

### 项目结构
```
tencent-cos/
├── SKILL.md                 # 技能主文档
├── README.md               # 项目README
├── install.sh              # 安装脚本
├── scripts/
│   └── cos_wrapper.py      # Python包装器
├── examples/
│   └── basic_usage.py      # 使用示例
├── config/
│   ├── template.json       # 配置模板
│   └── env.template        # 环境变量模板
└── LICENSE                 # 许可证文件
```

### 扩展功能
要添加新功能，可以：

1. **扩展Python包装器**:
   ```python
   class TencentCOSWrapper:
       def new_feature(self, params):
           # 实现新功能
           return self._call_mcp_tool('newTool', params)
   ```

2. **添加新的MCP工具**:
   需要修改cos-mcp服务器配置，添加新的工具定义

3. **创建新的使用示例**:
   在examples目录中添加新的示例文件

## 📊 性能优化

### 大文件处理
- 支持分片上传（默认5MB分片）
- 并发上传/下载
- 断点续传

### 缓存策略
- 本地文件缓存
- URL签名缓存
- 搜索结果缓存

### 错误处理
- 自动重试机制
- 详细的错误日志
- 优雅降级

## 🔒 安全建议

### 密钥管理
- 使用环境变量存储密钥
- 定期轮换访问密钥
- 使用子账号密钥，遵循最小权限原则

### 访问控制
- 设置存储桶访问权限
- 使用临时密钥进行敏感操作
- 启用操作日志审计

### 数据安全
- 启用服务器端加密
- 敏感数据单独存储
- 定期备份重要数据

## 🐛 故障排除

### 常见问题

1. **认证失败**
   ```
   错误: 检查SecretId和SecretKey是否正确
   解决方案: 重新生成密钥并更新配置
   ```

2. **网络连接问题**
   ```
   错误: 连接超时或网络错误
   解决方案: 检查网络连接，确认区域配置正确
   ```

3. **权限不足**
   ```
   错误: 操作被拒绝
   解决方案: 检查存储桶权限和密钥权限
   ```

### 调试模式
```bash
# 启用详细日志
export TENCENT_COS_DEBUG="true"

# 查看MCP服务器日志
cos-mcp --Region=ap-guangzhou --Bucket=test --SecretId=test --SecretKey=test --connectType=sse --port=3001
```

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 贡献流程
1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 开发环境
```bash
# 设置开发环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 运行测试
python3 -m pytest tests/
```

## 📄 许可证

本项目基于BSD-3许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- **腾讯云COS团队**: 提供优秀的对象存储服务
- **cos-mcp开发者**: 创建了优秀的MCP服务器
- **OpenClaw社区**: 提供了优秀的AI助手平台
- **所有贡献者**: 感谢你们的支持和贡献

## 📞 支持

- **问题反馈**: 在GitHub Issues中报告问题
- **功能请求**: 在GitHub Discussions中提出建议
- **文档问题**: 提交Pull Request修复文档

---
*最后更新: 2026-02-02 | 版本: 1.0.0*

**享受腾讯云COS带来的便捷存储体验吧！** 🚀