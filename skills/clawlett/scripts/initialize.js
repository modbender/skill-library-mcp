#!/usr/bin/env node

/**
 * Initialize Claw Wallet (Fully Autonomous)
 *
 * Agent does everything autonomously, then transfers ownership to human.
 *
 * Steps:
 * 1. Generate agent keypair (or use existing)
 * 2. Deploy Safe with agent as initial owner
 * 3. Deploy Zodiac Roles module
 * 4. Configure everything via MultiSend (enable module + permissions)
 * 5. Register on ERC-8004 Identity Registry
 * 6. Register with backend API
 *
 * Usage: node initialize.js --owner 0x123...
 */

import { ethers } from 'ethers'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const DEFAULT_RPC_URL = 'https://mainnet.base.org'
const CHAIN_ID = 8453
const API_BASE_URL = process.env.WALLET_API_URL || 'https://trenches.bid'
const VERCEL_BYPASS = process.env.VERCEL_PROTECTION_BYPASS || ''

// Wrap global fetch to inject Vercel protection bypass header when configured
const _origFetch = globalThis.fetch
if (VERCEL_BYPASS) {
    globalThis.fetch = (url, opts = {}) => {
        opts.headers = { ...opts.headers, 'x-vercel-protection-bypass': VERCEL_BYPASS }
        return _origFetch(url, opts)
    }
}

// Contract addresses
const CONTRACTS = {
    SafeProxyFactory: '0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2',
    SafeSingletonL2: '0x3E5c63644E683549055b9Be8653de26E0B4CD36E',
    CompatibilityFallbackHandler: '0xf48f2B2d2a534e402487b3ee7C18c33Aec0Fe5e4',
    MultiSend: '0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761',
    RolesSingleton: '0x9646fDAD06d3e24444381f44362a3B0eB343D337',
    ModuleProxyFactory: '0x000000000000aDdB49795b0f9bA5BC298cDda236',
    AeroUniversalRouter: '0x6Df1c91424F79E40E33B1A48F0687B666bE71075',
    ZodiacHelpers: '0x49E596467D5e3C876Eece999d88a2135596bde18',
    KyberSwapRouter: '0x6131B5fae19EA4f9D964eAc0408E4408b66337b5',
    IdentityRegistry: '0x8004A169FB4a3325136EB29fA0ceB6D2e539a432',
    CNS: '0x299319e0BC8d67e11AD8b17D4d5002033874De3a',
}

// ABIs
const SAFE_FACTORY_ABI = [
    'function createProxyWithNonce(address singleton, bytes initializer, uint256 saltNonce) returns (address)',
]

const SAFE_ABI = [
    'function setup(address[] owners, uint256 threshold, address to, bytes data, address fallbackHandler, address paymentToken, uint256 payment, address paymentReceiver)',
    'function enableModule(address module)',
    'function execTransaction(address to, uint256 value, bytes data, uint8 operation, uint256 safeTxGas, uint256 baseGas, uint256 gasPrice, address gasToken, address refundReceiver, bytes signatures) returns (bool)',
    'function getOwners() view returns (address[])',
    'function isModuleEnabled(address module) view returns (bool)',
    'function nonce() view returns (uint256)',
    'function addOwnerWithThreshold(address owner, uint256 _threshold)',
    'function removeOwner(address prevOwner, address owner, uint256 _threshold)',
]

const MODULE_FACTORY_ABI = [
    'function deployModule(address masterCopy, bytes initializer, uint256 saltNonce) returns (address)',
]

const ROLES_ABI = [
    'function setUp(bytes initParams)',
    'function setDefaultRole(address module, bytes32 roleKey)',
    'function assignRoles(address module, bytes32[] roleKeys, bool[] memberOf)',
    'function scopeTarget(bytes32 roleKey, address targetAddress)',
    'function allowTarget(bytes32 roleKey, address targetAddress, uint8 options)',
    'function owner() view returns (address)',
]

const MULTISEND_ABI = [
    'function multiSend(bytes transactions) payable',
]

const IDENTITY_REGISTRY_ABI = [
    'function register(string agentURI) returns (uint256 agentId)',
    'function transferFrom(address from, address to, uint256 tokenId)',
    'function ownerOf(uint256 tokenId) view returns (address)',
    'event Registered(uint256 indexed agentId, string agentURI, address indexed owner)',
]

