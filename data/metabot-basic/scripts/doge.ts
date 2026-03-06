import * as bitcoin from 'bitcoinjs-lib'
import ECPairFactory, { ECPairAPI } from 'ecpair'
import { getDogeWallet } from './wallet'
import { fetchDogeUtxos, DogeUTXO, broadcastDogeTx, fetchDogeFeeRates, DogeFeeRate } from './api'

export type DogeMetaidData = {
  body?: string | Buffer
  operation: 'init' | 'create' | 'modify' | 'revoke'
  path?: string
  contentType?: string
  encryption?: '0' | '1' | '2'
  version?: string
  encoding?: BufferEncoding
  revealAddr: string
  flag?: 'metaid'
}

export interface InscriptionRequest {
  feeRate: number
  metaidDataList: DogeMetaidData[]
  revealOutValue?: number
  changeAddress?: string
  service?: {
    address: string
    satoshis: string
  }
}

interface InscribeHexResult {
  commitTxHex: string
  revealTxsHex: string[]
  commitCost: number
  revealCost: number
  totalCost: number
}

interface InscribeTxIdResult {
  commitTxId: string
  revealTxIds: string[]
  commitCost: number
  revealCost: number
  totalCost: number
}

function initOptions() {
  return { noBroadcast: false }
}

const MAX_CHUNK_LEN = 240
const DEFAULT_OUTPUT_VALUE = 1000000 // 0.01 DOGE
const DUST_LIMIT = 600 // DOGE dust limit

export class DogeInscribe {
  static ECPair: ECPairAPI | null = null
  static eccInitialized = false

  static async ensureEccInitialized() {
    if (!this.eccInitialized) {
      const ecc = await import('@bitcoinerlab/secp256k1')
      bitcoin.initEccLib(ecc)
      this.ECPair = ECPairFactory(ecc)
      this.eccInitialized = true
    }
    return this.ECPair!
  }

  static pushData(data: Buffer): Buffer {
    const len = data.length
    if (len === 0) {
      return Buffer.from([bitcoin.opcodes.OP_0])
    } else if (len < 76) {
      return Buffer.concat([Buffer.from([len]), data])
    } else if (len <= 0xff) {
      return Buffer.concat([Buffer.from([bitcoin.opcodes.OP_PUSHDATA1, len]), data])
    } else if (len <= 0xffff) {
      const lenBuf = Buffer.alloc(2)
      lenBuf.writeUInt16LE(len)
      return Buffer.concat([Buffer.from([bitcoin.opcodes.OP_PUSHDATA2]), lenBuf, data])
    } else {
      const lenBuf = Buffer.alloc(4)
      lenBuf.writeUInt32LE(len)
      return Buffer.concat([Buffer.from([bitcoin.opcodes.OP_PUSHDATA4]), lenBuf, data])
    }
  }

  static buildMetaIdInscriptionScript(data: DogeMetaidData): Buffer {
    const body = typeof data.body === 'string' 
      ? Buffer.from(data.body, data.encoding || 'utf8') 
      : data.body || Buffer.alloc(0)

    const bodyParts: Buffer[] = []
    for (let i = 0; i < body.length; i += MAX_CHUNK_LEN) {
      bodyParts.push(body.slice(i, Math.min(i + MAX_CHUNK_LEN, body.length)))
    }
    
    if (bodyParts.length === 0) {
      bodyParts.push(Buffer.alloc(0))
    }

    const chunks: Buffer[] = []
    chunks.push(this.pushData(Buffer.from('metaid')))
    chunks.push(this.pushData(Buffer.from(data.operation)))
    chunks.push(this.pushData(Buffer.from(data.contentType || 'text/plain')))
    chunks.push(this.pushData(Buffer.from(data.encryption || '0')))
    chunks.push(this.pushData(Buffer.from(data.version || '0.0.1')))
    chunks.push(this.pushData(Buffer.from(data.path || '')))
    
    for (const part of bodyParts) {
      chunks.push(this.pushData(part))
    }

    return Buffer.concat(chunks)
  }

