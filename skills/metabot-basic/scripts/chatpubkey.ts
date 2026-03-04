#!/usr/bin/env node

/**
 * chatpubkey 生成模块
 * 使用 ECDH 与 MAN 公钥计算共享密钥，生成 ecdhPubKey 供 /info/chatpubkey 上链
 */

import * as crypto from 'crypto'
import { mvc } from 'meta-contract'
import { getCurrentWallet } from './wallet'
import { Chain } from './wallet'

const MAN_PUB_KEY =
  '048add0a6298f10a97785f7dd069eedb83d279a6f03e73deec0549e7d6fcaac4eef2c279cf7608be907a73c89eb44c28db084c27b588f1bd869321a6f104ec642d'

export interface EcdhResult {
  externalPubKey: string
  sharedSecret: string
  ecdhPubKey: string
  creatorPubkey: string
}

/** 可选：addressIndex 不传则使用 0，可与 account.path 经 parseAddressIndexFromPath 得到 */
export type GetEcdhPublickeyOptions = { addressIndex?: number }

/**
 * 使用钱包私钥与 MAN 公钥进行 ECDH，返回 ecdhPubKey 等
 */
export async function getEcdhPublickey(
  mnemonic: string,
  pubkey?: string,
  options?: GetEcdhPublickeyOptions
): Promise<EcdhResult | null> {
  try {
    const wallet = await getCurrentWallet(Chain.MVC, {
      mnemonic,
      addressIndex: options?.addressIndex,
    })
    const privateKeyWIF = wallet.getPrivateKey()
    const privKey = mvc.PrivateKey.fromWIF(privateKeyWIF)
    const privateKeyBuffer = Buffer.from((privKey as any).bn.toArray('be', 32))

    const externalPubKey = pubkey || MAN_PUB_KEY
    const _externalPubKey = Buffer.from(externalPubKey, 'hex')

    const ecdh = crypto.createECDH('prime256v1')
    ecdh.setPrivateKey(privateKeyBuffer)
    const _sharedSecret = ecdh.computeSecret(_externalPubKey)
    const sharedSecret = crypto.createHash('sha256').update(_sharedSecret).digest('hex')
    const ecdhPubKey = ecdh.getPublicKey().toString('hex')
    const creatorPubkey = wallet.getPublicKey().toString('hex')

    return {
      externalPubKey,
      sharedSecret,
      ecdhPubKey,
      creatorPubkey,
    }
  } catch (error) {
    console.error('getEcdhPublickey error:', error)
    return null
  }
}
