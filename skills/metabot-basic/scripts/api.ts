import { Chain } from '@metalet/utxo-wallet-service'
import { getNet, getCredential } from './wallet'

// Re-export Chain for use in other modules
export { Chain }

const METALET_HOST = 'https://www.metalet.space'

interface RequestOption {
  method: 'GET' | 'POST'
  data?: any | string
  params?: Record<string, any>
  headers?: Headers
  mode?: RequestMode
  withCredential?: boolean
  message?: string
  body?: string | URLSearchParams
}

type OptionData = any
type OptionParams = Record<string, any>

async function request<T = any>(url: string, options: RequestOption & { mnemonic?: string }): Promise<T> {
  if (!options?.headers) {
    options.headers = new Headers()
  }
  if (options?.withCredential && options.mnemonic) {
    const { publicKey, signature } = await getCredential({ 
      message: options?.message || 'metalet.space',
      mnemonic: options.mnemonic
    })
    options.headers.set('X-Signature', signature)
    options.headers.set('X-Public-Key', publicKey)
  }
  if (options?.params) {
    let cleanedParams = Object.entries(options.params ?? {})
      .filter(([, value]) => value !== undefined)
      .reduce((acc, [key, value]) => ({ ...acc, [key]: value!.toString() }), {})
    if (options.method === 'GET') {
      const params = new URLSearchParams(cleanedParams)
      url = `${url}?${params.toString()}`
    } else {
      options.body = new URLSearchParams(cleanedParams)
    }
    delete options.params
    options.headers.set('Content-Type', 'application/x-www-form-urlencoded')
  }

  if (options?.data) {
    if (options.headers.get('Content-Type') === 'text/plain') {
      options.body = options.data as string
    } else {
      options.body = JSON.stringify(options.data)
      if (!options.headers.has('Content-Type')) {
        options.headers.set('Content-Type', 'application/json')
      }
    }
    delete options.data
  }

  const response = await fetch(url, options as any)
  if (!response.ok) {
    throw new Error(response.statusText)
  }
  const data = await response.text()
  try {
    return JSON.parse(data)
  } catch (error) {
    return data as T
  }
}

enum MetaletV3_CODE {
  SUCCESS = 0,
  FAILED = 1,
}

interface MetaletV3Result<T> {
  code: MetaletV3_CODE
  message: string
  data: T
  processingTime: number
}

export interface UTXO {
  txId: string
  outputIndex: number
  satoshis: number
  confirmed: boolean
  rawTx?: string
}

export type MvcUtxo = {
  flag: string
  address: string
  txid: string
  outIndex: number
  value: number
  height: number
}

const metaletV3Request = <T>(url: string, options: RequestOption & { mnemonic?: string }): Promise<T> =>
  request<MetaletV3Result<T>>(url, options).then((result) => {
    if (result.code === MetaletV3_CODE.FAILED) {
      throw new Error(result.message)
    }
    return result.data
  })

export const metaletApiV3 = <T>(path: string, options?: Partial<RequestOption & { mnemonic?: string }>) => {
  const metaletHost = METALET_HOST + '/wallet-api/v3'
  return {
    get: (params?: OptionParams) =>
      metaletV3Request<T>(`${metaletHost}${path}`, { method: 'GET', params, withCredential: true, ...options } as any),
    post: (data?: OptionData) =>
      metaletV3Request<T>(`${metaletHost}${path}`, { method: 'POST', data, withCredential: true, ...options } as any),
  }
}

export const metaletApiV4 = <T>(path: string, options?: Partial<RequestOption & { mnemonic?: string }>) => {
  const metaletHost = METALET_HOST + '/wallet-api/v4'
  return {
    get: (params?: OptionParams) =>
      metaletV3Request<T>(`${metaletHost}${path}`, { method: 'GET', params, withCredential: true, ...options } as any),
    post: (data?: OptionData) =>
      metaletV3Request<T>(`${metaletHost}${path}`, { method: 'POST', data, withCredential: true, ...options } as any),
  }
}

export const fetchMVCUtxos = async (address: string, useUnconfirmed = true): Promise<MvcUtxo[]> => {
  const net = getNet()
  let allUtxos: MvcUtxo[] = []
  let flag: string | undefined
  let hasMore = true

  while (hasMore) {
    try {
      const { list = [] } = await metaletApiV4<{ list: MvcUtxo[] }>('/mvc/address/utxo-list', {
        withCredential: false,
      }).get({
        address,
        net,
        flag,
      })

      if (list.length === 0) {
        hasMore = false
        break
      }

      flag = list[list.length - 1]?.flag
      const filteredList = list.filter((utxo) => utxo.value >= 600 && (useUnconfirmed || utxo.height > 0))
      allUtxos = [...allUtxos, ...filteredList]
    } catch (error) {
      console.error('Error fetching UTXOs:', error)
      hasMore = false
    }
  }

  return allUtxos
}

