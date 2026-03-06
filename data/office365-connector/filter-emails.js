#!/usr/bin/env node
const { getRecent } = require('./email.js');

const sinceDate = process.argv[2] || '2026-02-07T08:00:00Z';

getRecent(30).then(emails => {
  const cutoff = new Date(sinceDate);
  const recentEmails = emails.filter(e => new Date(e.receivedDateTime) >= cutoff);
  
  console.log(`Emails since ${cutoff.toLocaleString('en-US')}:\n`);
  
  recentEmails.forEach(e => {
    const date = new Date(e.receivedDateTime);
    const isUnread = e.isRead === false ? '🔵 ' : '';
    const from = e.from?.emailAddress?.name || e.from?.emailAddress?.address || 'Unknown';
    
    console.log(`${isUnread}${e.subject}`);
    console.log(`  From: ${from}`);
    console.log(`  Date: ${date.toLocaleString('en-US')}`);
    
    if (e.bodyPreview) {
      console.log(`  Preview: ${e.bodyPreview.substring(0, 100)}...`);
    }
    console.log('');
  });
  
  console.log(`Total: ${recentEmails.length} emails`);
});
