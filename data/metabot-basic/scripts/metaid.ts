import { TxComposer, mvc } from 'meta-contract'
import { Chain, getCurrentWallet, getNet, getMvcRootPath, getDogeWallet, getMnemonicFromAccount } from './wallet'
import { fetchMVCUtxos, MvcUtxo, broadcastTx, fetchDogeFeeRates, DogeUTXO } from './api'
import { DogeInscribe, DogeMetaidData } from './doge'

export type Operation = 'init' | 'create' | 'modify' | 'revoke'

export type MetaidData = {
  operation: Operation
  path?: string
  body?: string | Buffer
  contentType?: string
  encryption?: '0' | '1' | '2'
  version?: string
  encoding?: BufferEncoding
  flag?: 'metaid'
  revealAddr?: string
}

export type Output = {
  address: string
  satoshis: string
}

export type PinOptions = {
  outputs?: Output[]
  service?: Output
  refs?: Record<string, number>
}

export type PinDetail = {
  metaidData: MetaidData
  options?: PinOptions
}

export type CreatePinParams = {
  chain: 'btc' | 'mvc' | 'doge'
  dataList: PinDetail[]
  feeRate?: number
  noBroadcast?: boolean
}

export type CreatePinResult = {
  commitTxId?: string
  revealTxIds?: string[]
  commitTxHex?: string
  revealTxsHex?: string[]
  txids?: string[]
  txHexList?: string[]
  commitCost?: number
  revealCost?: number
  totalCost: number
}

export type SA_utxo = {
  txId: string
  outputIndex: number
  satoshis: number
  address: string
  height: number
}

export const P2PKH_UNLOCK_SIZE = 1 + 1 + 72 + 1 + 33
export const DERIVE_MAX_DEPTH = 1000

/**
 * 规范化并校验 MetaID 数据：
 * - 将 path 统一转为小写（协议路径在链上统一使用小写）
 * - 当 operation 为 'modify' 时，要求必须显式指定要修改的 pinId，
 *   且 path 必须形如 `@<pinId>/protocols/xxx`
 */
function normalizeMetaidData(metaidData: MetaidData): MetaidData {
  const normalized: MetaidData = { ...metaidData }

  if (normalized.path) {
    normalized.path = normalized.path.toLowerCase()
  }

  if (normalized.operation === 'modify') {
    const path = normalized.path?.trim() || ''

    // 要求形如：@<pinId>/protocols/xxx
    const modifyPathReg = /^@[^/]+\/protocols\/[^/]+/
    if (!modifyPathReg.test(path)) {
      throw new Error(
        `operation "modify" requires target pinId in path, e.g. "@<pinId>/protocols/simplenote"（需要在 path 中传入要修改的 pinId）`
      )
    }
  }

  return normalized
}

function replaceRefs(body: string | Buffer, refs: Record<string, number>, txids: string[]): string | Buffer {
  if (Buffer.isBuffer(body)) {
    return body
  }
  
  let result = body
  for (const [placeholder, index] of Object.entries(refs)) {
    if (txids[index]) {
      result = result.replace(new RegExp(placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), txids[index])
    }
  }
  
  return result
}

function buildMvcOpReturn(metaidData: MetaidData): any[] {
  const result: any[] = ['metaid', metaidData.operation]
  
  if (metaidData.operation !== 'init') {
    result.push(metaidData.path || '')
    result.push(metaidData.encryption || '0')
    result.push(metaidData.version || '1.0.0')
    result.push(metaidData.contentType || 'text/plain;utf-8')
    
    const body = metaidData.body 
      ? Buffer.isBuffer(metaidData.body)
        ? metaidData.body
        : Buffer.from(metaidData.body, metaidData.encoding || 'utf-8')
      : undefined
    
    result.push(body)
  }
  
  return result
}

export async function parseLocalTransaction(transaction: mvc.Transaction): Promise<{
  messages: (string | Buffer)[]
  outputIndex: number | null
}> {
  const outputs = transaction.outputs
  const outputIndex = outputs.findIndex((output) => output.script.toASM().includes('OP_RETURN'))

  if (outputIndex === -1)
    return {
      messages: [],
      outputIndex: null,
    }

  const outputAsm = outputs[outputIndex].script.toASM()
  const asmFractions = outputAsm.split('OP_RETURN')[1].trim().split(' ')
  let messages: any = asmFractions.map((fraction: string) => {
    return Buffer.from(fraction, 'hex').toString()
  })

  const isBinary = messages[messages.length - 1] === 'binary'
  if (isBinary) {
    messages[5] = Buffer.from(asmFractions[5], 'hex')
  }

  return {
    messages,
    outputIndex,
  }
}