/** 获取 MVC 地址余额（satoshis） */
export async function getMvcBalance(address: string): Promise<number> {
  const utxos = await fetchMVCUtxos(address)
  return utxos.reduce((sum, u) => sum + (u.value || 0), 0)
}

export async function getBtcUtxos(address: string, needRawTx = false, useUnconfirmed = true): Promise<UTXO[]> {
  const net = getNet()
  let utxos =
    (await metaletApiV3<UTXO[]>('/address/btc-utxo', { withCredential: false }).get({
      net,
      address,
      unconfirmed: '1',
    })) || []

  utxos = utxos.filter((utxo) => utxo.satoshis >= 600)

  if (!useUnconfirmed) {
    utxos = utxos.filter((utxo) => utxo.confirmed)
  }
  if (needRawTx) {
    for (let utxo of utxos) {
      utxo.rawTx = await fetchBtcTxHex(utxo.txId, { withCredential: false })
    }
  }
  return utxos.sort((a, b) => {
    if (a.confirmed !== b.confirmed) {
      return b.confirmed ? 1 : -1
    }
    return a.satoshis - b.satoshis
  })
}

export const fetchBtcTxHex = async (
  txId: string,
  option?: {
    withCredential: boolean
  }
): Promise<string> => {
  const net = getNet()
  return metaletApiV3<{ rawTx: string }>(`/tx/raw`, option)
    .get({ net, txId, chain: 'btc' })
    .then((res) => res.rawTx)
}

// Get MVC rewards (gas subsidy)
export async function getMVCRewards(
  params: {
    address: string
    gasChain: 'mvc'
  },
): Promise<any> {
  const response = await fetch(
    'https://www.metaso.network/assist-open-api/v1/assist/gas/mvc/address-init',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    }
  )
  return response.json()
}

// Get MVC init rewards (with signature)
export async function getMVCInitRewards(
  params: {
    address: string
    gasChain: 'mvc'
  },
  signature: {
    'X-Signature': string
    'X-Public-Key': string
  },
  options?: { [key: string]: unknown }
): Promise<any> {
  const response = await fetch(
    'https://www.metaso.network/assist-open-api/v1/assist/gas/mvc/address-reward',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Signature': signature['X-Signature'] || '',
        'X-Public-Key': signature['X-Public-Key'] || '',
        ...(options?.headers || {}),
      },
      body: JSON.stringify(params),
      ...options,
    }
  )
  return response.json()
}

export function sleep(timer = 2000): Promise<void> {
  return new Promise<void>(resolve => {
    setTimeout(() => {
      resolve()
    }, timer)
  })
}

// Broadcast transaction
export const broadcastTx = async (rawTx: string, chain: Chain): Promise<string> => {
  const net = getNet()
  return await metaletApiV3<string>(`/tx/broadcast`).post({ chain, net, rawTx })
}

// DOGE related types and functions
export interface DogeUtxoListResponse {
  list: DogeUtxoApiItem[]
  total: number
}

export interface DogeUtxoApiItem {
  address: string
  txid: string
  outIndex: number
  value: number
  height: number
  flag?: string
}

export interface DogeUTXO {
  txId: string
  outputIndex: number
  satoshis: number
  address: string
  rawTx?: string
  confirmed?: boolean
  height?: number
}

export interface DogeFeeRate {
  title: string
  desc: string
  feeRate: number
}

export interface DogeFeeRateResponse {
  list: DogeFeeRate[]
}

/**
 * Fetch DOGE fee rates from API
 */
export async function fetchDogeFeeRates(): Promise<DogeFeeRate[]> {
  const net = getNet()
  
  const data = await metaletApiV4<DogeFeeRateResponse>('/doge/fee/summary', {
    withCredential: false,
  }).get({
    net,
  })

  return data.list
}

/**
 * Fetch DOGE UTXOs for an address
 */
