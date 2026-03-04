#!/usr/bin/env node

// Send Telegram reminder using exec to call the message tool
const { execSync } = require('child_process');

const gotchiCount = process.argv[2] || '3';
const gotchiList = process.argv[3] || '#9638, #10052, #21785';
const chatId = '322059822';

const message = `🐾 **PET TIME!** 👻

All ${gotchiCount} gotchis are ready for petting!

Gotchis: ${gotchiList}

Reply with 'pet all my gotchis' or I'll auto-pet them in 1 hour if you're busy! 🦞`;

try {
  // Create a temporary file with the command
  const fs = require('fs');
  const tmpFile = '/tmp/pet-reminder-command.txt';
  
  fs.writeFileSync(tmpFile, JSON.stringify({
    action: 'send',
    channel: 'telegram',
    target: chatId,
    message: message
  }));
  
  console.log(`[${new Date().toISOString()}] Sending Telegram reminder...`);
  console.log(`Message: ${message}`);
  
  // For now, just log it - we'll integrate with OpenClaw's message system
  console.log(`[${new Date().toISOString()}] ✅ Reminder logged (integration pending)`);
  
} catch (error) {
  console.error(`[${new Date().toISOString()}] ❌ Error:`, error.message);
  process.exit(1);
}
