#!/usr/bin/env node
/**
 * lattice-health.js - Check Lattice server health and time
 * 
 * Usage:
 *   lattice-health    # Check server health and time sync
 */

const LATTICE_URL = process.env.LATTICE_URL || 'https://lattice.quest';

async function checkHealth() {
  console.log('🏥 Checking Lattice server health...');
  console.log(`Server: ${LATTICE_URL}`);
  console.log('');
  
  try {
    const response = await fetch(`${LATTICE_URL}/api/v1/health`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Health check failed');
    }
    
    const data = await response.json();
    const serverTime = new Date(data.timestamp);
    const localTime = new Date();
    const diffMs = localTime.getTime() - serverTime.getTime();
    const diffSec = Math.abs(diffMs) / 1000;
    
    console.log('✅ Server is healthy');
    console.log('');
    console.log('Time Synchronization:');
    console.log('─────────────────────');
    console.log(`Server time: ${serverTime.toISOString()}`);
    console.log(`Local time:  ${localTime.toISOString()}`);
    console.log(`Difference:  ${diffSec.toFixed(2)}s ${diffMs > 0 ? '(local ahead)' : '(local behind)'}`);
    console.log('');
    
    if (diffSec > 300) {
      console.log('⚠️  WARNING: Clock skew detected (>5 minutes)');
      console.log('   This may cause AUTH_TIMESTAMP_EXPIRED errors.');
      console.log('   Consider using server time for signatures.');
    } else if (diffSec > 60) {
      console.log('⚠️  Notice: Minor clock skew (>1 minute)');
      console.log('   Should be acceptable, but monitor if issues occur.');
    } else {
      console.log('✅ Clocks are synchronized');
    }
    
    console.log('');
    console.log('Timestamp Format for Signing:');
    console.log(`  ${serverTime.getTime()}`);
    
  } catch (error) {
    console.error('❌ Health check failed:', error.message);
    process.exit(1);
  }
}

checkHealth();
