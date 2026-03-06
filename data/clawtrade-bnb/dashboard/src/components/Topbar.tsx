import React from 'react';
import { IconActive } from '../icons';

interface TopbarProps {
  status: string;
  isActive?: boolean;
  lastDecisionTime?: number;
}

export function Topbar({ status, isActive = true, lastDecisionTime }: TopbarProps) {
  // Agent is ALWAYS active now (running in background)
  const agentActive = true;

  const getLastDecisionText = () => {
    if (!lastDecisionTime) return 'Never';
    const now = Date.now() / 1000;
    const secondsAgo = Math.round(now - lastDecisionTime);
    if (secondsAgo < 60) return `${secondsAgo}s ago`;
    if (secondsAgo < 3600) return `${Math.round(secondsAgo / 60)}m ago`;
    return `${Math.round(secondsAgo / 3600)}h ago`;
  };

  return (
    <div className="topbar">
      <div className="topbar-left">
        <div className={`topbar-badge ${agentActive ? 'status-running' : 'status-paused'}`}>
          <IconActive size={8} color={agentActive ? 'var(--success)' : 'var(--text-muted)'} />
          <span>🟢 Autonomous Mode Active</span>
        </div>

        <div className="topbar-badge" style={{ background: 'rgba(59, 130, 246, 0.1)', borderColor: 'rgba(59, 130, 246, 0.3)', color: 'var(--primary-light)' }}>
          <span>BNB Testnet</span>
        </div>

        <div className="topbar-badge" style={{ background: 'rgba(245, 158, 11, 0.1)', borderColor: 'rgba(245, 158, 11, 0.3)', color: 'var(--warning)' }}>
          <span>Last Decision: {getLastDecisionText()}</span>
        </div>
      </div>

      <div className="topbar-right">
        <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          Status: <span style={{ color: 'var(--success)', fontWeight: '600' }}>{status}</span>
        </div>
      </div>
    </div>
  );
}
