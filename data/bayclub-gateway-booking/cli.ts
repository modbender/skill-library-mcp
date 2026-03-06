#!/usr/bin/env npx ts-node
import { bayclub_get_availability, bayclub_book_court } from './bayclub_skills';
import { Sport } from './BayClubBot';

const args = process.argv.slice(2);
const command = args[0];

async function main() {
  console.log('Starting CLI with command:', command);
  console.log('Environment check:');
  console.log('- BAYCLUB_USERNAME:', process.env.BAYCLUB_USERNAME ? '✓ set' : '✗ missing');
  console.log('- BAYCLUB_PASSWORD:', process.env.BAYCLUB_PASSWORD ? '✓ set' : '✗ missing');
  console.log('- NODE_ENV:', process.env.NODE_ENV || 'not set (will use LOCAL mode)');
  
  if (command === 'check' || command === 'availability') {
    const sport = (args[1] || 'tennis') as Sport;
    const day = args[2] || 'today';
    
    console.log(`\nChecking ${sport} availability for ${day}...`);
    const result = await bayclub_get_availability({ sport, day });
    console.log('\nResult:', JSON.stringify(result, null, 2));
  } else if (command === 'book') {
    const sport = (args[1] || 'tennis') as Sport;
    const day = args[2] || 'today';
    const time = args[3];
    
    if (!time) {
      console.error('Usage: cli.ts book <sport> <day> <time>');
      process.exit(1);
    }
    
    console.log(`\nBooking ${sport} for ${day} at ${time}...`);
    const result = await bayclub_book_court({ sport, day, time });
    console.log('\nResult:', JSON.stringify(result, null, 2));
  } else {
    console.log('Usage:');
    console.log('  cli.ts check [sport] [day]     - Check availability');
    console.log('  cli.ts book <sport> <day> <time> - Book a court');
    console.log('\nExamples:');
    console.log('  cli.ts check tennis today');
    console.log('  cli.ts book pickleball tomorrow "10:00 AM"');
  }
}

main().catch(err => {
  console.error('\n❌ Error:', err);
  process.exit(1);
});
