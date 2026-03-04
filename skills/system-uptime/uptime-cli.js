#!/usr/bin/env node

/**
 * System Uptime CLI for OpenClaw
 * Displays the current system uptime using the native 'uptime' command
 */

const { exec } = require('child_process');

function getUptime() {
  return new Promise((resolve, reject) => {
    exec('uptime', (error, stdout, stderr) => {
      if (error) {
        reject(error);
        return;
      }
      if (stderr) {
        reject(new Error(stderr));
        return;
      }
      resolve(stdout.trim());
    });
  });
}

async function main() {
  try {
    const uptimeInfo = await getUptime();
    console.log(uptimeInfo);
  } catch (error) {
    console.error('Error fetching system uptime:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}