import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { IconActive } from '../icons';
export function Topbar({ status, isActive = true, lastDecisionTime }) {
    // Agent is ALWAYS active now (running in background)
    const agentActive = true;
    const getLastDecisionText = () => {
        if (!lastDecisionTime)
            return 'Never';
        const now = Date.now() / 1000;
        const secondsAgo = Math.round(now - lastDecisionTime);
        if (secondsAgo < 60)
            return `${secondsAgo}s ago`;
        if (secondsAgo < 3600)
            return `${Math.round(secondsAgo / 60)}m ago`;
        return `${Math.round(secondsAgo / 3600)}h ago`;
    };
    return (_jsxs("div", { className: "topbar", children: [_jsxs("div", { className: "topbar-left", children: [_jsxs("div", { className: `topbar-badge ${agentActive ? 'status-running' : 'status-paused'}`, children: [_jsx(IconActive, { size: 8, color: agentActive ? 'var(--success)' : 'var(--text-muted)' }), _jsx("span", { children: "\uD83D\uDFE2 Autonomous Mode Active" })] }), _jsx("div", { className: "topbar-badge", style: { background: 'rgba(59, 130, 246, 0.1)', borderColor: 'rgba(59, 130, 246, 0.3)', color: 'var(--primary-light)' }, children: _jsx("span", { children: "BNB Testnet" }) }), _jsx("div", { className: "topbar-badge", style: { background: 'rgba(245, 158, 11, 0.1)', borderColor: 'rgba(245, 158, 11, 0.3)', color: 'var(--warning)' }, children: _jsxs("span", { children: ["Last Decision: ", getLastDecisionText()] }) })] }), _jsx("div", { className: "topbar-right", children: _jsxs("div", { style: { fontSize: '13px', color: 'var(--text-muted)' }, children: ["Status: ", _jsx("span", { style: { color: 'var(--success)', fontWeight: '600' }, children: status })] }) })] }));
}