function pickUtxo(utxos: SA_utxo[], amount: number, feeb: number) {
  let requiredAmount = amount + 34 * 2 * feeb + 100

  if (requiredAmount <= 0) {
    return []
  }

  const sum = utxos.reduce((acc, utxo) => acc + utxo.satoshis, 0)
  if (sum < requiredAmount) {
    throw new Error('Not enough balance')
  }

  const candidateUtxos: SA_utxo[] = []
  const confirmedUtxos = utxos
    .filter((utxo) => {
      return utxo.height > 0
    })
    .sort(() => Math.random() - 0.5)
  const unconfirmedUtxos = utxos
    .filter((utxo) => {
      return utxo.height <= 0
    })
    .sort(() => Math.random() - 0.5)

  let current = 0
  for (let utxo of confirmedUtxos) {
    current += utxo.satoshis
    requiredAmount += feeb * P2PKH_UNLOCK_SIZE
    candidateUtxos.push(utxo)
    if (current > requiredAmount) {
      return candidateUtxos
    }
  }
  for (let utxo of unconfirmedUtxos) {
    current += utxo.satoshis
    requiredAmount += feeb * P2PKH_UNLOCK_SIZE
    candidateUtxos.push(utxo)
    if (current > requiredAmount) {
      return candidateUtxos
    }
  }
  return candidateUtxos
}

async function fetchUtxos(chain: string, address: string): Promise<any[]> {
  if (chain === 'mvc') {
    return (await fetchMVCUtxos(address)) || []
  } else {
    throw new Error(`Chain ${chain} not supported for fetchUtxos`)
  }
}

export type WalletOptions = { addressIndex?: number; accountIndex?: number }

/**
 * 使用 account.json 当前操作用户为一批交易支付（选 UTXO、找零、签名）。
 * 等价于 payTransactions，但 mnemonic 从 account.json 指定用户读取。
 */
export async function pay(
  toPayTransactions: { txComposer: string; message?: string }[],
  hasMetaid: boolean = false,
  feeb?: number,
  options: { addressIndex?: number; accountIndex?: number } = {}
): Promise<string[]> {
  const { mnemonic, addressIndex: derivedIndex } = getMnemonicFromAccount({ accountIndex: options.accountIndex })
  const addressIndex = options.addressIndex ?? derivedIndex
  return payTransactions(mnemonic, toPayTransactions, hasMetaid, feeb, { addressIndex })
}