  static buildLockScript(publicKey: Buffer, inscriptionScript: Buffer): Buffer {
    const chunks: Buffer[] = []
    chunks.push(this.pushData(publicKey))
    chunks.push(Buffer.from([bitcoin.opcodes.OP_CHECKSIGVERIFY]))
    
    const dropCount = this.countScriptChunks(inscriptionScript)
    for (let i = 0; i < dropCount; i++) {
      chunks.push(Buffer.from([bitcoin.opcodes.OP_DROP]))
    }
    
    chunks.push(Buffer.from([bitcoin.opcodes.OP_TRUE]))
    return Buffer.concat(chunks)
  }

  static countScriptChunks(script: Buffer): number {
    let count = 0
    let i = 0

    while (i < script.length) {
      const opcode = script[i]

      if (opcode === 0) {
        count++
        i++
      } else if (opcode >= 1 && opcode <= 75) {
        count++
        i += 1 + opcode
      } else if (opcode === bitcoin.opcodes.OP_PUSHDATA1) {
        const len = script[i + 1]
        count++
        i += 2 + len
      } else if (opcode === bitcoin.opcodes.OP_PUSHDATA2) {
        const len = script[i + 1] | (script[i + 2] << 8)
        count++
        i += 3 + len
      } else if (opcode === bitcoin.opcodes.OP_PUSHDATA4) {
        const len = script[i + 1] | (script[i + 2] << 8) | (script[i + 3] << 16) | (script[i + 4] << 24)
        count++
        i += 5 + len
      } else {
        i++
      }
    }

    return count
  }

  static hash160(data: Buffer): Buffer {
    return bitcoin.crypto.hash160(data)
  }

  static buildP2SHOutputScript(lockScript: Buffer): Buffer {
    const lockHash = this.hash160(lockScript)
    return Buffer.concat([
      Buffer.from([bitcoin.opcodes.OP_HASH160]),
      this.pushData(lockHash),
      Buffer.from([bitcoin.opcodes.OP_EQUAL]),
    ])
  }

  static estimateTxSize(
    p2pkhInputCount: number, 
    outputCount: number, 
    p2shUnlockScriptSize: number = 0
  ): number {
    let size = 10
    
    if (p2shUnlockScriptSize > 0) {
      size += 32 + 4 + 3 + p2shUnlockScriptSize + 4
    }
    
    size += p2pkhInputCount * 148
    size += outputCount * 34

    return size
  }

  static selectUtxos(
    availableUtxos: DogeUTXO[],
    targetAmount: number,
    feeRate: number,
    outputCount: number,
    p2shUnlockScriptSize: number = 0
  ): { selectedUtxos: DogeUTXO[]; fee: number; totalInput: number } {
    const selectedUtxos: DogeUTXO[] = []
    let totalInput = 0

    const sortedUtxos = [...availableUtxos].sort((a, b) => b.satoshis - a.satoshis)

    for (const utxo of sortedUtxos) {
      selectedUtxos.push(utxo)
      totalInput += utxo.satoshis

      const txSize = this.estimateTxSize(selectedUtxos.length, outputCount, p2shUnlockScriptSize)
      const fee = Math.ceil((txSize * feeRate) / 1000)

      if (totalInput >= targetAmount + fee) {
        return { selectedUtxos, fee, totalInput }
      }
    }

    throw new Error(`Insufficient funds: need ${targetAmount}, have ${totalInput}`)
  }

  static buildP2PKHOutputScript(address: string, network: bitcoin.Network): Buffer {
    const decoded = bitcoin.address.fromBase58Check(address)
    return Buffer.concat([
      Buffer.from([bitcoin.opcodes.OP_DUP, bitcoin.opcodes.OP_HASH160]),
      this.pushData(decoded.hash),
      Buffer.from([bitcoin.opcodes.OP_EQUALVERIFY, bitcoin.opcodes.OP_CHECKSIG]),
    ])
  }

  static signP2PKHInput(
    tx: bitcoin.Transaction,
    inputIndex: number,
    keyPair: any,
    prevOutputScript: Buffer
  ): Buffer {
    const sigHash = tx.hashForSignature(inputIndex, prevOutputScript, bitcoin.Transaction.SIGHASH_ALL)
    const signature = keyPair.sign(sigHash)
    const signatureDER = bitcoin.script.signature.encode(signature, bitcoin.Transaction.SIGHASH_ALL)
    
    return Buffer.concat([
      this.pushData(signatureDER),
      this.pushData(keyPair.publicKey),
    ])
  }

