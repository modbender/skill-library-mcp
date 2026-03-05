// Traffic Data Skill - Main Entry
// Query real-time traffic data

const axios = require('axios');

// Get API keys from environment
const BAIDU_MAP_KEY = process.env.BAIDU_MAP_KEY || '';
const GAODE_MAP_KEY = process.env.GAODE_MAP_KEY || '';
const SCATS_API_KEY = process.env.SCATS_API_KEY || '';

const command = process.argv[2] || 'help';

async function help() {
  console.log(`
🚦 Traffic Data Skill

Usage: node traffic-data.js <command> [args]

Commands:
  road <city> <road>     - Query real-time road conditions
  incident <city>        - Query traffic incidents
  scats <intersection>   - Query SCATS intersection data
  config                - Show current configuration

Examples:
  node traffic-data.js road 广州 广州大道
  node traffic-data.js incident 广州
  node traffic-data.js scats 001
  `);
}

async function queryRoad(city, road) {
  if (!GAODE_MAP_KEY && !BAIDU_MAP_KEY) {
    console.log('Error: Please configure map API key in .env file');
    console.log('GAODE_MAP_KEY or BAIDU_MAP_KEY required');
    return;
  }
  
  console.log(`Querying ${city} ${road} traffic conditions...`);
  
  if (GAODE_MAP_KEY) {
    try {
      const url = `https://restapi.amap.com/v3/trafficstatus/road`;
      const params = {
        key: GAODE_MAP_KEY,
        city: city,
        name: road
      };
      const response = await axios.get(url, { params });
      console.log('Result:', JSON.stringify(response.data, null, 2));
    } catch (err) {
      console.log('Error:', err.message);
    }
  } else {
    console.log('Using Baidu API...');
  }
}

async function queryIncident(city) {
  console.log(`Querying ${city} traffic incidents...`);
  
  if (GAODE_MAP_KEY) {
    try {
      const url = `https://restapi.amap.com/v3/trafficstatus/status`;
      const params = {
        key: GAODE_MAP_KEY,
        city: city
      };
      const response = await axios.get(url, { params });
      console.log('Result:', JSON.stringify(response.data, null, 2));
    } catch (err) {
      console.log('Error:', err.message);
    }
  }
}

async function queryScats(intersection) {
  console.log(`Querying SCATS intersection ${intersection}...`);
  
  if (!SCATS_API_KEY) {
    console.log('Note: SCATS_API_KEY not configured');
    console.log('Please configure SCATS_API_KEY in .env for SCATS data access');
    return;
  }
  
  // Placeholder for SCATS API call
  console.log('SCATS API not implemented yet');
}

async function showConfig() {
  console.log('Current Configuration:');
  console.log(`BAIDU_MAP_KEY: ${BAIDU_MAP_KEY ? '***configured***' : 'NOT SET'}`);
  console.log(`GAODE_MAP_KEY: ${GAODE_MAP_KEY ? '***configured***' : 'NOT SET'}`);
  console.log(`SCATS_API_KEY: ${SCATS_API_KEY ? '***configured***' : 'NOT SET'}`);
}

// Main
(async () => {
  switch(command) {
    case 'road':
      await queryRoad(process.argv[3], process.argv[4]);
      break;
    case 'incident':
      await queryIncident(process.argv[3]);
      break;
    case 'scats':
      await queryScats(process.argv[3]);
      break;
    case 'config':
      await showConfig();
      break;
    default:
      await help();
  }
})();
