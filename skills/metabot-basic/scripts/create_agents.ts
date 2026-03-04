#!/usr/bin/env node

/**
 * Batch create MetaID Agents
 * 支持：头像、metaid 同步、chatpubkey、llm 配置
 */

import { generateMnemonic, getAllAddress, getPublicKey, getPath, getUtxos, getCredential, DEFAULT_PATH, parseAddressIndexFromPath } from './wallet'
import { getMVCRewards, getMVCInitRewards, sleep, getUserInfoByAddressByMs } from './api'
import { createPin, CreatePinParams } from './metaid'
import {
  readAccountFile,
  writeAccountFile,
  ensureAccountFile,
  Account,
  AccountProfile,
  readUserInfoFile,
  writeUserInfoFile,
  getAvatarUrl,
  applyProfileToAccount,
} from './utils'
import {
  hasAvatarFile,
  loadAvatarAsBase64,
  loadAvatarFromFilePath,
  isValidAvatarFilePath,
  AVATAR_SIZE_EXCEEDED_MSG,
} from './avatar'
import { getEcdhPublickey } from './chatpubkey'
import { getLLMConfigFromEnv } from './env-config'

/**
 * 同步 metaid 到 account.json 和 userInfo.json
 */
function syncMetaIdToFiles(mvcAddress: string, metaId: string): void {
  const accountData = readAccountFile()
  const accountIndex = accountData.accountList.findIndex((acc) => acc.mvcAddress === mvcAddress)
  if (accountIndex !== -1) {
    accountData.accountList[accountIndex].metaid = metaId
    writeAccountFile(accountData)
  }

  const userInfoData = readUserInfoFile()
  const userIndex = userInfoData.userList.findIndex((u) => u.address === mvcAddress)
  if (userIndex !== -1) {
    userInfoData.userList[userIndex].metaid = metaId
    writeUserInfoFile(userInfoData)
  }
}

/**
 * 创建单个 MetaID Agent
 * @param username 用户名（链上 name 节点）
 * @param profileOverrides 可选人设覆盖，未传则随机分配
 * @param avatarFilePath 可选，用户拖入对话框的图片路径；不传则从 static/avatar 读取
 */
