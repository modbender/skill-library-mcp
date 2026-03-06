import React, { useState } from 'react';

interface OperatorProps {
  onActivate: (profile: string) => void;
  isActive: boolean;
}

export function Operator({ onActivate, isActive }: OperatorProps) {
  const [selectedProfile, setSelectedProfile] = useState('balanced');
  const [showSaved, setShowSaved] = useState(false);
  
  const profiles = [
    { 
      id: 'conservative', 
      name: 'Conservative', 
      desc: 'Safe, steady growth',
      details: 'Lower yields, minimal risk exposure'
    },
    { 
      id: 'balanced', 
      name: 'Balanced', 
      desc: 'Moderate risk, good yields',
      details: 'Optimal risk-reward balance'
    },
    { 
      id: 'aggressive', 
      name: 'Aggressive', 
      desc: 'High-yield strategies',
      details: 'Maximum yield, higher volatility'
    }
  ];

  return (
    <div className="card hero-card">
      <div className="hero-content">
        <div className="hero-title">AI Yield Operator</div>
        <div className="hero-subtitle">
          Let autonomous AI manage your DeFi yield strategies with data-driven decision making.
        </div>

        <div className="profile-selector">
          <label className="profile-label">Risk Profile</label>
          <div className="profile-pills">
            {profiles.map(profile => (
              <button
                key={profile.id}
                className={`profile-pill ${selectedProfile === profile.id ? 'active' : ''}`}
                onClick={() => setSelectedProfile(profile.id)}
                title={profile.details}
              >
                <div className="profile-pill-name">{profile.name}</div>
                <div className="profile-pill-desc">{profile.desc}</div>
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={() => {
            onActivate(selectedProfile);
            setShowSaved(true);
            setTimeout(() => setShowSaved(false), 3000);
          }}
          className="btn-primary"
          style={{ marginTop: '20px' }}
        >
          Save Risk Profile
        </button>

        <div className="card" style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', marginTop: '16px', marginBottom: '0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <div style={{ 
              width: '12px', 
              height: '12px', 
              borderRadius: '50%', 
              background: 'var(--success)',
              animation: 'pulse 2s ease-in-out infinite'
            }}></div>
            <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--success)' }}>
              Agent Running Autonomously
            </div>
          </div>
          <div style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.6' }}>
            The AI agent is <strong>always active</strong> in the background, executing yield optimization strategies every 60 seconds.
            <br/>Current risk profile: <strong>{selectedProfile.charAt(0).toUpperCase() + selectedProfile.slice(1)}</strong>
          </div>
        </div>

        {showSaved && (
          <div className="activation-message" style={{ marginTop: '16px' }}>
            ✓ Risk profile updated to {selectedProfile}
          </div>
        )}
      </div>
    </div>
  );
}
