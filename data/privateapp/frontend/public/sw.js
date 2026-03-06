/* Private App Service Worker — handles push notifications and offline shell */

const CACHE_NAME = 'privateapp-v1'

self.addEventListener('install', () => {
  self.skipWaiting()
})

self.addEventListener('activate', event => {
  event.waitUntil(clients.claim())
})

/* Push notification handler */
self.addEventListener('push', event => {
  if (!event.data) return

  let data
  try {
    data = event.data.json()
  } catch {
    data = { title: 'Notification', body: event.data.text() }
  }

  const options = {
    body: data.body ?? '',
    icon: data.icon ?? '/icon-192.png',
    badge: '/icon-192.png',
    tag: data.tag ?? 'default',
    data: { url: data.url ?? '/' },
    vibrate: [200, 100, 200],
    requireInteraction: false,
  }

  event.waitUntil(
    self.registration.showNotification(data.title ?? 'Private App', options)
  )
})

/* Notification click → focus/open the app */
self.addEventListener('notificationclick', event => {
  event.notification.close()
  const urlPath = event.notification.data?.url ?? '/'
  // Build absolute URL (required for iOS PWA openWindow)
  const targetUrl = new URL(urlPath, self.location.origin).href

  event.waitUntil(
    clients
      .matchAll({ type: 'window', includeUncontrolled: true })
      .then(windowClients => {
        // Try to focus an existing PWA window and navigate it
        for (const client of windowClients) {
          if (new URL(client.url).origin === self.location.origin && 'focus' in client) {
            client.navigate(targetUrl)
            return client.focus()
          }
        }
        // No existing window — open a new one
        return clients.openWindow(targetUrl)
      })
  )
})