export async function createAgent(
  username: string,
  profileOverrides?: Partial<AccountProfile>,
  avatarFilePath?: string
): Promise<void> {
  console.log(`\n🚀 开始创建 MetaID Agent: ${username}`)
  console.log('='.repeat(50))

  try {
    ensureAccountFile()
    let accountData = readAccountFile()
    const llmFromEnv = getLLMConfigFromEnv()

    // Create new wallet（新建 agent 使用默认 path，addressIndex 为 0）
    console.log('🔐 生成钱包...')
    const mnemonic = await generateMnemonic()
    const newAgentAddressIndex = parseAddressIndexFromPath(DEFAULT_PATH)
    const addresses = await getAllAddress(mnemonic, { addressIndex: newAgentAddressIndex })
    const publicKey = await getPublicKey('mvc', mnemonic, { addressIndex: newAgentAddressIndex })
    const pathStr = getPath({ defaultPath: DEFAULT_PATH })

    const newAccount: Account = {
      mnemonic,
      mvcAddress: addresses.mvcAddress,
      btcAddress: addresses.btcAddress,
      dogeAddress: addresses.dogeAddress,
      publicKey,
      userName: '',
      path: pathStr,
      llm: [
        {
          provider: llmFromEnv.provider,
          apiKey: llmFromEnv.apiKey,
          baseUrl: llmFromEnv.baseUrl,
          model: llmFromEnv.model,
          temperature: llmFromEnv.temperature,
          maxTokens: llmFromEnv.maxTokens,
        },
      ],
    }

    // Add to account list (unshift to front)
    accountData.accountList.unshift(newAccount)
    writeAccountFile(accountData)
    console.log(`✅ 钱包创建成功`)
    console.log(`   MVC地址: ${addresses.mvcAddress}`)
    console.log(`   BTC地址: ${addresses.btcAddress}`)
    console.log(`   DOGE地址: ${addresses.dogeAddress}`)

    // Register MetaID
    console.log(`📝 注册 MetaID 账户...`)

    // Check if user has UTXOs
    const utxos = await getUtxos('mvc', mnemonic, { addressIndex: newAgentAddressIndex })

    if (utxos.length === 0) {
      // New user, claim gas subsidy
      console.log('💰 申请 Gas 补贴...')
      await getMVCRewards({
        address: addresses.mvcAddress,
        gasChain: 'mvc',
      })
      console.log('⏳ 等待补贴处理...')
      await sleep(5000) // Wait 5 seconds

      // Get credential for signing
      console.log('🔐 获取凭证用于初始奖励...')
      const sigRes = await getCredential({
        mnemonic: mnemonic,
        chain: 'btc',
        message: 'metaso.network',
        addressIndex: newAgentAddressIndex,
      })

      // Call getMVCInitRewards
      console.log('💰 申请初始奖励...')
      await getMVCInitRewards(
        {
          address: addresses.mvcAddress,
          gasChain: 'mvc',
        },
        {
          'X-Signature': sigRes.signature,
          'X-Public-Key': sigRes.publicKey,
        }
      )
      console.log('✅ 初始奖励申请成功')
    }

    // Create MetaID node with username
    console.log(`🏷️  创建 MetaID 节点，用户名: ${username}`)
    const namePinParams: CreatePinParams = {
      chain: 'mvc',
      dataList: [
        {
          metaidData: {
            operation: 'create',
            path: '/info/name',
            body: username,
            contentType: 'text/plain',
          },
        },
      ],
      feeRate: 1,
    }

    const namePinRes = await createPin(namePinParams, mnemonic, {
      addressIndex: newAgentAddressIndex,
    })

    if (namePinRes.txids && namePinRes.txids.length > 0) {
      console.log(`✅ MetaID 节点创建成功! TXID: ${namePinRes.txids[0]}`)

      // Wait a bit for the transaction to be indexed
      console.log('⏳ 等待交易索引...')
      await sleep(3000)

      // Fetch user info
      console.log('📋 获取用户信息...')
      const userInfo = await getUserInfoByAddressByMs(addresses.mvcAddress)

      // 4. 同步 metaid 到 account.json 和 userInfo.json
      if (userInfo?.metaId) {
        syncMetaIdToFiles(addresses.mvcAddress, userInfo.metaId)
        console.log(`✅ 已同步 metaid: ${userInfo.metaId}`)
      }

      // Update account with userName, globalMetaId，并写入人设（未指定则随机）
      accountData = readAccountFile()
      const accountIndex = accountData.accountList.findIndex((acc) => acc.mvcAddress === addresses.mvcAddress)
      if (accountIndex !== -1) {
        accountData.accountList[accountIndex].userName = username
        if (userInfo?.globalMetaId) {
          accountData.accountList[accountIndex].globalMetaId = userInfo.globalMetaId
          console.log(`✅ 获取到 globalMetaId: ${userInfo.globalMetaId}`)
        } else {
          console.log('⚠️  暂时无法获取 globalMetaId，但用户名已更新')
        }
        applyProfileToAccount(accountData.accountList[accountIndex], profileOverrides)
        console.log(`✅ 已写入 Agent 人设到 account.json`)
        writeAccountFile(accountData)
      }

      // 1. 头像：优先使用用户拖入的图片路径，否则从 static/avatar 读取（文件需小于 1MB）
      const hasAvatar =
        avatarFilePath && isValidAvatarFilePath(avatarFilePath)
          ? true
          : hasAvatarFile()
      if (hasAvatar) {
        let avatarData: { avatar: string; contentType: string } | null = null
        try {
          avatarData =
            avatarFilePath && isValidAvatarFilePath(avatarFilePath)
              ? await loadAvatarFromFilePath(avatarFilePath)
              : await loadAvatarAsBase64()
        } catch (e: any) {
          if (e?.message === AVATAR_SIZE_EXCEEDED_MSG) {
            console.log(`⚠️  ${AVATAR_SIZE_EXCEEDED_MSG}`)
          } else {
            throw e
          }
        }
        if (avatarData) {
          console.log('🖼️  创建头像节点...')
          const avatarPinParams: CreatePinParams = {
            chain: 'mvc',
            dataList: [
              {
                metaidData: {
                  operation: 'create',
                  path: '/info/avatar',
                  body: avatarData.avatar,
                  encoding: 'base64',
                  contentType: avatarData.contentType,
                },
              },
            ],
            feeRate: 1,
          }
          const avatarPinRes = await createPin(avatarPinParams, mnemonic, {
            addressIndex: newAgentAddressIndex,
          })
          if (avatarPinRes.txids && avatarPinRes.txids.length > 0) {
            const avatarPinId = avatarPinRes.txids[0] + 'i0'
            accountData = readAccountFile()
            const accIdx = accountData.accountList.findIndex(
              (acc) => acc.mvcAddress === addresses.mvcAddress
            )
            if (accIdx !== -1) {
              accountData.accountList[accIdx].avatarPinId = avatarPinId
              accountData.accountList[accIdx].avatar = getAvatarUrl(avatarPinId)
              writeAccountFile(accountData)
              console.log(`✅ 头像创建成功! avatarPinId: ${avatarPinId}`)
            }
          }
        }
      } else {
        console.log(
          'ℹ️  无头像图片，跳过头像设置（请将图片放入 metabot-basic/static/avatar 或提供路径后重试）'
        )
      }

      // 5. chatpubkey：若 userInfo.chatPublicKey 为空则创建
      const needChatPubkey =
        !userInfo?.chatPublicKey ||
        accountData.accountList.find((a) => a.mvcAddress === addresses.mvcAddress)?.chatPublicKey === '' ||
        !accountData.accountList.find((a) => a.mvcAddress === addresses.mvcAddress)?.chatPublicKey

      if (needChatPubkey) {
        const ecdh = await getEcdhPublickey(mnemonic, undefined, {
          addressIndex: newAgentAddressIndex,
        })
        if (ecdh?.ecdhPubKey) {
          console.log('🔑 创建 chatpubkey 节点...')
          const chatPubkeyPinParams: CreatePinParams = {
            chain: 'mvc',
            dataList: [
              {
                metaidData: {
                  operation: 'create',
                  path: '/info/chatpubkey',
                  body: ecdh.ecdhPubKey,
                  encoding: 'utf-8',
                  contentType: 'text/plain',
                },
              },
            ],
            feeRate: 1,
          }
          const chatPubkeyPinRes = await createPin(chatPubkeyPinParams, mnemonic, {
            addressIndex: newAgentAddressIndex,
          })
          if (chatPubkeyPinRes.txids && chatPubkeyPinRes.txids.length > 0) {
            const chatPublicKeyPinId = chatPubkeyPinRes.txids[0] + 'i0'
            accountData = readAccountFile()
            const accIdx = accountData.accountList.findIndex((acc) => acc.mvcAddress === addresses.mvcAddress)
            if (accIdx !== -1) {
              accountData.accountList[accIdx].chatPublicKey = ecdh.ecdhPubKey
              accountData.accountList[accIdx].chatPublicKeyPinId = chatPublicKeyPinId
              writeAccountFile(accountData)
              console.log(`✅ chatpubkey 创建成功! chatPublicKeyPinId: ${chatPublicKeyPinId}`)
            }
          }
        }
      } else {
        console.log('ℹ️  已有 chatPublicKey，跳过')
      }
    } else {
      throw new Error('MetaID 节点创建失败')
    }

    console.log(`\n✅ ${username} 创建完成!`)
    console.log('='.repeat(50))
  } catch (error: any) {
    console.error(`\n❌ 创建 ${username} 时出错:`, error.message)
    throw error
  }
}

