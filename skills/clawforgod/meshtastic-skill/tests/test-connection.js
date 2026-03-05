#!/usr/bin/env node

/**
 * Test Mesh Master connectivity and configuration
 */

const MeshtasticAgent = require('../scripts/meshtastic-agent');

async function runTests() {
  const agent = new MeshtasticAgent();

  console.log('🧪 Meshtastic Skill - Connectivity Tests\n');
  console.log(`Mesh Master URL: ${agent.baseUrl}`);
  console.log(`Timeout: ${agent.timeout}ms\n`);

  // Test 1: Health check
  console.log('1️⃣  Testing Mesh Master health...');
  const healthy = await agent.checkHealth();
  if (!healthy) {
    console.log('❌ FAILED - Cannot connect to Mesh Master');
    console.log('   Solutions:');
    console.log('   - Check Mesh Master is running on RPi');
    console.log('   - Verify MESH_MASTER_URL is correct');
    console.log('   - Check WiFi/network connectivity');
    console.log('   - Ensure port 5000 is not blocked by firewall');
    process.exit(1);
  }
  console.log('✅ PASSED - Connected to Mesh Master\n');

  // Test 2: Get device info
  console.log('2️⃣  Fetching device info...');
  const deviceResult = await agent.getDeviceInfo();
  if (deviceResult.success) {
    console.log(`✅ PASSED - Device: ${deviceResult.data.long_name}\n`);
  } else {
    console.log(`❌ FAILED - ${deviceResult.error}\n`);
  }

  // Test 3: Get nodes
  console.log('3️⃣  Fetching node list...');
  const nodesResult = await agent.getNodes();
  if (nodesResult.success) {
    console.log(`✅ PASSED - Found ${nodesResult.data.length} nodes\n`);
    nodesResult.data.slice(0, 3).forEach((n) => {
      console.log(`   • ${n.short_name} (${n.long_name})`);
    });
    if (nodesResult.data.length > 3) {
      console.log(`   ... and ${nodesResult.data.length - 3} more\n`);
    } else {
      console.log('');
    }
  } else {
    console.log(`❌ FAILED - ${nodesResult.error}\n`);
  }

  // Test 4: Get channels
  console.log('4️⃣  Fetching channels...');
  const channelsResult = await agent.getChannels();
  if (channelsResult.success) {
    console.log(`✅ PASSED - Found ${channelsResult.data.length} channels\n`);
    channelsResult.data.forEach((ch, idx) => {
      const status = ch.enabled ? '✓' : '✗';
      console.log(`   [${status}] ${idx}: ${ch.name || 'Unnamed'}`);
    });
    console.log('');
  } else {
    console.log(`❌ FAILED - ${channelsResult.error}\n`);
  }

  // Test 5: Get radio config
  console.log('5️⃣  Fetching radio config...');
  const configResult = await agent.getRadioConfig();
  if (configResult.success) {
    const cfg = configResult.data;
    console.log('✅ PASSED - Radio configuration:\n');
    console.log(`   Region: ${cfg.lora?.region || 'Unknown'}`);
    console.log(`   Channel: ${cfg.lora?.use_long_slow || 'Unknown'}`);
    console.log(`   Role: ${cfg.device?.role || 'Unknown'}\n`);
  } else {
    console.log(`❌ FAILED - ${configResult.error}\n`);
  }

  console.log('✨ All tests completed!');
  console.log('\nReady to use Meshtastic skill with Clawdbot');
}

runTests().catch((e) => {
  console.error('Test error:', e);
  process.exit(1);
});
