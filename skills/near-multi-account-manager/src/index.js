/**
 * NEAR Multi-Account Manager
 * Securely manage multiple NEAR Protocol accounts
 */

const { connect, keyStores, Account, utils } = require('near-api-js');
const CryptoJS = require('crypto-js');
const fs = require('fs-extra');
const path = require('path');

// Constants
const DATA_DIR = path.join(process.env.OPENCLAW_HOME || process.env.HOME || process.env.USERPROFILE, '.openclaw', 'skills', 'near-multi-account-manager');
const ACCOUNTS_FILE = path.join(DATA_DIR, 'accounts.enc');
const ACTIVE_ACCOUNT_FILE = path.join(DATA_DIR, 'active_account.txt');
const NETWORK_ID = 'mainnet';
const NEAR_CONFIG = {
  networkId: NETWORK_ID,
  nodeUrl: 'https://rpc.mainnet.near.org',
  walletUrl: 'https://wallet.mainnet.near.org',
  helperUrl: 'https://helper.mainnet.near.org',
  explorerUrl: 'https://explorer.mainnet.near.org',
};

/**
 * Get encryption key from environment or generate one
 */
function getEncryptionKey() {
  const key = process.env.NEAR_SKILL_KEY || 'default-key-change-in-production';
  return CryptoJS.enc.Utf8.parse(key);
}

/**
 * Encrypt data
 */
function encrypt(data) {
  const key = getEncryptionKey();
  const iv = CryptoJS.lib.WordArray.random(16);
  const encrypted = CryptoJS.AES.encrypt(JSON.stringify(data), key, {
    iv: iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
  });
  return iv.toString(CryptoJS.enc.Hex) + ':' + encrypted.toString();
}

/**
 * Decrypt data
 */
function decrypt(encryptedData) {
  try {
    const key = getEncryptionKey();
    const parts = encryptedData.split(':');
    const iv = CryptoJS.enc.Hex.parse(parts[0]);
    const encrypted = parts[1];
    const decrypted = CryptoJS.AES.decrypt(encrypted, key, {
      iv: iv,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7,
    });
    return JSON.parse(decrypted.toString(CryptoJS.enc.Utf8));
  } catch (error) {
    return null;
  }
}

/**
 * Ensure data directory exists
 */
async function ensureDataDir() {
  await fs.ensureDir(DATA_DIR);
}

/**
 * Load accounts from encrypted storage
 */
async function loadAccounts() {
  try {
    await ensureDataDir();
    const exists = await fs.pathExists(ACCOUNTS_FILE);
    if (!exists) return {};
    const encrypted = await fs.readFile(ACCOUNTS_FILE, 'utf8');
    return decrypt(encrypted) || {};
  } catch (error) {
    console.error('Error loading accounts:', error.message);
    return {};
  }
}

/**
 * Save accounts to encrypted storage
 */
async function saveAccounts(accounts) {
  await ensureDataDir();
  const encrypted = encrypt(accounts);
  await fs.writeFile(ACCOUNTS_FILE, encrypted, 'utf8');
}

/**
 * Get active account ID
 */
async function getActiveAccountId() {
  try {
    await ensureDataDir();
    const exists = await fs.pathExists(ACTIVE_ACCOUNT_FILE);
    if (!exists) return null;
    return await fs.readFile(ACTIVE_ACCOUNT_FILE, 'utf8');
  } catch (error) {
    return null;
  }
}

/**
 * Set active account ID
 */
async function setActiveAccountId(accountId) {
  await ensureDataDir();
  await fs.writeFile(ACTIVE_ACCOUNT_FILE, accountId, 'utf8');
}

/**
 * Create NEAR connection
 */
async function createConnection(privateKey) {
  const keyPair = utils.KeyPair.fromString(privateKey);
  const keyStore = new keyStores.InMemoryKeyStore();
  keyStore.setKey(NETWORK_ID, keyPair.getPublicKey().toString(), keyPair);

  return await connect({
    ...NEAR_CONFIG,
    keyStore,
  });
}

/**
 * Validate NEAR account
 */
async function validateAccount(accountId, privateKey) {
  try {
    const connection = await createConnection(privateKey);
    const account = new Account(connection, accountId);
    await account.state();
    return true;
  } catch (error) {
    console.error('Account validation failed:', error.message);
    return false;
  }
}

/**
 * Format NEAR amount
 */
function formatNear(yoctoNear) {
  return utils.format.formatNearAmount(yoctoNear, 4);
}

/**
 * Parse NEAR amount
 */
function parseNear(nearAmount) {
  return utils.format.parseNearAmount(nearAmount.toString());
}

// ==================== SKILL ENTRYPOINTS ====================

/**
 * Add a NEAR account to the manager
 */
