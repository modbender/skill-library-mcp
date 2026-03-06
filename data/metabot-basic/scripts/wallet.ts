import * as bip39 from '@scure/bip39'
import { wordlist } from '@scure/bip39/wordlists/english'
import { Chain, MvcWallet, BtcWallet, DogeWallet, AddressType, CoinType, ScriptType, Net } from '@metalet/utxo-wallet-service'
import { networks } from 'bitcoinjs-lib'
import ECPairFactory from 'ecpair'
import * as ecc from '@bitcoinerlab/secp256k1'
import CryptoJS from 'crypto-js'
import { mvc } from 'meta-contract'
import { readAccountFile } from './utils'

// Re-export Chain for use in other modules
export { Chain }

/** 从 account.json 获取当前操作用户的 mnemonic 与 addressIndex（用于 signTransaction、pay 等内置方法） */
export function getMnemonicFromAccount(options?: { accountIndex?: number }): { mnemonic: string; addressIndex: number } {
  const data = readAccountFile()
  const index = options?.accountIndex ?? 0
  const item = data.accountList[index]
  if (!item?.mnemonic || item.mnemonic.trim() === '') {
    throw new Error(`account.json 中 accountList[${index}] 的 mnemonic 为空`)
  }
  const path = item.path
  const addressIndex = path != null ? parseAddressIndexFromPath(path) : 0
  return { mnemonic: item.mnemonic.trim(), addressIndex }
}

/** 异步返回当前网络（与 getNet 一致，便于与异步流程统一） */
export async function getNetwork(): Promise<Net> {
  return getNet()
}

/** signTransaction 的输入类型 */
export type ToSignTransaction = {
  txHex: string
  scriptHex: string
  inputIndex: number
  inputIndexes?: number[]
  satoshis: number
  sigtype?: number
  path?: string
  hasMetaId?: boolean
  dataDependsOn?: number
}

/**
 * 使用 account.json 当前操作用户对交易进行签名。
 * @param params.transaction 待签名输入信息
 * @param returnsTransaction 若为 true 返回已签名的 txHex 与 txid，否则返回 publicKey、r、s、sig、sigtype、txid
 * @param options.accountIndex 指定 accountList 下标，不传默认 0；addressIndex 可由 path 推导或由此覆盖
 */
export async function signTransaction(
  params: { transaction: ToSignTransaction },
  returnsTransaction: boolean = false,
  options: { addressIndex?: number; accountIndex?: number } = {}
): Promise<
  | { txHex: string; txid: string }
  | { publicKey: string; r: string; s: string; sig: string; sigtype: number; txid: string }
> {
  const { mnemonic, addressIndex: derivedIndex } = getMnemonicFromAccount({ accountIndex: options.accountIndex })
  const addressIndex = options.addressIndex ?? derivedIndex
  const network = getNet() as 'livenet' | 'testnet'
  const { txHex, scriptHex, inputIndex, satoshis, sigtype: sigtypeIn, path } = params.transaction

  const mneObj = mvc.Mnemonic.fromString(mnemonic)
  const mvcWallet = await getCurrentWallet(Chain.MVC, { mnemonic, addressIndex })
  const hdpk = mneObj.toHDPrivateKey('', network as any)
  const rootPath = getMvcRootPath()
  const derivePath = path ? `${rootPath}/${path}` : getPath({ accountIndex: options.accountIndex })
  const privateKey = hdpk.deriveChild(derivePath).privateKey
  const publicKey = privateKey.toPublicKey()

  let sigtype = sigtypeIn
  if (sigtype == null) {
    sigtype = mvc.crypto.Signature.SIGHASH_ALL | mvc.crypto.Signature.SIGHASH_FORKID
  }

  const BN = mvc.crypto.BN
  const tx = new mvc.Transaction(txHex)
  const sighash = mvc.Transaction.Sighash.sighash(
    tx,
    sigtype,
    inputIndex,
    new mvc.Script(scriptHex),
    new BN(satoshis)
  ).toString('hex')
  const sig = mvc.crypto.ECDSA.sign(Buffer.from(sighash, 'hex'), privateKey, 'little')

  if (returnsTransaction) {
    const signedScript = mvc.Script.buildPublicKeyHashIn(publicKey, sig, sigtype)
    tx.inputs[inputIndex].setScript(signedScript)
    return { txHex: tx.toString(), txid: tx.id }
  }
  return {
    publicKey: publicKey.toString(),
    r: sig.r.toString('hex'),
    s: sig.s.toString('hex'),
    sig: sig.set({ nhashtype: sigtype }).toTxFormat().toString('hex'),
    sigtype,
    txid: tx.id,
  }
}

