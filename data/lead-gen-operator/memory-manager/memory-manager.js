#!/usr/bin/env node

/**
 * Memory Manager - JSON persistence for OpenClaw
 * 
 * Commands:
 *   node memory-manager.js read <file>
 *   node memory-manager.js add-lead <file> <company> <contact> <email>
 *   node memory-manager.js list <file>
 *   node memory-manager.js update-status <file> <company> <status>
 *   node memory-manager.js update-notes <file> <company> <notes>
 *   node memory-manager.js score-lead <file> <company>
 *   node memory-manager.js export-csv <file>
 *   node memory-manager.js get-followups <file>
 *   node memory-manager.js stats <file>
 *   node memory-manager.js bulk-update-status <file> <status>
 */

const fs = require('fs');
const path = require('path');

const MEMORY_DIR = path.join(process.env.HOME || process.env.USERPROFILE, '.openclaw/workspace/memory');

const args = process.argv.slice(2);
const command = args[0];

// Ensure memory directory exists
if (!fs.existsSync(MEMORY_DIR)) {
  fs.mkdirSync(MEMORY_DIR, { recursive: true });
}

function getFilePath(filename) {
  return path.join(MEMORY_DIR, filename);
}

function readFile(filename) {
  const filepath = getFilePath(filename);
  if (!fs.existsSync(filepath)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(filepath, 'utf8'));
}

function writeFile(filename, data) {
  const filepath = getFilePath(filename);
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
  return filepath;
}

// Score lead based on company data
function scoreLead(lead) {
  let score = 0;
  
  // Funding score
  const funding = (lead.funding || '').toLowerCase();
  if (funding.includes('series a')) score += 20;
  if (funding.includes('series b')) score += 30;
  if (funding.includes('series c')) score += 40;
  if (funding.includes('unicorn') || funding.includes('1b')) score += 50;
  
  // Size score
  const size = (lead.size || '').toLowerCase();
  if (size.includes('1-10')) score += 10;
  if (size.includes('11-50')) score += 20;
  if (size.includes('51-100')) score += 30;
  if (size.includes('100+')) score += 40;
  
  // Industry score
  const industry = (lead.industry || '').toLowerCase();
  if (industry.includes('ai') || industry.includes('ml')) score += 15;
  if (industry.includes('fintech') || industry.includes('finance')) score += 15;
  if (industry.includes('saas')) score += 10;
  
  return Math.min(score, 100);
}

const VALID_STATUSES = ['new', 'enriched', 'drafted', 'sent', 'replied', 'closed', 'lost'];

