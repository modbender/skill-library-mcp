import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
export function Operator({ onActivate, isActive }) {
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
    return (_jsx("div", { className: "card hero-card", children: _jsxs("div", { className: "hero-content", children: [_jsx("div", { className: "hero-title", children: "AI Yield Operator" }), _jsx("div", { className: "hero-subtitle", children: "Let autonomous AI manage your DeFi yield strategies with data-driven decision making." }), _jsxs("div", { className: "profile-selector", children: [_jsx("label", { className: "profile-label", children: "Risk Profile" }), _jsx("div", { className: "profile-pills", children: profiles.map(profile => (_jsxs("button", { className: `profile-pill ${selectedProfile === profile.id ? 'active' : ''}`, onClick: () => setSelectedProfile(profile.id), title: profile.details, children: [_jsx("div", { className: "profile-pill-name", children: profile.name }), _jsx("div", { className: "profile-pill-desc", children: profile.desc })] }, profile.id))) })] }), _jsx("button", { onClick: () => {
                        onActivate(selectedProfile);
                        setShowSaved(true);
                        setTimeout(() => setShowSaved(false), 3000);
                    }, className: "btn-primary", style: { marginTop: '20px' }, children: "Save Risk Profile" }), _jsxs("div", { className: "card", style: { background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', marginTop: '16px', marginBottom: '0' }, children: [_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }, children: [_jsx("div", { style: {
                                        width: '12px',
                                        height: '12px',
                                        borderRadius: '50%',
                                        background: 'var(--success)',
                                        animation: 'pulse 2s ease-in-out infinite'
                                    } }), _jsx("div", { style: { fontSize: '14px', fontWeight: '600', color: 'var(--success)' }, children: "Agent Running Autonomously" })] }), _jsxs("div", { style: { fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.6' }, children: ["The AI agent is ", _jsx("strong", { children: "always active" }), " in the background, executing yield optimization strategies every 60 seconds.", _jsx("br", {}), "Current risk profile: ", _jsx("strong", { children: selectedProfile.charAt(0).toUpperCase() + selectedProfile.slice(1) })] })] }), showSaved && (_jsxs("div", { className: "activation-message", style: { marginTop: '16px' }, children: ["\u2713 Risk profile updated to ", selectedProfile] }))] }) }));
}
