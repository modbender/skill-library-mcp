const Imap = require('imap');
const fs = require('fs');

const env = fs.readFileSync('../.env', 'utf8');
const config = {};
env.split('\n').forEach(line => {
  const [key, ...valueParts] = line.split('=');
  if (key && valueParts.length) {
    config[key.trim()] = valueParts.join('=').trim();
  }
});

console.log('Testing IMAP connection...');
console.log('Host:', config.IMAP_HOST);
console.log('User:', config.IMAP_USER);

const imap = new Imap({
  user: config.IMAP_USER,
  password: config.IMAP_PASS,
  host: config.IMAP_HOST,
  port: parseInt(config.IMAP_PORT) || 993,
  tls: config.IMAP_TLS === 'true',
  rejectUnauthorized: config.IMAP_REJECT_UNAUTHORIZED !== 'false'
});

imap.once('ready', () => {
  console.log('✅ Connected!');
  imap.end();
});

imap.once('error', (err) => {
  console.log('❌ Error:', err.message);
});

imap.connect();
