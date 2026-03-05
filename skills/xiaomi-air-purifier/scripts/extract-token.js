const { XiaomiMiHome } = require('xmihome');
const fs = require('fs');
const path = require('path');

const CREDS_FILE = path.join(process.env.HOME, '.config/xmihome/credentials.json');

async function extract() {
    if (!fs.existsSync(CREDS_FILE)) {
        console.error('❌ Credentials not found.');
        return;
    }
    const creds = JSON.parse(fs.readFileSync(CREDS_FILE, 'utf8'));
    const client = new XiaomiMiHome({ credentials: creds });
    
    // Request device list with tokens
    const response = await client.miot.request('/v2/home/device_list', { 
        getVirtualModel: false, 
        getHuamiDevices: 0 
    });
    
    const devices = response.result.list.filter(d => d.model && (d.model.includes('airp') || d.model.includes('airpurifier')));
    
    console.log('--- DEVICE TOKENS ---');
    devices.forEach(d => {
        console.log(`Name: ${d.name}`);
        console.log(`DID: ${d.did}`);
        console.log(`IP: ${d.localip || 'Unknown'}`);
        console.log(`Token: ${d.token}`);
        console.log('---------------------');
    });
}

extract().catch(console.error);
