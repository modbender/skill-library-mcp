const fs = require('fs');
const path = require('path');
const readline = require('readline');

const CONFIG_PATH = path.join(__dirname, 'config.json');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('--- Custom Microsoft Integration Setup ---');
console.log('Dit script helpt u bij het configureren van uw Entra ID (Azure AD) App.');
console.log('\nZorg ervoor dat in uw App Registratie onder "Authentication" > "Advanced settings"');
console.log('de optie "Allow public client flows" op "Yes" staat.\n');

rl.question('Voer uw Application (client) ID in: ', (clientId) => {
  rl.question('Voer uw Directory (tenant) ID in (of druk op Enter voor "common"): ', (tenantId) => {
    
    const config = {
      clientId: clientId.trim(),
      tenantId: tenantId.trim() || 'common',
      scopes: 'User.Read Mail.Read Calendars.Read Contacts.Read Files.Read.All offline_access'
    };

    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
    console.log(`\n✅ Configuratie opgeslagen in ${CONFIG_PATH}`);
    console.log('U kunt nu de integratie starten met: node index.js');
    rl.close();
  });
});
