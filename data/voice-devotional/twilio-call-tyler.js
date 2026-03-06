#!/usr/bin/env node

const twilio = require('twilio');

const accountSid = 'AC35fce9f5069e4a19358da26286380ca9';
const authToken = 'a7700999dcff89b738f62c78bd1e33c1';
const twilioNumber = '+19152237302';
const tylerNumber = '+19152134309';

const client = twilio(accountSid, authToken);

async function callTyler() {
  try {
    console.log(`📞 Calling Tyler...`);
    console.log(`From: ${twilioNumber}`);
    console.log(`To: ${tylerNumber}`);
    
    const call = await client.calls.create({
      url: 'http://demo.twilio.com/docs/voice.xml',
      to: tylerNumber,
      from: twilioNumber,
    });

    console.log(`✅ Call initiated! SID: ${call.sid}`);
    console.log(`Tyler's about to get rick rolled 😂`);
    
  } catch (err) {
    console.error(`❌ Error:`, err.message);
  }
}

callTyler();
