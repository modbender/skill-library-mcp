use anyhow::Result;

use crate::config;
use crate::output::{self, ConfigOutput, StatusMessage};

pub fn show(json: bool) -> Result<()> {
    let cfg = config::load()?;
    output::print(
        &ConfigOutput {
            name: cfg.name,
            announce_interval: cfg.announce_interval,
            peer_ttl: cfg.peer_ttl,
            discover_timeout: cfg.discover_timeout,
            capabilities: cfg.capabilities,
            openclaw_version: cfg.openclaw_version,
            mode: cfg.mode,
            metadata: cfg.metadata,
            discovery_port: cfg.discovery_port,
        },
        json,
    );
    Ok(())
}

pub fn set(key: &str, value: &str, json: bool) -> Result<()> {
    let cfg = config::set_value(key, value)?;
    if json {
        output::print(
            &ConfigOutput {
                name: cfg.name,
                announce_interval: cfg.announce_interval,
                peer_ttl: cfg.peer_ttl,
                discover_timeout: cfg.discover_timeout,
                capabilities: cfg.capabilities,
                openclaw_version: cfg.openclaw_version,
                mode: cfg.mode,
                metadata: cfg.metadata,
                discovery_port: cfg.discovery_port,
            },
            true,
        );
    } else {
        output::print(
            &StatusMessage {
                status: "ok".to_string(),
                message: Some(format!("set {key} = {value}")),
            },
            false,
        );
    }
    Ok(())
}

pub fn reset(json: bool) -> Result<()> {
    config::reset()?;
    output::print(
        &StatusMessage {
            status: "ok".to_string(),
            message: Some("configuration reset to defaults".to_string()),
        },
        json,
    );
    Ok(())
}
