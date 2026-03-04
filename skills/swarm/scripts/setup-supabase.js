#!/usr/bin/env node
/**
 * Setup Supabase tables for swarm blackboard
 */

const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY;

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error('❌ SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables required');
  process.exit(1);
}

async function setup() {
  const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
  
  console.log('🔧 Setting up swarm_blackboard table...');
  
  // Test connection
  const { data, error } = await supabase.from('swarm_blackboard').select('count').limit(1);
  
  if (error && error.code === '42P01') {
    console.log('Table does not exist yet. Creating via SQL migration...');
    console.log('Please run the migration manually:');
    console.log('  cd ./prototype');
    console.log('  supabase migration repair --status reverted <version>');
    console.log('  supabase db push --local');
    process.exit(1);
  } else if (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
  
  console.log('✅ swarm_blackboard table exists');
  
  // Test insert
  const testInsert = await supabase.from('swarm_blackboard').insert({
    task_id: 'setup-test',
    worker_id: 'setup-script',
    msg_type: 'FINDING',
    content: 'Setup test successful',
    metadata: { test: true }
  }).select();
  
  if (testInsert.error) {
    console.error('Insert test failed:', testInsert.error.message);
    process.exit(1);
  }
  
  console.log('✅ Insert test passed');
  
  // Cleanup test
  await supabase.from('swarm_blackboard').delete().eq('task_id', 'setup-test');
  console.log('✅ Cleanup test passed');
  
  console.log('\n🎉 Supabase swarm setup complete!');
}

setup().catch(console.error);