// Core chains supported by @metalet/utxo-wallet-service
export type CoreChain = 'btc' | 'mvc'

// All supported chains including custom implementations
export type SupportedChain = CoreChain | 'doge'

export const METALET_HOST = 'https://www.metalet.space'

export async function getV3AddressType(chain: SupportedChain): Promise<AddressType> {
  const chainStr = String(chain)
  if (chainStr === 'mvc' || chainStr === Chain.MVC) {
    return AddressType.LegacyMvc
  } else if (chainStr === 'doge' || chainStr === Chain.DOGE) {
    return AddressType.DogeSameAsMvc
  }
  return AddressType.SameAsMvc
}

/** 新建 agent 时的默认 path，与 getPath 无 account 时的回退值一致 */
export const DEFAULT_PATH = `m/44'/10001'/0'/0/0`

/** 从 BIP44 path（如 m/44'/10001'/0'/0/0）解析出 addressIndex，解析失败返回 0 */
export function parseAddressIndexFromPath(path: string): number {
  if (!path || typeof path !== 'string') return 0
  const m = path.match(/\/0\/(\d+)$/)
  return m ? parseInt(m[1], 10) : 0
}

/** 根据索引构造标准 MVC 派生路径：index=1 -> m/44'/10001'/0'/0/1 */
export function buildPathFromIndex(index: number): string {
  const safeIndex = Number.isFinite(index) && index >= 0 ? Math.floor(index) : 0
  const base = DEFAULT_PATH.replace(/\/\d+$/, '/')
  return `${base}${safeIndex}`
}

export async function getCurrentWallet<T extends SupportedChain>(
  chain: T,
  options?: {
    mnemonic?: string
    /** 不传则使用 0 */
    addressIndex?: number
  }
): Promise<T extends Chain.BTC ? BtcWallet : T extends Chain.DOGE ? DogeWallet : MvcWallet> {
  const network = getNet() as Net
  let mnemonic = options?.mnemonic
  if (!mnemonic) {
    throw new Error(`mnemonic is null`)
  }
  const addressIndex = options?.addressIndex ?? 0
  const addressType = await getV3AddressType(chain)
  const chainStr = String(chain)
  if (chainStr === 'btc' || chainStr === Chain.BTC) {
    const coinType = addressType === AddressType.SameAsMvc ? CoinType.MVC : CoinType.BTC
    return new BtcWallet({ coinType, addressType, addressIndex, network, mnemonic }) as any
  } else if (chainStr === 'mvc' || chainStr === Chain.MVC) {
    const coinType = CoinType.MVC 
    return new MvcWallet({ coinType, addressType, addressIndex, network, mnemonic }) as any
  } else if (chainStr === 'doge' || chainStr === Chain.DOGE) {
    const coinType = addressType === AddressType.DogeSameAsMvc ? CoinType.MVC : CoinType.BTC
    return new DogeWallet({ coinType, addressType, addressIndex, network, mnemonic }) as any
  } else {
    throw new Error(`Chain ${chain} is not supported`)
  }
}

export interface GetDogeWalletOptions {
  mnemonic?: string
  password?: string
  addressIndex?: number
  addressType?: AddressType
  coinType?: number
}

// Get DOGE wallet
export async function getDogeWallet(options?: GetDogeWalletOptions): Promise<DogeWallet> {
  const network = getNet() as Net
  let mnemonic = options?.mnemonic
  if (!mnemonic) {
    throw new Error(`mnemonic is null`)
  }
  
  const addressIndex = options?.addressIndex ?? 0
  const addressType = options?.addressType ?? (await getV3AddressType(Chain.DOGE))
  
  // Use custom MVC coinType if addressType is DogeSameAsMvc
  // This ensures DOGE Default address follows user's custom MVC path
  const coinType = options?.coinType ?? CoinType.MVC 

  return new DogeWallet({
    mnemonic,
    network,
    addressIndex,
    addressType,
    coinType,
  })
}

