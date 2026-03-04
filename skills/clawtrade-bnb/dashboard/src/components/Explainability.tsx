import React from 'react';
import { IconClose, IconSuccess, IconLink } from '../icons';

interface ExplainabilityProps {
  action: any;
  onClose: () => void;
}

export function Explainability({ action, onClose }: ExplainabilityProps) {
  if (!action) return null;

  const decision = action.decision || {};
  const confidence = (decision.confidence || 0.7) * 100;

  return (
    <div className="explainability-drawer">
      <div className="drawer-header">
        <h3 className="drawer-title">Why This Decision</h3>
        <button className="drawer-close" onClick={onClose}>
          <IconClose size={20} />
        </button>
      </div>

      <div className="drawer-content">
        {/* TIMESTAMP */}
        <div className="drawer-section">
          <div className="drawer-label">Decision Time</div>
          <div className="drawer-value">
            {new Date(action.timestamp * 1000).toLocaleString()}
          </div>
        </div>

        {/* ACTION SUMMARY */}
        <div className="drawer-section">
          <div className="drawer-label">Action</div>
          <div className="drawer-value" style={{ fontWeight: '600' }}>
            {action.action}
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px', fontWeight: 'normal' }}>
              Vault: {action.vault_id || action.vault || 'Unknown'}
            </div>
          </div>
        </div>

        {/* STATUS */}
        {action.status && (
          <div className="drawer-section">
            <div className="drawer-label">Status</div>
            <div className="drawer-value">
              {action.status === 'success' && (
                <span style={{ color: 'var(--success)' }}>✓ SUCCESS</span>
              )}
              {action.status === 'error' && (
                <span style={{ color: 'var(--error)' }}>✗ ERROR</span>
              )}
              {!action.status && (
                <span style={{ color: 'var(--warning)' }}>→ SUGGESTED</span>
              )}
            </div>
          </div>
        )}

        {/* RISK PROFILE */}
        <div className="drawer-section">
          <div className="drawer-label">Risk Profile</div>
          <div className="drawer-value" style={{ textTransform: 'capitalize' }}>
            {decision.profile || 'balanced'}
          </div>
        </div>

        {/* CONFIDENCE */}
        <div className="drawer-section">
          <div className="drawer-label">Confidence Score</div>
          <div className="confidence-bar">
            <div className="confidence-fill" style={{ width: `${confidence}%` }}></div>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '6px' }}>
            {confidence.toFixed(0)}% confident in this decision
          </div>
        </div>

        {/* RULES TRIGGERED */}
        {(decision.rules_triggered || []).length > 0 && (
          <div className="drawer-section">
            <div className="drawer-label">Rules Triggered</div>
            <div className="rules-list">
              {(decision.rules_triggered || []).map((rule: string, i: number) => (
                <div key={i} className="rule-item">
                  <IconSuccess size={12} color="var(--success)" style={{ marginRight: '6px' }} />
                  {rule}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* METRICS SNAPSHOT */}
        {decision.metrics_snapshot && (
          <div className="drawer-section">
            <div className="drawer-label">Metrics Snapshot</div>
            <div className="drawer-value" style={{ fontSize: '13px' }}>
              <div style={{ marginBottom: '8px' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Yield (USD)</div>
                <div style={{ fontWeight: '600', color: 'var(--success)' }}>
                  ${(decision.metrics_snapshot.yield_usd || 0).toFixed(2)}
                </div>
              </div>
              <div style={{ marginBottom: '8px' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Gas Cost (USD)</div>
                <div style={{ fontWeight: '600' }}>
                  ${(decision.metrics_snapshot.gas_usd || 0).toFixed(2)}
                </div>
              </div>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '11px' }}>APR Delta</div>
                <div style={{ fontWeight: '600', color: 'var(--primary-light)' }}>
                  {(decision.metrics_snapshot.delta_pct || 0).toFixed(2)}%
                </div>
              </div>
            </div>
          </div>
        )}

        {/* AGENT TRACE */}
        {(decision.agent_trace || []).length > 0 && (
          <div className="drawer-section">
            <div className="drawer-label">Agent Trace</div>
            <div>
              {(decision.agent_trace || []).map((trace: any, i: number) => (
                <div key={i} className="agent-trace-item">
                  <div className="agent-trace-name">{trace.agent}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    @ {new Date(trace.ts * 1000).toLocaleTimeString()}
                  </div>
                  <div className="agent-trace-message">{trace.message}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TRANSACTION HASH */}
        {action.tx_hash && action.tx_hash !== 'null' && (
          <div className="drawer-section">
            <div className="drawer-label">Transaction</div>
            <a
              href={`https://testnet.bscscan.com/tx/${action.tx_hash}`}
              target="_blank"
              rel="noreferrer"
              className="btn-secondary"
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', padding: '10px' }}
            >
              <IconLink size={14} />
              View on BSCScan
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
