#!/usr/bin/env node
/**
 * Feishu Image Send - Simple Wrapper
 * 
 * Quick usage for sending images via Feishu
 */

const { exec } = require('child_process');
const path = require('path');

const TOOL_PATH = path.join(__dirname, 'feishu-image-tool.js');

/**
 * Send an image to a Feishu user or chat
 * @param {string} target - User open_id or chat_id (omit for current conversation)
 * @param {string} filePath - Path to the image file
 * @param {string} message - Optional caption text
 * @returns {Promise<{success: boolean, image_key: string, message_id?: string}>}
 */
function sendImage(target, filePath, message) {
  return new Promise((resolve, reject) => {
    let cmd = `node "${TOOL_PATH}" send --file "${filePath}"`;
    if (target) cmd += ` --target "${target}"`;
    if (message) cmd += ` --message "${message}"`;
    
    exec(cmd, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(stderr || error.message));
        return;
      }
      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (e) {
        resolve({ success: true, output: stdout });
      }
    });
  });
}

/**
 * Upload an image and get image_key
 * @param {string} filePath - Path to the image file
 * @returns {Promise<{success: boolean, image_key: string}>}
 */
function uploadImage(filePath) {
  return new Promise((resolve, reject) => {
    const cmd = `node "${TOOL_PATH}" upload --file "${filePath}"`;
    
    exec(cmd, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(stderr || error.message));
        return;
      }
      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (e) {
        resolve({ success: true, output: stdout });
      }
    });
  });
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  const action = args[0];
  
  if (action === 'send' && args[1] && args[2]) {
    sendImage(args[1], args[2], args[3])
      .then(result => console.log('✅', result))
      .catch(err => console.error('❌', err.message));
  } else if (action === 'upload' && args[1]) {
    uploadImage(args[1])
      .then(result => console.log('✅', result))
      .catch(err => console.error('❌', err.message));
  } else {
    console.log('Usage:');
    console.log('  node index.js send <target> <file_path> [message]');
    console.log('  node index.js upload <file_path>');
  }
}

module.exports = { sendImage, uploadImage };
