/**
 * Verify Network Genesis & Entanglement
 */

'use strict';

const path = require('path');
const { networkState } = require('../lib/quantum/network-state');
const { KeyTriplet } = require('../lib/quantum/keytriplet');

async function verify() {
    console.log('🔍 Verifying Network Genesis...');
    
    // 1. Load Genesis
    const genesisPath = path.join(__dirname, '../data/content/genesis.json');
    if (!networkState.load(genesisPath)) {
        console.error('❌ Failed to load genesis record');
        process.exit(1);
    }
    
    // 2. Check Context
    const context = networkState.getContext();
    console.log(`✓ Network Context: ${context}`);
    
    if (context === 'BOOTSTRAP_PHASE') {
        console.error('❌ Network is in bootstrap mode (genesis failed to load)');
        process.exit(1);
    }
    
    // 3. Generate Entangled Key
    console.log('⚛️  Generating Entangled Identity...');
    const userTriplet = new KeyTriplet('user-test');
    userTriplet.generate(null, context);
    
    console.log(`✓ Identity Generated: ${userTriplet.nodeId}`);
    console.log(`✓ Public Key: ${userTriplet.pub.slice(0, 16)}...`);
    
    // 4. Verify Root Recognition
    const rootKey = networkState.alephKey;
    if (networkState.isRoot(rootKey)) {
        console.log('✓ Root Authority Recognized');
    } else {
        console.error('❌ Root Authority Validation Failed');
        process.exit(1);
    }
    
    console.log('\n✅ VERIFICATION SUCCESSFUL');
    console.log('   The network is anchored and ready for deployment.');
}

verify();
