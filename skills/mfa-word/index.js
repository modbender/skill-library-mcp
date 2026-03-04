const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const STORE_PATH = path.join(process.env.HOME, '.openclaw/mfa_vault.json');
const LOG_PATH = path.join(process.env.HOME, '.openclaw/mfa_audit.log');

const hash = (word) => crypto.createHash('sha256').update(word).digest('hex');

let sessionState = {
    isUnlocked: false,
    expiry: 0
};

const logEvent = (action, result) => {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ACTION: ${action} | RESULT: ${result}\n`;
    if (!fs.existsSync(path.dirname(LOG_PATH))) fs.mkdirSync(path.dirname(LOG_PATH), { recursive: true });
    fs.appendFileSync(LOG_PATH, logEntry);
};

export const initialize_mfa = ({ secret, super_secret, sensitive_list, use_dead_mans_switch = false }) => {
    const data = {
        secret_hash: hash(secret),
        super_hash: hash(super_secret),
        sensitive_list: sensitive_list || [".env", "password", "config", "sudo"],
        dead_mans_switch: use_dead_mans_switch
    };
    if (!fs.existsSync(path.dirname(STORE_PATH))) fs.mkdirSync(path.dirname(STORE_PATH), { recursive: true });
    fs.writeFileSync(STORE_PATH, JSON.stringify(data));
    logEvent("INITIALIZATION", "SUCCESS");
    return `✅ MFA Word active. Mode: ${use_dead_mans_switch ? "Dead Man's Switch" : "15-min Window"}`;
};

export const verify_access = ({ word }) => {
    if (!fs.existsSync(STORE_PATH)) return "❌ MFA not configured.";
    const vault = JSON.parse(fs.readFileSync(STORE_PATH));
    
    if (hash(word) === vault.secret_hash) {
        sessionState.isUnlocked = true;
        sessionState.expiry = Date.now() + (15 * 60 * 1000);
        logEvent("CHALLENGE", "SUCCESS");
        return "🔓 Access Granted.";
    }
    logEvent("CHALLENGE", "FAILED_ATTEMPT");
    return "🚫 Incorrect Secret Word.";
};

export const check_gate_status = () => {
    if (!fs.existsSync(STORE_PATH)) return { status: "LOCKED" };
    const vault = JSON.parse(fs.readFileSync(STORE_PATH));

    if (sessionState.isUnlocked && Date.now() < sessionState.expiry) {
        if (vault.dead_mans_switch) {
            sessionState.isUnlocked = false;
            logEvent("AUTO_LOCK", "DEAD_MAN_SWITCH_TRIGGERED");
            return { status: "OPEN_ONCE" };
        }
        return { status: "OPEN" };
    }
    sessionState.isUnlocked = false;
    return { status: "LOCKED" };
};

export const reset_mfa = ({ super_word, new_secret }) => {
    const vault = JSON.parse(fs.readFileSync(STORE_PATH));
    if (hash(super_word) === vault.super_hash) {
        vault.secret_hash = hash(new_secret);
        fs.writeFileSync(STORE_PATH, JSON.stringify(vault));
        logEvent("RESET", "SUCCESS");
        return "🔄 Secret word successfully reset.";
    }
    logEvent("RESET", "FAILED_CRITICAL");
    return "💀 CRITICAL: Super Secret Word incorrect.";
};