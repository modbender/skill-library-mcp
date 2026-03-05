#!/usr/bin/env node
// Generate new TOTP secret and QR code image
const path = require('path');
const { authenticator } = require('@otplib/preset-default');
const QRCode = require('qrcode');

const service = process.argv[2] || 'OpenClaw';
const account = process.argv[3] || 'admin';

// Generate new secret (base32)
const secret = authenticator.generateSecret();
const otpauth = authenticator.keyuri(account, service, secret);
const qrPath = path.join(__dirname, '..', 'qr.png');

QRCode.toFile(qrPath, otpauth, { type: 'png', width: 200, margin: 2 }, (err) => {
  if (err) {
    console.error('Failed to generate QR image:', err.message);
    process.exit(1);
  }

  console.log('New TOTP_SECRET:');
  console.log(secret);
  console.log(`\nQR code saved to: ${qrPath}`);
  console.log('\nManual setup:');
  console.log('1. Open Google Authenticator/Authy');
  console.log('2. Tap "+" > "Enter a setup key"');
  console.log(`3. Account: ${account}`);
  console.log('4. Key:', secret);
  console.log('5. Type: Time-based (TOTP)');
  console.log('\nAdd this line to your .env:');
  console.log(`TOTP_SECRET=${secret}`);
});
