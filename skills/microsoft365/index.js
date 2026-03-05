// custom-ms/index.js
const { getAccessToken } = require('./src/auth');
const { normalizeAccount } = require('./src/config');
const {
  setAccount,
  getEmails,
  getCalendarEvents,
  getContacts,
  listDriveRoot,
  sendEmail,
  createEvent,
  createContact,
  uploadFile
} = require('./src/api');
const readline = require('readline');

async function main() {
  // Parse --account flag
  let account = 'default';
  const args = process.argv.slice(2);
  const accountIdx = args.indexOf('--account');
  if (accountIdx !== -1 && args[accountIdx + 1]) {
    account = normalizeAccount(args[accountIdx + 1]);
  }

  setAccount(account);
  console.log(`Using account: ${account}`);

  try {
    const token = await getAccessToken(account); // triggert auth flow indien nodig
    if (!token) {
      console.error('Geen toegangstoken ontvangen. Stoppen.');
      process.exit(1);
    }
  } catch (err) {
    console.error('Authenticatie mislukt:', err.message);
    process.exit(1);
  }

  console.log('✅ Authenticated successfully!');

  if (args.includes('--calendar')) {
    console.log('Fetching calendar...');
    try {
      const events = await getCalendarEvents();
      console.log('\n--- Calendar Events ---');
      if (events && events.length > 0) {
        events.forEach(e => console.log(`- ${e.subject} (${e.start.dateTime} - ${e.end.dateTime})`));
      } else {
        console.log('No upcoming events found.');
      }
      process.exit(0);
    } catch (err) {
      console.error('Kon kalender niet ophalen:', err.message);
      process.exit(1);
    }
  }

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  function menu() {
    console.log(`\n--- Custom Microsoft Integration [${account}] ---`);
    console.log('1. List recent emails');
    console.log('2. List upcoming calendar events');
    console.log('3. List contacts');
    console.log('4. List OneDrive root files');
    console.log('5. Send Email');
    console.log('6. Create Calendar Event');
    console.log('7. Create Contact');
    console.log('8. Upload File (Sample)');
    console.log('9. Exit');

    rl.question('Select an option: ', async (answer) => {
      try {
        switch (answer.trim()) {
          case '1': {
            const emails = await getEmails();
            console.log('\n--- Recent Emails ---');
            emails.forEach(e => console.log(`- [${e.from?.emailAddress?.name || 'Unknown'}] ${e.subject}`));
            break;
          }
          case '2': {
            const events = await getCalendarEvents();
            console.log('\n--- Calendar Events ---');
            events.forEach(e => console.log(`- ${e.subject} (${e.start.dateTime} - ${e.end.dateTime})`));
            break;
          }
          case '3': {
            const contacts = await getContacts();
            console.log('\n--- Contacts ---');
            contacts.forEach(c => console.log(`- ${c.displayName} (${c.emailAddresses?.[0]?.address || 'No email'})`));
            break;
          }
          case '4': {
            const files = await listDriveRoot();
            console.log('\n--- OneDrive Root ---');
            files.forEach(f => console.log(`- ${f.name} (${f.folder ? 'Folder' : 'File'})`));
            break;
          }
          case '5':
            rl.question('To: ', (to) => {
              rl.question('Subject: ', (sub) => {
                rl.question('Body: ', async (body) => {
                  try {
                    await sendEmail(to, sub, body);
                    console.log('Email sent!');
                  } catch (err) {
                    console.error('Versturen mislukt:', err.message);
                  }
                  menu();
                });
              });
            });
            return;
          case '6':
            rl.question('Subject: ', (sub) => {
              rl.question('Start (YYYY-MM-DDTHH:MM): ', (start) => {
                rl.question('End (YYYY-MM-DDTHH:MM): ', async (end) => {
                  try {
                    await createEvent(sub, `${start}:00Z`, `${end}:00Z`, 'Meeting Room');
                    console.log('Event created!');
                  } catch (err) {
                    console.error('Event maken mislukt:', err.message);
                  }
                  menu();
                });
              });
            });
            return;
          case '7':
            rl.question('Name: ', (name) => {
              rl.question('Email: ', async (email) => {
                try {
                  await createContact(name, email, '555-0100');
                  console.log('Contact created!');
                } catch (err) {
                  console.error('Contact maken mislukt:', err.message);
                }
                menu();
              });
            });
            return;
          case '8':
            rl.question('Filename: ', async (name) => {
              try {
                await uploadFile(name, 'This is a test file content uploaded from CLI.');
                console.log('File uploaded!');
              } catch (err) {
                console.error('Upload mislukt:', err.message);
              }
              menu();
            });
            return;
          case '9':
            rl.close();
            return;
          default:
            console.log('Invalid option');
        }
      } catch (err) {
        console.error('Error:', err.message);
      }

      menu();
    });
  }

  menu();
}

main();
