#!/usr/bin/env node
/**
 * 使用 macOS 邮件应用发送邮件（绕过 SMTP）
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * 使用 AppleScript 通过 macOS 邮件应用发送邮件
 */
async function sendViaAppleMail(htmlContent, subject, to) {
  const { exec } = require('child_process');
  
  // 将 HTML 保存为临时文件
  const tempFile = path.join(__dirname, 'email-temp.html');
  fs.writeFileSync(tempFile, htmlContent);
  
  // AppleScript 发送邮件
  const script = `
    tell application "Mail"
      set newMessage to make new outgoing message with properties {subject:"${subject}", content:"${htmlContent.replace(/"/g, '"')}", visible:true}
      tell newMessage
        make new to recipient at end of to recipients with properties {address:"${to}"}
      end tell
      send newMessage
    end tell
  `.replace(/\n/g, ' ');
  
  return new Promise((resolve, reject) => {
    exec(`osascript -e '${script}'`, (error) => {
      fs.unlinkSync(tempFile);
      if (error) {
        reject(error);
      } else {
        resolve(true);
      }
    });
  });
}

/**
 * 使用 sendmail 发送
 */
async function sendViaSendmail(htmlContent, subject, to) {
  const { exec } = require('child_process');
  
  const emailContent = `To: ${to}
Subject: ${subject}
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8

${htmlContent}
`;
  
  const tempFile = path.join(__dirname, 'email-temp.txt');
  fs.writeFileSync(tempFile, emailContent);
  
  return new Promise((resolve, reject) => {
    exec(`/usr/sbin/sendmail -t < "${tempFile}"`, (error) => {
      fs.unlinkSync(tempFile);
      if (error) {
        reject(error);
      } else {
        resolve(true);
      }
    });
  });
}

module.exports = { sendViaAppleMail, sendViaSendmail };