const CNS_ABI = [
    {
        type: 'function', name: 'register', stateMutability: 'payable',
        inputs: [{
            name: '_signature', type: 'tuple',
            components: [
                { name: 'signature', type: 'bytes' },
                { name: 'data', type: 'bytes' },
                { name: 'expiresAt', type: 'uint256' },
            ],
        }],
        outputs: [{ name: 'tokenId', type: 'uint256' }],
    },
    'function fee() view returns (uint256)',
    'function isNameAvailable(string _name) view returns (bool)',
    'function balanceOf(address owner) view returns (uint256)',
    'function tokenOfOwnerByIndex(address owner, uint256 index) view returns (uint256)',
    'function tokenName(uint256 _tokenId) view returns (string)',
    'event NameRegistered(address indexed owner, uint256 indexed tokenId, string name)',
]

// Role key for wallet operations
const ROLE_KEY = ethers.keccak256(ethers.toUtf8Bytes('WalletSwapper'))

// Execution options for Roles
const ExecutionOptions = {
    None: 0,
    Send: 1,
    DelegateCall: 2,
    Both: 3,
}

// Initialization steps
const STEPS = {
    AGENT_CREATED: 'agent_created',
    SAFE_DEPLOYED: 'safe_deployed',
    ROLES_DEPLOYED: 'roles_deployed',
    CONFIGURED: 'configured',
    ERC8004_REGISTERED: 'erc8004_registered',
    COMPLETE: 'complete',
}

function parseArgs() {
    const args = process.argv.slice(2)
    const result = {
        owner: null,
        name: null,
        configDir: process.env.WALLET_CONFIG_DIR || path.join(__dirname, '..', 'config'),
        rpc: process.env.BASE_RPC_URL || DEFAULT_RPC_URL,
    }

    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--owner':
            case '-o':
                result.owner = args[++i]
                break
            case '--name':
            case '-n':
                result.name = args[++i]
                break
            case '--config-dir':
            case '-c':
                result.configDir = args[++i]
                break
            case '--rpc':
            case '-r':
                result.rpc = args[++i]
                break
            case '--help':
            case '-h':
                printHelp()
                process.exit(0)
        }
    }

    return result
}

function printHelp() {
    console.log(`
Usage: node initialize.js --owner <OWNER_ADDRESS> [--name <AGENT_NAME>]

Arguments:
  --owner, -o      Owner wallet address (will be sole Safe owner after setup)
  --name, -n       Unique agent name for CNS (optional, registers on Clawlett Name Service)
  --config-dir, -c Config directory (default: ../config)
  --rpc, -r        RPC URL (default: ${DEFAULT_RPC_URL})

This script is idempotent - run it multiple times to continue from where it left off.
`)
}

function loadState(configDir) {
    const statePath = path.join(configDir, 'init-state.json')
    if (fs.existsSync(statePath)) {
        return JSON.parse(fs.readFileSync(statePath, 'utf8'))
    }
    return { step: null }
}

function saveState(configDir, state) {
    const statePath = path.join(configDir, 'init-state.json')
    fs.writeFileSync(statePath, JSON.stringify(state, null, 2))
}

function clearState(configDir) {
    const statePath = path.join(configDir, 'init-state.json')
    if (fs.existsSync(statePath)) {
        fs.unlinkSync(statePath)
    }
}

// Backend registration functions
async function checkExistingAgent(wallet) {
    try {
        const url = `${API_BASE_URL}/api/skill/agent?wallet=${wallet}&chainId=${CHAIN_ID}`
        const response = await fetch(url)
        if (response.ok) {
            const data = await response.json()
            // If needsRegistration is true, agent doesn't exist yet
            if (data.needsRegistration) {
                return null
            }
            return data
        }
    } catch (e) {
        // Ignore - agent not found or API unavailable
    }
    return null
}

async function getRegistrationChallenge(wallet) {
    const url = `${API_BASE_URL}/api/skill/agent?wallet=${wallet}&chainId=${CHAIN_ID}`
    const response = await fetch(url)
    const data = await response.json()

    if (!response.ok) {
        throw new Error(data.error || 'Failed to get registration challenge')
    }

    if (!data.needsRegistration || !data.jwt) {
        throw new Error('Agent already registered')
    }

    return data.jwt
}

