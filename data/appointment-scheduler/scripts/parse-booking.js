#!/usr/bin/env node
/**
 * Parse booking request from natural language text
 * Usage: node parse-booking.js --text "내일 오후 3시에 컷 예약 가능할까요? - 김철수 010-1234-5678"
 */

const chrono = require('chrono-node');

const args = process.argv.slice(2);
const textIndex = args.indexOf('--text');
if (textIndex === -1 || !args[textIndex + 1]) {
  console.error('Usage: node parse-booking.js --text "booking request text"');
  process.exit(1);
}

const text = args[textIndex + 1];

// Parse date/time using chrono-node
const chronoParsed = chrono.parse(text, new Date(), { forwardDate: true });

// Extract service type (Korean keywords)
const servicePatterns = {
  '포토촬영': /포토|사진|촬영/,
  '컷': /커트|컷|자르|머리/,
  '펌': /펌/,
  '염색': /염색|컬러/
};

let service = null;
for (const [serviceName, pattern] of Object.entries(servicePatterns)) {
  if (pattern.test(text)) {
    service = serviceName;
    break;
  }
}

// Extract customer name (Korean name pattern: 2-4 characters before contact)
const nameMatch = text.match(/([가-힣]{2,4})\s*(?:010|02|031|032|01\d|[a-zA-Z0-9._-]+@)/);
const customerName = nameMatch ? nameMatch[1] : null;

// Extract phone number
const phoneMatch = text.match(/(01\d{1}-?\d{3,4}-?\d{4})/);
const phone = phoneMatch ? phoneMatch[1].replace(/-/g, '') : null;

// Extract email
const emailMatch = text.match(/([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/);
const email = emailMatch ? emailMatch[1] : null;

// Build result
const result = {
  raw_text: text,
  parsed: {
    date: chronoParsed.length > 0 ? chronoParsed[0].start.date().toISOString().split('T')[0] : null,
    time: chronoParsed.length > 0 && chronoParsed[0].start.get('hour') !== undefined 
      ? `${String(chronoParsed[0].start.get('hour')).padStart(2, '0')}:${String(chronoParsed[0].start.get('minute') || 0).padStart(2, '0')}`
      : null,
    service: service,
    customer_name: customerName,
    phone: phone,
    email: email,
    contact: phone || email
  },
  confidence: {
    date: chronoParsed.length > 0 ? 'high' : 'none',
    service: service ? 'high' : 'none',
    customer: customerName ? 'medium' : 'none',
    contact: (phone || email) ? 'high' : 'none'
  }
};

console.log(JSON.stringify(result, null, 2));

// Exit with code based on parse success
const requiredFields = ['date', 'time', 'service'];
const allRequired = requiredFields.every(field => result.parsed[field] !== null);
process.exit(allRequired ? 0 : 1);
