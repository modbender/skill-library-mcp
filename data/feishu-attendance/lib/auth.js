const { getToken } = require('../../feishu-common/index.js');

async function getTenantAccessToken(forceRefresh = false) {
  // Delegate to feishu-common
  return await getToken(forceRefresh);
}

module.exports = {
  getTenantAccessToken
};
