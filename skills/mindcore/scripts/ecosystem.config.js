module.exports = {
    apps: [
        {
            name: "mind-engine",
            script: "engine_supervisor.py",
            interpreter: "python3",
            watch: false,
            autorestart: true,
            max_restarts: 10,
            env: {
                PYTHONUNBUFFERED: "1"
            }
        },
        {
            name: "mind-bridge",
            script: "js_bridge/OpenClawBridge.js",
            watch: false,
            autorestart: true,
            max_restarts: 10,
            env: {
                // 子铭的 Telegram Chat ID
                OPENCLAW_TARGET: "6755864404",
                // Path to openclaw CLI if it's not globally available in PATH
                OPENCLAW_COMMAND: "openclaw",
                MOCK_MODE: "false"
            }
        }
    ]
};
