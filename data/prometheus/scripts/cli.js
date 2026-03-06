#!/usr/bin/env node

/**
 * Prometheus CLI - Query Prometheus monitoring data
 * 
 * Usage:
 *   node cli.js query '<promql>'              - Run instant query
 *   node cli.js range '<promql>' <start> <end> - Run range query
 *   node cli.js labels                        - List label names
 *   node cli.js label-values <label>          - Get values for label
 *   node cli.js series '<selector>'           - Find time series
 *   node cli.js metrics [pattern]             - Get metrics metadata
 *   node cli.js alerts                        - Get active alerts
 *   node cli.js targets                       - Get scrape targets
 * 
 * Environment variables:
 *   PROMETHEUS_URL      - Prometheus server URL (required)
 *   PROMETHEUS_USER     - HTTP Basic Auth username (optional)
 *   PROMETHEUS_PASSWORD - HTTP Basic Auth password (optional)
 */

import { 
  instantQuery, 
  rangeQuery, 
  getLabels, 
  getLabelValues, 
  getSeries, 
  getMetadata,
  getAlerts,
  getTargets
} from './query.js';

const command = process.argv[2];

function output(data) {
  console.log(JSON.stringify(data, null, 2));
}

function errorExit(message) {
  console.error(`Error: ${message}`);
  process.exit(1);
}

async function main() {
  try {
    switch (command) {
      case 'query':
      case 'q': {
        const queryStr = process.argv[3];
        if (!queryStr) errorExit('Query string required');
        const result = await instantQuery(queryStr);
        output(result);
        break;
      }

      case 'range':
      case 'r': {
        const queryStr = process.argv[3];
        const start = process.argv[4];
        const end = process.argv[5];
        const step = parseInt(process.argv[6]) || 60;
        if (!queryStr || !start || !end) {
          errorExit('Usage: range <query> <start> <end> [step]');
        }
        const result = await rangeQuery(queryStr, start, end, step);
        output(result);
        break;
      }

      case 'labels':
      case 'l': {
        const result = await getLabels();
        output(result);
        break;
      }

      case 'label-values':
      case 'lv': {
        const label = process.argv[3];
        if (!label) errorExit('Label name required');
        const result = await getLabelValues(label);
        output(result);
        break;
      }

      case 'series':
      case 's': {
        const match = process.argv[3];
        if (!match) errorExit('Series selector required (e.g., \'{__name__=\"up\"}\')');
        const result = await getSeries(match);
        output(result);
        break;
      }

      case 'metrics':
      case 'm': {
        const pattern = process.argv[3] || '';
        const result = await getMetadata(pattern);
        output(result);
        break;
      }

      case 'alerts':
      case 'a': {
        const result = await getAlerts();
        output(result);
        break;
      }

      case 'targets':
      case 't': {
        const result = await getTargets();
        output(result);
        break;
      }

      case 'help':
      case 'h':
      case '--help':
      case '-h':
      default: {
        console.log(`
Prometheus CLI - Query Prometheus monitoring data

Commands:
  query <promql>           Run instant query
  range <q> <start> <end>  Run range query (timestamps in RFC3339 or Unix)
  labels                   List all label names
  label-values <label>     Get values for a specific label
  series <selector>        Find time series by label matchers
  metrics [pattern]        Get metrics metadata
  alerts                   Get active alerts
  targets                  Get scrape targets

Environment variables:
  PROMETHEUS_URL           Prometheus server URL (required)
  PROMETHEUS_USER          HTTP Basic Auth username (optional)
  PROMETHEUS_PASSWORD      HTTP Basic Auth password (optional)

Examples:
  node cli.js query 'up'
  node cli.js query '100 - (node_filesystem_avail_bytes / node_filesystem_size_bytes * 100)'
  node cli.js labels
  node cli.js label-values instance
  node cli.js series '{__name__=~"node_cpu_.*"}'
`);
        break;
      }
    }
  } catch (err) {
    errorExit(err.message);
  }
}

main();
