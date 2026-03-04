// 龙港求职技能 - 爬虫主程序
// 使用方法: node crawl.js [偏好] [页数]

const http = require('http');
const iconv = require('iconv-lite');
const fs = require('fs');
const nodemailer = require('nodemailer');

// 获取命令行参数
const args = process.argv.slice(2);
let config = {
  preference: '电脑相关',
  pages: 5,
  email: ''  // 接收邮箱
};

// 解析参数
args.forEach(arg => {
  if (arg.startsWith('偏好:')) config.preference = arg.replace('偏好:', '').trim();
  if (arg.startsWith('页数:')) config.pages = parseInt(arg.replace('页数:', '').trim());
  if (arg.startsWith('邮箱:')) config.email = arg.replace('邮箱:', '').trim();
});

// 如果没有指定邮箱，使用默认值
if (!config.email) {
  config.email = '450733414@qq.com';
}

// 关键词配置
const keywordGroups = {
  '电脑相关': ['电脑', '计算机', '网络', 'IT', '程序员', '开发', '软件', '技术', '美工', '设计', '绘图', '制图', 'CAD', 'PS', '剪辑', '视频', '文员', '录入', '数据'],
  '客服': ['客服', '热线', '接单', '售后'],
  '外贸': ['外贸', '跟单', '跨境', '国际'],
  '文职': ['文员', '行政', '人事', '仓管', '仓库', '出纳', '收银', '会计'],
  '全部': []
};

function encodeGB2312(str) {
  return iconv.encode(str, 'gb2312').toString('binary')
    .replace(/./g, c => '%' + c.charCodeAt(0).toString(16).toUpperCase().padStart(2, '0'));
}

let allJobs = [];
let pageCount = 0;
const maxPages = config.pages;
const keywords = keywordGroups[config.preference] || keywordGroups['电脑相关'];

