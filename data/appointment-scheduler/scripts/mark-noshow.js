#!/usr/bin/env node
/**
 * Mark a booking as no-show
 * Usage: node mark-noshow.js --booking-id abc123
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const bookingId = args.includes('--booking-id') ? args[args.indexOf('--booking-id') + 1] : null;

if (!bookingId) {
  console.error('Usage: node mark-noshow.js --booking-id <id>');
  process.exit(1);
}

const DATA_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'data', 'appointments', 'bookings');
const NOSHOW_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'data', 'appointments', 'noshow');
const HISTORY_FILE = path.join(NOSHOW_DIR, 'history.json');
const FLAGGED_FILE = path.join(NOSHOW_DIR, 'flagged-customers.json');

// Create directories
if (!fs.existsSync(NOSHOW_DIR)) {
  fs.mkdirSync(NOSHOW_DIR, { recursive: true });
}

// Load config
const CONFIG_FILE = path.join(process.env.HOME, '.openclaw', 'workspace', 'config', 'appointment-scheduler.json');
const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));

// Find booking
let booking = null;
let bookingFile = null;

const files = fs.readdirSync(DATA_DIR).filter(f => f.endsWith('.json'));
for (const file of files) {
  const filePath = path.join(DATA_DIR, file);
  const bookings = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const found = bookings.find(b => b.id === bookingId);
  if (found) {
    booking = found;
    bookingFile = filePath;
    break;
  }
}

if (!booking) {
  console.error(`❌ Booking not found: ${bookingId}`);
  process.exit(1);
}

// Mark as no-show
booking.status = 'noshow';
booking.noshow_marked_at = new Date().toISOString();

// Save updated booking
const bookings = JSON.parse(fs.readFileSync(bookingFile, 'utf8'));
const index = bookings.findIndex(b => b.id === bookingId);
bookings[index] = booking;
fs.writeFileSync(bookingFile, JSON.stringify(bookings, null, 2));

// Add to no-show history
let history = [];
if (fs.existsSync(HISTORY_FILE)) {
  history = JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'));
}
history.push({
  booking_id: booking.id,
  customer_name: booking.customer.name,
  customer_phone: booking.customer.phone,
  customer_email: booking.customer.email,
  date: booking.date,
  time: booking.time,
  service: booking.service,
  marked_at: booking.noshow_marked_at
});
fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2));

// Check if customer should be flagged
const customerNoshows = history.filter(h => 
  h.customer_phone === booking.customer.phone || 
  h.customer_email === booking.customer.email
);

const threshold = config.noshow_policy?.flag_threshold || 3;
if (customerNoshows.length >= threshold) {
  let flagged = {};
  if (fs.existsSync(FLAGGED_FILE)) {
    flagged = JSON.parse(fs.readFileSync(FLAGGED_FILE, 'utf8'));
  }
  
  const key = booking.customer.phone || booking.customer.email;
  if (!flagged[key]) {
    flagged[key] = {
      customer_name: booking.customer.name,
      phone: booking.customer.phone,
      email: booking.customer.email,
      noshow_count: customerNoshows.length,
      flagged_at: new Date().toISOString(),
      require_deposit: config.noshow_policy?.require_deposit_when_flagged || false
    };
    fs.writeFileSync(FLAGGED_FILE, JSON.stringify(flagged, null, 2));
    console.log(`\n🚩 Customer flagged for repeat no-shows (${customerNoshows.length} times)`);
  } else {
    flagged[key].noshow_count = customerNoshows.length;
    fs.writeFileSync(FLAGGED_FILE, JSON.stringify(flagged, null, 2));
  }
}

console.log('✅ Booking marked as no-show:');
console.log(JSON.stringify(booking, null, 2));
console.log(`\nCustomer no-show history: ${customerNoshows.length} times`);
