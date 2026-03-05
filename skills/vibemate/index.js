#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');
const { program } = require('commander');

// ============ 配置 ============
const BOOK_EXTENSIONS = ['.epub', '.pdf', '.mobi', '.azw', '.azw3'];

const DEFAULT_SCAN_PATHS = [
  path.join(os.homedir(), 'Documents'),
  path.join(os.homedir(), 'Downloads')
];

const SENSITIVE_KEYWORDS = [
  'invoice', 'tax', 'salary', 'resume', 'password', 
  'contract', 'statement', 'bank', 'confidential', 'secret'
];

const WEB_FICTION_DOMAINS = [
  'archiveofourown.org/works/',
  'wattpad.com/story/',
  'royalroad.com/fiction/',
  'fanfiction.net/s/',
  'goodreads.com/book/',
  'amazon.com/dp/',
  'amazon.com/gp/product/',
  'book.douban.com/subject/',
  'douban.com/group/topic/',
  'reddit.com/r/FanFiction/',
  'reddit.com/r/Roleplay/',
  'reddit.com/r/WritingPrompts/'
];

const SERVER_URL = 'https://vibemate-server.vercel.app';
const CONFIG_PATH = path.join(os.homedir(), '.vibemate_config.json');

// ============ 工具函数 ============

// 获取或生成 master_id（跨平台唯一身份）
function getUserId() {
  let config = {};
  
  if (fs.existsSync(CONFIG_PATH)) {
    config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  }
  
  // 如果没有 master_id，生成一个
  if (!config.master_id) {
    config.master_id = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  }
  
  return config.master_id;
}

function isSensitive(filename) {
  const lower = filename.toLowerCase();
  
  for (const keyword of SENSITIVE_KEYWORDS) {
    if (lower.includes(keyword)) return true;
  }
  
  const nameWithoutExt = path.parse(filename).name;
  if (/^\d+$/.test(nameWithoutExt)) return true;
  
  return false;
}

function scanDirectory(dirPath, extensions, limit) {
  const results = [];
  
  function scan(currentPath) {
    if (results.length >= limit) return;
    
    let items;
    try {
      items = fs.readdirSync(currentPath);
    } catch (err) {
      return;
    }
    
    for (const item of items) {
      if (results.length >= limit) break;
      
      const fullPath = path.join(currentPath, item);
      
      let stat;
      try {
        stat = fs.statSync(fullPath);
      } catch (err) {
        continue;
      }
      
      if (stat.isDirectory()) {
        if (!item.startsWith('.')) {
          scan(fullPath);
        }
      } else if (stat.isFile()) {
        const ext = path.extname(item).toLowerCase();
        if (extensions.includes(ext) && !isSensitive(item)) {
          results.push({
            name: item,
            modified: stat.mtime
          });
        }
      }
    }
  }
  
  scan(dirPath);
  results.sort((a, b) => b.modified - a.modified);
  
  return results.slice(0, limit).map(r => r.name);
}

function scanMultipleDirectories(paths, extensions, limit) {
  let allResults = [];
  
  for (const dirPath of paths) {
    if (fs.existsSync(dirPath)) {
      const results = scanDirectory(dirPath, extensions, limit);
      allResults = allResults.concat(results);
    }
  }
  
  return [...new Set(allResults)].slice(0, limit);
}

function getPlatformName(url) {
  if (url.includes('archiveofourown.org')) return 'AO3';
  if (url.includes('wattpad.com')) return 'Wattpad';
  if (url.includes('royalroad.com')) return 'Royal Road';
  if (url.includes('fanfiction.net')) return 'FanFiction.net';
  if (url.includes('goodreads.com')) return 'Goodreads';
  if (url.includes('amazon.com')) return 'Amazon';
  if (url.includes('douban.com')) return 'Douban';
  if (url.includes('reddit.com/r/FanFiction')) return 'Reddit-FanFiction';
  if (url.includes('reddit.com/r/Roleplay')) return 'Reddit-Roleplay';
  if (url.includes('reddit.com/r/WritingPrompts')) return 'Reddit-WritingPrompts';
  return 'Other';
}

function readChromeBookmarks() {
  const bookmarksPath = path.join(
    os.homedir(),
    'Library/Application Support/Google/Chrome/Default/Bookmarks'
  );
  
  if (!fs.existsSync(bookmarksPath)) {
    console.log('Chrome bookmarks not found, skipping...');
    return [];
  }
  
  let data;
  try {
    data = JSON.parse(fs.readFileSync(bookmarksPath, 'utf8'));
  } catch (err) {
    console.log('Failed to read Chrome bookmarks, skipping...');
    return [];
  }
  
  const results = [];
  
  function traverse(node) {
    if (!node) return;
    
    if (node.url) {
      for (const domain of WEB_FICTION_DOMAINS) {
        if (node.url.includes(domain)) {
          results.push({
            title: node.name,
            url: node.url,
            platform: getPlatformName(node.url)
          });
          break;
        }
      }
    }
    
    if (node.children) {
      for (const child of node.children) {
        traverse(child);
      }
    }
  }
  
  if (data.roots) {
    traverse(data.roots.bookmark_bar);
    traverse(data.roots.other);
    traverse(data.roots.synced);
  }
  
  return results;
}

