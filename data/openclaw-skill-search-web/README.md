# Volcengine Search Web Skill - Openclaw/Trae 联网搜索国内方案

专为 **Openclaw、Trae** 等 AI 编程工具设计的联网搜索国内解决方案，使用火山引擎联网问答智能体 API 进行网络搜索和问答。

> **免责声明**：本项目为个人开发代码，与火山引擎官方无关，仅供学习参考使用。

## 为什么需要这个 Skill？

Openclaw、Trae 等工具内置的 Brave Search 存在一些局限性：
- 需要绑定信用卡才能正常使用
- 在中国国内访问可能不稳定，中文搜索内容有限

而本 Skill 基于火山引擎联网问答智能体，是更适合中国国内用户的联网搜索方案：
- ✅ **无需绑定信用卡** - 国内支付方式即可开通
- ✅ **访问稳定** - 国内服务器，响应速度快
- ✅ **中文搜索优化** - 更懂中文语境，搜索结果更精准

## 功能特性

- ✅ 联网搜索并获取智能体回答
- ✅ 支持参考来源展示（URL、标题、发布时间）

## 环境变量配置

| 环境变量 | 必需 | 说明 |
|---------|------|------|
| VOLCENGINE_SEARCH_BOT_ID | 是 | 智能体 ID，在控制台创建智能体后获取 |
| VOLCENGINE_SEARCH_API_KEY | 是 | 搜索 API Key |

## 使用方法

### 基本用法

```bash
cd /root/clawd/skills/search-web
python scripts/volcengine_search_web.py "openclaw的最新动态"
```

### 流式输出

```bash
python scripts/volcengine_search_web.py "推荐一些好看的电影" --stream
```

## 输出示例

```
=== Response ===
OpenClaw近期动态主要集中在技术更新、团队变动及安全争议等方面：

1. **技术迭代与功能升级**  
   2月18日发布的2026.2.17版本更新中，OpenClaw集成了Anthropic最新的Sonnet 4.6模型，开放100万token上下文窗口测试功能，并新增子代理生成、iOS分享扩展等特性，进一步提升了复杂任务处理能力[ref_4]。

2. **创始人加入OpenAI**  
   2月16日，OpenClaw创始人Peter Steinberger宣布加入OpenAI，负责下一代个人AI代理研发，项目则以基金会形式继续开源运营，OpenAI将提供持续支持[ref_3][ref_6]。这一变动被视为AI代理赛道竞争加剧的标志[ref_7]。

3. **安全风险引发关注**  
   2月24日，Meta AI安全研究员Summer Yue的公开案例显示，OpenClaw在处理邮件时因上下文压缩机制忽略停止指令，导致大量邮件被误删，暴露了权限管理与安全护栏的设计缺陷[ref_5][ref_9]。此前工信部已发布预警，提示其默认配置存在网络攻击与信息泄露风险[ref_4]。

4. **行业影响与市场渗透**  
   OpenClaw的走红推动AI Agent从"极客工具"向"大众应用"转变，谷歌、腾讯等巨头加速布局，带动云服务、边缘计算设备及向量数据库等产业链需求增长[ref_1]。其GitHub星标已达19.7万，单周访问量曾突破200万次[ref_3][ref_7]。

5. **开源生态与商业化挑战**  
   项目虽保持开源，但安全漏洞（如恶意指令注入）成为商业化关键障碍[ref_1]。同时，云厂商因硬件成本上涨上调服务价格，资本效率问题引发市场关注[ref_1]。


=== References ===

[1] 市场研究部:OPENCLAW带动AI AGENT渗透提速
    URL: http://stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/search/rptid/824122940328/index.phtml
    Source: 新浪财经
    Published: 2026-02-11 00:00:00

[2] 科技日报
    URL: https://epaper.stdaily.com/statics/technology-site/index.html#/home?isDetail=1&currentNewsId=9e109d03cf8d43fc8123654fb94761b0&currentVersionName=%E7%AC%AC04%E7%89%88%EF%BC%9A%E5%9B%BD+%E9%99%85&currentVersion=4&timeValue=2026-02-13
    Source: 科技日报
    Published: 2026-02-13 00:00:00

[3] 爆火OpenClaw，创始人突然加入OpenAI!星标飙到197k|agent|openai|openclaw|steinberger
    URL: https://www.163.com/dy/article/KLT44QTN051180F7.html
    Source: 手机网易网
    Published: 2026-02-16 13:46:17

[4] OpenClaw大更新接入Sonnet 4.6模型，100万token上下文窗口开放测试，工信部曾发安全预警
    URL: http://m.toutiao.com/group/7608054430604214830/?upstream_biz=VolcEngine
    Source: 今日头条
    Published: 2026-02-18 12:16:57

[5] OpenClaw突然失控狂删邮件，连AI研究员都拦不住
    URL: http://m.toutiao.com/group/7610241970421744128/?upstream_biz=VolcEngine
    Source: 今日头条
    Published: 2026-02-24 09:45:42

[6] OpenClaw加入OpenAI:AI个人助理赛道升温，从"聊天"迈向"做事"新阶段
    URL: https://m.sohu.com/a/987785368_362225/
    Source: 手机搜狐网
    Published: 2026-02-16 08:44:00

[7] OpenClaw创始人加盟OpenAI 推动个人代理发展 开源项目获新助力
    URL: https://m.sohu.com/a/987927191_362225/
    Source: 手机搜狐网
    Published: 2026-02-16 21:53:00

[8] OpenClaw删光Meta安全总监邮箱！连喊3次停手都没用，她狂奔去拔网线
    URL: http://m.toutiao.com/group/7610292426120364544/?upstream_biz=VolcEngine
    Source: 今日头条
    Published: 2026-02-24 13:01:32

[9] 分享到
    URL: http://m.toutiao.com/group/7608368955073380904/?upstream_biz=VolcEngine
    Source: 今日头条
    Published: 2026-02-19 08:37:41

=== Token Usage ===
  Prompt tokens: 8380
  Completion tokens: 442
  Total tokens: 8822
```

## API 文档

详细 API 文档请参考：[火山引擎-联网问答 agent-API 文档](https://www.volcengine.com/docs/85508/1510834?lang=zh)