// Decode JWT to get the message (without verification - server will verify)
function getMessageFromJwt(jwt) {
    const parts = jwt.split('.')
    if (parts.length !== 3) throw new Error('Invalid JWT')
    const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString())
    return payload.message
}

async function registerAgent(agentWallet, jwt, agentData) {
    // Sign the challenge message
    const message = getMessageFromJwt(jwt)
    const signature = await agentWallet.signMessage(message)

    const url = `${API_BASE_URL}/api/skill/agent`
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            jwt,
            signature,
            wallet: agentWallet.address,
            ...agentData,
        }),
    })

    const result = await response.json()
    if (!response.ok) {
        throw new Error(result.error || 'Failed to register agent')
    }

    // Extract cookies from response (same as web auth)
    const cookies = response.headers.getSetCookie?.() || []
    const cookieString = cookies.map(c => c.split(';')[0]).join('; ')

    return { ...result, cookies: cookieString }
}

// Backend auth — GET challenge, sign, POST to get session cookies
async function authenticateAgent(agentWallet) {
    // Step 1: Get challenge
    const challengeRes = await fetch(
        `${API_BASE_URL}/api/auth/wallet?wallet=${agentWallet.address.toLowerCase()}`
    )
    const challengeData = await challengeRes.json()
    if (!challengeRes.ok) {
        throw new Error(challengeData.error || 'Failed to get auth challenge')
    }

    // Step 2: Sign challenge and authenticate
    const message = challengeData.message || getMessageFromJwt(challengeData.jwt)
    const signature = await agentWallet.signMessage(message)

    const authRes = await fetch(`${API_BASE_URL}/api/auth/wallet`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            wallet: agentWallet.address.toLowerCase(),
            signature,
            jwt: challengeData.jwt,
        }),
    })

    const authData = await authRes.json()
    if (!authRes.ok) {
        throw new Error(authData.error || 'Authentication failed')
    }

    const cookies = authRes.headers.getSetCookie?.() || []
    const cookieString = cookies.map(c => c.split(';')[0]).join('; ')
    return cookieString
}

// CNS — request signature from backend, then register on-chain
async function getCnsSignature(cookies, name) {
    const res = await fetch(`${API_BASE_URL}/api/cns/signature`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Cookie': cookies,
        },
        body: JSON.stringify({ name, chainId: String(CHAIN_ID) }),
    })

    const data = await res.json()
    if (!res.ok) {
        throw new Error(data.error || 'Failed to get CNS signature')
    }

    return data
}

function saveConfig(configDir, config) {
    const configPath = path.join(configDir, 'wallet.json')
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2))
}

// MultiSend encoding helpers
function encodeMultiSendTx(operation, to, value, data) {
    const dataBytes = ethers.getBytes(data)
    return ethers.solidityPacked(
        ['uint8', 'address', 'uint256', 'uint256', 'bytes'],
        [operation, to, value, dataBytes.length, dataBytes]
    )
}

function encodeMultiSend(transactions) {
    const encoded = ethers.concat(
        transactions.map(tx => encodeMultiSendTx(tx.operation || 0, tx.to, tx.value || 0n, tx.data))
    )
    const multiSendInterface = new ethers.Interface(MULTISEND_ABI)
    return multiSendInterface.encodeFunctionData('multiSend', [encoded])
}

// Execute Safe transaction as owner
async function execSafeTransaction(safe, to, value, data, operation, signer) {
    const safeTxGas = 0
    const baseGas = 0
    const gasPrice = 0
    const gasToken = ethers.ZeroAddress
    const refundReceiver = ethers.ZeroAddress

    // Pre-approved signature for owner
    const signature = ethers.concat([
        ethers.zeroPadValue(signer.address, 32),
        ethers.zeroPadValue('0x', 32),
        '0x01'
    ])

    const tx = await safe.execTransaction(
        to, value, data, operation,
        safeTxGas, baseGas, gasPrice, gasToken, refundReceiver,
        signature
    )

    return tx.wait(3) // Wait for 3 confirmations
}

