---
name: aliyun-oss
description: "阿里云OSS文件上传工具 - 安全、高效的文件上传和临时链接生成"
metadata:
  {
    "openclaw":
      {
        "emoji": "☁️",
        "requires": { "bins": ["python3"] },
        "install": [],
      },
  }
---

# 阿里云OSS文件上传工具

**安全、高效的文件上传和临时链接生成工具**

## 🎯 核心功能

- **✅ 单文件上传**: 支持上传单个本地文件到OSS
- **✅ 批量上传**: 支持同时上传多个文件
- **✅ 大文件分片上传**: 自动处理超过100MB的大文件
- **✅ 指定目录上传**: 可指定OSS中的存储路径
- **✅ 文件大小限制**: 拒绝超过2GB的文件
- **✅ 自动重命名**: 避免文件名冲突（UUID或时间戳策略）
- **✅ 预签名URL生成**: 自动生成临时访问链接
- **✅ 链接有效期自定义**: 支持1小时、6小时、1天、7天等选项
- **✅ 文件检索**: 根据文件名搜索OSS中的文件

## 🔒 安全特性

- **✅ AK/SK认证**: 使用阿里云AccessKey进行认证
- **✅ 配置分离**: 所有敏感信息通过外部配置文件管理
- **✅ 链接时效性**: 预签名URL自动过期，降低数据泄露风险
- **✅ 文件大小限制**: 防止上传超大文件

## ⚙️ 配置要求

创建配置文件 `/root/.openclaw/aliyun-oss-config.json`:

```json
{
  "endpoint": "oss-cn-shanghai.aliyuncs.com",
  "bucket_name": "your-bucket-name",
  "auth": {
    "access_key_id": "your-access-key-id",
    "access_key_secret": "your-access-key-secret"
  },
  "max_file_size_mb": 2048,
  "default_expire_hours": 0.5,
  "large_file_threshold_mb": 100,
  "default_prefix": "uploads/"
}
```

## 🚀 使用方法

### 命令行使用
```bash
# 上传单个文件
python3 main.py upload /path/to/file.txt uploads/

# 批量上传
python3 main.py batch_upload file1.txt file2.txt file3.txt uploads/

# 搜索文件
python3 main.py search filename.txt
```

### OpenClaw集成
- 支持作为媒体处理器处理文件上传
- 可通过OpenClaw的消息系统触发上传任务
- 生成的临时链接可直接在聊天中分享

## 🔧 技术细节

- **依赖**: `oss2`, `requests`
- **分片上传**: 使用OSS SDK的multipartUpload
- **预签名URL**: 使用OSS SDK的sign_url方法
- **错误处理**: 完善的异常处理和重试机制

## 🛡️ 安全最佳实践

1. **使用RAM用户**: 创建专门的RAM用户用于OSS上传
2. **最小权限**: 用户权限仅包含 `oss:PutObject`, `oss:GetObject`, `oss:ListObjects`
3. **配置文件权限**: 设置为600（仅所有者可读写）
4. **定期轮换**: 定期更新AccessKey

## 🆘 故障排除

- **403错误**: 检查RAM用户权限和AccessKey
- **文件大小超限**: 确认文件不超过2GB限制
- **上传失败**: 检查网络连接和OSS配置

## 💡 开发规范

此技能严格遵循以下开发准则：
1. ✅ **开源兼容性**: 完全符合开源skills的配置要求和目录结构
2. ✅ **合规性**: 完全符合当地的法律法规要求  
3. ✅ **功能完整性**: 仅包含已实现和测试通过的功能，无占位符或未完成代码

## 📦 部署说明

- **生产就绪**: 所有测试代码和临时文件已在发布前清理
- **安全配置**: 敏感信息通过外部配置文件管理，不在源码中硬编码
- **依赖管理**: 仅依赖必要的Python包（oss2, requests）