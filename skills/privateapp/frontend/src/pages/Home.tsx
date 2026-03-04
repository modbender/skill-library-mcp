import { useEffect, useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

interface AppEntry {
  id: string
  name: string
  icon: string
  description: string
  url: string
}

interface AppsResponse {
  apps: Array<{
    id: string
    name: string
    icon: string
    description: string
    builtin: boolean
    enabled: boolean
    status: string
    url?: string
  }>
}

// iOS-style solid gradient backgrounds per app
const APP_GRADIENTS: Record<string, string> = {
  'system-monitor': 'linear-gradient(135deg, #007AFF, #5856D6)',
  'file-browser':   'linear-gradient(135deg, #5856D6, #AF52DE)',
}

const DEFAULT_GRADIENT = 'linear-gradient(135deg, #8E8E93, #636366)'

function sortApps(apps: AppEntry[], order: string): AppEntry[] {
  if (!order) return apps
  const ids = order.split(',').map(s => s.trim()).filter(Boolean)
  const map = new Map(apps.map(a => [a.id, a]))
  const sorted: AppEntry[] = []
  for (const id of ids) {
    const app = map.get(id)
    if (app) {
      sorted.push(app)
      map.delete(id)
    }
  }
  // Append any apps not in the order list
  for (const app of map.values()) sorted.push(app)
  return sorted
}

export default function Home() {
  const navigate = useNavigate()
  const [apps, setApps] = useState<AppEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [editMode, setEditMode] = useState(false)
  const [dragIdx, setDragIdx] = useState<number | null>(null)
  const [overIdx, setOverIdx] = useState<number | null>(null)
  const gridRef = useRef<HTMLDivElement>(null)
  const longPressTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const touchStartPos = useRef<{ x: number; y: number } | null>(null)

  useEffect(() => {
    Promise.all([
      fetch('/api/apps').then(r => r.json()),
      fetch('/api/settings/preferences').then(r => r.json()),
    ]).then(([appsData, prefs]: [AppsResponse, { app_order?: string }]) => {
      const enabled = (appsData.apps ?? [])
        .filter(a => a.enabled && a.status === 'active')
        .map(a => ({
          id: a.id,
          name: a.name,
          icon: a.icon,
          description: a.description,
          url: a.url ?? `/app/${a.id}/`,
        }))
      setApps(sortApps(enabled, prefs.app_order ?? ''))
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const saveOrder = useCallback((newApps: AppEntry[]) => {
    const order = newApps.map(a => a.id).join(',')
    fetch('/api/settings/preferences', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ app_order: order }),
    }).catch(() => {})
  }, [])

  const openApp = (url: string) => {
    if (editMode) return
    window.location.href = url
  }

  // Long press to enter edit mode
  const handleTouchStart = (idx: number, e: React.TouchEvent) => {
    const touch = e.touches[0]
    touchStartPos.current = { x: touch.clientX, y: touch.clientY }
    longPressTimer.current = setTimeout(() => {
      setEditMode(true)
      setDragIdx(idx)
      // Haptic feedback if available
      if (navigator.vibrate) navigator.vibrate(50)
    }, 500)
  }

  const handleTouchMove = (e: React.TouchEvent) => {
    // Cancel long press if finger moves too much
    if (longPressTimer.current && touchStartPos.current) {
      const touch = e.touches[0]
      const dx = Math.abs(touch.clientX - touchStartPos.current.x)
      const dy = Math.abs(touch.clientY - touchStartPos.current.y)
      if (dx > 10 || dy > 10) {
        clearTimeout(longPressTimer.current)
        longPressTimer.current = null
      }
    }

    if (dragIdx === null || !gridRef.current) return
    e.preventDefault()
    const touch = e.touches[0]
    const tiles = gridRef.current.querySelectorAll('.app-tile')
    for (let i = 0; i < tiles.length; i++) {
      const rect = tiles[i].getBoundingClientRect()
      if (touch.clientX >= rect.left && touch.clientX <= rect.right &&
          touch.clientY >= rect.top && touch.clientY <= rect.bottom) {
        setOverIdx(i)
        break
      }
    }
  }

  const handleTouchEnd = () => {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current)
      longPressTimer.current = null
    }
    if (dragIdx !== null && overIdx !== null && dragIdx !== overIdx) {
      const newApps = [...apps]
      const [moved] = newApps.splice(dragIdx, 1)
      newApps.splice(overIdx, 0, moved)
      setApps(newApps)
      saveOrder(newApps)
    }
    setDragIdx(null)
    setOverIdx(null)
  }

  // Desktop drag support
  const handleDragStart = (idx: number) => {
    if (!editMode) return
    setDragIdx(idx)
  }

  const handleDragOver = (idx: number, e: React.DragEvent) => {
    e.preventDefault()
    setOverIdx(idx)
  }

  const handleDrop = (idx: number) => {
    if (dragIdx !== null && dragIdx !== idx) {
      const newApps = [...apps]
      const [moved] = newApps.splice(dragIdx, 1)
      newApps.splice(idx, 0, moved)
      setApps(newApps)
      saveOrder(newApps)
    }
    setDragIdx(null)
    setOverIdx(null)
  }

  return (
    <div className="page">
      <div className="nav-bar">
        {editMode ? (
          <button
            className="nav-btn"
            onClick={() => setEditMode(false)}
            style={{ fontSize: 14, fontWeight: 600, color: 'var(--accent)' }}
          >
            Done
          </button>
        ) : (
          <div className="spacer" />
        )}
        <div className="title">Private App</div>
        <button
          className="nav-btn"
          onClick={() => editMode ? setEditMode(false) : navigate('/settings')}
          aria-label="Settings"
          style={{ fontSize: 20 }}
        >
          {editMode ? '' : '⚙️'}
        </button>
      </div>

      <div className="content">
        {loading ? (
          <div className="loading"><div className="spinner" /></div>
        ) : apps.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📦</div>
            <div className="empty-text">No apps installed</div>
          </div>
        ) : (
          <>
            <div className="app-grid" ref={gridRef} onTouchMove={handleTouchMove} onTouchEnd={handleTouchEnd}>
              {apps.map((app, idx) => (
                <button
                  key={app.id}
                  className={`app-tile ${editMode ? 'wiggle' : ''} ${dragIdx === idx ? 'dragging' : ''} ${overIdx === idx && dragIdx !== idx ? 'drop-target' : ''}`}
                  onClick={() => openApp(app.url)}
                  onTouchStart={(e) => handleTouchStart(idx, e)}
                  draggable={editMode}
                  onDragStart={() => handleDragStart(idx)}
                  onDragOver={(e) => handleDragOver(idx, e)}
                  onDrop={() => handleDrop(idx)}
                  onDragEnd={() => { setDragIdx(null); setOverIdx(null) }}
                  aria-label={app.name}
                >
                  <div
                    className="app-icon-wrap"
                    style={{ background: APP_GRADIENTS[app.id] || DEFAULT_GRADIENT }}
                  >
                    {app.icon}
                  </div>
                  <div className="app-name">{app.name}</div>
                </button>
              ))}
            </div>
            {!editMode && (
              <div style={{ textAlign: 'center', marginTop: 20, fontSize: 12, color: 'var(--text-secondary)' }}>
                Long press to reorder
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
