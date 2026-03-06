const { publish } = require('./scripts/publish');

const config = {
  title: 'MiniMax + OpenClay 打造AI助手',
  content: `🤖 为什么选择 MiniMax + OpenClaw？

1. 国产大模型，性价比之王
- MiniMax M2.5 模型性能强劲
- API 价格亲民，适合个人开发者
- 国内节点，响应速度快

2. OpenClaw：你的私人 AI 调度中心
- 支持多模型切换（MiniMax、Kimi、Claude 等）
- 本地部署，数据安全可控
- 插件丰富，扩展性强

3. 7×24 小时待命的数字员工
- 自动处理重复性工作
- 智能调度任务优先级
- 学习你的习惯，越用越聪明

💡 能做什么？

📝 自动写作：文章、报告、邮件一键生成
📊 数据分析：快速整理信息，提炼要点
🛠️ 自动化工作流：定时任务、批量处理
💬 智能客服：处理咨询，自动回复
🎨 内容创作：小红书、公众号文案

🔧 快速上手
1. 下载 OpenClaw
2. 配置 MiniMax API
3. 安装需要的技能（Skill）
4. 开始你的 AI 之旅！

📱 了解更多
关注我，下期讲讲如何用 OpenClaw 搭建自动化工作流！`,
  images: ['C:\\Users\\90781\\.openclaw\\workspace\\skills\\xiaohongshu-publisher\\minimax_cover.jpg'],
  tags: ['AI工具', '个人助理', 'OpenClaw', 'MiniMax', '效率提升', '智能办公', '国产大模型']
};

publish(config).then(result => {
  if (result.success) {
    console.log('✅ 小红书发布成功！');
  } else {
    console.log('❌ 发布失败:', result.error);
    process.exit(1);
  }
}).catch(err => {
  console.error('❌ 错误:', err);
  process.exit(1);
});