async function postData(url, data) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
}

async function getData(url) {
  const response = await fetch(url);
  return response.json();
}

// ============ 命令 ============

program
  .name('vibemate')
  .description('Scan your local books and find reading buddies')
  .version('1.3.0');

program
  .command('scan')
  .description('Scan local books and Chrome bookmarks')
  .option('-l, --limit <number>', 'Maximum files to scan', '50')
  .action((options) => {
    console.log('🔍 VibeMate scanning...\n');
    
    const limit = parseInt(options.limit);
    
    console.log('📁 Scanning local books:');
    console.log('   Paths: ~/Documents, ~/Downloads');
    console.log(`   Formats: ${BOOK_EXTENSIONS.join(', ')}`);
    const localBooks = scanMultipleDirectories(DEFAULT_SCAN_PATHS, BOOK_EXTENSIONS, limit);
    console.log(`   Found ${localBooks.length} books\n`);
    
    console.log('🌐 Scanning Chrome bookmarks...');
    console.log('   Platforms: AO3, Wattpad, Royal Road, FanFiction.net,');
    console.log('              Goodreads, Amazon, Douban, Reddit');
    const webFiction = readChromeBookmarks();
    console.log(`   Found ${webFiction.length} bookmarks\n`);
    
    const platformCounts = {};
    webFiction.forEach(item => {
      platformCounts[item.platform] = (platformCounts[item.platform] || 0) + 1;
    });
    if (Object.keys(platformCounts).length > 0) {
      console.log('   Platform breakdown:');
      Object.entries(platformCounts).forEach(([platform, count]) => {
        console.log(`     - ${platform}: ${count}`);
      });
      console.log('');
    }
    
    const output = {
      generated_at: new Date().toISOString(),
      local_books: localBooks,
      web_fiction: webFiction
    };
    
    const outputPath = path.join(process.cwd(), 'vibemate_profile.json');
    fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
    
    console.log('✅ Scan complete!');
    console.log(`📄 Results saved to: ${outputPath}`);
  });

program
  .command('upload')
  .description('Upload your reading profile to find matches')
  .option('-v, --vibes <vibes>', 'Your reading vibes (comma separated)', '')
  .option('-i, --interests <interests>', 'Your interests (comma separated)', '')
  .action(async (options) => {
    const profilePath = path.join(process.cwd(), 'vibemate_profile.json');
    
    if (!fs.existsSync(profilePath)) {
      console.log('❌ Please run "vibemate scan" first');
      return;
    }
    
    const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
    const userId = getUserId();
    
    const vibes = options.vibes ? options.vibes.split(',').map(v => v.trim()) : [];
    const interests = options.interests ? options.interests.split(',').map(i => i.trim()) : [];
    
    console.log('📤 Uploading profile to VibeMate server...\n');
    console.log(`   User ID: ${userId}`);
    console.log(`   Books: ${profile.local_books.length}`);
    console.log(`   Bookmarks: ${profile.web_fiction.length}`);
    
    try {
      const result = await postData(`${SERVER_URL}/api/profile`, {
        user_id: userId,
        local_books: profile.local_books,
        web_fiction: profile.web_fiction,
        vibes: vibes,
        interests: interests
      });
      
      console.log('\n✅ Upload successful!');
      console.log(`📊 Total users: ${result.total_profiles}`);
    } catch (err) {
      console.log('\n❌ Upload failed:', err.message);
    }
  });

program
  .command('match')
  .description('Find reading buddies with similar taste')
  .action(async () => {
    const userId = getUserId();
    
    console.log('🔍 Finding reading buddies...\n');
    
    try {
      const result = await getData(`${SERVER_URL}/api/match?user_id=${userId}`);
      
      if (result.error) {
        console.log('❌', result.error);
        return;
      }
      
      console.log(`📚 Your vibes: ${result.your_vibes.join(', ') || 'Not set'}`);
      console.log(`🎯 Your interests: ${result.your_interests.join(', ') || 'Not set'}`);
      console.log('\n' + result.message + '\n');
      
      if (result.matches.length > 0) {
        result.matches.forEach((match, i) => {
          console.log(`--- Buddy ${i + 1} ---`);
          console.log(`Common: ${[...match.common_vibes, ...match.common_interests].join(', ')}`);
          console.log(`Their books: ${match.their_books.join(', ')}`);
          if (match.their_fiction.length > 0) {
            console.log(`Their bookmarks: ${match.their_fiction.map(f => f.title).join(', ')}`);
          }
          console.log('');
        });
      }
    } catch (err) {
      console.log('❌ Match failed:', err.message);
    }
  });

program
  .command('whoami')
  .description('Show your VibeMate user ID')
  .action(() => {
    const userId = getUserId();
    const configPath = CONFIG_PATH;
    
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      console.log(`🆔 Your VibeMate ID: ${userId}`);
      console.log(`📍 Config location: ${configPath}`);
    } else {
      console.log(`🆔 Your VibeMate ID: ${userId}`);
    }
  });

program.parse();