export async function fetchDogeUtxos(
  address: string, 
  needRawTx: boolean = false
): Promise<DogeUTXO[]> {
  const net = getNet()
  
  const data = await metaletApiV4<DogeUtxoListResponse>('/doge/address/utxo-list', {
    withCredential: false,
  }).get({
    net,
    address,
  })

  const utxos: DogeUTXO[] = data.list.map((item) => ({
    txId: item.txid,
    outputIndex: item.outIndex,
    satoshis: item.value,
    address: item.address,
    height: item.height,
    confirmed: item.height > 0,
  }))

  // Fetch raw transaction data if needed
  if (needRawTx) {
    for (const utxo of utxos) {
      utxo.rawTx = await fetchDogeTxHex(utxo.txId)
    }
  }

  // Filter out dust UTXOs (less than 0.01 DOGE = 1000000 satoshis)
  return utxos.filter((utxo) => utxo.satoshis >= 1000000)
}

/**
 * Fetch DOGE transaction hex
 */
export async function fetchDogeTxHex(txId: string): Promise<string> {
  const net = getNet()
  return metaletApiV4<{ rawTx: string }>(`/doge/tx/raw`, {
    withCredential: false,
  }).get({ net, txId })
    .then((res) => res.rawTx)
}

/**
 * Broadcast DOGE transaction
 */
export async function broadcastDogeTx(rawTx: string): Promise<string> {
  const net = getNet()
  
  const data = await metaletApiV4<{ TxId: string }>('/doge/tx/broadcast', {
    withCredential: false,
  }).post({
    net,
    rawTx,
  })

  return data.TxId
}

/**
 * HttpRequest class for making HTTP requests using fetch
 */
export class HttpRequest {
  private baseUrl: string
  private options: any

  constructor(baseUrl: string, options: any = {}) {
    this.baseUrl = baseUrl
    this.options = options
  }

  private async makeRequest(
    method: string,
    url: string,
    data?: any,
    headers?: Record<string, string>
  ): Promise<any> {
    const fullUrl = url.startsWith('http') ? url : `${this.baseUrl}${url}`
    
    const requestHeaders = new Headers({
      'Content-Type': 'application/json',
      ...headers,
    })

    const requestOptions: RequestInit = {
      method,
      headers: requestHeaders,
    }

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      requestOptions.body = JSON.stringify(data)
    }

    try {
      const response = await fetch(fullUrl, requestOptions)
      
      // Handle response
      if (this.options.responseHandler) {
        // Parse JSON first, then pass to handler
        const data = await response.json()
        return await this.options.responseHandler({ ...response, data })
      }

      // Default response handling
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      // Handle error
      if (this.options.errorHandler) {
        return await this.options.errorHandler(error)
      }
      throw error
    }
  }

  get(url: string, headers?: Record<string, string>): Promise<any> {
    return this.makeRequest('GET', url, undefined, headers)
  }

  post(url: string, data?: any, headers?: Record<string, string>): Promise<any> {
    return this.makeRequest('POST', url, data, headers)
  }

  put(url: string, data?: any, headers?: Record<string, string>): Promise<any> {
    return this.makeRequest('PUT', url, data, headers)
  }

  delete(url: string, headers?: Record<string, string>): Promise<any> {
    return this.makeRequest('DELETE', url, undefined, headers)
  }
}

/**
 * UserInfo interface for MetaID user information
 */
export interface UserInfo {
  address: string
  avatar: string
  avatarPinId: string
  chatPublicKey: string
  chatPublicKeyId: string
  metaId: string
  globalMetaId?: string // 全局 MetaId，支持多链（MVC/BTC/DOGE）
  name: string
  namePinId: string
  chainName: string
}

// Create metafs API instance
const metafsApiInstance = new HttpRequest(
  'https://file.metaid.io/metafile-indexer/api',
  {
    // 自定义响应处理器（适配 MAN API 的响应格式）
    responseHandler: (response: any) => {
      return new Promise((resolve, reject) => {
        const { data } = response
        
        // MAN API 响应格式：{ code: 1, data: {...}, message: '...' }
        if (data && typeof data.code === 'number') {
          if (data.code === 0) {
            // 成功：返回 data 字段
            resolve(data.data)
          } else {
            // 失败：返回错误信息
            reject({
              code: data.code,
              message: data.message || '请求失败',
            })
          }
        } else {
          // 兼容其他格式，直接返回 data
          resolve(data.data || data)
        }
      })
    },
  }
)

// 导出 API 实例（保持原有的使用方式）
const metafsApi = {
  get: metafsApiInstance.get.bind(metafsApiInstance),
  post: metafsApiInstance.post.bind(metafsApiInstance),
  put: metafsApiInstance.put.bind(metafsApiInstance),
  delete: metafsApiInstance.delete.bind(metafsApiInstance),
}

/**
 * Get user info by address from MetaID service
 */
export const getUserInfoByAddressByMs = async (address: string): Promise<UserInfo> => {
  return metafsApi.get(`/v1/users/address/${address}`).then(res => {
    return res
  })
}
