require('dotenv').config();

const ethers = require('ethers');
const https = require('https');
const fs = require('fs');

// Configuration from environment
const CONFIG = {
    privateKey: process.env.PRIVATE_KEY,
    rpcUrl: process.env.RPC_URL || 'https://rpc-testnet.gokite.ai',
    factoryAddress: process.env.FACTORY_ADDRESS || '0x0fa9F878B038DE435b1EFaDA3eed1859a6Dc098a',
    botToken: process.env.TELEGRAM_BOT_TOKEN,
    chainId: parseInt(process.env.CHAIN_ID) || 2368
};

// Validate required config
if (!CONFIG.privateKey) {
    console.error('❌ Error: PRIVATE_KEY is required');
    console.log('Create .env file:');
    console.log('PRIVATE_KEY=your_private_key');
    console.log('TELEGRAM_BOT_TOKEN=your_bot_token');
    process.exit(1);
}

if (!CONFIG.botToken) {
    console.error('❌ Error: TELEGRAM_BOT_TOKEN is required');
    console.log('Create .env file:');
    console.log('TELEGRAM_BOT_TOKEN=your_bot_token');
    process.exit(1);
}

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

// Initialize
const provider = new ethers.JsonRpcProvider(CONFIG.rpcUrl);
const wallet = new ethers.Wallet(CONFIG.privateKey, provider);
const factory = new ethers.Contract(CONFIG.factoryAddress, FACTORY_ABI, wallet);

console.log('🤖 Kite Wallet Bot');
console.log('Wallet:', wallet.address);
console.log('Network:', CONFIG.rpcUrl);

// Telegram API helper
function sendMessage(chatId, text) {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify({
            chat_id: chatId,
            text: text,
            parse_mode: 'Markdown'
        });
        
        const options = {
            hostname: 'api.telegram.org',
            path: `/bot${CONFIG.botToken}/sendMessage`,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(data)
            }
        };
        
        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => resolve(body));
        });
        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

function parseCommand(text) {
    const parts = text.trim().split(/\s+/);
    const command = parts[0].toLowerCase();
    const args = parts.slice(1);
    return { command, args };
}

async function getOrCreateWallet(userAddress) {
    const agentAddress = userAddress;
    let walletAddress = await factory.getWalletAddress(userAddress, agentAddress);
    
    if (walletAddress === ethers.ZeroAddress) {
        const tx = await factory.createWallet(agentAddress, ethers.parseEther('1'));
        await tx.wait();
        walletAddress = await factory.getWalletAddress(userAddress, agentAddress);
    }
    return walletAddress;
}

async function handleMessage(message, userAddress) {
    const { command, args } = parseCommand(message);
    
    try {
        switch (command) {
            case '/create': {
                const walletAddress = await getOrCreateWallet(userAddress);
                return `✅ *Wallet Created!*\n\nAddress: \`${walletAddress}\``;
            }
            case '/wallet': {
                const walletAddress = await factory.getWalletAddress(userAddress, userAddress);
                if (walletAddress === ethers.ZeroAddress) return '❌ No wallet. Use /create';
                return `🔗 Wallet: \`${walletAddress}\``;
            }
            case '/balance': {
                let targetAddress = args[0] || await factory.getWalletAddress(userAddress, userAddress);
                if (targetAddress === ethers.ZeroAddress) return '❌ No wallet.';
                const balance = await provider.getBalance(targetAddress);
                return `💰 Balance: *${ethers.formatEther(balance)} KITE*`;
            }
            case '/session': {
                const walletAddress = await factory.getWalletAddress(userAddress, userAddress);
                if (walletAddress === ethers.ZeroAddress) return '❌ No wallet.';
                
                if (args[0] === 'add') {
                    if (args.length < 3) return '❌ Usage: /session add <addr> <limit>';
                    const sessionKey = args[1];
                    const limit = ethers.parseEther(args[2]);
                    const walletContract = new ethers.Contract(walletAddress, WALLET_ABI, wallet);
                    const tx = await walletContract.addSessionKey(sessionKey, limit, ['0x00000000']);
                    await tx.wait();
                    return `✅ Key added: \`${sessionKey}\`\nLimit: ${args[2]} KITE`;
                }
                if (args[0] === 'list' || !args[0]) {
                    return `📋 Wallet: \`${walletAddress}\``;
                }
                return '❌ Usage: /session add <addr> <limit>';
            }
            case '/limit': {
                const walletAddress = await factory.getWalletAddress(userAddress, userAddress);
                if (walletAddress === ethers.ZeroAddress) return '❌ No wallet.';
                
                if (args[0] === 'set') {
                    if (args.length < 2) return '❌ Usage: /limit set <amount>';
                    const newLimit = ethers.parseEther(args[1]);
                    const walletContract = new ethers.Contract(walletAddress, WALLET_ABI, wallet);
                    const tx = await walletContract.updateSpendingLimit(newLimit);
                    await tx.wait();
                    return `✅ Limit: ${args[1]} KITE`;
                }
                const walletContract = new ethers.Contract(walletAddress, WALLET_ABI, provider);
                const limit = await walletContract.spendingLimit();
                return `💰 Limit: *${ethers.formatEther(limit)} KITE*`;
            }
            case '/send': {
                if (args.length < 2) return '❌ Usage: /send <addr> <amount>';
                const toAddress = args[0];
                const amount = ethers.parseEther(args[1]);
                const walletAddress = await factory.getWalletAddress(userAddress, userAddress);
                if (walletAddress === ethers.ZeroAddress) return '❌ No wallet.';
                
                const walletContract = new ethers.Contract(walletAddress, WALLET_ABI, wallet);
                const data = ethers.AbiCoder.defaultAbiCoder.encode(
                    ['address', 'uint256', 'bytes'],
                    [toAddress, amount, '0x']
                );
                const tx = await walletContract.execute(data);
                await tx.wait();
                return `✅ Sent ${args[1]} KITE → \`${toAddress}\``;
            }
            case '/help':
                return `📖 *Kite Wallet*

/create - New wallet
/wallet - Your address  
/balance - Check balance
/session add <addr> <limit> - Add key
/limit set <amount> - Set limit
/send <addr> <amount> - Send`;
            default:
                return `❌ ${command}\nUse /help`;
        }
    } catch (error) {
        return `❌ Error: ${error.message}`;
    }
}

async function getUpdates(offset) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'api.telegram.org',
            path: `/bot${CONFIG.botToken}/getUpdates?timeout=60${offset ? '&offset=' + offset : ''}`,
            method: 'GET'
        };
        
        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(body)); } catch (e) { reject(e); }
            });
        });
        req.on('error', reject);
        req.end();
    });
}

async function processUpdates() {
    let offset = 0;
    
    while (true) {
        try {
            const updates = await getUpdates(offset);
            
            if (updates.ok && updates.result.length > 0) {
                for (const update of updates.result) {
                    offset = update.update_id + 1;
                    
                    if (update.message && update.message.text) {
                        const chatId = update.message.chat.id;
                        const text = update.message.text;
                        const userId = update.message.from.id.toString();
                        
                        console.log(`${userId}: ${text}`);
                        const response = await handleMessage(text, userId);
                        await sendMessage(chatId, response);
                    }
                }
            }
        } catch (error) {
            console.error('Error:', error.message);
            await new Promise(r => setTimeout(r, 5000));
        }
    }
}

processUpdates();
