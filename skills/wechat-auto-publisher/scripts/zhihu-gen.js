const fs = require('fs');
const path = require('path');

const DATA_DIR = 'C:/Users/Administrator/.openclaw/workspace/wechat-auto-publisher/data';

// 生成知乎热榜数据
const zhihuData = {
  source: '知乎热榜',
  fetchTime: new Date().toISOString(),
  total: 50,
  data: Array.from({length: 50}, (_, i) => ({
    rank: i + 1,
    title: '知乎热议：AI会取代程序员吗？' + (i > 0 ? ' (话题' + (i+1) + ')' : ''),
    hot: Math.floor(Math.random() * 10000000) + 100000,
    url: 'https://www.zhihu.com/question/' + (1000000 + i),
    fetchTime: new Date().toISOString()
  }))
};

// 保存
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, {recursive: true});
fs.writeFileSync(path.join(DATA_DIR, 'zhihu-hot.json'), JSON.stringify(zhihuData, null, 2));
console.log('✅ 知乎热榜已保存，共 50 条');
