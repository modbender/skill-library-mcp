import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { IconHarvest, IconCompound, IconRebalance, IconSuccess, IconError, IconTX, IconWhy } from '../icons';
export function ActivityFeed({ records, onSelectAction }) {
    const getActionCategory = (action) => {
        if (action.includes('HARVEST'))
            return 'harvest';
        if (action.includes('COMPOUND'))
            return 'compound';
        if (action.includes('REBALANCE'))
            return 'rebalance';
        return 'error';
    };
    const getActionIcon = (category) => {
        switch (category) {
            case 'harvest': return IconHarvest;
            case 'compound': return IconCompound;
            case 'rebalance': return IconRebalance;
            default: return IconError;
        }
    };
    const formatTime = (timestamp) => {
        const date = new Date(timestamp * 1000);
        const now = new Date();
        const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
        if (diff < 60)
            return `${diff}s ago`;
        if (diff < 3600)
            return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400)
            return `${Math.floor(diff / 3600)}h ago`;
        return date.toLocaleDateString();
    };
    if (records.length === 0) {
        return (_jsxs("div", { className: "card", children: [_jsx("div", { className: "card-header", children: _jsx("h3", { className: "card-title", children: "Activity Feed" }) }), _jsxs("div", { className: "empty-state", children: [_jsx("div", { className: "empty-state-icon", children: "\u23F3" }), _jsx("div", { className: "empty-state-text", children: "Waiting for first agent action..." }), _jsx("div", { className: "empty-state-subtext", children: "Activate the agent to start executing strategies" })] })] }));
    }
    return (_jsxs("div", { className: "card", children: [_jsxs("div", { className: "card-header", children: [_jsx("h3", { className: "card-title", children: "Activity Feed" }), _jsxs("span", { style: { fontSize: '12px', color: 'var(--text-muted)' }, children: [records.length, " actions"] })] }), _jsx("div", { className: "activity-feed", children: records.map((record, i) => {
                    const category = getActionCategory(record.action);
                    const Icon = getActionIcon(category);
                    const vaultId = record.vault_id || record.vault || 'Unknown Vault';
                    return (_jsxs("div", { className: `activity-item ${category}`, onClick: () => onSelectAction(record), children: [_jsxs("div", { className: "activity-header", children: [_jsxs("div", { className: "activity-action", children: [_jsx("div", { className: "activity-icon", children: _jsx(Icon, { size: 18, color: "currentColor" }) }), _jsxs("div", { children: [_jsx("div", { style: { fontWeight: '600', marginBottom: '2px' }, children: record.action }), _jsx("div", { style: { fontSize: '12px', color: 'var(--text-muted)' }, children: vaultId })] })] }), _jsx("div", { className: "activity-time", children: formatTime(record.timestamp) })] }), _jsxs("div", { className: "activity-details", children: [_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '6px' }, children: [record.status === 'success' && (_jsxs(_Fragment, { children: [_jsx(IconSuccess, { size: 14, color: "var(--success)" }), _jsx("span", { style: { color: 'var(--success)' }, children: "SUCCESS" })] })), record.status === 'error' && (_jsxs(_Fragment, { children: [_jsx(IconError, { size: 14, color: "var(--error)" }), _jsx("span", { style: { color: 'var(--error)' }, children: "ERROR" })] })), !record.status && (_jsx("span", { style: { color: 'var(--warning)' }, children: "SUGGESTED" }))] }), record.rewards_usd && (_jsxs("div", { style: { color: 'var(--success)', fontWeight: '600' }, children: ["+$", parseFloat(String(record.rewards_usd)).toFixed(2)] }))] }), _jsxs("div", { style: { display: 'flex', gap: '12px', alignItems: 'center' }, children: [_jsx("span", { className: "activity-vault", children: "Vault" }), _jsxs("div", { className: "activity-actions", children: [record.tx_hash && record.tx_hash !== 'null' && (_jsxs("a", { href: `https://testnet.bscscan.com/tx/${record.tx_hash}`, target: "_blank", rel: "noreferrer", className: "btn-secondary", onClick: (e) => e.stopPropagation(), title: "View transaction on BSCScan", children: [_jsx(IconTX, { size: 12 }), " View TX"] })), _jsxs("button", { className: "btn-secondary", onClick: (e) => {
                                                    e.stopPropagation();
                                                    onSelectAction(record);
                                                }, title: "View decision reasoning", children: [_jsx(IconWhy, { size: 12 }), " Why?"] })] })] })] }, i));
                }) })] }));
}
