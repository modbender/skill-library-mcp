#!/usr/bin/env node

/**
 * InstantDB integration for OpenClaw
 * Handles admin operations and real-time subscriptions
 */

const { init, tx, id } = require('@instantdb/admin');
const { WebSocket } = require('ws');

class InstantDBClient {
  constructor(appId, adminToken) {
    this.appId = appId;
    this.adminToken = adminToken;
    this.db = init({ 
      appId, 
      adminToken 
    });
    this.subscriptions = new Map();
  }

  // ADMIN OPERATIONS

  async query(queryObj) {
    const result = await this.db.query(queryObj);
    return result;
  }

  async transact(txs) {
    const result = await this.db.transact(txs);
    return result;
  }

  async createEntity(namespace, data, entityId = null) {
    const eid = entityId || id();
    const result = await this.db.transact([
      tx[namespace][eid].update(data)
    ]);
    return { entityId: eid, result };
  }

  async updateEntity(entityId, namespace, data) {
    const result = await this.db.transact([
      tx[namespace][entityId].update(data)
    ]);
    return result;
  }

  async deleteEntity(entityId, namespace) {
    const result = await this.db.transact([
      tx[namespace][entityId].delete()
    ]);
    return result;
  }

  async linkEntities(parentId, childId, linkName) {
    const result = await this.db.transact([
      tx[linkName][parentId].link({ [linkName]: childId })
    ]);
    return result;
  }

  async unlinkEntities(parentId, childId, linkName) {
    const result = await this.db.transact([
      tx[linkName][parentId].unlink({ [linkName]: childId })
    ]);
    return result;
  }

  // REAL-TIME SUBSCRIPTIONS

  subscribe(queryObj, callback, errorCallback = null) {
    const unsubscribe = this.db.subscribeQuery(queryObj, (result) => {
      if (result.error && errorCallback) {
        errorCallback(result.error);
      } else {
        callback(result.data);
      }
    });

    const subscriptionId = Date.now().toString() + Math.random().toString(36);
    this.subscriptions.set(subscriptionId, unsubscribe);
    
    return subscriptionId;
  }

  unsubscribe(subscriptionId) {
    const unsubscribe = this.subscriptions.get(subscriptionId);
    if (unsubscribe) {
      unsubscribe();
      this.subscriptions.delete(subscriptionId);
    }
  }

  unsubscribeAll() {
    for (const unsubscribe of this.subscriptions.values()) {
      unsubscribe();
    }
    this.subscriptions.clear();
  }
}

// CLI INTERFACE

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 1) {
    console.error('Usage: instantdb.js <command> [args...]');
    console.error('Commands: query, create, update, delete, link, unlink, subscribe, transact');
    process.exit(1);
  }

  const appId = process.env.INSTANTDB_APP_ID;
  const adminToken = process.env.INSTANTDB_ADMIN_TOKEN;

  if (!appId) {
    console.error('Error: INSTANTDB_APP_ID environment variable not set');
    process.exit(1);
  }

  if (!adminToken) {
    console.error('Error: INSTANTDB_ADMIN_TOKEN environment variable not set');
    process.exit(1);
  }

  const client = new InstantDBClient(appId, adminToken);
  const command = args[0];

  try {
    switch (command) {
      case 'query': {
        const query = JSON.parse(args[1]);
        const result = await client.query(query);
        console.log(JSON.stringify(result, null, 2));
        break;
      }

      case 'create': {
        const namespace = args[1];
        const data = JSON.parse(args[2]);
        const entityId = args[3] || null;
        const result = await client.createEntity(namespace, data, entityId);
        console.log(JSON.stringify(result, null, 2));
        break;
      }

      case 'update': {
        const entityId = args[1];
        const namespace = args[2];
        const data = JSON.parse(args[3]);
        const result = await client.updateEntity(entityId, namespace, data);
        console.log(JSON.stringify(result, null, 2));
        break;
      }

      case 'delete': {
        const entityId = args[1];
        const namespace = args[2];
        const result = await client.deleteEntity(entityId, namespace);
        console.log(JSON.stringify(result, null, 2));
        break;
      }

      case 'link': {
        const parentId = args[1];
        const childId = args[2];
        const linkName = args[3];
        const result = await client.linkEntities(parentId, childId, linkName);
        console.log(JSON.stringify(result, null, 2));
        break;
      }

      case 'unlink': {
        const parentId = args[1];
        const childId = args[2];
        const linkName = args[3];
        const result = await client.unlinkEntities(parentId, childId, linkName);
        console.log(JSON.stringify(result, null, 2));
        break;
      }

      case 'subscribe': {
        const query = JSON.parse(args[1]);
        const duration = parseInt(args[2] || '60', 10);
        
        console.error(`Subscribing to query. Listening for ${duration}s...`);
        
        const subscriptionId = client.subscribe(
          query,
          (data) => {
            console.log(JSON.stringify({ type: 'update', data }, null, 2));
          },
          (error) => {
            console.error(JSON.stringify({ type: 'error', error }, null, 2));
          }
        );

        await new Promise(resolve => setTimeout(resolve, duration * 1000));
        
        client.unsubscribe(subscriptionId);
        console.error('Subscription ended');
        break;
      }

      case 'transact': {
        const txs = JSON.parse(args[1]);
        const result = await client.transact(txs);
        console.log(JSON.stringify(result, null, 2));
        break;
      }

      default:
        console.error(`Unknown command: ${command}`);
        process.exit(1);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(error => {
    console.error(error);
    process.exit(1);
  });
}

module.exports = { InstantDBClient };
