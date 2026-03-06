/**
 * Google Calendar API 클라이언트
 */

const fs = require('fs').promises;
const path = require('path');
const { google } = require('googleapis');
const os = require('os');

const CREDENTIALS_PATH = path.join(os.homedir(), '.secrets', 'google-calendar-credentials.json');
const TOKEN_PATH = path.join(os.homedir(), '.secrets', 'google-calendar-token.json');

async function getCalendar() {
  // credentials 읽기
  const credentialsContent = await fs.readFile(CREDENTIALS_PATH, 'utf8');
  const credentials = JSON.parse(credentialsContent);
  const { client_id, client_secret, redirect_uris } = credentials.installed || credentials.web;

  const oauth2Client = new google.auth.OAuth2(
    client_id,
    client_secret,
    redirect_uris ? redirect_uris[0] : 'http://localhost:3000/oauth2callback'
  );

  // 토큰 읽기
  try {
    const tokenContent = await fs.readFile(TOKEN_PATH, 'utf8');
    const token = JSON.parse(tokenContent);
    oauth2Client.setCredentials(token);
  } catch (err) {
    console.error('❌ 토큰이 없습니다. 먼저 인증하세요: node scripts/auth.js');
    process.exit(1);
  }

  // 토큰 갱신 콜백
  oauth2Client.on('tokens', async (tokens) => {
    if (tokens.refresh_token) {
      const currentTokens = JSON.parse(await fs.readFile(TOKEN_PATH, 'utf8'));
      currentTokens.refresh_token = tokens.refresh_token;
      await fs.writeFile(TOKEN_PATH, JSON.stringify(currentTokens, null, 2));
    }
  });

  return google.calendar({ version: 'v3', auth: oauth2Client });
}

module.exports = { getCalendar };
