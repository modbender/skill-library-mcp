/**
 * Push notification utilities for Private App.
 */

let _reg: ServiceWorkerRegistration | null = null
let _regPromise: Promise<ServiceWorkerRegistration | null> | null = null

/** Register the service worker. */
export function registerSW(): Promise<ServiceWorkerRegistration | null> {
  if (!('serviceWorker' in navigator)) return Promise.resolve(null)
  if (!_regPromise) {
    _regPromise = navigator.serviceWorker
      .register('/sw.js')
      .then(reg => { _reg = reg; return reg })
      .catch(e => { console.error('SW registration failed:', e); return null })
  }
  return _regPromise
}

async function ensureSW(): Promise<ServiceWorkerRegistration | null> {
  if (_reg) return _reg
  return registerSW()
}

/** True if this browser supports push. */
export function pushSupported(): boolean {
  return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window
}

/** Is this device currently subscribed? */
export async function isSubscribed(): Promise<boolean> {
  const reg = await ensureSW()
  if (!reg) return false
  const sub = await reg.pushManager.getSubscription()
  return sub !== null
}

/** Subscribe this device to push notifications. Returns true on success. */
export async function subscribePush(): Promise<boolean> {
  const reg = await ensureSW()
  if (!reg) return false

  const permission = await Notification.requestPermission()
  if (permission !== 'granted') return false

  try {
    const resp = await fetch('/api/push/vapid-key')
    if (!resp.ok) throw new Error('No VAPID key')
    const { publicKey } = await resp.json() as { publicKey: string }

    const subscription = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: _urlBase64ToUint8Array(publicKey),
    })

    await fetch('/api/push/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(subscription.toJSON()),
    })
    return true
  } catch (e) {
    console.error('Push subscribe failed:', e)
    return false
  }
}

/** Unsubscribe this device from push notifications. */
export async function unsubscribePush(): Promise<boolean> {
  const reg = await ensureSW()
  if (!reg) return false
  try {
    const sub = await reg.pushManager.getSubscription()
    if (!sub) return true
    await sub.unsubscribe()
    await fetch('/api/push/unsubscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ endpoint: sub.endpoint }),
    })
    return true
  } catch (e) {
    console.error('Push unsubscribe failed:', e)
    return false
  }
}

function _urlBase64ToUint8Array(base64: string): Uint8Array {
  const padding = '='.repeat((4 - (base64.length % 4)) % 4)
  const b64 = (base64 + padding).replace(/-/g, '+').replace(/_/g, '/')
  const raw = atob(b64)
  const arr = new Uint8Array(raw.length)
  for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i)
  return arr
}
