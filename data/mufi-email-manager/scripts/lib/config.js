const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

// 계정 설정 정보
const ACCOUNTS = {
  gmail: {
    imap: {
      host: process.env.GMAIL_IMAP_HOST || 'imap.gmail.com',
      port: parseInt(process.env.GMAIL_IMAP_PORT) || 993,
      user: process.env.GMAIL_USER,
      password: process.env.GMAIL_PASS,
      tls: true,
      tlsOptions: { rejectUnauthorized: true }
    },
    smtp: {
      host: process.env.GMAIL_SMTP_HOST || 'smtp.gmail.com',
      port: parseInt(process.env.GMAIL_SMTP_PORT) || 587,
      secure: false, // STARTTLS
      auth: {
        user: process.env.GMAIL_USER,
        pass: process.env.GMAIL_PASS
      }
    }
  },
  naver: {
    imap: {
      host: process.env.NAVER_IMAP_HOST || 'imap.naver.com',
      port: parseInt(process.env.NAVER_IMAP_PORT) || 993,
      user: process.env.NAVER_USER,
      password: process.env.NAVER_PASS,
      tls: true,
      tlsOptions: { rejectUnauthorized: true }
    },
    smtp: {
      host: process.env.NAVER_SMTP_HOST || 'smtp.naver.com',
      port: parseInt(process.env.NAVER_SMTP_PORT) || 587,
      secure: false, // STARTTLS
      auth: {
        user: process.env.NAVER_USER,
        pass: process.env.NAVER_PASS
      }
    }
  },
  daum: {
    imap: {
      host: process.env.DAUM_IMAP_HOST || 'imap.daum.net',
      port: parseInt(process.env.DAUM_IMAP_PORT) || 993,
      user: process.env.DAUM_USER,
      password: process.env.DAUM_PASS,
      tls: true,
      tlsOptions: { rejectUnauthorized: true }
    },
    smtp: {
      host: process.env.DAUM_SMTP_HOST || 'smtp.daum.net',
      port: parseInt(process.env.DAUM_SMTP_PORT) || 465,
      secure: true, // SSL
      auth: {
        user: process.env.DAUM_USER,
        pass: process.env.DAUM_PASS
      }
    }
  },
  kakao: {
    imap: {
      host: process.env.KAKAO_IMAP_HOST || 'imap.kakao.com',
      port: parseInt(process.env.KAKAO_IMAP_PORT) || 993,
      user: process.env.KAKAO_USER,
      password: process.env.KAKAO_PASS,
      tls: true,
      tlsOptions: { rejectUnauthorized: true }
    },
    smtp: {
      host: process.env.KAKAO_SMTP_HOST || 'smtp.kakao.com',
      port: parseInt(process.env.KAKAO_SMTP_PORT) || 465,
      secure: true, // SSL
      auth: {
        user: process.env.KAKAO_USER,
        pass: process.env.KAKAO_PASS
      }
    }
  }
};

// 필터 키워드
const IMPORTANT_KEYWORDS = (process.env.IMPORTANT_KEYWORDS || '결제,청구,납부,계약,승인,보안,비밀번호,urgent,invoice').split(',');
const SPAM_KEYWORDS = (process.env.SPAM_KEYWORDS || '광고,홍보,이벤트,쿠폰,할인').split(',');

// 기본 계정
const DEFAULT_ACCOUNT = process.env.DEFAULT_ACCOUNT || 'gmail';

function getAccountConfig(accountName) {
  const account = ACCOUNTS[accountName];
  if (!account) {
    throw new Error(`Unknown account: ${accountName}. Available: ${Object.keys(ACCOUNTS).join(', ')}`);
  }
  if (!account.imap.user || !account.imap.password) {
    throw new Error(`Account ${accountName} not configured. Set ${accountName.toUpperCase()}_USER and ${accountName.toUpperCase()}_PASS in .env`);
  }
  return account;
}

function getAllConfiguredAccounts() {
  return Object.keys(ACCOUNTS).filter(name => {
    const account = ACCOUNTS[name];
    return account.imap.user && account.imap.password;
  });
}

module.exports = {
  ACCOUNTS,
  IMPORTANT_KEYWORDS,
  SPAM_KEYWORDS,
  DEFAULT_ACCOUNT,
  getAccountConfig,
  getAllConfiguredAccounts
};