async function main() {
  const args = process.argv.slice(2)
  const avatarIdx = args.indexOf('--avatar')
  const avatarFilePath =
    avatarIdx >= 0 && args[avatarIdx + 1] ? args[avatarIdx + 1] : undefined
  const agents =
    avatarIdx >= 0
      ? args.filter((a, i) => a !== '--avatar' && (i < avatarIdx || i > avatarIdx + 1))
      : args
  const agentList = agents.length > 0 ? agents : ['小橙', 'Nova', '墨白']

  console.log('🎯 开始批量创建 MetaID Agents')
  console.log(`📋 将创建以下 Agents: ${agentList.join(', ')}`)
  if (avatarFilePath) console.log(`🖼️  头像图片: ${avatarFilePath}`)

  for (const agentName of agentList) {
    try {
      await createAgent(agentName, undefined, avatarFilePath)
      // Wait between creations to avoid rate limiting
      if (agentName !== agentList[agentList.length - 1]) {
        console.log('\n⏳ 等待 5 秒后创建下一个...')
        await sleep(5000)
      }
    } catch (error: any) {
      console.error(`\n❌ 创建 ${agentName} 失败:`, error.message)
      // Continue with next agent
    }
  }

  console.log('\n🎉 批量创建完成!')
}

main().catch((error) => {
  console.error('Fatal error:', error)
  process.exit(1)
})
