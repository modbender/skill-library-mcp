#!/usr/bin/env node
/**
 * Porkbun DNS Management Tool
 * Interact with Porkbun API v3 for DNS management
 *
 * API Docs: https://porkbun.com/api/json/v3/documentation
 *
 * Usage:
 *   node porkbun-dns.js <command> [options]
 *
 * Commands:
 *   ping                     Test API connection
 *   list                     List all domains
 *   list-domains             Alias for list
 *   records <domain>         List all DNS records for a domain
 *   get <domain> [type] [name]  Get specific record(s)
 *   create <domain>           Create a DNS record
 *   edit <domain> <id>        Edit a record by ID
 *   edit-by <domain> <type> [name]  Edit by type/subdomain
 *   delete <domain> <id>      Delete a record by ID
 *   delete-by <domain> <type> [name]  Delete by type/subdomain
 *
 * Environment (required):
 *   PORKBUN_API_KEY        Your API key
 *   PORKBUN_SECRET_API_KEY Your secret API key
 *
 * Or use config file: ~/.config/porkbun/config.json
 */

'use strict';

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

class PorkbunAPI {
  constructor(apiKey, secretApiKey) {
    this.apiKey = apiKey;
    this.secretApiKey = secretApiKey;
    this.baseUrl = 'https://api.porkbun.com/api/json/v3';
  }

  async _request(endpoint, data = {}) {
    return new Promise((resolve, reject) => {
      const url = new URL(`${this.baseUrl}${endpoint}`);
      const payload = JSON.stringify({
        ...data,
        secretapikey: this.secretApiKey,
        apikey: this.apiKey,
      });

      const options = {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(payload),
        },
      };

      const protocol = url.protocol === 'https:' ? https : http;
      const req = protocol.request(options, (res) => {
        let body = '';
        res.on('data', (chunk) => body += chunk);
        res.on('end', () => {
          try {
            const json = JSON.parse(body);
            if (res.statusCode !== 200 || json.status !== 'SUCCESS') {
              reject(new Error(json.message || `HTTP ${res.statusCode}`));
            } else {
              resolve(json);
            }
          } catch (e) {
            reject(new Error(`Invalid JSON response: ${body}`));
          }
        });
      });

      req.on('error', reject);
      req.write(payload);
      req.end();
    });
  }

  // Ping - Test API connection
  async ping() {
    return await this._request('/ping');
  }

  // List all domains
  async listDomains() {
    return await this._request('/domain/listAll', { includeLabels: 'yes' });
  }

  // Get all DNS records for a domain
  async getRecords(domain) {
    return await this._request(`/dns/retrieve/${domain}`);
  }

  // Get DNS records by domain, type, and optionally subdomain
  async getRecordsByNameType(domain, type, name = null) {
    const endpoint = name
      ? `/dns/retrieveByNameType/${domain}/${type}/${name}`
      : `/dns/retrieveByNameType/${domain}/${type}`;
    return await this._request(endpoint);
  }

  // Create a DNS record
  async createRecord(domain, record) {
    const required = ['type', 'content'];
    for (const field of required) {
      if (!record[field]) {
        throw new Error(`Missing required field: ${field}`);
      }
    }

    const validTypes = ['A', 'MX', 'CNAME', 'ALIAS', 'TXT', 'NS', 'AAAA', 'SRV', 'TLSA', 'CAA', 'HTTPS', 'SVCB', 'SSHFP'];
    if (!validTypes.includes(record.type)) {
      throw new Error(`Invalid type: ${record.type}. Valid types: ${validTypes.join(', ')}`);
    }

    return await this._request(`/dns/create/${domain}`, record);
  }

  // Edit a record by ID
  async editRecord(domain, id, record) {
    return await this._request(`/dns/edit/${domain}/${id}`, record);
  }

  // Edit records by type and subdomain
  async editRecordByNameType(domain, type, record, name = null) {
    const endpoint = name
      ? `/dns/editByNameType/${domain}/${type}/${name}`
      : `/dns/editByNameType/${domain}/${type}`;
    return await this._request(endpoint, record);
  }

  // Delete a record by ID
  async deleteRecord(domain, id) {
    return await this._request(`/dns/delete/${domain}/${id}`);
  }

  // Delete records by type and subdomain
  async deleteRecordByNameType(domain, type, name = null) {
    const endpoint = name
      ? `/dns/deleteByNameType/${domain}/${type}/${name}`
      : `/dns/deleteByNameType/${domain}/${type}`;
    return await this._request(endpoint);
  }
}

