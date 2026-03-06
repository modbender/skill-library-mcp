#!/usr/bin/env node

import * as path from 'path'
import { generateMnemonic, getAllAddress, getPublicKey, getPath, getUtxos, getCredential, DEFAULT_PATH, parseAddressIndexFromPath, buildPathFromIndex } from './wallet'
import { getMVCRewards, getMVCInitRewards, sleep, getUserInfoByAddressByMs } from './api'
import { createPin, CreatePinParams } from './metaid'
import { createBuzz } from './buzz'
import {
  readAccountFile,
  writeAccountFile,
  ensureAccountFile,
  findAccountByKeyword,
  logError,
  extractUsername,
  extractBuzzContent,
  extractWalletPathFromPrompt,
  shouldCreateWallet,
  extractProfileFromPrompt,
  applyProfileToAccount,
  Account,
} from './utils'

async function main() {
  const userPrompt = process.argv[2] || ''
  
  if (!userPrompt) {
    console.error('Usage: ts-node main.ts "<user_prompt>"')
    process.exit(1)
  }

  try {
    // Step 1: Check if we need to create a new wallet or use existing
    const needCreateWallet = shouldCreateWallet(userPrompt)
    ensureAccountFile()
    let accountData = readAccountFile()
    let currentAccount: Account | null = null

    if (needCreateWallet || accountData.accountList.length === 0) {
      // Create new wallet（可从 userPrompt 指定 path / index，未指定则使用默认）
      console.log('🔐 Creating new wallet...')
      const mnemonic = await generateMnemonic()
      const walletPathConfig = extractWalletPathFromPrompt(userPrompt)

      let path: string
      let newWalletAddressIndex: number

      if (walletPathConfig?.path) {
        // 用户显式给出完整 path
        path = walletPathConfig.path
        newWalletAddressIndex = parseAddressIndexFromPath(path)
      } else if (walletPathConfig?.index != null) {
        // 用户只给出索引：例如「路径1」-> m/44'/10001'/0'/0/1
        newWalletAddressIndex = walletPathConfig.index
        path = buildPathFromIndex(newWalletAddressIndex)
      } else {
        // 未指定时回退默认 path（account.json 无 account 时也会用 DEFAULT_PATH）
        path = getPath({ defaultPath: DEFAULT_PATH })
        newWalletAddressIndex = parseAddressIndexFromPath(path)
      }

      const addresses = await getAllAddress(mnemonic, { addressIndex: newWalletAddressIndex })
      const publicKey = await getPublicKey('mvc', mnemonic, { addressIndex: newWalletAddressIndex })

      const newAccount: Account = {
        mnemonic,
        mvcAddress: addresses.mvcAddress,
        btcAddress: addresses.btcAddress,
        dogeAddress: addresses.dogeAddress,
        publicKey,
        userName: '',
        path
      }

      // Unshift to front of array
      accountData.accountList.unshift(newAccount)
      writeAccountFile(accountData)
      currentAccount = newAccount
      console.log('✅ Wallet created successfully')
    } else {
      // Select existing wallet
      const username = extractUsername(userPrompt)
      if (username) {
        currentAccount = findAccountByKeyword(username, accountData)
      }
      
      if (!currentAccount) {
        // Use first account as default
        currentAccount = accountData.accountList[0]
      }
      console.log(`📝 Using wallet: ${currentAccount.mvcAddress}`)
    }

    if (!currentAccount) {
      throw new Error('No account available')
    }

    // Step 2: Extract username and buzz content from prompt
    const username = extractUsername(userPrompt)
    if (!username && needCreateWallet) {
      throw new Error('Username is required. Please provide a username in your prompt (e.g., "名字叫\'Sunny\'")')
    }

    const buzzContent = extractBuzzContent(userPrompt)

    // Step 3: Register MetaID if userName is empty
    if (!currentAccount.userName && username) {
      console.log('📝 Registering MetaID account...')
      
      // Check if user has UTXOs
      const utxos = await getUtxos('mvc', currentAccount.mnemonic, {
        addressIndex: parseAddressIndexFromPath(currentAccount.path),
      })
      
      if (utxos.length === 0) {
        // New user, claim gas subsidy
        console.log('💰 Claiming gas subsidy...')
        await getMVCRewards({
          address: currentAccount.mvcAddress,
          gasChain: 'mvc'
        })
        console.log('⏳ Waiting for subsidy to be processed...')
        await sleep(5000) // Wait 5 seconds
        
        // Get credential for signing
        console.log('🔐 Getting credential for init rewards...')
        const sigRes = await getCredential({
          mnemonic: currentAccount.mnemonic,
          chain: 'btc',
          message: 'metaso.network',
          addressIndex: parseAddressIndexFromPath(currentAccount.path),
        })
        
        // Call getMVCInitRewards
        console.log('💰 Claiming init rewards...')
        await getMVCInitRewards({
          address: currentAccount.mvcAddress,
          gasChain: 'mvc'
        }, {
          'X-Signature': sigRes.signature,
          'X-Public-Key': sigRes.publicKey
        })
        console.log('✅ Init rewards claimed successfully')
      }

      // Create MetaID node with username
      console.log(`🏷️  Creating MetaID node with username: ${username}`)
      const namePinParams: CreatePinParams = {
        chain: 'mvc',
        dataList: [
          {
            metaidData: {
              operation: 'create',
              path: '/info/name',
              body: username,
              contentType: 'text/plain',
            }
          }
        ],
        feeRate: 1,
      }

      const namePinRes = await createPin(namePinParams, currentAccount.mnemonic, {
        addressIndex: parseAddressIndexFromPath(currentAccount.path),
      })
      
      if (namePinRes.txids && namePinRes.txids.length > 0) {
        console.log('✅ MetaID node created successfully')
        
        // Get user info by address to retrieve globalMetaId
        console.log('📋 Fetching user info to get globalMetaId...')
        try {
          const userInfo = await getUserInfoByAddressByMs(currentAccount.mvcAddress)
          if (userInfo && userInfo.globalMetaId) {
            console.log(`✅ Retrieved globalMetaId: ${userInfo.globalMetaId}`)
            
            // Update account with username and globalMetaId
            const accountIndex = accountData.accountList.findIndex(
              acc => acc.mvcAddress === currentAccount!.mvcAddress
            )
            if (accountIndex >= 0) {
              accountData.accountList[accountIndex].userName = username
              accountData.accountList[accountIndex].globalMetaId = userInfo.globalMetaId
              const profileFromPrompt = extractProfileFromPrompt(userPrompt)
              applyProfileToAccount(accountData.accountList[accountIndex], profileFromPrompt)
              writeAccountFile(accountData)
              currentAccount.userName = username
              currentAccount.globalMetaId = userInfo.globalMetaId
            }
          } else {
            // Update account with username only if globalMetaId is not available
            const accountIndex = accountData.accountList.findIndex(
              acc => acc.mvcAddress === currentAccount!.mvcAddress
            )
            if (accountIndex >= 0) {
              accountData.accountList[accountIndex].userName = username
              const profileFromPrompt = extractProfileFromPrompt(userPrompt)
              applyProfileToAccount(accountData.accountList[accountIndex], profileFromPrompt)
              writeAccountFile(accountData)
              currentAccount.userName = username
            }
            console.log('⚠️  globalMetaId not found in user info')
          }
        } catch (error: any) {
          console.log(`⚠️  Failed to fetch user info: ${error.message}`)
          // Continue with username update even if user info fetch fails
          const accountIndex = accountData.accountList.findIndex(
            acc => acc.mvcAddress === currentAccount!.mvcAddress
          )
          if (accountIndex >= 0) {
            accountData.accountList[accountIndex].userName = username
            const profileFromPrompt = extractProfileFromPrompt(userPrompt)
            applyProfileToAccount(accountData.accountList[accountIndex], profileFromPrompt)
            writeAccountFile(accountData)
            currentAccount.userName = username
          }
        }
      } else {
        throw new Error('Failed to create MetaID node: no txids returned')
      }
    } else if (currentAccount.userName) {
      console.log(`✅ MetaID already registered: ${currentAccount.userName}`)
    }

    // Step 4: Send Buzz message if content is provided
    if (buzzContent) {
      console.log(`📢 Sending Buzz message: ${buzzContent}`)
      const buzzResult = await createBuzz(currentAccount.mnemonic, buzzContent, 1, {
        addressIndex: parseAddressIndexFromPath(currentAccount.path),
      })
      
      if (buzzResult.txids && buzzResult.txids.length > 0) {
        console.log(`✅ Buzz sent successfully!`)
        console.log(`   TXID: ${buzzResult.txids[0]}`)
        console.log(`   Cost: ${buzzResult.totalCost} satoshis`)
      } else {
        throw new Error('Failed to send buzz: no txids returned')
      }
    }

    console.log('\n✅ All operations completed successfully!')
    
  } catch (error: any) {
    const errorMessage = error.message || 'Unknown error'
    const errorStack = error.stack || ''
    console.error(`\n❌ Error: ${errorMessage}`)
    
    // Log error to file
    logError(error, 'Main execution flow', 'main()')
    
    process.exit(1)
  }
}

// Run main function
main().catch((error) => {
  console.error('Fatal error:', error)
  logError(error, 'Main execution', 'main()')
  process.exit(1)
})
