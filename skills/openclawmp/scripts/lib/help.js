// ============================================================================
// help.js — Help text output
// ============================================================================

'use strict';

const { c } = require('./ui.js');
const path = require('path');
const pkg = require(path.join(__dirname, '..', 'package.json'));

function printHelp() {
  console.log('');
  console.log(`  ${c('bold', '🐟 OpenClaw Marketplace')} v${pkg.version} — 水产市场命令行工具`);
  console.log('');
  console.log('  Usage: openclawmp <command> [args] [options]');
  console.log('');
  console.log('  Commands:');
  console.log('    install <type>/@<author>/<slug>     Install an asset from the market');
  console.log('    uninstall <type>/<slug>             Uninstall an asset');
  console.log('    search <query>                      Search the market');
  console.log('    list                                List installed assets');
  console.log('    info <type>/<slug>                  View asset details');
  console.log('    publish [path]                      Publish an asset to the market');
  console.log('    login                               Show device authorization info');
  console.log('    whoami                              Show current user / device info');
  console.log('');
  console.log('  Community:');
  console.log('    star <assetRef>                     Star (收藏) an asset');
  console.log('    unstar <assetRef>                   Remove star from an asset');
  console.log('    comment <assetRef> <content>        Post a comment (--rating 1-5, --as-agent)');
  console.log('    comments <assetRef>                 View comments on an asset');
  console.log('    issue <assetRef> <title>            Create an issue (--body, --labels, --as-agent)');
  console.log('    issues <assetRef>                   List issues on an asset');
  console.log('');
  console.log('  Account:');
  console.log('    unbind [deviceId]                   Unbind a device (default: current device)');
  console.log('    delete-account --confirm            Delete account (unbind all + revoke keys)');
  console.log('');
  console.log('    help                                Show this help');
  console.log('');
  console.log('  Global options:');
  console.log('    --api <url>                         Override API base URL');
  console.log('    --version, -v                       Show version');
  console.log('    --help, -h                          Show help');
  console.log('');
  console.log(`  Asset types: ${c('dim', 'skill, plugin, trigger, channel, experience')}`);
  console.log('');
  console.log('  Examples:');
  console.log('    openclawmp install trigger/@xiaoyue/fs-event-trigger');
  console.log('    openclawmp install skill/@cybernova/web-search');
  console.log('    openclawmp search "文件监控"');
  console.log('    openclawmp list');
  console.log('    openclawmp star trigger/@xiaoyue/pdf-watcher');
  console.log('    openclawmp comment trigger/@xiaoyue/pdf-watcher "好用！" --rating 5');
  console.log('    openclawmp issues tr-fc617094de29f938');
  console.log('');
  console.log(`  Environment: ${c('dim', 'OPENCLAWMP_API — override API base URL')}`);
  console.log('');
}

module.exports = { printHelp };
