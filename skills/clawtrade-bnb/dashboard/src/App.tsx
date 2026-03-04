import { useState, useEffect } from 'react'
import { Sidebar } from './components/Sidebar'
import { Topbar } from './components/Topbar'
import { Operator } from './components/Operator'
import { AgentTeam } from './components/AgentTeam'
import { ActivityFeed } from './components/ActivityFeed'
import { PerformanceMetrics } from './components/PerformanceMetrics'
import { Explainability } from './components/Explainability'
import './design-system.css'

interface ExecutionRecord {
  timestamp: number
  action: string
  vault_id?: string
  vault?: string
  vault_name?: string
  tx_hash?: string
  confidence?: number
  rewards_usd?: number | string
  cycle?: number
  status?: string
  error?: string
  decision?: any
}

interface PerformanceMetricsData {
  totalHarvested: number
  totalCompounded: number
  realizedAPR: number | string
  vaults: Record<string, any>
}

export default function App() {
  const [records, setRecords] = useState<ExecutionRecord[]>([])
  const [metrics, setMetrics] = useState<PerformanceMetricsData | null>(null)
  const [status, setStatus] = useState('Connecting...')
  const [isActive, setIsActive] = useState(false)
  const [selectedAction, setSelectedAction] = useState<ExecutionRecord | null>(null)
  const [activeTab, setActiveTab] = useState('operator')

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        const apiBase = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3001'
        const res = await fetch(`${apiBase}/api/logs`)
        const data = await res.json()
        
        const validData = Array.isArray(data) ? data.filter((r: any) => r && r.action) : []
        setRecords(validData.slice(-20))
        
        if (validData.length > 0) {
          const harvested = validData
            .filter((r: any) => r.action?.includes('HARVEST'))
            .reduce((sum: number, r: any) => sum + (parseFloat(String(r.rewards_usd)) || 0), 0)
          
          const compounded = validData
            .filter((r: any) => r.action?.includes('COMPOUND'))
            .reduce((sum: number, r: any) => sum + (parseFloat(String(r.rewards_usd)) || 0), 0)
          
          setMetrics({
            totalHarvested: harvested,
            totalCompounded: compounded,
            realizedAPR: compounded > 0 ? ((compounded / 1000) * 365 * 100).toFixed(2) : '0',
            vaults: validData.reduce((acc: any, r: any) => {
              const id = r.vault_id || r.vault || 'unknown'
              if (!acc[id]) acc[id] = { actions: 0, rewards: 0 }
              acc[id].actions += 1
              acc[id].rewards += parseFloat(String(r.rewards_usd)) || 0
              return acc
            }, {})
          })
        }
        setStatus('Live')
      } catch (err) {
        console.error('Error:', err)
        setStatus('Error')
      }
    }
    fetchRecords()
    const interval = setInterval(fetchRecords, 30000)
    return () => clearInterval(interval)
  }, [])

  const getLastDecisionTime = (): number | undefined => {
    if (records.length > 0) {
      return records[records.length - 1].timestamp
    }
    return undefined
  }

  const successCount = records.filter(r => r.status === 'success').length
  const successRate = records.length > 0 ? (successCount / records.length) * 100 : 0

  return (
    <div className="app-container">
      {/* SIDEBAR */}
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* MAIN CONTENT */}
      <div className="main-content">
        {/* TOPBAR */}
        <Topbar 
          status={status} 
          isActive={isActive}
          lastDecisionTime={getLastDecisionTime()}
        />

        {/* MAIN PANEL */}
        <div className="main-panel">
          {/* OPERATOR TAB */}
          {activeTab === 'operator' && (
            <>
              <Operator 
                onActivate={(profile) => {
                  setIsActive(true)
                  console.log(`Agent activated with ${profile} profile`)
                }} 
                isActive={isActive}
              />
              <AgentTeam isActive={isActive} lastCycle={records[records.length - 1]} />
            </>
          )}

          {/* LIVE ACTIVITY TAB */}
          {activeTab === 'activity' && (
            <>
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Live Activity Stream</h3>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {records.length} total actions
                  </span>
                </div>
              </div>
              <ActivityFeed 
                records={records} 
                onSelectAction={setSelectedAction}
              />
            </>
          )}

          {/* ANALYTICS TAB */}
          {activeTab === 'analytics' && (
            <>
              <div style={{ marginBottom: '24px' }}>
                <h2 style={{ color: 'var(--text-primary)', marginBottom: '16px' }}>Analytics Dashboard</h2>
              </div>
              {metrics && (
                <PerformanceMetrics
                  totalHarvested={metrics.totalHarvested}
                  totalCompounded={metrics.totalCompounded}
                  realizedAPR={metrics.realizedAPR}
                  successRate={successRate}
                  totalActions={records.length}
                />
              )}
              <ActivityFeed 
                records={records} 
                onSelectAction={setSelectedAction}
              />
            </>
          )}

          {/* SETTINGS TAB */}
          {activeTab === 'settings' && (
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Settings</h3>
              </div>
              <div style={{ padding: '24px' }}>
                <div style={{ marginBottom: '20px' }}>
                  <h4 style={{ color: 'var(--text-muted)', marginBottom: '12px' }}>Network</h4>
                  <div style={{ padding: '12px', backgroundColor: 'var(--bg-hover)', borderRadius: 'var(--radius-md)', fontSize: '14px' }}>
                    BNB Testnet (0xae13d989daC2f0dEFF460025B5D3d3054f687FB4)
                  </div>
                </div>
                <div style={{ marginBottom: '20px' }}>
                  <h4 style={{ color: 'var(--text-muted)', marginBottom: '12px' }}>Execution Settings</h4>
                  <div style={{ padding: '12px', backgroundColor: 'var(--bg-hover)', borderRadius: 'var(--radius-md)', fontSize: '14px' }}>
                    <div style={{ marginBottom: '8px' }}>• Cycle Interval: 60 seconds</div>
                    <div style={{ marginBottom: '8px' }}>• Min Gas Balance: $0.05</div>
                    <div>• Auto-Reinvest: Enabled</div>
                  </div>
                </div>
                <div>
                  <h4 style={{ color: 'var(--text-muted)', marginBottom: '12px' }}>System Info</h4>
                  <div style={{ padding: '12px', backgroundColor: 'var(--bg-hover)', borderRadius: 'var(--radius-md)', fontSize: '12px', color: 'var(--text-muted)' }}>
                    <div style={{ marginBottom: '6px' }}>Status: {status}</div>
                    <div style={{ marginBottom: '6px' }}>Total Cycles: {records.length}</div>
                    <div>Success Rate: {successRate.toFixed(1)}%</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* DEFAULT VIEW: Show Operator + Metrics on top level */}
          {!['operator', 'activity', 'analytics', 'settings'].includes(activeTab) && (
            <>
              <Operator 
                onActivate={(profile) => {
                  setIsActive(true)
                  console.log(`Agent activated with ${profile} profile`)
                }} 
                isActive={isActive}
              />
              <AgentTeam isActive={isActive} lastCycle={records[records.length - 1]} />
              {metrics && (
                <PerformanceMetrics
                  totalHarvested={metrics.totalHarvested}
                  totalCompounded={metrics.totalCompounded}
                  realizedAPR={metrics.realizedAPR}
                  successRate={successRate}
                  totalActions={records.length}
                />
              )}
              <ActivityFeed 
                records={records} 
                onSelectAction={setSelectedAction}
              />
            </>
          )}
        </div>
      </div>

      {/* EXPLAINABILITY DRAWER */}
      {selectedAction && (
        <div>
          <div 
            style={{
              position: 'fixed',
              left: 0,
              top: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.6)',
              zIndex: 999
            }}
            onClick={() => setSelectedAction(null)}
          ></div>
          <Explainability 
            action={selectedAction} 
            onClose={() => setSelectedAction(null)}
          />
        </div>
      )}
    </div>
  )
}