switch (command) {
  case 'read':
    if (!args[1]) {
      console.error('Usage: node memory-manager.js read <filename>');
      process.exit(1);
    }
    const data = readFile(args[1]);
    console.log(JSON.stringify(data, null, 2));
    break;
    
  case 'add-lead':
    if (!args[1] || !args[2]) {
      console.error('Usage: node memory-manager.js add-lead <filename> <company> [contact] [email] [size] [industry] [funding]');
      process.exit(1);
    }
    const filename = args[1];
    let leadsData = readFile(filename) || { leads: [], metrics: {} };
    if (!leadsData.leads) leadsData.leads = [];
    if (!leadsData.metrics) leadsData.metrics = { total_found: 0, total_enriched: 0, total_drafted: 0, total_sent: 0 };
    
    const newLead = {
      id: Date.now().toString(),
      company: args[2],
      contact: args[3] || '',
      email: args[4] || '',
      size: args[5] || '',
      industry: args[6] || '',
      funding: args[7] || '',
      status: 'new',
      notes: '',
      score: 0,
      created_at: new Date().toISOString().split('T')[0],
      last_updated: new Date().toISOString()
    };
    
    // Calculate score
    newLead.score = scoreLead(newLead);
    
    leadsData.leads.push(newLead);
    leadsData.metrics.total_found = (leadsData.metrics.total_found || 0) + 1;
    
    writeFile(filename, leadsData);
    console.log(`Lead added: ${args[2]} (score: ${newLead.score})`);
    break;
    
  case 'update-status':
    if (!args[1] || !args[2] || !args[3]) {
      console.error('Usage: node memory-manager.js update-status <filename> <company> <status>');
      console.error('Valid statuses:', VALID_STATUSES.join(', '));
      process.exit(1);
    }
    const updateFile = args[1];
    const companyName = args[2].toLowerCase();
    const newStatus = args[3].toLowerCase();
    
    if (!VALID_STATUSES.includes(newStatus)) {
      console.error('Invalid status:', newStatus);
      console.error('Valid statuses:', VALID_STATUSES.join(', '));
      process.exit(1);
    }
    
    let updateData = readFile(updateFile);
    if (!updateData || !updateData.leads) {
      console.error('No leads found');
      process.exit(1);
    }
    
    let found = false;
    for (let lead of updateData.leads) {
      if (lead.company.toLowerCase() === companyName) {
        lead.status = newStatus;
        lead.last_updated = new Date().toISOString();
        found = true;
        console.log(`Updated ${lead.company} status to ${newStatus}`);
      }
    }
    
    if (!found) {
      console.error('Company not found:', args[2]);
      process.exit(1);
    }
    
    writeFile(updateFile, updateData);
    break;
    
  case 'update-notes':
    if (!args[1] || !args[2] || !args[3]) {
      console.error('Usage: node memory-manager.js update-notes <filename> <company> <notes>');
      process.exit(1);
    }
    const notesFile = args[1];
    const notesCompany = args[2].toLowerCase();
    const notes = args.slice(3).join(' ');
    
    let notesData = readFile(notesFile);
    if (!notesData || !notesData.leads) {
      console.error('No leads found');
      process.exit(1);
    }
    
    let notesFound = false;
    for (let lead of notesData.leads) {
      if (lead.company.toLowerCase() === notesCompany) {
        lead.notes = notes;
        lead.last_updated = new Date().toISOString();
        notesFound = true;
        console.log(`Updated notes for ${lead.company}: "${notes}"`);
      }
    }
    
    if (!notesFound) {
      console.error('Company not found:', args[2]);
      process.exit(1);
    }
    
    writeFile(notesFile, notesData);
    break;
    
  case 'score-lead':
    if (!args[1] || !args[2]) {
      console.error('Usage: node memory-manager.js score-lead <filename> <company>');
      process.exit(1);
    }
    const scoreFile = args[1];
    const scoreCompany = args[2].toLowerCase();
    
    let scoreData = readFile(scoreFile);
    if (!scoreData || !scoreData.leads) {
      console.error('No leads found');
      process.exit(1);
    }
    
    let scored = false;
    for (let lead of scoreData.leads) {
      if (lead.company.toLowerCase() === scoreCompany) {
        const newScore = scoreLead(lead);
        lead.score = newScore;
        lead.last_updated = new Date().toISOString();
        scored = true;
        console.log(`${lead.company}: Score ${newScore}/100`);
        console.log(`  Funding: ${lead.funding || 'N/A'}`);
        console.log(`  Size: ${lead.size || 'N/A'}`);
        console.log(`  Industry: ${lead.industry || 'N/A'}`);
      }
    }
    
    if (!scored) {
      console.error('Company not found:', args[2]);
      process.exit(1);
    }
    
    writeFile(scoreFile, scoreData);
    break;
    
  case 'list':
    if (!args[1]) {
      console.error('Usage: node memory-manager.js list <filename>');
      process.exit(1);
    }
    const listData = readFile(args[1]);
    if (listData && listData.leads) {
      console.log(`\n# ${args[1]} - ${listData.leads.length} leads\n`);
      listData.leads.forEach((lead, i) => {
        console.log(`${i + 1}. ${lead.company} | ${lead.status} | Score: ${lead.score || 0} | ${lead.notes ? '📝' : ''}`);
      });
      console.log('');
    } else {
      console.log('No data found');
    }
    break;
    
  case 'bulk-update-status':
    if (!args[1] || !args[2]) {
      console.error('Usage: node memory-manager.js bulk-update-status <filename> <status>');
      console.error('Valid statuses:', VALID_STATUSES.join(', '));
      process.exit(1);
    }
    const bulkFile = args[1];
    const bulkStatus = args[2].toLowerCase();
    
    if (!VALID_STATUSES.includes(bulkStatus)) {
      console.error('Invalid status:', bulkStatus);
      process.exit(1);
    }
    
    let bulkData = readFile(bulkFile);
    if (!bulkData || !bulkData.leads) {
      console.error('No leads found');
      process.exit(1);
    }
    
    let updated = 0;
    for (let lead of bulkData.leads) {
      if (lead.status === 'drafted') {
        lead.status = bulkStatus;
        lead.last_updated = new Date().toISOString();
        updated++;
      }
    }
    
    writeFile(bulkFile, bulkData);
    console.log(`Updated ${updated} leads to ${bulkStatus}`);
    break;
    
  case 'export-csv':
    if (!args[1]) {
      console.error('Usage: node memory-manager.js export-csv <filename>');
      process.exit(1);
    }
    const csvData = readFile(args[1]);
    if (!csvData || !csvData.leads) {
      console.error('No leads found');
      process.exit(1);
    }
    
    // CSV header
    console.log('ID,Company,Contact,Email,Size,Industry,Funding,Status,Score,Notes,Created,Last Updated');
    
    // CSV rows
    csvData.leads.forEach(lead => {
      console.log(`${lead.id},"${lead.company}","${lead.contact}","${lead.email}","${lead.size}","${lead.industry}","${lead.funding}",${lead.status},${lead.score || 0},"${lead.notes || ''}",${lead.created_at},${lead.last_updated || ''}`);
    });
    break;
    
  case 'get-followups':
    if (!args[1]) {
      console.error('Usage: node memory-manager.js get-followups <filename>');
      process.exit(1);
    }
    const followData = readFile(args[1]);
    if (!followData || !followData.leads) {
      console.log('No leads found');
      process.exit(0);
    }
    
    const now = new Date();
    const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    console.log('\n# Follow-up recommendations:\n');
    
    let foundFollowups = false;
    followData.leads.forEach(lead => {
      if (lead.status === 'sent' && lead.last_updated) {
        const lastUpdated = new Date(lead.last_updated);
        if (lastUpdated < sevenDaysAgo) {
          foundFollowups = true;
          const daysAgo = Math.floor((now - lastUpdated) / (1000 * 60 * 60 * 24));
          console.log(`- ${lead.company}: Sent ${daysAgo} days ago, no response`);
        }
      }
    });
    
    if (!foundFollowups) {
      console.log('No follow-ups needed right now.');
    }
    console.log('');
    break;
    
  case 'stats':
    if (!args[1]) {
      console.error('Usage: node memory-manager.js stats <filename>');
      process.exit(1);
    }
    const statsData = readFile(args[1]);
    if (!statsData || !statsData.leads) {
      console.log('No leads found');
      process.exit(0);
    }
    
    const counts = { new: 0, enriched: 0, drafted: 0, sent: 0, replied: 0, closed: 0, lost: 0 };
    let totalScore = 0;
    statsData.leads.forEach(lead => {
      counts[lead.status] = (counts[lead.status] || 0) + 1;
      totalScore += (lead.score || 0);
    });
    
    console.log('\n# Lead Stats:\n');
    Object.keys(counts).forEach(status => {
      console.log(`${status}: ${counts[status]}`);
    });
    console.log(`\nTotal leads: ${statsData.leads.length}`);
    console.log(`Average score: ${Math.round(totalScore / statsData.leads.length)}/100\n`);
    break;
    
  default:
    console.log('Memory Manager - JSON persistence for OpenClaw');
    console.log('');
    console.log('Commands:');
    console.log('  read <file>                      - Read JSON file');
    console.log('  add-lead <file> <company> [contact] [email] [size] [industry] [funding] - Add lead');
    console.log('  update-status <file> <company> <status> - Update lead status');
    console.log('  update-notes <file> <company> <notes> - Add notes to lead');
    console.log('  score-lead <file> <company>     - Score a lead');
    console.log('  list <file>                      - List leads with scores');
    console.log('  bulk-update-status <file> <status> - Update all drafted leads');
    console.log('  export-csv <file>                - Export to CSV');
    console.log('  get-followups <file>             - Get follow-up recommendations');
    console.log('  stats <file>                     - Show statistics');
    console.log('');
    console.log('Valid statuses: new, enriched, drafted, sent, replied, closed, lost');
    console.log('Memory directory:', MEMORY_DIR);
}
