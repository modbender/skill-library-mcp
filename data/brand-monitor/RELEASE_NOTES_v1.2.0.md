# Brand Monitor Skill v1.2.0 发布说明

## 🎉 新能源汽车品牌舆情监控 Skill

专为汽车品牌打造的零代码舆情监控解决方案。

## ✨ 主要特性

- 🔍 **多平台监控** - 覆盖 9+ 国内主流平台（微博、小红书、知乎、汽车之家、懂车帝、易车网、百度贴吧、抖音/快手）
- 😊 **情感分析** - 自动分析正面/中性/负面情感
- 🚨 **实时警报** - 及时发现负面提及和病毒式传播
- 📊 **趋势分析** - 生成品牌趋势报告
- 🎭 **官方账号过滤** - 关注第三方真实声音，默认排除品牌官方账号
- ⚡ **稳定可靠** - 使用 SerpAPI 专业搜索服务
- 📈 **数据质量评估** - 自动评估和补充数据完整度

## 🆕 v1.2.0 新功能

### 官方账号过滤
- 默认排除品牌官方自媒体账号
- 重点关注第三方真实声音
- 支持 `--include-official` 参数控制

### 数据质量改进
- 智能数据完整度评估
- 自动使用 web_fetch 补充重要内容
- 作者影响力估算（补充缺失的粉丝数）
- 汽车媒体白名单识别

### 改进的影响力计算
- 降低对缺失数据的依赖
- 增加作者影响力维度
- 更准确的影响力评分

## 📦 安装

### 方法 1: 通过 Git（推荐）

```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/你的用户名/brand-monitor-skill.git
cd brand-monitor-skill
./install.sh
```

### 方法 2: 手动下载

1. 下载 [brand-monitor-skill-v1.2.0.zip](https://github.com/你的用户名/brand-monitor-skill/releases/download/v1.2.0/brand-monitor-skill-v1.2.0.zip)
2. 解压到 `~/.openclaw/workspace/skills/brand-monitor-skill`
3. 运行 `./install.sh`

## 🚀 快速开始

### 1. 获取 SerpAPI Key

访问 https://serpapi.com/ 注册并获取 API Key（免费额度 100 次/月）

### 2. 设置环境变量

```bash
# Linux/macOS
export SERPAPI_KEY='your_api_key_here'
export SERPAPI_ENGINE='baidu'

# Windows (PowerShell)
$env:SERPAPI_KEY='your_api_key_here'
$env:SERPAPI_ENGINE='baidu'
```

### 3. 配置 Skill

```bash
cd ~/.openclaw/workspace/skills/brand-monitor-skill
cp config.example.json config.json
nano config.json
```

最小配置：
```json
{
  "brand_name": "理想汽车",
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook"
}
```

### 4. 重启 OpenClaw

```bash
openclaw gateway restart
```

### 5. 执行监控

在 OpenClaw 中发送消息：
```
执行品牌监控
```

或使用命令行：
```bash
openclaw agent --message "执行品牌监控"
```

## 📚 文档

- [README.md](README.md) - 完整文档
- [快速参考.md](快速参考.md) - 快速参考
- [如何使用Skill.md](如何使用Skill.md) - 使用指南
- [使用指南-SerpAPI版.md](使用指南-SerpAPI版.md) - 详细指南
- [获取飞书Webhook指南.md](获取飞书Webhook指南.md) - 飞书配置
- [CHANGELOG.md](CHANGELOG.md) - 完整更新日志

## 🔧 技术细节

### 支持的平台

- 📕 小红书 (xiaohongshu.com)
- 🔴 微博 (weibo.com)
- 🚗 汽车之家 (autohome.com.cn)
- 🎬 懂车帝 (dongchedi.com)
- 🚙 易车网 (yiche.com)
- 🤔 知乎 (zhihu.com)
- 💬 百度贴吧 (tieba.baidu.com)
- 🎵 抖音/快手

### 搜索引擎

- Google（国际用户）
- 百度（推荐，中文平台效果最好）
- Bing

### 数据提取

从搜索结果摘要中提取：
- 发布时间
- 作者信息
- 互动数据（点赞、评论、转发）
- 粉丝数
- 内容摘要

### 影响力评估

综合考虑：
- 互动数据（点赞、评论、转发）
- 作者影响力（粉丝数）
- 平台权重
- 数据完整度

## 🐛 Bug 修复

- 修复了 Windows UTF-8 编码问题
- 改进了官方账号识别逻辑
- 优化了数据提取准确率
- 修复了数据不完整的问题

## 📊 性能

- 每次搜索约 2-5 秒
- 支持 Mock 模式（无限免费测试）
- API 配额：100 次/月（免费）
- 推荐监控频率：每天 1-2 次

## 🔒 安全性

- 使用 SerpAPI 专业服务
- 本地数据处理
- 不存储敏感信息
- 遵守平台使用规则

## 🤝 贡献

欢迎贡献！请查看 [README.md](README.md) 了解贡献指南。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 🙏 致谢

感谢所有贡献者和用户的支持！

## 📞 联系方式

- GitHub Issues: https://github.com/你的用户名/brand-monitor-skill/issues
- OpenClaw 社区: https://community.openclaw.com

---

**Made with ❤️ for New Energy Vehicle Brands**
