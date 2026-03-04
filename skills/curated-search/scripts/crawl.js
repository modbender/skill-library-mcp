#!/usr/bin/env node
// SECURITY MANIFEST:
//   Environment variables accessed: NONE
//   External endpoints called: User-configured domains from config.yaml during crawling (whitelist only)
//   Local files read: config.yaml
//   Local files written: data/index/*
/**
 * Curated Crawler Runner
 *
 * Entry point for `npm run crawl`.
 * Loads config, initializes indexer, starts crawler.
 */

const fs = require('fs');
const path = require('path');
const yaml = require('yaml');
const CuratedCrawler = require('../src/crawler');
const Indexer = require('../src/indexer');

async function main() {
  try {
    // Load configuration
    const configPath = path.resolve(__dirname, '..', 'config.yaml');
    if (!fs.existsSync(configPath)) {
      console.error(`Configuration not found: ${configPath}`);
      process.exit(1);
    }

    const yamlStr = fs.readFileSync(configPath, 'utf8');
    const config = yaml.parse(yamlStr);

    // Ensure index directory exists
    const indexPath = path.isAbsolute(config.index.path)
      ? config.index.path
      : path.resolve(__dirname, '..', config.index.path);
    const indexDir = path.dirname(indexPath);
    if (!fs.existsSync(indexDir)) {
      fs.mkdirSync(indexDir, { recursive: true });
    }

    // Initialize indexer
    const indexer = new Indexer({ ...config.index, path: indexPath });
    indexer.open();

    // Initialize and start crawler
    const crawler = new CuratedCrawler(config, indexer);
    await crawler.start();

    // Note: crawler.start() calls finalize() which exits the process on completion.
    // But if it rejects, we catch below.
  } catch (error) {
    console.error('Crawler failed:', error);
    process.exit(1);
  }
}

main();
