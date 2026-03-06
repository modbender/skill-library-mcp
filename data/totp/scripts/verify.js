#!/usr/bin/env node
// Verify TOTP OTP tokens
const { authenticator } = require('@otplib/preset-default');

// Use window 2 (1 minute tolerance)
authenticator.options = { window: 2 };

const secret = process.env.TOTP_SECRET;
const token = process.argv[2];

if (!secret) {
	console.error('Error: TOTP_SECRET not set in environment');
	process.exit(1);
}

if (!token) {
	console.error('Usage: node verify.js <6-digit-token>');
	console.error('   Or: TOTP_SECRET=secret node verify.js <token>');
	process.exit(1);
}

const verified = authenticator.verify({ token, secret });

if (verified) {
	console.log('OTP_VALID');
	process.exit(0);
} else {
	console.log('OTP_INVALID');
	process.exit(1);
}
