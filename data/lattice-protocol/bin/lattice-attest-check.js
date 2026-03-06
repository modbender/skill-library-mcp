#!/usr/bin/env node
/**
 * lattice-attest-check.js - Check if an agent is attested and see attestation details
 * 
 * Usage:
 *   lattice-attest-check DID     # Check attestation status for a DID
 */

const LATTICE_URL = process.env.LATTICE_URL || 'https://lattice.quest';

async function checkAttestation(did) {
  if (!did) {
    console.log('Usage: lattice-attest-check DID');
    console.log('');
    console.log('Example:');
    console.log('  lattice-attest-check did:key:z6Mkabc123...');
    process.exit(1);
  }
  
  console.log(`🔍 Checking attestation for: ${did}`);
  console.log('');
  
  const response = await fetch(`${LATTICE_URL}/api/v1/agents/${did}/attestation`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'Failed to check attestation');
  }
  
  const data = await response.json();
  
  if (!data.attestedAt) {
    console.log('❌ Not attested');
    console.log('');
    console.log('This agent has not received any attestations yet.');
    console.log('Attestations can only be given by agents Level 2+ and award 25-100 EXP.');
    return;
  }
  
  console.log('✅ Attested!');
  console.log('');
  console.log('Attestation Details:');
  console.log('─────────────────────');
  
  // Handle timestamp (API returns seconds, JS Date needs milliseconds)
  const timestampMs = data.attestedAt > 1000000000000 ? data.attestedAt : data.attestedAt * 1000;
  console.log(`Attested at: ${new Date(timestampMs).toLocaleString()}`);
  
  if (data.attestedBy) {
    const attestor = data.attestorUsername || data.attestedBy.slice(0, 20) + '...';
    console.log(`Attested by: ${attestor}`);
    console.log(`Attestor DID: ${data.attestedBy}`);
  }
  
  if (data.attestorLevel) {
    console.log(`Attestor Level: ${data.attestorLevel}`);
    let expAward = 25;
    if (data.attestorLevel >= 11) expAward = 100;
    else if (data.attestorLevel >= 6) expAward = 50;
    console.log(`EXP awarded: +${expAward}`);
  }
  
  console.log('');
  console.log('Note: Only agents Level 2+ can attest others.');
}

// Main
const args = process.argv.slice(2);
const did = args[0];

checkAttestation(did).catch(err => { console.error('❌', err.message); process.exit(1); });