// Load config from file
function loadConfig() {
  const configPath = path.join(process.env.HOME, '.config', 'porkbun', 'config.json');
  if (fs.existsSync(configPath)) {
    try {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      return {
        apiKey: config.apiKey || process.env.PORKBUN_API_KEY,
        secretApiKey: config.secretApiKey || process.env.PORKBUN_SECRET_API_KEY,
      };
    } catch (e) {
      console.error(`Error reading config file: ${e.message}`);
    }
  }
  return null;
}

// Initialize API client
function createAPI() {
  let apiKey = process.env.PORKBUN_API_KEY;
  let secretApiKey = process.env.PORKBUN_SECRET_API_KEY;

  // Try config file if env vars not set
  if (!apiKey || !secretApiKey) {
    const config = loadConfig();
    if (config) {
      apiKey = apiKey || config.apiKey;
      secretApiKey = secretApiKey || config.secretApiKey;
    }
  }

  if (!apiKey || !secretApiKey) {
    console.error('Error: PORKBUN_API_KEY and PORKBUN_SECRET_API_KEY must be set');
    console.error('');
    console.error('Either set environment variables or create a config file:');
    console.error('  ~/.config/porkbun/config.json');
    console.error('');
    console.error('Config file format:');
    console.err(JSON.stringify({
      apiKey: 'your-api-key',
      secretApiKey: 'your-secret-api-key',
    }, null, 2));
    process.exit(1);
  }

  return new PorkbunAPI(apiKey, secretApiKey);
}

// Print helper functions
function printJSON(data) {
  console.log(JSON.stringify(data, null, 2));
}

function printTable(data) {
  if (!data.length) {
    console.log('No records found.');
    return;
  }

  const columns = ['id', 'name', 'type', 'content', 'ttl', 'prio'];
  const widths = {};
  columns.forEach(col => widths[col] = Math.max(col.length, ...data.map(r => String(r[col] || '').length)));

  // Header
  console.log(columns.map(col => col.padEnd(widths[col])).join(' | '));
  console.log(columns.map(() => '-'.repeat(40)).join('-+-'));

  // Rows
  data.forEach(row => {
    console.log(
      columns.map(col => {
        let val = String(row[col] || '');
        if (col === 'content' && val.length > widths[col]) {
          val = val.slice(0, widths[col] - 3) + '...';
        }
        return val.padEnd(widths[col]);
      }).join(' | ')
    );
  });
}