async function main() {
    const args = parseArgs()

    if (!args.owner) {
        console.error('Error: --owner is required')
        printHelp()
        process.exit(1)
    }

    const owner = ethers.getAddress(args.owner)
    const agentName = args.name ? args.name.toUpperCase() : null
    const provider = new ethers.JsonRpcProvider(args.rpc)

    console.log('\n========================================')
    console.log('     Claw Wallet Initialization')
    console.log('========================================\n')
    console.log(`Owner: ${owner}`)
    console.log(`Chain: Base (${CHAIN_ID})`)

    // Ensure config directory exists
    if (!fs.existsSync(args.configDir)) {
        fs.mkdirSync(args.configDir, { recursive: true })
    }

    // Load state for resume capability
    let state = loadState(args.configDir)

    // Step 1: Agent keypair
    console.log('\n--- Step 1: Agent Keypair ---')
    const agentPkPath = path.join(args.configDir, 'agent.pk')
    let agentWallet

    if (fs.existsSync(agentPkPath)) {
        let pk = fs.readFileSync(agentPkPath, 'utf8').trim()
        if (!pk.startsWith('0x')) pk = '0x' + pk
        agentWallet = new ethers.Wallet(pk, provider)
        console.log(`Agent exists: ${agentWallet.address}`)
    } else {
        agentWallet = ethers.Wallet.createRandom().connect(provider)
        fs.writeFileSync(agentPkPath, agentWallet.privateKey.slice(2), { mode: 0o600 })
        console.log(`Agent created: ${agentWallet.address}`)
        state = { step: STEPS.AGENT_CREATED }
        saveState(args.configDir, state)
    }

    const agentBalance = await provider.getBalance(agentWallet.address)
    console.log(`Balance: ${ethers.formatEther(agentBalance)} ETH`)

    if (agentBalance < ethers.parseEther('0.000005')) {
        console.log(`\n⚠️  Agent needs gas for deployment.`)
        console.log(`   Send at least 0.00002 ETH to: ${agentWallet.address}`)
        console.log(`   Then run this script again.\n`)
        process.exit(0)
    }

    // Generate deterministic salt from owner + agent
    const saltNonce = BigInt(ethers.keccak256(
        ethers.solidityPacked(['address', 'address'], [owner, agentWallet.address])
    ))

    let safeAddress = state.safe
    let rolesAddress = state.roles

    // Step 2: Deploy Safe (with agent as initial owner)
    if (!safeAddress || state.step === STEPS.AGENT_CREATED) {
        console.log('\n--- Step 2: Deploy Safe ---')
        console.log('   Deploying Safe with agent as initial owner...')

        const safeFactory = new ethers.Contract(CONTRACTS.SafeProxyFactory, SAFE_FACTORY_ABI, agentWallet)
        const safeInterface = new ethers.Interface(SAFE_ABI)

        // Agent is initial owner (will transfer to human later)
        const safeInitializer = safeInterface.encodeFunctionData('setup', [
            [agentWallet.address],  // Agent as initial owner
            1,
            ethers.ZeroAddress,
            '0x',
            CONTRACTS.CompatibilityFallbackHandler,
            ethers.ZeroAddress,
            0,
            ethers.ZeroAddress,
        ])

        const safeTx = await safeFactory.createProxyWithNonce(
            CONTRACTS.SafeSingletonL2,
            safeInitializer,
            saltNonce
        )
        console.log(`   Transaction: ${safeTx.hash}`)
        console.log('   Waiting for 3 confirmations...')
        const safeReceipt = await safeTx.wait(3)

        const proxyCreationTopic = ethers.id('ProxyCreation(address,address)')
        const safeCreationEvent = safeReceipt.logs.find(
            log => log.topics[0] === proxyCreationTopic
        )
        // Address can be in topics[1] or in data depending on event definition
        if (safeCreationEvent.topics.length > 1) {
            safeAddress = ethers.getAddress('0x' + safeCreationEvent.topics[1].slice(-40))
        } else {
            const decoded = ethers.AbiCoder.defaultAbiCoder().decode(['address', 'address'], safeCreationEvent.data)
            safeAddress = decoded[0]
        }
        console.log(`   Safe deployed: ${safeAddress}`)

        state = {
            ...state,
            step: STEPS.SAFE_DEPLOYED,
            safe: safeAddress,
            safeTxHash: safeReceipt.hash,
            safeBlockNumber: safeReceipt.blockNumber,
            safeBlockTime: new Date().toISOString(),
        }
        saveState(args.configDir, state)
    } else {
        console.log(`\n--- Step 2: Safe ---`)
        console.log(`   Already deployed: ${safeAddress}`)
    }

    const safe = new ethers.Contract(safeAddress, SAFE_ABI, agentWallet)

    // Step 3: Deploy Roles
    if (!rolesAddress || state.step === STEPS.SAFE_DEPLOYED) {
        console.log('\n--- Step 3: Deploy Zodiac Roles ---')
        const moduleFactory = new ethers.Contract(CONTRACTS.ModuleProxyFactory, MODULE_FACTORY_ABI, agentWallet)
        const rolesInterface = new ethers.Interface(ROLES_ABI)

        const rolesInitializer = rolesInterface.encodeFunctionData('setUp', [
            ethers.AbiCoder.defaultAbiCoder().encode(
                ['address', 'address', 'address'],
                [safeAddress, safeAddress, safeAddress]
            )
        ])

        const rolesTx = await moduleFactory.deployModule(
            CONTRACTS.RolesSingleton,
            rolesInitializer,
            saltNonce + 1n
        )
        console.log(`   Transaction: ${rolesTx.hash}`)
        console.log('   Waiting for 3 confirmations...')
        const rolesReceipt = await rolesTx.wait(3)

        const rolesEvent = rolesReceipt.logs.find(
            log => log.topics[0] === ethers.id('ModuleProxyCreation(address,address)')
        )
        rolesAddress = ethers.getAddress('0x' + rolesEvent.topics[1].slice(26))
        console.log(`   Roles deployed: ${rolesAddress}`)

        state = { ...state, step: STEPS.ROLES_DEPLOYED, roles: rolesAddress }
        saveState(args.configDir, state)
    } else {
        console.log(`\n--- Step 3: Zodiac Roles ---`)
        console.log(`   Already deployed: ${rolesAddress}`)
    }

    // Step 4: Configure Roles via MultiSend (no ownership transfer yet)
    const isModuleEnabled = await safe.isModuleEnabled(rolesAddress)

    if (!isModuleEnabled || state.step === STEPS.ROLES_DEPLOYED) {
        console.log('\n--- Step 4: Configure Roles ---')
        console.log('   Batching configuration via MultiSend...')

        const safeInterface = new ethers.Interface(SAFE_ABI)
        const rolesInterface = new ethers.Interface(ROLES_ABI)

        const transactions = []

        // Enable module on Safe (if not already)
        if (!isModuleEnabled) {
            console.log('   - enableModule(roles)')
            transactions.push({
                to: safeAddress,
                data: safeInterface.encodeFunctionData('enableModule', [rolesAddress]),
            })
        }

        // Scope and allow Aerodrome Universal Router
        console.log('   - scopeTarget(AeroUniversalRouter)')
        transactions.push({
            to: rolesAddress,
            data: rolesInterface.encodeFunctionData('scopeTarget', [ROLE_KEY, CONTRACTS.AeroUniversalRouter]),
        })

        console.log('   - allowTarget(AeroUniversalRouter, Send)')
        transactions.push({
            to: rolesAddress,
            data: rolesInterface.encodeFunctionData('allowTarget', [ROLE_KEY, CONTRACTS.AeroUniversalRouter, ExecutionOptions.Send]),
        })

        // Scope and allow ZodiacHelpers (with DelegateCall)
        console.log('   - scopeTarget(ZodiacHelpers)')
        transactions.push({
            to: rolesAddress,
            data: rolesInterface.encodeFunctionData('scopeTarget', [ROLE_KEY, CONTRACTS.ZodiacHelpers]),
        })

        console.log('   - allowTarget(ZodiacHelpers, Both)')
        transactions.push({
            to: rolesAddress,
            data: rolesInterface.encodeFunctionData('allowTarget', [ROLE_KEY, CONTRACTS.ZodiacHelpers, ExecutionOptions.Both]),
        })

        // Assign role to agent
        console.log('   - assignRoles(agent, WalletSwapper)')
        transactions.push({
            to: rolesAddress,
            data: rolesInterface.encodeFunctionData('assignRoles', [agentWallet.address, [ROLE_KEY], [true]]),
        })

        // Set default role for agent
        console.log('   - setDefaultRole(agent, WalletSwapper)')
        transactions.push({
            to: rolesAddress,
            data: rolesInterface.encodeFunctionData('setDefaultRole', [agentWallet.address, ROLE_KEY]),
        })

        console.log(`\n   Executing ${transactions.length} operations in single MultiSend...`)
        const multiSendData = encodeMultiSend(transactions)

        const receipt = await execSafeTransaction(safe, CONTRACTS.MultiSend, 0n, multiSendData, 1, agentWallet)
        console.log(`   Transaction: ${receipt.hash}`)
        console.log('   Confirmed (3 blocks)')
        console.log('   Configuration complete!')

        state = { ...state, step: STEPS.CONFIGURED }
        saveState(args.configDir, state)
    } else {
        console.log('\n--- Step 4: Configuration ---')
        console.log('   Already configured!')
    }

    // Step 5: Register with backend
    let registration = state.registration
    if (!registration) {
        console.log('\n--- Step 5: Register with Backend ---')
        const existingAgent = await checkExistingAgent(agentWallet.address.toLowerCase())
        if (existingAgent && !existingAgent.error && !existingAgent.needsRegistration) {
            console.log('   Already registered!')
            registration = existingAgent
        } else {
            try {
                const jwt = await getRegistrationChallenge(agentWallet.address.toLowerCase())
                const block = await provider.getBlock('latest')
                registration = await registerAgent(agentWallet, jwt, {
                    owner,
                    safe: safeAddress,
                    roles: rolesAddress,
                    approvalHelper: CONTRACTS.ZodiacHelpers,
                    roleKey: ROLE_KEY,
                    chainId: CHAIN_ID,
                    evt_tx_hash: state.safeTxHash || '',
                    evt_block_number: state.safeBlockNumber?.toString() || block.number.toString(),
                    evt_block_time: state.safeBlockTime || new Date(Number(block.timestamp) * 1000).toISOString(),
                })
                console.log(`   Registered! Agent ID: ${registration.id || 'N/A'}`)
                if (registration.referralCode) {
                    console.log(`   Referral code: ${registration.referralCode}`)
                }
                state = { ...state, registration }
                saveState(args.configDir, state)
            } catch (error) {
                console.log(`   Warning: Registration failed: ${error.message}`)
                console.log('   Continuing setup...')
            }
        }
    } else {
        console.log('\n--- Step 5: Backend ---')
        console.log('   Already registered!')
    }

    // Step 6: Register CNS name (via Safe — backend signs with account=safe)
    let cnsTokenId = state.cnsTokenId
    if (!agentName) {
        console.log('\n--- Step 6: CNS Name ---')
        console.log('   Skipped (--name not provided)')
    } else if (!cnsTokenId) {
        console.log('\n--- Step 6: Register CNS Name ---')
        const cns = new ethers.Contract(CONTRACTS.CNS, CNS_ABI, provider)

        // Check if Safe already owns a CNS token (from interrupted previous run)
        const safeCnsBalance = await cns.balanceOf(safeAddress)
        if (safeCnsBalance > 0n) {
            const existingTokenId = await cns.tokenOfOwnerByIndex(safeAddress, 0)
            const existingName = await cns.tokenName(existingTokenId)
            cnsTokenId = Number(existingTokenId)
            console.log(`   Safe already owns CNS name: ${existingName} (Token ID: ${cnsTokenId})`)
            state = { ...state, cnsTokenId }
            saveState(args.configDir, state)
        } else {
            // Check if name is available on-chain
            const available = await cns.isNameAvailable(agentName)
            if (!available) {
                console.error(`   Error: Name "${agentName}" is already taken.`)
                process.exit(1)
            }

            const fee = await cns.fee()
            console.log(`   Name: ${agentName}`)
            console.log(`   Fee: ${ethers.formatEther(fee)} ETH`)

            try {
                console.log('   Authenticating with backend...')
                const cookies = await authenticateAgent(agentWallet)

                console.log('   Requesting CNS signature...')
                const sigResponse = await getCnsSignature(cookies, agentName)

                // Backend wraps in { signature: { signature, data, expiresAt } }
                const sig = sigResponse.signature || sigResponse
                if (!sig.signature || !sig.data || sig.expiresAt === undefined) {
                    console.log('   Backend response:', JSON.stringify(sigResponse, null, 2))
                    throw new Error('Backend returned incomplete signature data')
                }

                console.log(`   Signature received (expires: ${sig.expiresAt})`)
                console.log('   Registering on-chain via Safe...')

                // Encode register() call — must go through Safe since backend
                // signs with account=safe address (msg.sender must be Safe)
                const cnsInterface = new ethers.Interface(CNS_ABI)
                const registerData = cnsInterface.encodeFunctionData('register', [
                    [sig.signature, sig.data, BigInt(sig.expiresAt)],
                ])

                const receipt = await execSafeTransaction(
                    safe, CONTRACTS.CNS, fee, registerData, 0, agentWallet
                )
                console.log(`   Transaction: ${receipt.hash}`)

                const nameRegTopic = ethers.id('NameRegistered(address,uint256,string)')
                const nameRegEvent = receipt.logs.find(log => log.topics[0] === nameRegTopic)
                if (nameRegEvent) {
                    cnsTokenId = Number(nameRegEvent.topics[2])
                }

                console.log(`   CNS registered! Name: ${agentName}, Token ID: ${cnsTokenId || 'N/A'}`)
                state = { ...state, cnsTokenId }
                saveState(args.configDir, state)
            } catch (error) {
                console.log(`   Warning: CNS registration failed: ${error.message}`)
                console.log('   Continuing setup...')
            }
        }
    } else {
        console.log('\n--- Step 6: CNS Name ---')
        console.log(`   Already registered! Token ID: ${cnsTokenId}`)
    }

    // Step 7: Transfer ownership (add human owner, remove agent)
    const currentOwners = await safe.getOwners()
    const ownerIsHuman = currentOwners.some(o => o.toLowerCase() === owner.toLowerCase())
    const agentIsOwner = currentOwners.some(o => o.toLowerCase() === agentWallet.address.toLowerCase())

    if (agentIsOwner) {
        console.log('\n--- Step 7: Transfer Ownership ---')
        const safeInterface = new ethers.Interface(SAFE_ABI)
        const transactions = []

        if (!ownerIsHuman) {
            console.log(`   - addOwnerWithThreshold(${owner.slice(0, 10)}...)`)
            transactions.push({
                to: safeAddress,
                data: safeInterface.encodeFunctionData('addOwnerWithThreshold', [owner, 1]),
            })
        }

        console.log(`   - removeOwner(${agentWallet.address.slice(0, 10)}...)`)
        // prevOwner is the owner that points to the agent in the linked list
        // After addOwner, the new owner is at the front, so prevOwner = owner
        const prevOwner = ownerIsHuman ? owner : owner
        transactions.push({
            to: safeAddress,
            data: safeInterface.encodeFunctionData('removeOwner', [prevOwner, agentWallet.address, 1]),
        })

        const multiSendData = encodeMultiSend(transactions)
        const receipt = await execSafeTransaction(safe, CONTRACTS.MultiSend, 0n, multiSendData, 1, agentWallet)
        console.log(`   Transaction: ${receipt.hash}`)
        console.log('   Confirmed (3 blocks)')
        console.log('   Ownership transferred!')
    } else {
        console.log('\n--- Step 7: Ownership ---')
        console.log('   Already transferred!')
    }

    // Verify ownership
    const finalOwners = await safe.getOwners()
    if (finalOwners.length !== 1 || finalOwners[0].toLowerCase() !== owner.toLowerCase()) {
        console.error(`\n   Warning: Unexpected owners: ${finalOwners.join(', ')}`)
    }

    // Step 8: Register on ERC-8004 Identity Registry
    // Agent mints the identity NFT, then transfers it to the Safe
    let erc8004AgentId = state.erc8004AgentId
    if (state.step !== STEPS.ERC8004_REGISTERED && state.step !== STEPS.COMPLETE) {
        console.log('\n--- Step 8: Register on ERC-8004 ---')

        const identityRegistry = new ethers.Contract(
            CONTRACTS.IdentityRegistry,
            IDENTITY_REGISTRY_ABI,
            agentWallet
        )

        // Phase 1: Mint identity NFT (if not already done)
        if (!erc8004AgentId) {
            const agentRegistration = {
                type: 'https://eips.ethereum.org/EIPS/eip-8004#registration-v1',
                name: 'Clawlett',
                description: `Autonomous MEV-protected token swap agent on Base. Safe: ${safeAddress}`,
                image: '',
                services: [
                    {
                        name: 'web',
                        endpoint: API_BASE_URL,
                    },
                ],
                x402Support: false,
                active: true,
                registrations: [],
            }

            const agentURI = 'data:application/json;base64,' + Buffer.from(JSON.stringify(agentRegistration)).toString('base64')

            console.log('   Registering agent identity on-chain...')
            const tx = await identityRegistry.register(agentURI)
            console.log(`   Transaction: ${tx.hash}`)
            console.log('   Waiting for 3 confirmations...')
            const receipt = await tx.wait(3)

            // Parse Registered event to get agentId
            const registeredTopic = ethers.id('Registered(uint256,string,address)')
            const registeredEvent = receipt.logs.find(log => log.topics[0] === registeredTopic)
            if (registeredEvent) {
                erc8004AgentId = Number(registeredEvent.topics[1])
            } else {
                // Fallback: parse from ERC-721 Transfer event
                const transferTopic = ethers.id('Transfer(address,address,uint256)')
                const transferEvent = receipt.logs.find(log => log.topics[0] === transferTopic)
                if (transferEvent) {
                    erc8004AgentId = Number(transferEvent.topics[3])
                }
            }

            if (!erc8004AgentId) {
                console.log('   Warning: Could not parse agentId from events, skipping.')
                state = { ...state, step: STEPS.ERC8004_REGISTERED }
                saveState(args.configDir, state)
            } else {
                console.log(`   Minted identity NFT #${erc8004AgentId}`)
                // Save immediately so we can resume transfer if interrupted
                state = { ...state, erc8004AgentId }
                saveState(args.configDir, state)
            }
        }

        // Phase 2: Transfer NFT to Safe (if agent still owns it)
        if (erc8004AgentId) {
            const nftOwner = await identityRegistry.ownerOf(erc8004AgentId)
            if (nftOwner.toLowerCase() === agentWallet.address.toLowerCase()) {
                console.log(`   Transferring identity NFT to Safe...`)
                const tx = await identityRegistry.transferFrom(agentWallet.address, safeAddress, erc8004AgentId)
                console.log(`   Transaction: ${tx.hash}`)
                console.log('   Waiting for 3 confirmations...')
                await tx.wait(3)
                console.log(`   Safe now owns ERC-8004 ID: ${erc8004AgentId}`)
            } else if (nftOwner.toLowerCase() === safeAddress.toLowerCase()) {
                console.log(`   Safe already owns ERC-8004 ID: ${erc8004AgentId}`)
            } else {
                console.log(`   Warning: NFT #${erc8004AgentId} owned by unexpected address: ${nftOwner}`)
            }
        }

        state = { ...state, step: STEPS.ERC8004_REGISTERED, erc8004AgentId }
        saveState(args.configDir, state)
    } else {
        console.log('\n--- Step 8: ERC-8004 Identity ---')
        if (erc8004AgentId) {
            console.log(`   Already registered! ID: ${erc8004AgentId}`)
        } else {
            console.log('   Already registered!')
        }
    }

    // Save final config
    const config = {
        chainId: CHAIN_ID,
        owner,
        agent: agentWallet.address,
        safe: safeAddress,
        roles: rolesAddress,
        roleKey: ROLE_KEY,
        name: agentName || null,
        cnsTokenId: cnsTokenId || null,
        erc8004AgentId: erc8004AgentId || null,
        contracts: CONTRACTS,
        createdAt: new Date().toISOString(),
        cookies: registration?.cookies,
    }
    saveConfig(args.configDir, config)
    clearState(args.configDir)

    // Summary
    console.log('\n========================================')
    console.log('         Setup Complete!')
    console.log('========================================')
    console.log(`\nSafe:   ${safeAddress}`)
    console.log(`Roles:  ${rolesAddress}`)
    console.log(`Agent:  ${agentWallet.address}`)
    console.log(`Owner:  ${owner}`)
    console.log(`\nFund your Safe to start trading:`)
    console.log(`   ${safeAddress}`)
    console.log(`\nUsage:`)
    console.log(`   node balance.js --all`)
    console.log(`   node swap.js --from ETH --to USDC --amount 0.1`)
    console.log('')
}

main().catch(error => {
    console.error(`\n❌ Error: ${error.message}`)
    process.exit(1)
})
