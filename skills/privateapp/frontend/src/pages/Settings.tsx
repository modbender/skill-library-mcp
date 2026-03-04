import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { pushSupported, isSubscribed, subscribePush, unsubscribePush } from '../pushUtils'

interface ToggleProps {
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
  label?: string
}

function Toggle({ checked, onChange, disabled, label }: ToggleProps) {
  return (
    <label className="toggle" style={{ opacity: disabled ? 0.5 : 1 }} aria-label={label}>
      <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} disabled={disabled} />
      <div className="toggle-track" />
      <div className="toggle-thumb" />
    </label>
  )
}

const TIMEZONES = [
  'America/Los_Angeles', 'America/Denver', 'America/Chicago', 'America/New_York',
  'America/Anchorage', 'Pacific/Honolulu', 'America/Phoenix',
  'America/Sao_Paulo', 'America/Argentina/Buenos_Aires', 'America/Mexico_City',
  'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Moscow',
  'Africa/Cairo', 'Africa/Johannesburg',
  'Asia/Dubai', 'Asia/Kolkata', 'Asia/Bangkok', 'Asia/Singapore',
  'Asia/Shanghai', 'Asia/Tokyo', 'Asia/Seoul',
  'Australia/Sydney', 'Pacific/Auckland',
  'UTC',
]

const LANGUAGES = [
  'English',
  'Chinese 中文',
  'Japanese 日本語',
  'Korean 한국어',
  'Spanish',
  'French',
  'German',
  'Portuguese',
  'Russian',
  'Arabic',
  'Hindi',
]

export default function Settings() {
  const navigate = useNavigate()
  const [pushOn, setPushOn] = useState(false)
  const [pushLoading, setPushLoading] = useState(false)
  const [testSent, setTestSent] = useState(false)
  const [timezone, setTimezone] = useState('America/Los_Angeles')
  const [language, setLanguage] = useState('English')

  useEffect(() => {
    if (pushSupported()) isSubscribed().then(setPushOn)
    fetch('/api/settings/preferences')
      .then(r => r.json())
      .then(data => {
        if (data.timezone) setTimezone(data.timezone)
        if (data.language) setLanguage(data.language)
      })
      .catch(() => {})
  }, [])

  const handlePushToggle = async (checked: boolean) => {
    setPushLoading(true)
    try {
      if (checked) { setPushOn(await subscribePush()) }
      else { await unsubscribePush(); setPushOn(false) }
    } finally { setPushLoading(false) }
  }

  const sendTest = async () => {
    await fetch('/api/push/test').catch(() => {})
    setTestSent(true)
    setTimeout(() => setTestSent(false), 3000)
  }

  const savePreference = (key: string, value: string) => {
    fetch('/api/settings/preferences', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ [key]: value }),
    }).catch(() => {})
  }

  const handleTimezoneChange = (value: string) => {
    setTimezone(value)
    savePreference('timezone', value)
  }

  const handleLanguageChange = (value: string) => {
    setLanguage(value)
    savePreference('language', value)
  }

  return (
    <div className="page">
      <div className="nav-bar">
        <button className="nav-btn" onClick={() => navigate('/')}>← Back</button>
        <div className="title">Settings</div>
        <div className="spacer" />
      </div>

      <div className="content" style={{ padding: '12px 16px' }}>
        {/* Push Notifications */}
        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>
          Notifications
        </div>
        <div className="stat-card" style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 15, fontWeight: 500 }}>Push Notifications</div>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 2 }}>
                {!pushSupported() ? 'Add to Home Screen from Safari to enable push notifications' : pushOn ? 'Enabled on this device' : 'Get alerts from the server'}
              </div>
            </div>
            {pushSupported() && <Toggle checked={pushOn} onChange={handlePushToggle} disabled={pushLoading} label="Push Notifications" />}
          </div>
          {pushOn && (
            <button className="btn btn-secondary btn-full" style={{ marginTop: 14 }} onClick={sendTest}>
              {testSent ? '✓ Sent!' : '🔔 Send Test Notification'}
            </button>
          )}
        </div>

        {/* Preferences */}
        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>
          Preferences
        </div>
        <div className="stat-card" style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '0.5px solid var(--border)' }}>
            <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>Timezone</span>
            <select
              value={timezone}
              onChange={e => handleTimezoneChange(e.target.value)}
              className="settings-select"
            >
              {TIMEZONES.map(tz => <option key={tz} value={tz}>{tz.replace(/_/g, ' ')}</option>)}
            </select>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0' }}>
            <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>Translate Language</span>
            <select
              value={language}
              onChange={e => handleLanguageChange(e.target.value)}
              className="settings-select"
            >
              {LANGUAGES.map(lang => <option key={lang} value={lang}>{lang}</option>)}
            </select>
          </div>
        </div>

        {/* About */}
        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>
          About
        </div>
        <div className="stat-card">
          <div style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--text-secondary)' }}>
            Private App is a personal app server for your server.
            Add to home screen for a native app experience.
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 10, fontStyle: 'italic' }}>
            🔒 Secured by Tailscale — no auth required
          </div>
        </div>
      </div>
    </div>
  )
}
