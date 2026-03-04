/**
 * Kite AI Wallet V3 - OpenClaw Integration
 */

const ethers = require('ethers');

const CONFIG = {
    rpcUrl: 'https://rpc-testnet.gokite.ai',
    factoryAddress: '0x0fa9F878B038DE435b1EFaDA3eed1859a6Dc098a'
};

const FACTORY_ABI = [
    'function createWallet(address agent, uint256 spendingLimit) returns (address)',
    'function getWalletAddress(address owner, address agent) view returns (address)'
];

const WALLET_ABI = [
    'function owner() view returns (address)',
    'function agent() view returns (address)',
    'function spendingLimit() view returns (uint256)',
    'function isSessionKey(address) view returns (bool)',
    'function sessionLimits(address) view returns (uint256)',
    'function addSessionKey(address sessionKey, uint256 limit, bytes4[] functions)',
    'function removeSessionKey(address sessionKey)',
    'function updateSpendingLimit(uint256 newLimit)',
    'function execute(bytes data) payable'
];

let provider, wallet, factory;

function init(privateKey) {
    if (!privateKey) {
        console.log('⚠️ KITE_WALLET_PRIVATE_KEY not set');
        return false;
    }
    try {
        provider = new ethers.JsonRpcProvider(CONFIG.rpcUrl);
        wallet = new ethers.Wallet(privateKey, provider);
        factory = new ethers.Contract(CONFIG.factoryAddress, FACTORY_ABI, wallet);
        console.log('🤖 Kite Wallet initialized:', wallet.address);
        return true;
    } catch (e) {
        console.error('Init error:', e.message);
        return false;
    }
}

function parseCommand(text) {
    const parts = text.trim().toLowerCase().split(/\s+/);
    return {
        cmd: parts[0],
        sub: parts[1],
        args: parts.slice(2)
    };
}

function userIdToAddress(userId) {
    // Convert userId to address format
    const id = userId.toString().padStart(40, '0');
    return '0x' + id.slice(-40);
}

async function getUserWallet(userId) {
    const agentAddr = userIdToAddress(userId);
    const walletAddr = await factory.getWalletAddress(wallet.address, agentAddr);
    return walletAddr;
}

