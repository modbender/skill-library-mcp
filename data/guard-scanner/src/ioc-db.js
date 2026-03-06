/**
 * guard-scanner — Indicators of Compromise (IoC) Database
 *
 * @security-manifest
 *   env-read: []
 *   env-write: []
 *   network: none
 *   fs-read: []
 *   fs-write: []
 *   exec: none
 *   purpose: IoC data definitions only — no I/O, pure data export
 *
 * Known malicious IPs, domains, URLs, usernames, filenames, and typosquats.
 * Sources: ClawHavoc campaign, Snyk ToxicSkills, Polymarket scams, community reports.
 *
 * Last updated: 2026-02-12
 */

const KNOWN_MALICIOUS = {
    ips: [
        '91.92.242.30',           // ClawHavoc C2
    ],
    domains: [
        'webhook.site',            // Common exfil endpoint
        'requestbin.com',          // Common exfil endpoint
        'hookbin.com',             // Common exfil endpoint
        'pipedream.net',           // Common exfil endpoint
        'ngrok.io',                // Tunnel (context-dependent)
        'download.setup-service.com', // ClawHavoc decoy domain
        'socifiapp.com',           // ClawHavoc v2 AMOS C2
    ],
    urls: [
        'glot.io/snippets/hfd3x9ueu5',  // ClawHavoc macOS payload
        'github.com/Ddoy233',            // ClawHavoc payload host
    ],
    usernames: ['zaycv', 'Ddoy233', 'Sakaen736jih'],   // Known malicious actors
    filenames: ['openclaw-agent.zip', 'openclawcli.zip'],
    typosquats: [
        // ClawHavoc campaign
        'clawhub', 'clawhub1', 'clawhubb', 'clawhubcli', 'clawwhub', 'cllawhub', 'clawdhub1',
        // Polymarket scams
        'polymarket-trader', 'polymarket-pro', 'polytrading',
        'better-polymarket', 'polymarket-all-in-one',
        // YouTube scams
        'youtube-summarize', 'youtube-thumbnail-grabber', 'youtube-video-downloader',
        // Misc
        'auto-updater-agent', 'yahoo-finance-pro', 'x-trends-tracker',
        'lost-bitcoin-finder', 'solana-wallet-tracker', 'rankaj',
        // Snyk ToxicSkills confirmed malicious
        'moltyverse-email', 'buy-anything', 'youtube-data', 'prediction-markets-roarin',
    ],
};

module.exports = { KNOWN_MALICIOUS };
