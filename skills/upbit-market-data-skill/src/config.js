const fs = require("fs");
const path = require("path");
const { UpbitError } = require("./upbit/errors");

const DEFAULT_PATH = path.join(__dirname, "..", "config", "config.json");

let cachedConfig = null;

function loadConfig() {
  if (cachedConfig) return cachedConfig;

  const configPath = process.env.UPBIT_SKILL_CONFIG
    ? path.resolve(process.env.UPBIT_SKILL_CONFIG)
    : DEFAULT_PATH;

  if (!fs.existsSync(configPath)) {
    throw new UpbitError(`Config file not found: ${configPath}`);
  }

  const raw = fs.readFileSync(configPath, "utf8");
  try {
    cachedConfig = JSON.parse(raw);
  } catch (err) {
    throw new UpbitError("Invalid JSON format in config file", { configPath });
  }

  return cachedConfig;
}

module.exports = { loadConfig };

