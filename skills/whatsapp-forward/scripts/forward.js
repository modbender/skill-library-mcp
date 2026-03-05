#!/usr/bin/env node
// WhatsApp Forward - VCard generation, invite parsing, and forwarding templates
// MIT License

/**
 * Generate a VCard for contact sharing
 * @param {string} name - Contact name
 * @param {string} phone - Phone number
 */
function generateVCard(name, phone) {
  const cleanPhone = phone.replace(/\D/g, '');

  const vcard = `BEGIN:VCARD
VERSION:3.0
N:;${name};;;
FN:${name}
TEL;type=CELL;type=VOICE;waid=${cleanPhone}:+${cleanPhone}
END:VCARD`;

  console.log(JSON.stringify({
    displayName: name,
    phone: cleanPhone,
    vcard
  }, null, 2));
}

/**
 * Show forwarding templates and API reference
 */
function forwardTemplate() {
  console.log(JSON.stringify({
    info: 'Templates for message forwarding',
    forwardMessage: {
      description: 'Forward an existing message',
      params: {
        chatId: 'Destination chat ID (e.g. 5511999999999@s.whatsapp.net)',
        messageId: 'ID of the message to forward',
        displayCaptionText: 'Show caption text (true/false)'
      }
    },
    sendContact: {
      description: 'Send a contact card',
      params: {
        chatId: 'Destination chat ID',
        vcard: 'Object with displayName and vcard'
      }
    },
    sendGroupInvite: {
      description: 'Send a group invitation',
      params: {
        inviteCode: 'Invite code',
        inviteCodeExpiration: 'Expiration timestamp',
        groupId: 'Group ID'
      }
    }
  }, null, 2));
}

/**
 * Parse a WhatsApp group invite link
 * @param {string} link - Invite URL
 */
function parseInviteLink(link) {
  const match = link.match(/chat\.whatsapp\.com\/([A-Za-z0-9]+)/);

  if (match) {
    console.log(JSON.stringify({
      valid: true,
      inviteCode: match[1],
      fullLink: `https://chat.whatsapp.com/${match[1]}`
    }, null, 2));
  } else {
    console.log(JSON.stringify({
      valid: false,
      error: 'Invalid invite link',
      example: 'https://chat.whatsapp.com/ABC123XYZ'
    }, null, 2));
  }
}

/**
 * Generate multiple VCards from a JSON array
 * @param {string} contactsJson - JSON string of [{name, phone}]
 */
function multiVCard(contactsJson) {
  try {
    const contacts = JSON.parse(contactsJson);
    const vcards = contacts.map(c => ({
      displayName: c.name,
      vcard: `BEGIN:VCARD
VERSION:3.0
N:;${c.name};;;
FN:${c.name}
TEL;type=CELL;type=VOICE;waid=${c.phone}:+${c.phone}
END:VCARD`
    }));

    console.log(JSON.stringify({ total: vcards.length, vcards }, null, 2));
  } catch (error) {
    console.log(JSON.stringify({
      error: 'Invalid JSON',
      example: '[{"name":"John","phone":"5511999999999"}]'
    }));
  }
}

// CLI
const cmd = process.argv[2];
const arg1 = process.argv[3];
const arg2 = process.argv[4];

switch (cmd) {
  case 'vcard':
    if (!arg1 || !arg2) { console.error('Usage: forward.js vcard "Name" "phone"'); process.exit(1); }
    generateVCard(arg1, arg2); break;
  case 'multi-vcard':
    if (!arg1) { console.error('Usage: forward.js multi-vcard \'[{"name":"X","phone":"Y"}]\''); process.exit(1); }
    multiVCard(arg1); break;
  case 'parse-invite':
    if (!arg1) { console.error('Usage: forward.js parse-invite <link>'); process.exit(1); }
    parseInviteLink(arg1); break;
  case 'template': forwardTemplate(); break;
  default:
    console.log(JSON.stringify({
      usage: 'forward.js [vcard|multi-vcard|parse-invite|template] [args]',
      commands: {
        vcard: 'Generate VCard: vcard "Name" "phone"',
        'multi-vcard': 'Multiple VCards: multi-vcard \'[...]\'',
        'parse-invite': 'Parse group invite: parse-invite <url>',
        template: 'Show forwarding templates'
      }
    }, null, 2));
}
