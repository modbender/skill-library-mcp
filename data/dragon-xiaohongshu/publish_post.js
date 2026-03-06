const { publish } = require('./scripts/publish');

const config = {
  title: '你最想用 AI 做什么？',
  content: `🤖 2025年了，AI已经不是科幻电影里的东西，而是真正能帮你干活的"数字员工"！

👇 以下 7 大 "数字员工" 功能，你的需求优先级是什么？
（选 3 个最刚需的，可多选）

A. 数字程序员 💻
   写代码 / 改代码，让开发效率翻倍

B. 数字测试员 🐛
   自动测 Bug，再也不用通宵改问题

C. 数字运营 ✍️
   写公众号/小红书文案 + 生成配图

D. 数字设计师 🎨
   自动生成 PPT，汇报不再愁

E. 数字运维 🚀
   一键部署应用到服务器

F. 数字发布员 📱
   社媒定时自动发布

G. 数字客服 💬
   处理售后 + Agent 更新提醒

💡 评论区告诉我你的选择！
比如：A、C、F

#AI工具 #效率神器 #数字化转型 #职场技能 #人工智能`,
  images: ['C:\\Users\\90781\\.openclaw\\workspace\\skills\\xiaohongshu-publisher\\cover.jpg'],
  tags: ['AI工具', '效率神器', '人工智能', '职场技能', '数字化转型']
};

publish(config).then(result => {
  if (result.success) {
    console.log('发布成功！');
  } else {
    console.log('发布失败:', result.error);
    process.exit(1);
  }
}).catch(err => {
  console.error('错误:', err);
  process.exit(1);
});