/**
 * 文章生成模块
 * 使用百炼 API（通义千问）自动生成公众号文章
 */

const fs = require('fs');
const path = require('path');
const config = require('./config');
const HotMonitor = require('./hot-monitor');

// 加载环境变量
require('dotenv').config();

class ArticleGenerator {
  constructor() {
    this.draftsDir = path.join(__dirname, config.storage.draftsDir);
    
    // 确保草稿目录存在
    if (!fs.existsSync(this.draftsDir)) {
      fs.mkdirSync(this.draftsDir, { recursive: true });
    }
  }

  /**
   * 调用百炼 API（通义千问）
   */
  async callLLM(prompt, systemPrompt = null) {
    const apiKey = process.env.DASHSCOPE_API_KEY;
    
    if (!apiKey) {
      console.log('[警告] 未配置 DASHSCOPE_API_KEY，使用模拟内容');
      return this.getMockContent(prompt);
    }
    
    console.log('[LLM] 调用百炼 API...');
    
    const { default: fetch } = await import('node-fetch');
    
    const messages = [];
    if (systemPrompt) {
      messages.push({ role: 'system', content: systemPrompt });
    }
    messages.push({ role: 'user', content: prompt });
    
    try {
      const response = await fetch(`${config.llm.baseURL}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          model: config.llm.model,
          messages: messages,
          temperature: config.llm.temperature,
          max_tokens: config.llm.maxTokens
        })
      });
      
      if (!response.ok) {
        const error = await response.text();
        throw new Error(`API 调用失败: ${response.status} ${error}`);
      }
      
      const data = await response.json();
      const content = data.choices[0]?.message?.content || '';
      
      console.log(`[LLM] 生成完成，共 ${content.length} 字`);
      return content;
      
    } catch (error) {
      console.error('[LLM] 调用失败:', error.message);
      return this.getMockContent(prompt);
    }
  }

  /**
   * 生成文章标题（3 个备选）
   */
  async generateTitles(topic) {
    const systemPrompt = `你是一名资深公众号编辑，擅长写爆款标题。
风格要求：
- 有冲突、有悬念、带情绪
- 能吸引眼球，让人想点进去
- 长度 20-30 字`;

    const prompt = `主题：${topic.title}
赛道：AI/科技资讯
目标读者：25-40 岁，对科技感兴趣的职场人士

请生成 3 个公众号文章标题，要求：
1. 吸引眼球，有点击欲
2. 包含关键词（AI/科技相关）
3. 可以用数字、疑问句、对比等技巧
4. 避免标题党，内容要能撑得起标题

直接输出 3 个标题，每行一个，不要编号，不要其他内容。`;

    const result = await this.callLLM(prompt, systemPrompt);
    return result.split('\n').filter(t => t.trim()).slice(0, 3);
  }

  /**
   * 生成完整文章（一次性生成，更高效）
   */
  async generateFullArticle(topic) {
    const { targetLength } = config.content;
    
    const systemPrompt = `你是一名资深科技公众号作者，文风犀利、有态度、善用对比反讽。

写作风格要求：
1. 标题：有冲突、有悬念、带情绪
2. 开头：金句 + 反转，吸引读者
3. 语言：犀利、有态度、善用对比反讽
4. 数据：具体数字 + 来源
5. 结尾：留白 + 金句，引发思考
6. 字数：${targetLength} 字左右

禁止：
- AI 味浓的表达（如"让我们一起..."、"总之..."）
- 小标题段落总结
- 强调结尾结束语
- ":解读"格式`;

    const prompt = `请写一篇公众号文章，选题如下：

【选题】${topic.title}
【来源】${topic.source}
【热度】${topic.hotValue}

要求：
1. 字数 ${targetLength} 字左右
2. 口语化程度 ≥85%
3. 段落 8-12 段，每段 2-4 句
4. 善用比喻、设问、金句
5. 开头要有吸引力，结尾要留白引发思考
6. 可以适当用 emoji，但不要太多

直接输出文章，格式如下：
# 标题

正文内容...`;

    return await this.callLLM(prompt, systemPrompt);
  }

  /**
   * 生成完整文章（主流程）
   */
  async generate(topic) {
    console.log('\n========== 文章生成开始 ==========');
    console.log(`选题：${topic.title}`);
    console.log(`来源：${topic.source} | 热度：${topic.hotValue}`);
    console.log('==================================\n');
    
    const startTime = Date.now();
    
    // 一次性生成完整文章
    console.log('[1/2] 生成文章...');
    const article = await this.generateFullArticle(topic);
    
    // 解析标题和正文
    const lines = article.split('\n');
    let title = topic.title;
    let content = article;
    
    // 如果第一行是 # 标题格式
    if (lines[0]?.startsWith('# ')) {
      title = lines[0].replace(/^# /, '').trim();
      content = lines.slice(1).join('\n').trim();
    }
    
    // 生成备选标题
    console.log('\n[2/2] 生成备选标题...');
    const titles = [title];
    try {
      const altTitles = await this.generateTitles(topic);
      if (altTitles.length > 0) {
        titles.length = 0;
        titles.push(...altTitles);
      }
    } catch (e) {
      console.log('[提示] 标题生成失败，使用原标题');
    }
    
    // 保存草稿
    const draft = this.saveDraft(topic, titles, content);
    
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    console.log(`\n========== 文章生成完成 (${elapsed}s) ==========`);
    console.log(`草稿已保存：${draft.fileName}`);
    
    return draft;
  }

  /**
   * 保存草稿
   */
  saveDraft(topic, titles, content) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const safeTitle = topic.title.slice(0, 20).replace(/[\\/:*?"<>|]/g, '');
    const fileName = `${timestamp}_${safeTitle}.md`;
    const filePath = path.join(this.draftsDir, fileName);
    
    const markdown = `---
title: ${titles[0]}
altTitles:
${titles.map(t => `  - ${t}`).join('\n')}
topic: ${topic.title}
source: ${topic.source}
hotValue: ${topic.hotValue}
createdAt: ${new Date().toISOString()}
status: draft
---

# ${titles[0]}

${content}

---

【备选标题】
${titles.map((t, i) => `${i + 1}. ${t}`).join('\n')}
`;
    
    fs.writeFileSync(filePath, markdown, 'utf8');
    
    return {
      filePath,
      fileName,
      title: titles[0],
      altTitles: titles,
      content,
      topic,
      createdAt: new Date().toISOString()
    };
  }

  /**
   * 从监控生成文章（批量）
   */
  async generateFromMonitor(limit = 3) {
    const monitor = new HotMonitor();
    
    // 加载最新选题
    let topics = monitor.loadLatestTopics();
    
    if (topics.length === 0) {
      console.log('[生成] 没有找到选题，先运行监控...');
      topics = await monitor.monitor();
    }
    
    if (topics.length === 0) {
      console.log('[生成] 仍然没有找到选题，退出');
      return [];
    }
    
    // 生成文章
    const drafts = [];
    for (let i = 0; i < Math.min(limit, topics.length); i++) {
      const draft = await this.generate(topics[i]);
      drafts.push(draft);
      
      // 避免频繁调用
      if (i < limit - 1) {
        console.log('\n等待 3 秒后生成下一篇...\n');
        await new Promise(r => setTimeout(r, 3000));
      }
    }
    
    return drafts;
  }

  /**
   * 模拟内容（API 未配置时使用）
   */
  getMockContent(prompt) {
    return `# AI 这波操作，有点东西

最近科技圈又炸了。

不是哪个大厂又发新机，也不是哪个 CEO 又上热搜，而是 AI 圈出了个大新闻。

说实话，看到这个消息的时候，我第一反应是：**又来？**

但仔细了解之后，发现这次确实有点不一样。

## 01 这波升级，动真格的

先说数据：性能提升 50%，成本降低 30%。

这不是 PPT 上的数字，是实打实的 benchmark 结果。

最关键的是，这次不再是"炫技"，而是真的能落地。

有开发者提前体验后说："以前用 AI 写代码，还得改半天；现在生成的代码，基本能直接用。"

这就有点东西了。

## 02 对普通人意味着什么？

短期看，不会有太大变化。

但长期看，**门槛在快速降低**。

以前想做个小程序，得学编程、学框架、学部署。现在？描述清楚需求，AI 帮你搞定 80%。

剩下那 20%？才是你真正的竞争力。

所以我的建议是：

1. 别抗拒，学会和 AI 协作
2. 把省下来的时间，用在 AI 做不了的事上
3. 保持学习，但学的是思路，不是死记硬背

## 03 一些思考

每次技术变革，都会有人焦虑。

当年 Excel 出现时，会计们担心失业；现在 AI 来了，大家又开始担心。

但回过头看，Excel 没让会计消失，反而让财务工作更高效。

AI 大概率也会是这样。

**真正被淘汰的，从来不是某个职业，而是不愿学习的人。`;

  }
}

// 直接运行时生成文章
if (require.main === module) {
  const generator = new ArticleGenerator();
  generator.generateFromMonitor(1).then(drafts => {
    console.log(`\n✅ 生成了 ${drafts.length} 篇草稿！`);
    drafts.forEach(d => console.log(`   - ${d.title}`));
  }).catch(console.error);
}

module.exports = ArticleGenerator;