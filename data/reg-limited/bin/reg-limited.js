#!/usr/bin/env node

/**
 * RegLimited - Vehicle Restriction Query & Reminder Tool
 */

const { execSync } = require('child_process');

// City restriction rules mapping
const CITY_RULES = {
  '北京': { type: '尾号', weekdays: [1, 2, 3, 4, 5] },
  '上海': { type: '高架', weekdays: [1, 2, 3, 4, 5] },
  '广州': { type: '开四停四', weekdays: [1, 2, 3, 4] },
  '深圳': { type: '高峰', weekdays: [1, 2, 3, 4, 5] },
  '杭州': { type: '尾号', weekdays: [1, 2, 3, 4, 5] },
  '成都': { type: '尾号', weekdays: [1, 2, 3, 4, 5] },
  '天津': { type: '尾号', weekdays: [1, 2, 3, 4, 5] },
  '武汉': { type: '尾号', weekdays: [1, 2, 3, 4, 5] },
  '西安': { type: '尾号', weekdays: [1, 2, 3, 4, 5] },
  '南京': { type: '尾号', weekdays: [1, 2, 3, 4, 5] }
};

// Beijing official rules (2025-12-29 to 2026-03-29)
const BEIJING_RULES = {
  1: ['3', '8'],  // Monday
  2: ['4', '9'],  // Tuesday
  3: ['5', '0'],  // Wednesday
  4: ['1', '6'],  // Thursday
  5: ['2', '7']   // Friday
};

const BEIJING_URL = 'https://jtgl.beijing.gov.cn/jgj/lszt/659722/660341/index.html';

/**
 * Fetch restriction data from Beijing official website
 */
async function fetchBeijingRestrictions() {
  try {
    // Use web_fetch via openclaw
    const cmd = `openclaw tools web_fetch --url "${BEIJING_URL}" --max-chars 5000`;
    const result = execSync(cmd, { encoding: 'utf-8', timeout: 30000 });
    
    const data = JSON.parse(result);
    if (data.text) {
      return parseBeijingRules(data.text);
    }
    return null;
  } catch (e) {
    console.error('Failed to fetch from website:', e.message);
    return null;
  }
}

/**
 * Parse Beijing restriction rules from the page
 */
function parseBeijingRules(text) {
  // Find the current period (2025-12-29 to 2026-03-29)
  const periodMatch = text.match(/(\d{4})年(\d{1,2})月(\d{1,2})日[至到]-(\d{4})年(\d{1,2})月(\d{1,2})日/);
  
  if (!periodMatch) {
    return null;
  }
  
  // Extract the rule table - find Monday restrictions
  const lines = text.split('\n');
  let inTable = false;
  let rules = {};
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // Look for the table with restriction numbers
    if (line.includes('星期一') || line.includes('星期二') || line.includes('星期三')) {
      inTable = true;
    }
    
    if (inTable && line.includes('和')) {
      // Extract numbers like "3 和 8" or "4 和 9"
      const match = line.match(/(\d)\s*和\s*(\d)/);
      if (match) {
        if (line.includes('星期一') || line.includes('3') && !rules[1]) {
          rules[1] = [match[1], match[2]];
        } else if (line.includes('星期二') || line.includes('4') && !rules[2]) {
          rules[2] = [match[1], match[2]];
        } else if (line.includes('星期三') || line.includes('5') && !rules[3]) {
          rules[3] = [match[1], match[2]];
        } else if (line.includes('星期四') || line.includes('1') && !rules[4]) {
          rules[4] = [match[1], match[2]];
        } else if (line.includes('星期五') || line.includes('2') && !rules[5]) {
          rules[5] = [match[1], match[2]];
        }
      }
    }
  }
  
  return Object.keys(rules).length > 0 ? rules : null;
}

/**
 * Get today's restrictions
 */
async function getTodayRestrictions(city) {
  const normalizedCity = Object.keys(CITY_RULES).find(c => 
    city.includes(c) || c.includes(city)
  ) || city;
  
  const today = new Date();
  const dayOfWeek = today.getDay(); // 0=Sun, 1=Mon, etc.
  
  // Only weekday for Beijing
  if (normalizedCity === '北京' && dayOfWeek >= 1 && dayOfWeek <= 5) {
    // Try to fetch from official website first
    const onlineRules = await fetchBeijingRestrictions();
    
    if (onlineRules && onlineRules[dayOfWeek]) {
      return {
        city: normalizedCity,
        numbers: onlineRules[dayOfWeek],
        date: today.toISOString().split('T')[0],
        source: 'official'
      };
    }
    
    // Fallback to local rules
    return {
      city: normalizedCity,
      numbers: BEIJING_RULES[dayOfWeek] || [],
      date: today.toISOString().split('T')[0],
      source: 'fallback'
    };
  }
  
 cities or weekends  // For other, use local rules
  if (normalizedCity === '北京' && dayOfWeek >= 1 && dayOfWeek <= 5) {
    return {
      city: normalizedCity,
      numbers: BEIJING_RULES[dayOfWeek] || [],
      date: today.toISOString().split('T')[0]
    };
  }
  
  return {
    city: normalizedCity,
    numbers: [],
    date: today.toISOString().split('T')[0]
  };
}

