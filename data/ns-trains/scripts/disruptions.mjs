#!/usr/bin/env node
/**
 * NS Disruptions Checker
 * Usage: node disruptions.mjs [--from "Station" --to "Station"]
 */

import { nsFetch, requireNsSubscriptionKey } from './ns-api.mjs';

const NS_SUBSCRIPTION_KEY = (() => {
  try { return requireNsSubscriptionKey(); }
  catch (e) { console.error(`❌ ${e.message}. Missing subscription key env var; set it and retry.`); process.exit(1); }
})();

const BASE_URL = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/disruptions';

// Parse arguments  
const args = process.argv.slice(2);
const getArg = (flag) => {
  const idx = args.indexOf(flag);
  return idx !== -1 ? args[idx + 1] : null;
};

const fromStation = getArg('--from');
const toStation = getArg('--to');
const showAll = args.includes('--all');

async function getDisruptions() {
  const params = new URLSearchParams({
    isActive: 'true'
  });

  const url = `${BASE_URL}?${params}`;
  
  try {
    const response = await nsFetch(url, {
      subscriptionKey: NS_SUBSCRIPTION_KEY,
    });

    if (!response.ok) {
      const error = await response.text();
      console.error(`❌ API Error (${response.status}): ${error}`);
      process.exit(1);
    }

    const data = await response.json();
    let disruptions = data.payload || data || [];
    
    // Flatten if nested
    if (!Array.isArray(disruptions)) {
      disruptions = disruptions.disruptions || [];
    }
    
    if (disruptions.length === 0) {
      console.log('✅ No active disruptions!');
      process.exit(0);
    }
    
    // Filter for route if specified
    if (fromStation || toStation) {
      const searchTerms = [fromStation, toStation].filter(Boolean).map(s => s.toLowerCase());
      disruptions = disruptions.filter(d => {
        const title = (d.title || '').toLowerCase();
        const desc = (d.description || d.timespans?.[0]?.situation?.label || '').toLowerCase();
        const stations = (d.registrationNumbers || []).join(' ').toLowerCase();
        const trajectory = (d.trajectory?.stations || []).map(s => s.name).join(' ').toLowerCase();
        
        const fullText = `${title} ${desc} ${stations} ${trajectory}`;
        return searchTerms.some(term => fullText.includes(term));
      });
      
      if (disruptions.length === 0) {
        console.log(`✅ No disruptions affecting ${fromStation || ''} ${toStation ? '→ ' + toStation : ''}`);
        process.exit(0);
      }
    }
    
    // Limit unless --all
    if (!showAll && disruptions.length > 10) {
      disruptions = disruptions.slice(0, 10);
    }

    console.log(`\n⚠️  Active Disruptions${fromStation ? ` (${fromStation}${toStation ? ' → ' + toStation : ''})` : ''}`);
    console.log('═'.repeat(50));
    
    disruptions.forEach((d, i) => {
      const title = d.title || 'Unknown disruption';
      const type = d.type || 'DISRUPTION';
      const phase = d.phase?.label || d.phase || '';
      
      // Get description from timespans
      let description = '';
      if (d.timespans && d.timespans.length > 0) {
        const ts = d.timespans[0];
        description = ts.situation?.label || ts.cause?.label || '';
        if (ts.alternativeTransport?.label) {
          description += ` | ${ts.alternativeTransport.label}`;
        }
      }
      
      const emoji = type === 'MAINTENANCE' ? '🔧' : '⚠️';
      
      console.log(`\n${emoji} ${title}`);
      if (description) {
        console.log(`   ${description}`);
      }
      if (phase) {
        console.log(`   📍 Phase: ${phase}`);
      }
      
      // Expected duration
      if (d.expectedDuration?.description) {
        console.log(`   ⏰ ${d.expectedDuration.description}`);
      }
      
      // Affected stations
      if (d.trajectory?.stations && d.trajectory.stations.length > 0) {
        const stations = d.trajectory.stations.map(s => s.name).slice(0, 5).join(' ↔ ');
        console.log(`   🚉 ${stations}`);
      }
    });
    
    console.log('\n' + '─'.repeat(50));
    console.log(`⏱️  Checked: ${new Date().toLocaleTimeString('nl-NL')}`);
    if (!showAll && data.payload?.length > 10) {
      console.log(`ℹ️  Showing 10 of ${data.payload.length}. Use --all to see all.`);
    }
    
  } catch (err) {
    console.error(`❌ Error: ${err.message}`);
    process.exit(1);
  }
}

getDisruptions();