function crawlPage(pageNum, callback) {
  const path = pageNum === 1 ? '/ucregs/indexlist.asp' : `/ucregs/indexlist.asp?page=${pageNum}`;
  
  const options = {
    hostname: 'www.325802.net',
    path: path,
    method: 'GET',
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
  };

  const req = http.request(options, (res) => {
    const chunks = [];
    res.on('data', (chunk) => chunks.push(chunk));
    res.on('end', () => {
      const buffer = Buffer.concat(chunks);
      const text = iconv.decode(buffer, 'gbk');
      
      const rows = text.split('<tr ');
      
      rows.forEach((row) => {
        if (row.includes('action=申请&id=') && row.includes('class="red"')) {
          const posMatch = row.match(/class="red"[^>]*><font[^>]*>([^<]+)<\/font>/);
          const compMatch = row.match(/Viewcomp\.asp\?cname=([^&"]+)/);
          const idMatch = row.match(/action=申请&id=(\d+)/);
          
          if (posMatch) {
            const position = posMatch[1].trim();
            const company = compMatch ? decodeURIComponent(compMatch[1]) : '';
            
            const isMatch = config.preference === '全部' || 
              keywords.some(kw => position.toLowerCase().includes(kw.toLowerCase()));
            
            if (isMatch) {
              allJobs.push({
                id: idMatch ? idMatch[1] : '',
                position: position,
                company: company,
                companyEncoded: company ? encodeGB2312(company) : ''
              });
            }
          }
        }
      });
      
      pageCount++;
      console.log(`Page ${pageNum} done, matched jobs: ${allJobs.length}`);
      
      if (pageCount < maxPages) {
        setTimeout(() => crawlPage(pageCount + 1, callback), 800);
      } else {
        callback();
      }
    });
  });

  req.on('error', (e) => {
    console.error('Error on page ' + pageNum + ':', e.message);
    callback();
  });
  
  req.end();
}

function deduplicate(jobs) {
  const seen = new Map();
  jobs.forEach(job => {
    if (!seen.has(job.company)) {
      seen.set(job.company, job);
    }
  });
  return Array.from(seen.values());
}

function sendEmail(content) {
  // 邮件配置
  const transporter = nodemailer.createTransport({
    host: 'smtp.qq.com',
    port: 465,
    secure: true,
    auth: {
      user: '450733414@qq.com',
      pass: 'okjybcgpuprncbah'
    }
  });

  const mailOptions = {
    from: '450733414@qq.com',
    to: config.email,
    subject: `龙港325802求职信息 - ${new Date().toLocaleDateString('zh-CN')}`,
    text: content
  };

  transporter.sendMail(mailOptions, (err, info) => {
    if (err) {
      console.log('\n邮件发送失败:', err.message);
    } else {
      console.log('\n邮件已发送!', info.response);
    }
  });
}

function fetchJobDetails(job, callback) {
  if (!job.company || !job.companyEncoded) {
    job.contact = '未找到';
    job.phone = '未找到';
    job.address = '未找到';
    job.experience = '未找到';
    job.education = '未找到';
    job.description = '未找到';
    callback();
    return;
  }
  
  // 访问公司详情页
  const path = `/ucregs/Viewcomp.asp?cname=${job.companyEncoded}`;
  
  const options = {
    hostname: 'www.325802.net',
    port: 80,
    path: path,
    method: 'GET',
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
  };

  const req = http.request(options, (res) => {
    const chunks = [];
    res.on('data', (chunk) => chunks.push(chunk));
    res.on('end', () => {
      try {
        const buffer = Buffer.concat(chunks);
        const text = iconv.decode(buffer, 'gbk');
        
        // 提取公司信息
        const contactMatch = text.match(/联 系 人：<\/td>[^<]*<td[^>]*>([^<]+)/);
        const phoneMatch = text.match(/联系电话：<\/td>[^<]*<td[^>]*>([^<]+)/);
        const mobileMatch = text.match(/手　　机：<\/td>[^<]*<td[^>]*>([^<]+)/);
        const addressMatch = text.match(/通讯地址：<\/td>[^<]*<td[^>]*>([^<]+)/);
        
        job.contact = contactMatch ? contactMatch[1].trim() : '未找到';
        job.phone = phoneMatch ? phoneMatch[1].trim() : (mobileMatch ? mobileMatch[1].trim() : '未找到');
        job.address = addressMatch ? addressMatch[1].trim() : '未找到';
        
        // 提取职位详细信息
        let expMatch = text.match(/工作经验[：:]\s*<\/div><\/td>[^<]*<td[^>]*>([^<]+)/);
        if (!expMatch) expMatch = text.match(/工作经验[：:][^<]{0,20}([^<\n]+)/);
        
        let eduMatch = text.match(/学历要求[：:]\s*<\/div><\/td>[^<]*<td[^>]*>([^<]+)/);
        if (!eduMatch) eduMatch = text.match(/学历要求[：:][^<]{0,20}([^<\n]+)/);
        
        // 职位描述 - 在最后的td colspan=2中
        const descMatch = text.match(/<tr>[^<]*<td[^>]*colspan="2"[^>]*>[^<]*([^<]{20,})/);
        
        const descText = descMatch ? descMatch[1].trim().replace(/<br>/g, ' ').replace(/&nbsp;/g, ' ').replace(/^nbsp;/, '').substring(0, 200) : '';
        
        job.experience = expMatch ? expMatch[1].trim().replace(/&nbsp;/g, ' ') : '未找到';
        job.education = eduMatch ? eduMatch[1].trim().replace(/&nbsp;/g, ' ') : '未找到';
        job.description = descText && descText.length > 5 ? descText : '';
        
      } catch (err) {
        job.contact = '解析失败';
        job.phone = '解析失败';
        job.address = '解析失败';
        job.experience = '解析失败';
        job.education = '解析失败';
        job.description = '解析失败';
      }
      callback();
    });
  });

  req.on('error', (e) => {
    job.contact = '获取失败';
    job.phone = '获取失败';
    job.address = '获取失败';
    job.experience = '获取失败';
    job.education = '获取失败';
    job.description = '获取失败';
    callback();
  });
  
  req.end();
}

console.log('=== 龙港求职技能启动 ===');
console.log(`配置: 偏好=${config.preference}, 页数=${config.pages}\n`);

console.log('Step 1: 抓取职位信息...\n');

crawlPage(1, () => {
  console.log(`\n总计匹配职位: ${allJobs.length}`);
  
  console.log('\nStep 2: 获取公司详情...\n');
  
  let processed = 0;
  
  function processNext() {
    if (processed >= allJobs.length) {
      // 生成输出
      let output = `=== 龙港325802人才招聘网 - 职位信息 ===\n\n`;
      output += `求职偏好: ${config.preference}\n`;
      output += `搜索范围: 前${config.pages}页\n`;
      output += `匹配职位: ${allJobs.length}个\n\n`;
      
      allJobs.forEach((job, i) => {
        output += `${i + 1}. ${job.company}\n`;
        output += `   职位: ${job.position}\n`;
        output += `   地址: ${job.address}\n`;
        output += `   电话: ${job.phone}\n`;
        output += `   工作经验: ${job.experience}\n`;
        output += `   学历要求: ${job.education}\n`;
        if (job.description && job.description.length > 5) {
          output += `   职位描述: ${job.description}\n`;
        }
        output += '\n';
      });
      
      fs.writeFileSync('jobs_result.txt', output, 'utf8');
      console.log('\n已保存到 jobs_result.txt');
      
      // 发送邮件
      sendEmail(output);
      return;
    }
    
    const job = allJobs[processed];
    process.stdout.write(`[${processed + 1}/${allJobs.length}] ${job.company.substring(0, 15)}...`);
    
    fetchJobDetails(job, () => {
      console.log(` 电话:${job.phone} 经验:${job.experience} 学历:${job.education}`);
      processed++;
      setTimeout(processNext, 300);
    });
  }
  
  processNext();
});