  static signP2SHInput(
    tx: bitcoin.Transaction,
    inputIndex: number,
    tempKeyPair: any,
    lockScript: Buffer,
    inscriptionScript: Buffer
  ): Buffer {
    // For P2SH, we need to sign with the redeem script
    const sigHash = tx.hashForSignature(inputIndex, lockScript, bitcoin.Transaction.SIGHASH_ALL)
    const signature = tempKeyPair.sign(sigHash)
    const signatureDER = bitcoin.script.signature.encode(signature, bitcoin.Transaction.SIGHASH_ALL)
    
    // P2SH unlock script: <signature> <pubkey> <inscriptionScript> <redeemScript>
    return Buffer.concat([
      this.pushData(signatureDER),
      this.pushData(tempKeyPair.publicKey),
      this.pushData(inscriptionScript),
      this.pushData(lockScript),
    ])
  }

  static async buildDogeInscriptionTxs(
    metaidData: DogeMetaidData,
    utxos: DogeUTXO[],
    walletKeyPair: any,
    feeRate: number,
    changeAddress: string,
    network: bitcoin.Network,
    revealOutValue: number = DEFAULT_OUTPUT_VALUE,
    ECPairInstance: ECPairAPI
  ): Promise<{ commitTx: bitcoin.Transaction; revealTx: bitcoin.Transaction; commitFee: number; revealFee: number }> {
    
    const tempKeyPair = ECPairInstance.makeRandom({ network })
    const tempPublicKey = tempKeyPair.publicKey

    const inscriptionScript = this.buildMetaIdInscriptionScript(metaidData)
    const lockScript = this.buildLockScript(tempPublicKey, inscriptionScript)
    const p2shOutputScript = this.buildP2SHOutputScript(lockScript)
    
    const estimatedUnlockSize = inscriptionScript.length + 72 + lockScript.length + 10

    // Build Commit transaction
    const commitTx = new bitcoin.Transaction()
    commitTx.version = 2
    
    commitTx.addOutput(p2shOutputScript, DEFAULT_OUTPUT_VALUE)
    
    const { selectedUtxos: commitUtxos, fee: commitFee, totalInput: commitTotalInput } = this.selectUtxos(
      utxos,
      DEFAULT_OUTPUT_VALUE,
      feeRate,
      2,
      0
    )
    
    for (const utxo of commitUtxos) {
      const txIdBuffer = Buffer.from(utxo.txId, 'hex').reverse()
      commitTx.addInput(txIdBuffer, utxo.outputIndex)
    }
    
    const commitChange = commitTotalInput - DEFAULT_OUTPUT_VALUE - commitFee
    if (commitChange >= DUST_LIMIT) {
      const changeScript = this.buildP2PKHOutputScript(changeAddress, network)
      commitTx.addOutput(changeScript, commitChange)
    }
    
    for (let i = 0; i < commitUtxos.length; i++) {
      const utxo = commitUtxos[i]
      const prevOutputScript = this.buildP2PKHOutputScript(utxo.address, network)
      const sigScript = this.signP2PKHInput(commitTx, i, walletKeyPair, prevOutputScript)
      commitTx.setInputScript(i, sigScript)
    }

    // Build Reveal transaction
    const revealTx = new bitcoin.Transaction()
    revealTx.version = 2
    
    const commitTxId = commitTx.getId()
    const commitTxIdBuffer = Buffer.from(commitTxId, 'hex').reverse()
    revealTx.addInput(commitTxIdBuffer, 0)
    
    const revealOutputScript = this.buildP2PKHOutputScript(metaidData.revealAddr, network)
    revealTx.addOutput(revealOutputScript, revealOutValue)
    
    let availableUtxos = utxos.filter(u => !commitUtxos.some(cu => cu.txId === u.txId && cu.outputIndex === u.outputIndex))
    if (commitChange >= DUST_LIMIT) {
      availableUtxos.push({
        txId: commitTxId,
        outputIndex: commitTx.outs.length - 1,
        satoshis: commitChange,
        address: changeAddress,
      })
    }
    
    const p2shInputAmount = DEFAULT_OUTPUT_VALUE
    const { selectedUtxos: revealUtxos, fee: revealFee, totalInput: revealTotalInput } = this.selectUtxos(
      availableUtxos,
      revealOutValue - p2shInputAmount,
      feeRate,
      2,
      estimatedUnlockSize
    )
    
    for (const utxo of revealUtxos) {
      const txIdBuffer = Buffer.from(utxo.txId, 'hex').reverse()
      revealTx.addInput(txIdBuffer, utxo.outputIndex)
    }
    
    const revealChange = p2shInputAmount + revealTotalInput - revealOutValue - revealFee
    if (revealChange >= DUST_LIMIT) {
      const changeScript = this.buildP2PKHOutputScript(changeAddress, network)
      revealTx.addOutput(changeScript, revealChange)
    }
    
    for (let i = 0; i < revealUtxos.length; i++) {
      const utxo = revealUtxos[i]
      const prevOutputScript = this.buildP2PKHOutputScript(utxo.address, network)
      const sigScript = this.signP2PKHInput(revealTx, i + 1, walletKeyPair, prevOutputScript)
      revealTx.setInputScript(i + 1, sigScript)
    }
    
    const unlockScript = this.signP2SHInput(revealTx, 0, tempKeyPair, lockScript, inscriptionScript)
    revealTx.setInputScript(0, unlockScript)

    return { commitTx, revealTx, commitFee, revealFee }
  }

