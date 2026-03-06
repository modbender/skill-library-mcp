#!/usr/bin/env node
/**
 * Check the status of a Sideload generation job
 * Usage: node status.js <jobId>
 */

const jobId = process.argv[2];

if (!jobId) {
  console.error('Usage: node status.js <jobId>');
  console.error('Example: node status.js avt-a1b2c3d4');
  process.exit(1);
}

const url = `https://sideload.gg/api/agent/generate/${jobId}/status`;

console.log(`🔍 Checking job: ${jobId}\n`);

try {
  const response = await fetch(url);
  const data = await response.json();

  console.log(`Status: ${data.status}`);

  if (data.status === 'processing') {
    const step = data.stepDescription || data.step || 'working';
    const progress = data.progress != null ? ` (${data.progress}%)` : '';
    console.log(`Step:   ${step}${progress}`);
  }

  if (data.status === 'completed' && data.result) {
    console.log('');
    console.log('📦 Results:');
    if (data.result.glbUrl) console.log(`   GLB:   ${data.result.glbUrl}`);
    if (data.result.vrmUrl) console.log(`   VRM:   ${data.result.vrmUrl}`);
    if (data.result.mmlUrl) console.log(`   MML:   ${data.result.mmlUrl}`);
    if (data.result.processedImageUrl) console.log(`   Image: ${data.result.processedImageUrl}`);
  }

  if (data.status === 'failed') {
    console.log(`Error: ${data.error || 'Unknown'}`);
  }

  console.log('');
  console.log(JSON.stringify(data, null, 2));

} catch (error) {
  console.error(`❌ Error: ${error.message}`);
  process.exit(1);
}
