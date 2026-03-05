#!/usr/bin/env node
/**
 * Google Calendar OAuth 인증
 * 실행: node auth.js
 * 결과: ~/.secrets/google-calendar-token.json 생성
 */

const fs = require('fs').promises;
const path = require('path');
const { google } = require('googleapis');
const http = require('http');
const { parse } = require('url');
const opener = require('opener');
const os = require('os');

const CREDENTIALS_PATH = path.join(os.homedir(), '.secrets', 'google-calendar-credentials.json');
const TOKEN_PATH = path.join(os.homedir(), '.secrets', 'google-calendar-token.json');
const SCOPES = ['https://www.googleapis.com/auth/calendar'];
const REDIRECT_URI = 'http://localhost:3000/oauth2callback';

async function authenticate() {
  // credentials.json 읽기
  const credentialsContent = await fs.readFile(CREDENTIALS_PATH, 'utf8');
  const credentials = JSON.parse(credentialsContent);
  const { client_id, client_secret } = credentials.installed || credentials.web;

  const oauth2Client = new google.auth.OAuth2(client_id, client_secret, REDIRECT_URI);

  // 로컬 서버로 OAuth 콜백 받기
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
  });

  console.log('브라우저에서 인증을 진행합니다...');
  console.log(authUrl);
  opener(authUrl);

  const code = await new Promise((resolve, reject) => {
    const server = http.createServer(async (req, res) => {
      try {
        if (req.url.indexOf('/oauth2callback') > -1) {
          const qs = parse(req.url, true).query;
          res.end('인증 완료! 이 창을 닫고 터미널로 돌아가세요.');
          server.close();
          resolve(qs.code);
        }
      } catch (e) {
        reject(e);
      }
    });
    server.listen(3000, () => {
      console.log('로컬 서버 시작: http://localhost:3000');
    });
  });

  // 토큰 교환
  const { tokens } = await oauth2Client.getToken(code);
  oauth2Client.setCredentials(tokens);

  // 토큰 저장
  await fs.mkdir(path.dirname(TOKEN_PATH), { recursive: true });
  await fs.writeFile(TOKEN_PATH, JSON.stringify(tokens, null, 2));
  console.log(`✅ 토큰 저장 완료: ${TOKEN_PATH}`);
}

authenticate().catch(console.error);