async function add_account({ accountId, privateKey, name }) {
  if (!accountId || !privateKey) {
    return {
      success: false,
      error: ' accountId and privateKey are required',
    };
  }

  // Validate private key format
  if (!privateKey.startsWith('ed25519:')) {
    return {
      success: false,
      error: 'Private key must start with "ed25519:"',
    };
  }

  // Validate account
  const isValid = await validateAccount(accountId, privateKey);
  if (!isValid) {
    return {
      success: false,
      error: 'Invalid account credentials or account does not exist',
    };
  }

  const accounts = await loadAccounts();

  if (accounts[accountId]) {
    return {
      success: false,
      error: 'Account already exists in manager',
    };
  }

  // Store account
  accounts[accountId] = {
    accountId,
    privateKey,
    name: name || accountId,
    addedAt: new Date().toISOString(),
  };

  await saveAccounts(accounts);

  return {
    success: true,
    message: `Account "${accountId}" added successfully`,
    account: {
      accountId,
      name: accounts[accountId].name,
      addedAt: accounts[accountId].addedAt,
    },
  };
}

/**
 * List all managed NEAR accounts
 */
async function list_accounts() {
  const accounts = await loadAccounts();
  const activeAccountId = await getActiveAccountId();

  const accountList = Object.values(accounts).map(acc => ({
    accountId: acc.accountId,
    name: acc.name,
    isActive: acc.accountId === activeAccountId,
    addedAt: acc.addedAt,
  }));

  return {
    success: true,
    count: accountList.length,
    accounts: accountList,
  };
}

/**
 * Set the active NEAR account
 */
async function set_active_account({ accountId }) {
  if (!accountId) {
    return {
      success: false,
      error: 'accountId is required',
    };
  }

  const accounts = await loadAccounts();

  if (!accounts[accountId]) {
    return {
      success: false,
      error: 'Account not found in manager',
    };
  }

  await setActiveAccountId(accountId);

  return {
    success: true,
    message: `Active account set to "${accountId}"`,
    accountId,
    name: accounts[accountId].name,
  };
}

/**
 * Get balance for specified or active account
 */
async function get_balance({ accountId } = {}) {
  const accounts = await loadAccounts();

  let targetAccount = accountId;

  if (!targetAccount) {
    targetAccount = await getActiveAccountId();
    if (!targetAccount) {
      return {
        success: false,
        error: 'No active account set. Please specify accountId or set an active account.',
      };
    }
  }

  if (!accounts[targetAccount]) {
    return {
      success: false,
      error: 'Account not found in manager',
    };
  }

  try {
    const connection = await createConnection(accounts[targetAccount].privateKey);
    const account = new Account(connection, targetAccount);
    const balance = await account.getAccountBalance();

    return {
      success: true,
      accountId: targetAccount,
      name: accounts[targetAccount].name,
      balances: {
        available: formatNear(balance.available),
        staked: formatNear(balance.staked),
        total: formatNear(balance.total),
        stateStaked: formatNear(balance.stateStaked),
      },
      rawBalances: balance,
    };
  } catch (error) {
    return {
      success: false,
      error: `Failed to fetch balance: ${error.message}`,
    };
  }
}

/**
 * Get balances for all accounts
 */
async function get_all_balances() {
  const accounts = await loadAccounts();
  const activeAccountId = await getActiveAccountId();

  const balances = [];

  for (const [accountId, accountData] of Object.entries(accounts)) {
    try {
      const connection = await createConnection(accountData.privateKey);
      const account = new Account(connection, accountId);
      const balance = await account.getAccountBalance();

      balances.push({
        accountId,
        name: accountData.name,
        isActive: accountId === activeAccountId,
        available: formatNear(balance.available),
        staked: formatNear(balance.staked),
        total: formatNear(balance.total),
      });
    } catch (error) {
      balances.push({
        accountId,
        name: accountData.name,
        isActive: accountId === activeAccountId,
        error: error.message,
      });
    }
  }

  return {
    success: true,
    count: balances.length,
    balances,
  };
}

/**
 * Transfer NEAR between accounts
 */
async function transfer({ from, to, amount, note }) {
  if (!to || !amount) {
    return {
      success: false,
      error: 'to and amount are required',
    };
  }

  const accounts = await loadAccounts();

  // Determine source account
  let fromAccount = from;
  if (!fromAccount) {
    fromAccount = await getActiveAccountId();
    if (!fromAccount) {
      return {
        success: false,
        error: 'No active account set. Please specify from or set an active account.',
      };
    }
  }

  // Validate source account
  if (!accounts[fromAccount]) {
    return {
      success: false,
      error: 'Source account not found in manager',
    };
  }

  try {
    const parsedAmount = parseNear(amount);

    const connection = await createConnection(accounts[fromAccount].privateKey);
    const account = new Account(connection, fromAccount);

    const result = await account.sendMoney(to, parsedAmount);

    return {
      success: true,
      message: `Transferred ${amount} NEAR from ${fromAccount} to ${to}`,
      transaction: {
        from: fromAccount,
        to,
        amount,
        transactionHash: result.transaction.hash,
        note: note || '',
      },
    };
  } catch (error) {
    return {
      success: false,
      error: `Transfer failed: ${error.message}`,
    };
  }
}

/**
 * Get transaction history for an account
 */