async function handleKiteCommand(text, userId) {
    if (!text.toLowerCase().startsWith('/kite')) return null;
    if (!wallet) return '⚠️ 钱包未配置';
    
    const { cmd, sub, args } = parseCommand(text);
    const fullCmd = sub ? `${cmd} ${sub}` : cmd;
    
    try {
        switch (fullCmd) {
            case '/kite':
            case '/kite help':
                return `📖 *Kite Wallet*\n\n` +
                    `*基础命令*\n` +
                    `/kite create - 创建钱包\n` +
                    `/kite wallet - 查看地址\n` +
                    `/kite balance - 查看余额\n\n` +
                    `*转账*\n` +
                    `/kite send <地址> <数量> - 转账\n\n` +
                    `*授权管理*\n` +
                    `/kite session add <地址> <限额> - 添加授权\n` +
                    `/kite session remove <地址> - 移除授权\n` +
                    `/kite session list - 查看授权\n\n` +
                    `*限额管理*\n` +
                    `/kite limit set <数量> - 设置限额\n` +
                    `/kite limit get - 查看限额`;
            
            // === 基础命令 ===
            case '/kite create': {
                const agentAddr = userIdToAddress(userId);
                const existingWallet = await getUserWallet(userId);
                
                if (existingWallet !== ethers.ZeroAddress) {
                    return `ℹ️ 钱包已存在: \`${existingWallet}\``;
                }
                
                const tx = await factory.createWallet(agentAddr, ethers.parseEther('10'));
                await tx.wait();
                const walletAddr = await getUserWallet(userId);
                
                return `✅ *钱包创建成功！*\n\n` +
                    `地址: \`${walletAddr}\`\n\n` +
                    `充值测试币: https://faucet.gokite.ai`;
            }
            
            case '/kite wallet': {
                const walletAddr = await getUserWallet(userId);
                if (walletAddr === ethers.ZeroAddress) {
                    return '❌ 未找到钱包。使用 /kite create 创建';
                }
                return `🔗 *钱包地址:*\n\n\`${walletAddr}\``;
            }
            
            case '/kite balance': {
                // Check main wallet balance
                const mainBalance = await provider.getBalance(wallet.address);
                
                // Check user wallet if exists
                const userWalletAddr = await getUserWallet(userId);
                let userBalance = '0';
                if (userWalletAddr !== ethers.ZeroAddress) {
                    try {
                        userBalance = await provider.getBalance(userWalletAddr);
                    } catch (e) {}
                }
                
                return `💰 *余额查询*\n\n` +
                    `主钱包: *${ethers.formatEther(mainBalance)} KITE*\n` +
                    `用户钱包: *${ethers.formatEther(userBalance)} KITE*`;
            }
            
            // === 转账 ===
            case '/kite send': {
                if (args.length < 2) {
                    return `❌ *用法错误*\n\n` +
                        `格式: /kite send <地址> <数量>\n\n` +
                        `例: /kite send 0xABC... 0.1`;
                }
                
                const toAddress = args[0];
                const amount = args[1];
                
                // Validate address
                if (!ethers.isAddress(toAddress)) {
                    return '❌ 无效的地址格式';
                }
                
                // Validate amount
                const amountWei = ethers.parseEther(amount);
                const balance = await provider.getBalance(wallet.address);
                
                if (amountWei > balance) {
                    return `❌ 余额不足\n\n` +
                        `当前余额: ${ethers.formatEther(balance)} KITE\n` +
                        `尝试转账: ${amount} KITE`;
                }
                
                const tx = await wallet.sendTransaction({
                    to: toAddress,
                    value: amountWei
                });
                await tx.wait();
                
                return `✅ *转账成功！*\n\n` +
                    `发送: *${amount} KITE*\n` +
                    `到: \`${toAddress}\`\n\n` +
                    `交易: ${tx.hash}`;
            }
            
            // === Session Keys ===
            case '/kite session': {
                if (args.length === 0) {
                    return `📋 *用法:*\n\n` +
                        `/kite session add <地址> <限额> - 添加授权\n` +
                        `/kite session remove <地址> - 移除授权\n` +
                        `/kite session list - 查看授权`;
                }
                
                const action = args[0];
                
                if (action === 'add') {
                    if (args.length < 3) {
                        return '❌ 用法: /kite session add <地址> <限额>';
                    }
                    
                    const sessionAddr = args[1];
                    const limit = args[2];
                    
                    const walletAddr = await getUserWallet(userId);
                    if (walletAddr === ethers.ZeroAddress) {
                        return '❌ 先用 /kite create 创建钱包';
                    }
                    
                    if (!ethers.isAddress(sessionAddr)) {
                        return '❌ 无效的授权地址';
                    }
                    
                    const walletContract = new ethers.Contract(walletAddr, WALLET_ABI, wallet);
                    const tx = await walletContract.addSessionKey(
                        sessionAddr,
                        ethers.parseEther(limit),
                        ['0x00000000'] // Allow all functions
                    );
                    await tx.wait();
                    
                    return `✅ *授权添加成功！*\n\n` +
                        `授权账号: \`${sessionAddr}\`\n` +
                        `限额: *${limit} KITE*`;
                }
                
                if (action === 'remove') {
                    if (args.length < 2) {
                        return '❌ 用法: /kite session remove <地址>';
                    }
                    
                    const sessionAddr = args[1];
                    const walletAddr = await getUserWallet(userId);
                    if (walletAddr === ethers.ZeroAddress) {
                        return '❌ 未找到钱包';
                    }
                    
                    const walletContract = new ethers.Contract(walletAddr, WALLET_ABI, wallet);
                    const tx = await walletContract.removeSessionKey(sessionAddr);
                    await tx.wait();
                    
                    return `✅ *授权已移除:*\n\n\`${sessionAddr}\``;
                }
                
                if (action === 'list' || action === 'get') {
                    return '📋 *Session Keys*\n\n' +
                        '如需查看完整授权列表，请使用合约浏览器查看';
                }
                
                return '❌ 未知session命令';
            }
            
            // === 限额 ===
            case '/kite limit': {
                const action = args[0];
                
                const walletAddr = await getUserWallet(userId);
                if (walletAddr === ethers.ZeroAddress) {
                    return '❌ 先用 /kite create 创建钱包';
                }
                
                const walletContract = new ethers.Contract(walletAddr, WALLET_ABI, provider);
                
                if (action === 'set') {
                    if (args.length < 2) {
                        return '❌ 用法: /kite limit set <数量>';
                    }
                    
                    const newLimit = args[1];
                    const walletContractWrite = new ethers.Contract(walletAddr, WALLET_ABI, wallet);
                    const tx = await walletContractWrite.updateSpendingLimit(ethers.parseEther(newLimit));
                    await tx.wait();
                    
                    return `✅ *限额已更新！*\n\n新限额: *${newLimit} KITE*`;
                }
                
                if (action === 'get' || !action) {
                    const limit = await walletContract.spendingLimit();
                    return `💰 *当前限额:*\n\n*${ethers.formatEther(limit)} KITE*`;
                }
                
                return '❌ 未知limit命令';
            }
            
            default:
                return `❌ 未知命令: ${sub || ''}\n使用 /kite help 查看所有命令`;
        }
    } catch (e) {
        console.error('Kite command error:', e.message);
        return `❌ 错误: ${e.message.slice(0, 150)}`;
    }
}

module.exports = { init, handleKiteCommand, config: CONFIG };