// Get new mnemonic
export async function generateMnemonic(): Promise<string> {
  const mnemonic = bip39.generateMnemonic(wordlist)
  return mnemonic
}

// Get address for a specific chain
export async function getAddress(
  chain: SupportedChain = 'mvc',
  mnemonic: string,
  options?: { addressIndex?: number }
): Promise<string> {
  if (!mnemonic) {
    throw new Error(`mnemonic is null`)
  }

  if (chain === 'doge') {
    const wallet = await getDogeWallet({ mnemonic, addressIndex: options?.addressIndex })
    return wallet.getAddress()
  }
  const wallet = await getCurrentWallet(chain as CoreChain, { mnemonic, addressIndex: options?.addressIndex })
  return wallet.getAddress()
}

// Get all addresses (MVC, BTC, DOGE)
export async function getAllAddress(
  mnemonic: string,
  options?: { addressIndex?: number }
): Promise<{
  mvcAddress: string
  btcAddress: string
  dogeAddress: string
}> {
  if (!mnemonic) {
    throw new Error(`mnemonic is null`)
  }

  const addressIndex = options?.addressIndex
  const dogeWallet = await getDogeWallet({ mnemonic, addressIndex })
  const wallet = await getCurrentWallet(Chain.MVC, { mnemonic, addressIndex })
  return {
    mvcAddress: wallet.getAddress(),
    btcAddress: wallet.getAddress(),
    dogeAddress: dogeWallet.getAddress()
  }
}

// Get public key for MVC
export async function getPublicKey(
  chain: CoreChain = 'mvc',
  mnemonic: string,
  options?: { addressIndex?: number }
): Promise<string> {
  if (!mnemonic) {
    throw new Error(`mnemonic is null`)
  }

  const wallet = await getCurrentWallet(chain, { mnemonic, addressIndex: options?.addressIndex })
  return wallet.getPublicKey().toString('hex')
}

export function getNet(): Net {
  return 'livenet' as Net
}

/** 从 account.json 要操作的 accountList 项获取 path；新建 agent 时可通过 defaultPath 指定默认路径 */
export function getPath(options?: { accountIndex?: number; defaultPath?: string }): string {
  if (options?.defaultPath != null) {
    return options.defaultPath
  }
  try {
    const data = readAccountFile()
    const index = options?.accountIndex ?? 0
    const item = data.accountList[index]
    if (item?.path) return item.path
  } catch {
    /* ignore */
  }
  return DEFAULT_PATH
}

export function getMvcRootPath(): string {
  return `m/44'/10001'/0'/0`
}

// Get MetaID from address
export function getMetaId(address: string): string {
  return CryptoJS.SHA256(address).toString()
}

// Get credential for signing
export async function getCredential({
  mnemonic = '',
  chain = 'btc' as CoreChain,
  message = 'metalet.space',
  encoding = 'base64' as BufferEncoding,
  addressIndex,
}: {
  mnemonic: string
  chain?: CoreChain
  message?: string
  encoding?: BufferEncoding
  /** 不传则使用 0，可与 account.path 经 parseAddressIndexFromPath 得到 */
  addressIndex?: number
}): Promise<{ address: string; publicKey: string; signature: string }> {
  if (!mnemonic) {
    throw new Error(`mnemonic is null`)
  }

  const wallet = await getCurrentWallet(chain, { mnemonic, addressIndex })
  const signature = wallet.signMessage(message, encoding)

  return {
    signature,
    address: wallet.getAddress(),
    publicKey: wallet.getPublicKey().toString('hex'),
  }
}

// Get UTXOs for a chain
export async function getUtxos(
  chain: SupportedChain = 'mvc',
  mnemonic: string,
  options?: { addressIndex?: number }
) {
  if (!mnemonic) {
    throw new Error(`mnemonic is null`)
  }
  const address = await getAddress(chain, mnemonic, options)
  if (chain === 'mvc') {
    const { fetchMVCUtxos } = await import('./api')
    return await fetchMVCUtxos(address)
  } else if (chain === 'doge') {
    const { fetchDogeUtxos } = await import('./api')
    return await fetchDogeUtxos(address)
  } else {
    throw new Error(`Chain ${chain} not supported for getUtxos`)
  }
}
