use std::fs;
use std::path::PathBuf;

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};

const APP_NAME: &str = "clawnet";

/// Application configuration.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// Bot name for announcements
    #[serde(default = "default_name")]
    pub name: String,

    /// Announce interval in seconds for daemon mode
    #[serde(default = "default_announce_interval")]
    pub announce_interval: u64,

    /// TTL for peer cache entries in seconds
    #[serde(default = "default_peer_ttl")]
    pub peer_ttl: u64,

    /// Default discovery timeout in seconds
    #[serde(default = "default_discover_timeout")]
    pub discover_timeout: u64,

    /// Bot capabilities to advertise
    #[serde(default)]
    pub capabilities: Vec<String>,

    /// OpenClaw version string
    #[serde(default)]
    pub openclaw_version: Option<String>,

    /// Agent mode (shared, dedicated, local)
    #[serde(default)]
    pub mode: Option<String>,

    /// Custom metadata key-value pairs
    #[serde(default)]
    pub metadata: std::collections::HashMap<String, String>,

    /// UDP port for discovery probes (well-known port)
    #[serde(default = "default_discovery_port")]
    pub discovery_port: u16,
}

fn default_name() -> String {
    "clawnet-bot".to_string()
}

fn default_announce_interval() -> u64 {
    60
}

fn default_peer_ttl() -> u64 {
    300
}

fn default_discover_timeout() -> u64 {
    10
}

fn default_discovery_port() -> u16 {
    19851
}

impl Default for Config {
    fn default() -> Self {
        Self {
            name: default_name(),
            announce_interval: default_announce_interval(),
            peer_ttl: default_peer_ttl(),
            discover_timeout: default_discover_timeout(),
            capabilities: Vec::new(),
            openclaw_version: None,
            mode: None,
            metadata: std::collections::HashMap::new(),
            discovery_port: default_discovery_port(),
        }
    }
}

/// Get the configuration directory path.
pub fn config_dir() -> Result<PathBuf> {
    let dir = dirs::config_dir()
        .context("could not determine config directory")?
        .join(APP_NAME);
    Ok(dir)
}

/// Get the data directory path (for identity key, peer cache, etc).
pub fn data_dir() -> Result<PathBuf> {
    let dir = dirs::data_dir()
        .context("could not determine data directory")?
        .join(APP_NAME);
    Ok(dir)
}

/// Get the path to the config file.
fn config_path() -> Result<PathBuf> {
    Ok(config_dir()?.join("config.toml"))
}

/// Load configuration from disk, or return defaults.
pub fn load() -> Result<Config> {
    let path = config_path()?;
    if path.exists() {
        let contents = fs::read_to_string(&path).context("failed to read config file")?;
        let config: Config = toml::from_str(&contents).context("failed to parse config file")?;
        Ok(config)
    } else {
        Ok(Config::default())
    }
}

/// Save configuration to disk.
pub fn save(config: &Config) -> Result<()> {
    let path = config_path()?;
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).context("failed to create config directory")?;
    }
    let contents = toml::to_string_pretty(config).context("failed to serialize config")?;
    fs::write(&path, contents).context("failed to write config file")?;
    Ok(())
}

/// Reset configuration to defaults.
pub fn reset() -> Result<()> {
    save(&Config::default())
}

/// Set a single configuration value by key.
pub fn set_value(key: &str, value: &str) -> Result<Config> {
    let mut config = load()?;
    match key {
        "name" => config.name = value.to_string(),
        "announce_interval" => {
            config.announce_interval = value.parse().context("invalid number")?;
        }
        "peer_ttl" => {
            config.peer_ttl = value.parse().context("invalid number")?;
        }
        "discover_timeout" => {
            config.discover_timeout = value.parse().context("invalid number")?;
        }
        "openclaw_version" => {
            config.openclaw_version = Some(value.to_string());
        }
        "mode" => {
            config.mode = Some(value.to_string());
        }
        "discovery_port" => {
            config.discovery_port = value.parse().context("invalid port number")?;
        }
        _ => {
            if let Some(cap_key) = key.strip_prefix("metadata.") {
                config.metadata.insert(cap_key.to_string(), value.to_string());
            } else {
                anyhow::bail!("unknown config key: {key}");
            }
        }
    }
    save(&config)?;
    Ok(config)
}
