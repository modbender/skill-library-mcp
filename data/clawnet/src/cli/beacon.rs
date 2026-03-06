use anyhow::Result;
use serde_json::json;

use crate::identity;

/// Register this bot with a beacon registry via HTTP.
pub async fn register(
    url: &str,
    name: Option<String>,
    capabilities: Vec<String>,
    json_output: bool,
) -> Result<()> {
    let secret_key = identity::load_or_generate()?;
    let node_id = secret_key.public().to_string();
    let bot_name = name.unwrap_or_else(|| format!("clawnet-{}", &node_id[..8]));
    let caps = if capabilities.is_empty() {
        vec!["chat".to_string(), "openclaw".to_string()]
    } else {
        capabilities
    };

    let body = json!({
        "node_id": node_id,
        "name": bot_name,
        "capabilities": caps,
        "mode": "dedicated",
        "metadata": {}
    });

    let client = reqwest::Client::new();
    let res = client
        .post(format!("{}/api/bots/register", url.trim_end_matches('/')))
        .json(&body)
        .send()
        .await?;

    let status = res.status();
    let resp_body: serde_json::Value = res.json().await?;

    if json_output {
        println!(
            "{}",
            serde_json::to_string_pretty(&json!({
                "status": if status.is_success() { "ok" } else { "error" },
                "http_status": status.as_u16(),
                "node_id": node_id,
                "name": bot_name,
                "beacon_url": url,
                "response": resp_body,
            }))?
        );
    } else if status.is_success() {
        println!("Registered with beacon at {url}");
        println!("  Node ID: {node_id}");
        println!("  Name:    {bot_name}");
        println!("  Caps:    {}", caps.join(", "));
    } else {
        anyhow::bail!("Beacon returned {status}: {resp_body}");
    }

    Ok(())
}

/// Check beacon health/status.
pub async fn status(url: &str, json_output: bool) -> Result<()> {
    let client = reqwest::Client::new();
    let res = client
        .get(format!("{}/api/health", url.trim_end_matches('/')))
        .send()
        .await?;

    let body: serde_json::Value = res.json().await?;

    if json_output {
        println!("{}", serde_json::to_string_pretty(&body)?);
    } else {
        println!("Beacon: {url}");
        if let Some(status) = body.get("status").and_then(|v| v.as_str()) {
            println!("  Status:      {status}");
        }
        if let Some(node_id) = body.get("node_id").and_then(|v| v.as_str()) {
            println!("  Node ID:     {node_id}");
        }
        if let Some(active) = body.get("active_bots").and_then(|v| v.as_u64()) {
            println!("  Active bots: {active}");
        }
    }

    Ok(())
}
