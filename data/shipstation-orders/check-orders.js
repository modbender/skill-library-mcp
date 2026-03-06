#!/usr/bin/env node
/**
 * ShipStation Order Monitor
 * Checks for new orders and flags issues
 */

const fs = require('fs');
const path = require('path');

// Load environment variables from .env
function loadEnv() {
  const envPath = path.join(__dirname, '.env');
  const envContent = fs.readFileSync(envPath, 'utf8');
  const env = {};
  
  envContent.split('\n').forEach(line => {
    const match = line.match(/^([^#=]+)=(.*)$/);
    if (match) {
      env[match[1].trim()] = match[2].trim();
    }
  });
  
  return env;
}

// Load state
function loadState() {
  const statePath = path.join(__dirname, 'state.json');
  try {
    return JSON.parse(fs.readFileSync(statePath, 'utf8'));
  } catch (err) {
    return {
      lastChecks: {},
      processedOrders: [],
      pendingAlerts: [],
      inventoryWarnings: {}
    };
  }
}

// Save state
function saveState(state) {
  const statePath = path.join(__dirname, 'state.json');
  fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
}

// Call ShipStation API
async function callShipStation(endpoint, apiKey, apiSecret) {
  const auth = Buffer.from(`${apiKey}:${apiSecret}`).toString('base64');
  
  const response = await fetch(`https://ssapi.shipstation.com${endpoint}`, {
    headers: {
      'Authorization': `Basic ${auth}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error(`ShipStation API error: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

// Check for new orders
async function checkOrders() {
  const env = loadEnv();
  const state = loadState();
  
  const apiKey = env.SHIPSTATION_API_KEY;
  const apiSecret = env.SHIPSTATION_API_SECRET;
  
  if (!apiKey || !apiSecret || apiKey.includes('your_') || apiSecret.includes('your_')) {
    console.error('❌ ShipStation API credentials not configured in .env');
    process.exit(1);
  }
  
  // Check orders modified in last 24 hours
  const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  
  try {
    const data = await callShipStation(
      `/orders?modifyDateStart=${yesterday}&pageSize=100`,
      apiKey,
      apiSecret
    );
    
    const orders = data.orders || [];
    const newOrders = orders.filter(o => !state.processedOrders.includes(o.orderId));
    
    // Track check time
    state.lastChecks.shipstation = Date.now();
    
    // Results
    const results = {
      total: orders.length,
      new: newOrders.length,
      newOrdersList: [],
      alerts: []
    };
    
    // Check for issues
    for (const order of newOrders) {
      // Track new orders for notification
      if (order.orderStatus === 'awaiting_shipment' || order.orderStatus === 'awaiting_payment') {
        results.newOrdersList.push({
          orderId: order.orderNumber,
          status: order.orderStatus,
          total: order.orderTotal,
          customer: order.shipTo?.name || 'Unknown',
          orderDate: order.orderDate,
          marketplace: order.advancedOptions?.source || 'Unknown'
        });
      }
      // Flag orders awaiting shipment for > 2 days
      const orderDate = new Date(order.orderDate);
      const ageHours = (Date.now() - orderDate.getTime()) / (1000 * 60 * 60);
      
      if (order.orderStatus === 'awaiting_shipment' && ageHours > 48) {
        results.alerts.push({
          orderId: order.orderNumber,
          issue: `⚠️ Order ${order.orderNumber} awaiting shipment for ${Math.floor(ageHours)}h`,
          orderDate: order.orderDate,
          customer: order.shipTo?.name || 'Unknown'
        });
      }
      
      // Flag orders on hold
      if (order.orderStatus === 'on_hold') {
        results.alerts.push({
          orderId: order.orderNumber,
          issue: `🛑 Order ${order.orderNumber} on hold`,
          orderDate: order.orderDate,
          customer: order.shipTo?.name || 'Unknown'
        });
      }
      
      // Add to processed list
      state.processedOrders.push(order.orderId);
    }
    
    // Keep only last 1000 processed orders
    if (state.processedOrders.length > 1000) {
      state.processedOrders = state.processedOrders.slice(-1000);
    }
    
    saveState(state);
    
    // Output results
    console.log(JSON.stringify(results, null, 2));
    
    // Exit with code 1 if there are alerts OR new orders (so heartbeat knows to notify)
    process.exit((results.alerts.length > 0 || results.newOrdersList.length > 0) ? 1 : 0);
    
  } catch (err) {
    console.error('❌ Error checking ShipStation:', err.message);
    process.exit(2);
  }
}

checkOrders();
