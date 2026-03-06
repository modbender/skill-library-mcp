import React from 'react';
import { IconHarvest, IconCompound, IconRebalance, IconSuccess, IconError, IconTX, IconWhy } from '../icons';

interface ExecutionRecord {
  timestamp: number;
  action: string;
  vault_id?: string;
  vault?: string;
  tx_hash?: string;
  confidence?: number;
  status?: string;
  rewards_usd?: number | string;
}

interface ActivityFeedProps {
  records: ExecutionRecord[];
  onSelectAction: (action: ExecutionRecord) => void;
}

export function ActivityFeed({ records, onSelectAction }: ActivityFeedProps) {
  const getActionCategory = (action: string): 'harvest' | 'compound' | 'rebalance' | 'error' => {
    if (action.includes('HARVEST')) return 'harvest';
    if (action.includes('COMPOUND')) return 'compound';
    if (action.includes('REBALANCE')) return 'rebalance';
    return 'error';
  };

  const getActionIcon = (category: string) => {
    switch (category) {
      case 'harvest': return IconHarvest;
      case 'compound': return IconCompound;
      case 'rebalance': return IconRebalance;
      default: return IconError;
    }
  };

  const formatTime = (timestamp: number): string => {
    const date = new Date(timestamp * 1000);
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleDateString();
  };

  if (records.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Activity Feed</h3>
        </div>
        <div className="empty-state">
          <div className="empty-state-icon">⏳</div>
          <div className="empty-state-text">Waiting for first agent action...</div>
          <div className="empty-state-subtext">Activate the agent to start executing strategies</div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Activity Feed</h3>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          {records.length} actions
        </span>
      </div>
      <div className="activity-feed">
        {records.map((record, i) => {
          const category = getActionCategory(record.action);
          const Icon = getActionIcon(category);
          const vaultId = record.vault_id || record.vault || 'Unknown Vault';

          return (
            <div
              key={i}
              className={`activity-item ${category}`}
              onClick={() => onSelectAction(record)}
            >
              <div className="activity-header">
                <div className="activity-action">
                  <div className="activity-icon">
                    <Icon size={18} color="currentColor" />
                  </div>
                  <div>
                    <div style={{ fontWeight: '600', marginBottom: '2px' }}>
                      {record.action}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      {vaultId}
                    </div>
                  </div>
                </div>
                <div className="activity-time">{formatTime(record.timestamp)}</div>
              </div>

              <div className="activity-details">
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {record.status === 'success' && (
                    <>
                      <IconSuccess size={14} color="var(--success)" />
                      <span style={{ color: 'var(--success)' }}>SUCCESS</span>
                    </>
                  )}
                  {record.status === 'error' && (
                    <>
                      <IconError size={14} color="var(--error)" />
                      <span style={{ color: 'var(--error)' }}>ERROR</span>
                    </>
                  )}
                  {!record.status && (
                    <span style={{ color: 'var(--warning)' }}>SUGGESTED</span>
                  )}
                </div>
                {record.rewards_usd && (
                  <div style={{ color: 'var(--success)', fontWeight: '600' }}>
                    +${parseFloat(String(record.rewards_usd)).toFixed(2)}
                  </div>
                )}
              </div>

              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                <span className="activity-vault">Vault</span>

                <div className="activity-actions">
                  {record.tx_hash && record.tx_hash !== 'null' && (
                    <a
                      href={`https://testnet.bscscan.com/tx/${record.tx_hash}`}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-secondary"
                      onClick={(e) => e.stopPropagation()}
                      title="View transaction on BSCScan"
                    >
                      <IconTX size={12} /> View TX
                    </a>
                  )}
                  <button
                    className="btn-secondary"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectAction(record);
                    }}
                    title="View decision reasoning"
                  >
                    <IconWhy size={12} /> Why?
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