  static async process({
    mnemonic,
    data: { metaidDataList, service, feeRate, revealOutValue },
    options = initOptions(),
  }: {
    mnemonic: string
    data: InscriptionRequest
    options?: { noBroadcast: boolean }
  }): Promise<InscribeHexResult | InscribeTxIdResult> {
    if (!mnemonic) {
      throw new Error(`mnemonic is null`)
    }

    const ECPairInstance = await this.ensureEccInitialized()

    const wallet = await getDogeWallet({ mnemonic: mnemonic })
    const address = wallet.getAddress()
    const privateKeyWIF = wallet.getPrivateKey()
    const network = wallet.getNetwork() as bitcoin.Network
    
    const walletKeyPair = ECPairInstance.fromWIF(privateKeyWIF, network)

    const rawUtxos = await fetchDogeUtxos(address, true)
    const utxos: DogeUTXO[] = rawUtxos.map((utxo: any) => ({
      txId: utxo.txId,
      outputIndex: utxo.outputIndex,
      satoshis: utxo.satoshis,
      address: utxo.address || address,
      rawTx: utxo.rawTx,
      height: utxo.height,
      confirmed: utxo.confirmed,
    }))

    if (utxos.length === 0) {
      throw new Error('No UTXOs available')
    }

    let totalCommitCost = 0
    let totalRevealCost = 0
    const commitTxs: bitcoin.Transaction[] = []
    const revealTxs: bitcoin.Transaction[] = []

    let availableUtxos = [...utxos]
    
    for (const metaidData of metaidDataList) {
      const { commitTx, revealTx, commitFee, revealFee } = await this.buildDogeInscriptionTxs(
        metaidData,
        availableUtxos,
        walletKeyPair,
        feeRate,
        address,
        network,
        revealOutValue || DEFAULT_OUTPUT_VALUE,
        ECPairInstance
      )

      commitTxs.push(commitTx)
      revealTxs.push(revealTx)
      totalCommitCost += commitFee
      totalRevealCost += revealFee
    }

    const totalCost = totalCommitCost + totalRevealCost + (service ? parseInt(service.satoshis) : 0)

    if (!options.noBroadcast) {
      const commitTxIds: string[] = []
      const revealTxIds: string[] = []

      for (let i = 0; i < commitTxs.length; i++) {
        const commitTxId = await broadcastDogeTx(commitTxs[i].toHex())
        commitTxIds.push(commitTxId)

        const revealTxId = await broadcastDogeTx(revealTxs[i].toHex())
        revealTxIds.push(revealTxId)
      }

      return {
        commitTxId: commitTxIds[0],
        revealTxIds,
        commitCost: totalCommitCost,
        revealCost: totalRevealCost,
        totalCost,
      }
    }

    return {
      commitTxHex: commitTxs[0]?.toHex() || '',
      revealTxsHex: revealTxs.map((tx) => tx.toHex()),
      commitCost: totalCommitCost,
      revealCost: totalRevealCost,
      totalCost,
    }
  }
}