// CLI Handler
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === 'help' || args[0] === '--help' || args[0] === '-h') {
    console.log(fs.readFileSync(__filename, 'utf8').match(/\/\*\*[\s\S]*?\*\//)[0]
      .replace(/\/\*\*|\*\//g, '')
      .replace(/^\s*\*\s?/gm, ''));
    process.exit(0);
  }

  const api = createAPI();
  const command = args[0];

  try {
    switch (command) {
      case 'ping':
        const ping = await api.ping();
        printJSON(ping);
        break;

      case 'list':
      case 'list-domains':
        const domains = await api.listDomains();
        console.log(`${domains.domains.length} domain(s) found:\n`);
        domains.domains.forEach(d => {
          console.log(`  ${d.domain} (${d.status})`);
          console.log(`    Expires: ${d.expireDate}`);
          console.log(`    Auto-renew: ${d.autoRenew ? 'ON' : 'OFF'}`);
          if (d.labels && d.labels.length) {
            console.log(`    Labels: ${d.labels.map(l => l.title).join(', ')}`);
          }
        });
        break;

      case 'records': {
        const domain = args[1];
        if (!domain) {
          console.error('Error: domain required');
          console.error('Usage: node porkbun-dns.js records <domain>');
          process.exit(1);
        }
        const records = await api.getRecords(domain);
        console.log(`${records.records.length} DNS record(s) for ${domain}:\n`);
        printTable(records.records);
        break;
      }

      case 'get': {
        const [_, _cmd, domain, type, name] = args;
        if (!domain) {
          console.error('Error: domain required');
          console.error('Usage: node porkbun-dns.js get <domain> [type] [name]');
          process.exit(1);
        }
        let result;
        if (type) {
          result = await api.getRecordsByNameType(domain, type, name);
        } else {
          result = await api.getRecords(domain);
        }
        console.log(`${result.records.length} record(s) found:\n`);
        printTable(result.records);
        break;
      }

      case 'create': {
        const [, domain, ...recordArgs] = args;
        if (!domain) {
          console.error('Error: domain required');
          console.error('Usage: node porkbun-dns.js create <domain>');
          console.error('Then provide record fields as key=value pairs:');
          console.error('  type=A name=www content=1.1.1.1 ttl=600');
          process.exit(1);
        }

        // Parse record arguments
        const record = {};
        for (const arg of recordArgs) {
          const [key, ...valParts] = arg.split('=');
          const value = valParts.join('=');
          if (!value) {
            console.error(`Error: Invalid argument format: ${arg}`);
            console.error('Expected: key=value');
            process.exit(1);
          }
          record[key] = value;
        }

        const result = await api.createRecord(domain, record);
        console.log(`✅ Record created successfully!`);
        console.log(`   ID: ${result.id}`);
        break;
      }

      case 'edit': {
        const [_, _cmd, domain, id, ...recordArgs] = args;
        if (!domain || !id) {
          console.error('Error: domain and ID required');
          console.error('Usage: node porkbun-dns.js edit <domain> <id>');
          console.error('Then provide record fields to update as key=value pairs:');
          console.error('  content=1.1.1.2 ttl=600');
          process.exit(1);
        }

        const record = {};
        for (const arg of recordArgs) {
          const [key, ...valParts] = arg.split('=');
          const value = valParts.join('=');
          if (!value) {
            console.error(`Error: Invalid argument format: ${arg}`);
            process.exit(1);
          }
          record[key] = value;
        }

        await api.editRecord(domain, id, record);
        console.log(`✅ Record ${id} updated successfully!`);
        break;
      }

      case 'edit-by': {
        const [_, _cmd, domain, type, ...rest] = args;
        if (!domain || !type) {
          console.error('Error: domain and type required');
          console.error('Usage: node porkbun-dns.js edit-by <domain> <type> [name]');
          console.error('Then provide record fields to update as key=value pairs:');
          console.error('  content=1.1.1.2 ttl=600');
          process.exit(1);
        }

        const name = rest[0] && rest[0].includes('=') ? null : rest[0];
        const recordArgs = name ? rest.slice(1) : rest;

        const record = {};
        for (const arg of recordArgs) {
          const [key, ...valParts] = arg.split('=');
          const value = valParts.join('=');
          if (!value) {
            console.error(`Error: Invalid argument format: ${arg}`);
            process.exit(1);
          }
          record[key] = value;
        }

        await api.editRecordByNameType(domain, type, record, name);
        console.log(`✅ Records for ${domain}${name ? `/${name}` : ''} (${type}) updated successfully!`);
        break;
      }

      case 'delete': {
        const [_, _cmd, domain, id] = args;
        if (!domain || !id) {
          console.error('Error: domain and ID required');
          console.error('Usage: node porkbun-dns.js delete <domain> <id>');
          process.exit(1);
        }

        await api.deleteRecord(domain, id);
        console.log(`✅ Record ${id} deleted successfully!`);
        break;
      }

      case 'delete-by': {
        const [_, _cmd, domain, type, name = null] = args;
        if (!domain || !type) {
          console.error('Error: domain and type required');
          console.error('Usage: node porkbun-dns.js delete-by <domain> <type> [name]');
          process.exit(1);
        }

        await api.deleteRecordByNameType(domain, type, name);
        console.log(`✅ Records for ${domain}${name ? `/${name}` : ''} (${type}) deleted successfully!`);
        break;
      }

      default:
        console.error(`Unknown command: ${command}`);
        console.error('Run: node porkbun-dns.js help');
        process.exit(1);
    }
  } catch (error) {
    console.error(`❌ Error: ${error.message}`);
    process.exit(1);
  }
}

main();