async function get_transactions({ accountId, limit = 10 } = {}) {
  const accounts = await loadAccounts();

  let targetAccount = accountId;

  if (!targetAccount) {
    targetAccount = await getActiveAccountId();
    if (!targetAccount) {
      return {
        success: false,
        error: 'No active account set. Please specify accountId or set an active account.',
      };
    }
  }

  if (!accounts[targetAccount]) {
    return {
      success: false,
      error: 'Account not found in manager',
    };
  }

  try {
    const connection = await createConnection(accounts[targetAccount].privateKey);
    const account = new Account(connection, targetAccount);

    // Get account state which includes recent transactions
    const state = await account.state();

    // Note: NEAR API doesn't provide direct transaction history without indexing
    // We provide basic info and recommend using explorer for full history
    return {
      success: true,
      accountId: targetAccount,
      name: accounts[targetAccount].name,
      accountInfo: {
        amount: formatNear(state.amount),
        locked: formatNear(state.locked),
        codeHash: state.code_hash,
        storageUsage: state.storage_usage,
        storagePaid: formatNear(state.storage_paid),
      },
      message: 'For full transaction history, visit: https://explorer.mainnet.near.org/accounts/' + targetAccount,
      explorerUrl: `https://explorer.mainnet.near.org/accounts/${targetAccount}`,
      note: 'Transaction history requires indexer integration. Use the explorer link above for full history.',
    };
  } catch (error) {
    return {
      success: false,
      error: `Failed to fetch transactions: ${error.message}`,
    };
  }
}

/**
 * Get a summary of all managed accounts
 */
async function account_summary() {
  const accounts = await loadAccounts();
  const activeAccountId = await getActiveAccountId();

  const summary = {
    totalAccounts: Object.keys(accounts).length,
    activeAccount: activeAccountId,
    accounts: [],
    totalBalance: '0',
  };

  let totalBalanceYocto = BigInt(0);

  for (const [accountId, accountData] of Object.entries(accounts)) {
    try {
      const connection = await createConnection(accountData.privateKey);
      const account = new Account(connection, accountId);
      const balance = await account.getAccountBalance();

      totalBalanceYocto += BigInt(balance.total);

      summary.accounts.push({
        accountId,
        name: accountData.name,
        isActive: accountId === activeAccountId,
        available: formatNear(balance.available),
        staked: formatNear(balance.staked),
        total: formatNear(balance.total),
        addedAt: accountData.addedAt,
      });
    } catch (error) {
      summary.accounts.push({
        accountId,
        name: accountData.name,
        isActive: accountId === activeAccountId,
        error: error.message,
      });
    }
  }

  summary.totalBalance = formatNear(totalBalanceYocto.toString());

  return {
    success: true,
    ...summary,
  };
}

/**
 * Remove an account from the manager
 */
async function remove_account({ accountId, confirm }) {
  if (!accountId) {
    return {
      success: false,
      error: 'accountId is required',
    };
  }

  const accounts = await loadAccounts();

  if (!accounts[accountId]) {
    return {
      success: false,
      error: 'Account not found in manager',
    };
  }

  if (confirm !== accountId) {
    return {
      success: false,
      error: 'Please confirm by setting confirm parameter to the accountId',
    };
  }

  // Remove account
  delete accounts[accountId];
  await saveAccounts(accounts);

  // Clear active account if it was the removed one
  const activeAccountId = await getActiveAccountId();
  if (activeAccountId === accountId) {
    await fs.remove(ACTIVE_ACCOUNT_FILE);
  }

  return {
    success: true,
    message: `Account "${accountId}" removed from manager`,
  };
}

/**
 * Export account information (without private keys)
 */
async function export_accounts() {
  const accounts = await loadAccounts();
  const activeAccountId = await getActiveAccountId();

  const exportData = {
    exportedAt: new Date().toISOString(),
    activeAccount: activeAccountId,
    accounts: Object.values(accounts).map(acc => ({
      accountId: acc.accountId,
      name: acc.name,
      addedAt: acc.addedAt,
    })),
  };

  return {
    success: true,
    export: exportData,
    note: 'Private keys are NOT included in export for security',
  };
}

/**
 * Import an account from backup (requires adding private key separately)
 */
async function import_account({ accountId, name }) {
  if (!accountId) {
    return {
      success: false,
      error: 'accountId is required',
    };
  }

  const accounts = await loadAccounts();

  if (accounts[accountId]) {
    return {
      success: false,
      error: 'Account already exists. Cannot import duplicate.',
    };
  }

  // Create placeholder entry - user must call add_account with privateKey
  accounts[accountId] = {
    accountId,
    privateKey: null, // Must be added via add_account
    name: name || accountId,
    addedAt: new Date().toISOString(),
    needsPrivateKey: true,
  };

  await saveAccounts(accounts);

  return {
    success: true,
    message: `Account "${accountId}" imported. Please call add_account with privateKey to activate.`,
    accountId,
    needsPrivateKey: true,
  };
}

// Export all entrypoints
module.exports = {
  add_account,
  list_accounts,
  set_active_account,
  get_balance,
  get_all_balances,
  transfer,
  get_transactions,
  account_summary,
  remove_account,
  export_accounts,
  import_account,
};
