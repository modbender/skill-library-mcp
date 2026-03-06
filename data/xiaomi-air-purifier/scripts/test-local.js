const { XiaomiMiHome } = require('xmihome');

const DEVICE_IP = '192.168.1.4';
const DEVICE_TOKEN = '3a8e11ebfb306f9d87e941c6b0f0e910';
const DEVICE_DID = '875218925';

async function testLocal() {
    console.log(`Connecting to ${DEVICE_IP} using token ${DEVICE_TOKEN.slice(0,4)}...`);
    
    // Initialize with miio preference
    const miHome = new XiaomiMiHome({
        connectionType: 'miio',
        logLevel: 'info'
    });

    try {
        // Get device instance manually
        const device = await miHome.getDevice({
            id: DEVICE_DID,
            address: DEVICE_IP,
            token: DEVICE_TOKEN,
            model: 'zhimi.airp.rmb1', // 4 Lite model
            name: 'Air Purifier 4 Lite'
        });

        console.log('Device object created. Connecting...');
        
        await device.connect(); 
        console.log(`✅ Connected via: ${device.connectionType}`);

        // Try to get properties (using raw MIOT spec mapping)
        // siid 2 piid 1 = Power
        // siid 3 piid 4 = PM2.5
        const props = await device.getProperties([
            { did: DEVICE_DID, siid: 2, piid: 1 },
            { did: DEVICE_DID, siid: 3, piid: 4 }
        ]);
        
        console.log('📊 Status:', JSON.stringify(props, null, 2));

        // Cleanup
        await device.disconnect();
        miHome.destroy();
        
    } catch (error) {
        console.error('❌ Error:', error);
        miHome.destroy();
    }
}

testLocal();