export const payTransactions = async (
  mnemonic: string,
  toPayTransactions: {
    txComposer: string
    message?: string
  }[],
  hasMetaid: boolean = false,
  feeb?: number,
  options?: WalletOptions
) => {
  if (!mnemonic) {
    throw new Error(`mnemonic is null`)
  }
  const network = mvc.Networks.livenet
  const wallet = await getCurrentWallet(Chain.MVC, { mnemonic, addressIndex: options?.addressIndex })
  const address = wallet.getAddress()
  if (!feeb) {
    feeb = 1
  }
  let usableUtxos = ((await fetchUtxos('mvc', address)) as MvcUtxo[]).map((u) => {
    return {
      txId: u.txid,
      outputIndex: u.outIndex,
      satoshis: u.value,
      address,
      height: u.height,
    }
  })

  const txids = new Map<string, string>()
  toPayTransactions.forEach(({ txComposer: txComposerSerialized }) => {
    const txid = TxComposer.deserialize(txComposerSerialized).getTxId()
    txids.set(txid, txid)
  })

  const payedTransactions = []
  for (let i = 0; i < toPayTransactions.length; i++) {
    const toPayTransaction = toPayTransactions[i]
    const currentTxid = TxComposer.deserialize(toPayTransaction.txComposer).getTxId()

    const txComposer = TxComposer.deserialize(toPayTransaction.txComposer)
    const tx = txComposer.tx

    const inputs = tx.inputs
    const existingInputsLength = tx.inputs.length
    for (let i = 0; i < inputs.length; i++) {
      if (!inputs[i].output) {
        throw new Error('The output of every input of the transaction must be provided')
      }
    }

    if (hasMetaid) {
      const { messages: metaIdMessages, outputIndex } = await parseLocalTransaction(tx)

      if (outputIndex !== null) {
        let replaceFound = false
        const prevTxids = Array.from(txids.keys())

        for (let i = 0; i < metaIdMessages.length; i++) {
          for (let j = 0; j < prevTxids.length; j++) {
            if (typeof metaIdMessages[i] !== 'string') continue

            if (metaIdMessages[i].includes(prevTxids[j])) {
              replaceFound = true
              metaIdMessages[i] = (metaIdMessages[i] as string).replace(prevTxids[j], txids.get(prevTxids[j])!)
            }
          }
        }

        if (replaceFound) {
          const opReturnOutput = new mvc.Transaction.Output({
            script: mvc.Script.buildSafeDataOut(metaIdMessages),
            satoshis: 0,
          })

          tx.outputs[outputIndex] = opReturnOutput
        }
      }
    }

    const addressObj = new mvc.Address(address, network as any)
    const totalOutput = tx.outputs.reduce((acc, output) => acc + output.satoshis, 0)
    const totalInput = tx.inputs.reduce((acc, input) => acc + input.output!.satoshis, 0)
    const currentSize = tx.toBuffer().length
    const currentFee = feeb * currentSize
    const difference = totalOutput - totalInput + currentFee

    const pickedUtxos = pickUtxo(usableUtxos, difference, feeb)

    for (let i = 0; i < pickedUtxos.length; i++) {
      const utxo = pickedUtxos[i]
      txComposer.appendP2PKHInput({
        address: addressObj,
        txId: utxo.txId,
        outputIndex: utxo.outputIndex,
        satoshis: utxo.satoshis,
      })

      usableUtxos = usableUtxos.filter((u) => {
        return u.txId !== utxo.txId || u.outputIndex !== utxo.outputIndex
      })
    }

    const changeIndex = txComposer.appendChangeOutput(addressObj, feeb)
    const changeOutput = txComposer.getOutput(changeIndex)

    const mneObj = mvc.Mnemonic.fromString(mnemonic)
    const hdpk = mneObj.toHDPrivateKey('', network as any)

    const rootPath = getMvcRootPath()
    const basePrivateKey = hdpk.deriveChild(rootPath)
    
    const rootPrivateKey = mvc.PrivateKey.fromWIF(wallet.getPrivateKey())

    const toUsePrivateKeys = new Map<number, mvc.PrivateKey>()
    for (let i = 0; i < existingInputsLength; i++) {
      const input = txComposer.getInput(i)
      const prevTxId = input.prevTxId.toString('hex')
      if (txids.has(prevTxId)) {
        input.prevTxId = Buffer.from(txids.get(prevTxId)!, 'hex')
      }

      const inputAddress = mvc.Address.fromString(
        input.output!.script.toAddress().toString(),
        network as any
      ).toString()
      let deriver = 0
      let toUsePrivateKey: mvc.PrivateKey | undefined = undefined
      while (deriver < DERIVE_MAX_DEPTH) {
        const childPk = basePrivateKey.deriveChild(0).deriveChild(deriver)
        const childAddress = childPk.publicKey.toAddress(network as any).toString()

        if (childAddress === inputAddress.toString()) {
          toUsePrivateKey = childPk.privateKey
          break
        }

        deriver++
      }

      if (!toUsePrivateKey) {
        throw new Error(`Cannot find the private key of index #${i} input`)
      }

      toUsePrivateKeys.set(i, toUsePrivateKey)
    }

    toUsePrivateKeys.forEach((privateKey, index) => {
      txComposer.unlockP2PKHInput(privateKey, index)
    })

    pickedUtxos.forEach((v, index) => {
      txComposer.unlockP2PKHInput(rootPrivateKey, index + existingInputsLength)
    })

    const txid = txComposer.getTxId()
    txids.set(currentTxid, txid)

    payedTransactions.push(txComposer.serialize())

    if (changeIndex >= 0) {
      usableUtxos.push({
        txId: txComposer.getTxId(),
        outputIndex: changeIndex,
        satoshis: changeOutput.satoshis,
        address,
        height: -1,
      })
    }
  }

  return payedTransactions
}

