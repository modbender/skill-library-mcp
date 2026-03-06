#!/usr/bin/env node

/**
 * 发送 Buzz 到 MVC 网络
 * Usage:
 *   npx ts-node scripts/send_buzz.ts <agentName> <content>
 *   npx ts-node scripts/send_buzz.ts <agentName> @<filepath>   # 从文件读取内容
 */

import * as fs from 'fs'
import * as path from 'path'
import { createBuzz } from './buzz'
import { parseAddressIndexFromPath } from './wallet'
import { readAccountFile, findAccountByKeyword } from './utils'

async function main() {
  const args = process.argv.slice(2)
  const agentName = args[0] || 'AI Eason'
  let content: string

  if (args[1]?.startsWith('@')) {
    const filePath = args[1].slice(1)
    const fullPath = path.isAbsolute(filePath) ? filePath : path.join(process.cwd(), filePath)
    if (!fs.existsSync(fullPath)) {
      console.error(`❌ 文件不存在: ${fullPath}`)
      process.exit(1)
    }
    content = fs.readFileSync(fullPath, 'utf-8')
  } else {
    content = args.slice(1).join(' ').trim()
  }

  if (!content) {
    console.error('❌ 请提供 Buzz 内容')
    console.error('   Usage: npx ts-node scripts/send_buzz.ts "AI Eason" "内容"')
    console.error('   或:    npx ts-node scripts/send_buzz.ts "AI Eason" @./content.txt')
    process.exit(1)
  }

  const accountData = readAccountFile()
  const account = findAccountByKeyword(agentName, accountData)
  if (!account) {
    console.error(`❌ 未找到账户: ${agentName}`)
    console.error('   请确保 account.json 中存在该 Agent')
    process.exit(1)
  }

  if (!account.mnemonic) {
    console.error(`❌ 账户 ${agentName} 无 mnemonic`)
    process.exit(1)
  }

  console.log(`📢 使用 ${agentName} 发送 Buzz 到 MVC 网络...`)
  console.log(`   内容长度: ${content.length} 字符`)

  try {
    const result = await createBuzz(account.mnemonic, content, 1, {
      addressIndex: parseAddressIndexFromPath(account.path),
    })
    if (result.txids?.length) {
      console.log(`✅ Buzz 发送成功!`)
      console.log(`   TXID: ${result.txids[0]}`)
      console.log(`   消耗: ${result.totalCost} satoshis`)
    } else {
      throw new Error('No txids returned')
    }
  } catch (error: any) {
    console.error(`❌ 发送失败: ${error?.message || error}`)
    process.exit(1)
  }
}

main()
