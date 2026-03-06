// ============================================================================
// commands/delete-account.js — Delete (deactivate) account + unbind devices
// ============================================================================

'use strict';

const api = require('../api.js');
const { fish, ok, err, warn, c, detail } = require('../ui.js');

async function run(args, flags) {
  fish('Requesting account deletion...');

  // Safety: require --confirm flag
  if (!flags.confirm && !flags.yes && !flags.y) {
    console.log('');
    warn('This will permanently deactivate your account:');
    console.log('');
    console.log('  • 软删除账号（设置 deleted_at）');
    console.log('  • 解绑所有设备');
    console.log('  • 撤销所有 API Key');
    console.log('  • 解除 OAuth 关联（GitHub/Google 可重新注册）');
    console.log('  • 已发布的资产保留，不删除');
    console.log('');
    console.log(`  To confirm, run: ${c('bold', 'openclawmp delete-account --confirm')}`);
    console.log('');
    return;
  }

  const { status, data } = await api.del('/api/auth/account');

  if (status >= 200 && status < 300 && data?.success) {
    console.log('');
    ok('账号已注销');
    console.log('');
    detail('状态', '设备已解绑，API Key 已撤销，OAuth 已解除关联');
    detail('资产', '已发布的资产仍会保留');
    console.log('');
  } else {
    err(data?.message || data?.error || `Account deletion failed (HTTP ${status})`);
    process.exit(1);
  }
}

module.exports = { run };