async function createPinMvc(
  params: CreatePinParams,
  mnemonic: string,
  options?: WalletOptions
): Promise<CreatePinResult> {
  if (!mnemonic) {
    throw new Error(`mnemonic is null`)
  }

  const wallet = await getCurrentWallet(Chain.MVC, { mnemonic, addressIndex: options?.addressIndex })
  const network = mvc.Networks.livenet
  const address = wallet.getAddress()
  
  const toPayTransactions: { txComposer: string; message?: string }[] = []
  const txids: string[] = []
  
  for (let i = 0; i < params.dataList.length; i++) {
    const detail = params.dataList[i]
    const txComposer = new TxComposer()
    
    txComposer.appendP2PKHOutput({
      address: new mvc.Address(address, network as any),
      satoshis: 1,
    })
    
    let metaidData = normalizeMetaidData({ ...detail.metaidData })
    if (detail.options?.refs && metaidData.body) {
      metaidData.body = replaceRefs(metaidData.body, detail.options.refs, txids)
    }
    
    const opreturn = buildMvcOpReturn(metaidData)
    txComposer.appendOpReturnOutput(opreturn)
    
    if (detail.options?.service) {
      txComposer.appendP2PKHOutput({
        address: new mvc.Address(detail.options.service.address, network as any),
        satoshis: Number(detail.options.service.satoshis),
      })
    }
    
    if (detail.options?.outputs) {
      for (const output of detail.options.outputs) {
        txComposer.appendP2PKHOutput({
          address: new mvc.Address(output.address, network as any),
          satoshis: Number(output.satoshis),
        })
      }
    }
    
    txids.push(txComposer.getTxId())
    
    toPayTransactions.push({
      txComposer: txComposer.serialize(),
      message: `Create PIN: ${detail.metaidData.path || 'unknown'}`,
    })
  }
  
  if (params.noBroadcast) {
    const payedTxs = await payTransactions(mnemonic, toPayTransactions, true, params.feeRate, options)
    
    let totalCost = 0
    for (const txStr of payedTxs) {
      const tx = TxComposer.deserialize(txStr)
      const mvcTx = tx.tx
      
      const inputTotal = mvcTx.inputs.reduce((sum, input) => {
        return sum + (input.output?.satoshis || 0)
      }, 0)
      
      const outputTotal = mvcTx.outputs.reduce((sum, output) => {
        return sum + output.satoshis
      }, 0)
      
      totalCost += (inputTotal - outputTotal)
    }
    
    return {
      txHexList: payedTxs.map(tx => TxComposer.deserialize(tx).getRawHex()),
      totalCost,
    }
  }
  
  const payedTransactions = await payTransactions(
    mnemonic,
    toPayTransactions,
    true,
    params.feeRate,
    options
  )

  let totalCost = 0
  for (const txStr of payedTransactions) {
    const tx = TxComposer.deserialize(txStr)
    const mvcTx = tx.tx

    const inputTotal = mvcTx.inputs.reduce((sum, input) => {
      return sum + (input.output?.satoshis || 0)
    }, 0)

    const outputTotal = mvcTx.outputs.reduce((sum, output) => {
      return sum + output.satoshis
    }, 0)

    totalCost += (inputTotal - outputTotal)
  }

  const broadcastedTxids: string[] = []
  for (const txStr of payedTransactions) {
    const tx = TxComposer.deserialize(txStr)
    const txid = await broadcastTx(tx.getRawHex(), Chain.MVC)
    broadcastedTxids.push(txid)
  }
  
  return {
    txids: broadcastedTxids,
    totalCost,
  }
}

export async function createPin(
  params: CreatePinParams,
  mnemonic: string,
  options?: WalletOptions
): Promise<CreatePinResult> {
  if (!mnemonic) {
    throw new Error(`mnemonic is null`)
  }

  switch (params.chain) {
    case 'btc':
      throw new Error('BTC chain not yet supported')
    case 'doge':
      return await createPinDoge(params, mnemonic, options)
    case 'mvc':
      return await createPinMvc(params, mnemonic, options)
    default:
      throw new Error(`Unsupported chain: ${params.chain}`)
  }
}

/**
 * 创建 PIN (DOGE)
 */
async function createPinDoge(
  params: CreatePinParams,
  mnemonic: string,
  options?: WalletOptions
): Promise<CreatePinResult> {
  if (!mnemonic) {
    throw new Error(`mnemonic is null`)
  }

  const wallet = await getDogeWallet({
    mnemonic,
    addressIndex: options?.addressIndex,
  })
  const walletAddress = wallet.getAddress()
  let feeRate: number
  
  // 收集所有 service
  let globalService: Output | undefined
  
  for (const detail of params.dataList) {
    if (detail.options?.service && !globalService) {
      globalService = detail.options.service
    }
  }
  
  // 构建 metaidDataList
  const metaidDataList: DogeMetaidData[] = params.dataList.map(detail => {
    const metaidData = normalizeMetaidData({ ...detail.metaidData })
    return {
      ...metaidData,
      revealAddr: metaidData.revealAddr || walletAddress,
    }
  })

  if (!params.feeRate) {
    const feeRateRes = await fetchDogeFeeRates()
    if (feeRateRes.length) {
      feeRate = feeRateRes[0].feeRate
    } else {
      feeRate = 5000000
    }
  } else {
    feeRate = params.feeRate
  }
  
  // 调用 DOGE inscribe
  const result = await DogeInscribe.process({
    mnemonic,
    data: {
      metaidDataList,
      service: globalService,
      feeRate: feeRate,
      revealOutValue: params.dataList[0]?.options?.outputs?.[0] ? parseInt(params.dataList[0].options.outputs[0].satoshis) : undefined,
    },
    options: { noBroadcast: params.noBroadcast || false },
  })
  
  return result
}
