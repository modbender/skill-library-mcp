const Imap = require('imap');
const fs = require('fs');

const env = fs.readFileSync('../.env', 'utf8');
const config = {};
env.split('\n').forEach(line => {
  const [key, ...valueParts] = line.split('=');
  if (key && valueParts.length && !key.startsWith('#')) {
    config[key.trim()] = valueParts.join('=').trim();
  }
});

console.log('📬 正在检查未读邮件...\n');

const imap = new Imap({
  user: config.IMAP_USER,
  password: config.IMAP_PASS,
  host: config.IMAP_HOST,
  port: parseInt(config.IMAP_PORT) || 993,
  tls: config.IMAP_TLS === 'true',
  rejectUnauthorized: config.IMAP_REJECT_UNAUTHORIZED !== 'false',
  connTimeout: 15000,
  authTimeout: 15000
});

function decodeSubject(subject) {
  if (!subject) return '(无主题)';
  try {
    return subject.replace(/=\?([\w-]+)\?B\?([^\?]+)\?=/gi, (match, charset, text) => {
      return Buffer.from(text, 'base64').toString('utf-8');
    });
  } catch (e) {
    return subject;
  }
}

imap.once('ready', () => {
  imap.openBox('INBOX', true, (err, box) => {
    if (err) {
      console.log('❌ 打开邮箱失败:', err.message);
      imap.end();
      return;
    }
    
    imap.search(['UNSEEN'], (err, results) => {
      if (err) {
        console.log('❌ 搜索失败:', err.message);
        imap.end();
        return;
      }
      
      console.log(`📬 未读邮件总数: ${results.length} 封\n`);
      
      if (results.length === 0) {
        imap.end();
        return;
      }
      
      // Get latest 5 emails
      const latest = results.slice(-5).reverse();
      const f = imap.fetch(latest, { 
        bodies: 'HEADER',
        struct: true 
      });
      
      let count = 0;
      
      f.on('message', (msg, seqno) => {
        let headerStr = '';
        
        msg.on('body', (stream, info) => {
          // Get headers
          stream.on('data', (chunk) => { 
            headerStr += chunk.toString('utf8'); 
          });
          stream.once('end', () => {
            // Parse headers
            const lines = headerStr.split(/\r?\n/);
            let from = '', subject = '', date = '';
            let key = '', val = '';
            
            for (let line of lines) {
              if (line.match(/^[ \t]/)) {
                val += ' ' + line.trim();
              } else if (line.includes(':')) {
                if (key) {
                  if (key.toLowerCase() === 'from') from = val;
                  if (key.toLowerCase() === 'subject') subject = val;
                  if (key.toLowerCase() === 'date') date = val;
                }
                const idx = line.indexOf(':');
                key = line.slice(0, idx);
                val = line.slice(idx + 1).trim();
              }
            }
            // Last header
            if (key) {
              if (key.toLowerCase() === 'from') from = val;
              if (key.toLowerCase() === 'subject') subject = val;
              if (key.toLowerCase() === 'date') date = val;
            }
            
            count++;
            console.log(`${count}. 📧 ${from || '未知'}`);
            console.log(`   📝 ${decodeSubject(subject)}`);
            console.log(`   📅 ${date}`);
            console.log('');
          });
        });
      });
      
      f.once('end', () => {
        imap.end();
      });
    });
  });
});

imap.once('error', (err) => {
  console.log('❌ 连接错误:', err.message);
});

imap.connect();