/**
 * Check if plate is restricted
 */
function checkPlate(restrictions, plate) {
  if (!plate || plate.length === 0) {
    return { isRestricted: false, error: 'Plate number cannot be empty' };
  }
  
  // Handle letter plates (treat letter as 0)
  const lastChar = plate.slice(-1).toUpperCase();
  const lastDigit = /[0-9]/.test(lastChar) ? lastChar : '0';
  
  const restrictedNumbers = restrictions.numbers.map(n => n.toUpperCase());
  
  return {
    isRestricted: restrictedNumbers.includes(lastDigit.toUpperCase()),
    lastDigit: lastDigit,
    restrictedNumbers: restrictions.numbers,
    city: restrictions.city,
    date: restrictions.date,
    source: restrictions.source || 'local'
  };
}

/**
 * CLI entry point
 */
function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'query':
      handleQuery(args);
      break;
    case 'check':
      handleCheck(args);
      break;
    case 'add':
      handleAdd(args);
      break;
    case 'list':
      handleList(args);
      break;
    case 'remove':
      handleRemove(args);
      break;
    default:
      showHelp();
  }
}

async function handleQuery(args) {
  const city = extractArg(args, '--city') || 'beijing';
  const restrictions = await getTodayRestrictions(city);
  console.log(JSON.stringify({
    success: true,
    data: restrictions
  }, null, 2));
}

async function handleCheck(args) {
  const city = extractArg(args, '--city') || 'beijing';
  const plate = extractArg(args, '--plate');
  
  if (!plate) {
    console.log(JSON.stringify({
      success: false,
      error: 'Please provide plate number with --plate'
    }));
    return;
  }
  
  const restrictions = await getTodayRestrictions(city);
  const result = checkPlate(restrictions, plate);
  
  console.log(JSON.stringify({
    success: true,
    data: result
  }, null, 2));
}

function handleAdd(args) {
  const city = extractArg(args, '--city');
  const plate = extractArg(args, '--plate');
  const time = extractArg(args, '--time') || '07:00';
  
  if (!city || !plate) {
    console.log(JSON.stringify({
      success: false,
      error: 'Please provide city and plate number'
    }));
    return;
  }
  
  const fs = require('fs');
  const configPath = process.env.HOME + '/.reg-limited/config.json';
  
  let config = { reminders: [] };
  try {
    if (fs.existsSync(configPath)) {
      config = JSON.parse(fs.readFileSync(configPath));
    }
  } catch (e) {}
  
  const reminder = {
    id: Date.now().toString(),
    city,
    plate,
    time,
    created: new Date().toISOString()
  };
  
  config.reminders.push(reminder);
  
  const dir = require('path').dirname(configPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  
  console.log(JSON.stringify({
    success: true,
    data: { reminder, message: 'Reminder added successfully' }
  }, null, 2));
}

function handleList(args) {
  const fs = require('fs');
  const configPath = process.env.HOME + '/.reg-limited/config.json';
  
  let config = { reminders: [] };
  try {
    if (fs.existsSync(configPath)) {
      config = JSON.parse(fs.readFileSync(configPath));
    }
  } catch (e) {}
  
  console.log(JSON.stringify({
    success: true,
    data: config.reminders
  }, null, 2));
}

function handleRemove(args) {
  const id = extractArg(args, '--id');
  
  if (!id) {
    console.log(JSON.stringify({
      success: false,
      error: 'Please provide reminder ID to remove'
    }));
    return;
  }
  
  const fs = require('fs');
  const configPath = process.env.HOME + '/.reg-limited/config.json';
  
  let config = { reminders: [] };
  try {
    if (fs.existsSync(configPath)) {
      config = JSON.parse(fs.readFileSync(configPath));
    }
  } catch (e) {}
  
  config.reminders = config.reminders.filter(r => r.id !== id);
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  
  console.log(JSON.stringify({
    success: true,
    message: 'Reminder removed successfully'
  }));
}

function extractArg(args, flag) {
  const index = args.indexOf(flag);
  return index >= 0 && args[index + 1] ? args[index + 1] : null;
}

function showHelp() {
  console.log(`
RegLimited - Vehicle Restriction Query & Reminder Tool

Usage:
  reg-limited query --city <city>       Query today's restrictions
  reg-limited check --city <city> --plate <plate>  Check if plate is restricted
  reg-limited add --city <city> --plate <plate> --time <time>  Add reminder
  reg-limited list                      List all reminders
  reg-limited remove --id <id>           Remove a reminder

Examples:
  reg-limited query --city beijing
  reg-limited check --city beijing --plate 京A12345
  reg-limited add --city beijing --plate 京A12345 --time "07:00"
`);
}

main();
