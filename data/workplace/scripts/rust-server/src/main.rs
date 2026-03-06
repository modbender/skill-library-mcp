use chrono::Utc;
use notify::{Config, RecommendedWatcher, RecursiveMode, Watcher};
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::env;
use std::fs;
use std::io::{self, BufRead, BufReader, Seek, SeekFrom};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::mpsc::channel;
use std::sync::Arc;
use std::time::Duration;

#[derive(Debug, Serialize, Deserialize)]
struct ChatMessage {
    timestamp: String,
    sender: String,
    recipient: String,
    broadcast: Vec<String>,
    message: String,
    line_number: usize,
}

#[derive(Debug, Serialize, Deserialize)]
struct ProcessStatus {
    #[serde(default)]
    server: ServerStatus,
}

#[derive(Debug, Serialize, Deserialize, Default)]
struct ServerStatus {
    status: String,
    pid: u32,
    #[serde(rename = "startedAt")]
    started_at: String,
    #[serde(rename = "lastEvent")]
    last_event: Option<String>,
    error: Option<String>,
}

fn parse_chat_line(line: &str) -> Option<ChatMessage> {
    // Pattern: [sender-to-recipient]: message
    // Pattern: [sender-to-recipient] @ [target1, target2]: message
    let re = Regex::new(
        r"^\[([a-zA-Z0-9_-]+)-to-([a-zA-Z0-9_-]+)\](?:\s*@\s*\[([^\]]*)\])?\s*:\s*(.+)$",
    )
    .ok()?;

    let caps = re.captures(line.trim())?;

    let sender = caps.get(1)?.as_str().to_string();
    let recipient = caps.get(2)?.as_str().to_string();

    let broadcast: Vec<String> = caps
        .get(3)
        .map(|m| {
            m.as_str()
                .split(',')
                .map(|s| s.trim().to_string())
                .filter(|s| !s.is_empty())
                .collect()
        })
        .unwrap_or_default();

    let message = caps.get(4)?.as_str().to_string();

    Some(ChatMessage {
        timestamp: Utc::now().to_rfc3339(),
        sender,
        recipient,
        broadcast,
        message,
        line_number: 0,
    })
}

fn write_process_status(workplace_dir: &Path, status: &str, error: Option<&str>) {
    let status_path = workplace_dir.join("process-status.json");

    // Read existing status or create new
    let mut proc_status: serde_json::Value =
        if let Ok(content) = fs::read_to_string(&status_path) {
            serde_json::from_str(&content).unwrap_or(serde_json::json!({}))
        } else {
            serde_json::json!({})
        };

    proc_status["server"] = serde_json::json!({
        "status": status,
        "pid": std::process::id(),
        "startedAt": Utc::now().to_rfc3339(),
        "lastEvent": Utc::now().to_rfc3339(),
        "error": error,
    });

    if let Ok(json) = serde_json::to_string_pretty(&proc_status) {
        let _ = fs::write(&status_path, json);
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        eprintln!("Usage: workplace-server <path-to-workplace-dir>");
        eprintln!("  Watches .workplace/chat.md for inter-agent messages");
        std::process::exit(1);
    }

    let workplace_dir = PathBuf::from(&args[1]);
    let wp_internal = workplace_dir.join(".workplace");
    let chat_file = wp_internal.join("chat.md");

    if !wp_internal.exists() {
        eprintln!(
            "Error: No .workplace directory found at {}",
            workplace_dir.display()
        );
        std::process::exit(1);
    }

    // Create chat.md if it doesn't exist
    if !chat_file.exists() {
        if let Err(e) = fs::write(&chat_file, "") {
            eprintln!("Error creating chat.md: {}", e);
            std::process::exit(1);
        }
    }

    // Graceful shutdown
    let running = Arc::new(AtomicBool::new(true));
    let r = running.clone();
    ctrlc::set_handler(move || {
        r.store(false, Ordering::SeqCst);
    })
    .expect("Error setting Ctrl-C handler");

    // Write initial status
    write_process_status(&wp_internal, "running", None);

    eprintln!(
        "🔄 Workplace server started — watching {}",
        chat_file.display()
    );

    // Track file position to only read new lines
    let mut last_pos: u64 = fs::metadata(&chat_file)
        .map(|m| m.len())
        .unwrap_or(0);
    let mut line_count: usize = BufReader::new(fs::File::open(&chat_file).unwrap_or_else(|_| {
        eprintln!("Error opening chat.md");
        std::process::exit(1);
    }))
    .lines()
    .count();

    // Set up file watcher
    let (tx, rx) = channel();

    let mut watcher: RecommendedWatcher =
        Watcher::new(tx, Config::default().with_poll_interval(Duration::from_millis(500)))
            .unwrap_or_else(|e| {
                eprintln!("Error creating watcher: {}", e);
                write_process_status(&wp_internal, "error", Some(&format!("{}", e)));
                std::process::exit(1);
            });

    if let Err(e) = watcher.watch(&chat_file, RecursiveMode::NonRecursive) {
        eprintln!("Error watching chat.md: {}", e);
        write_process_status(&wp_internal, "error", Some(&format!("{}", e)));
        std::process::exit(1);
    }

    while running.load(Ordering::SeqCst) {
        match rx.recv_timeout(Duration::from_secs(1)) {
            Ok(Ok(_event)) => {
                // File changed — read new lines
                let file = match fs::File::open(&chat_file) {
                    Ok(f) => f,
                    Err(e) => {
                        eprintln!("Error opening chat.md: {}", e);
                        continue;
                    }
                };

                let current_len = file.metadata().map(|m| m.len()).unwrap_or(0);

                if current_len < last_pos {
                    // File was truncated — reset
                    last_pos = 0;
                    line_count = 0;
                }

                if current_len > last_pos {
                    let mut reader = BufReader::new(&file);
                    if let Err(e) = reader.seek(SeekFrom::Start(last_pos)) {
                        eprintln!("Error seeking: {}", e);
                        continue;
                    }

                    let mut new_lines = Vec::new();
                    for line in reader.lines() {
                        match line {
                            Ok(l) => {
                                if !l.trim().is_empty() {
                                    new_lines.push(l);
                                }
                            }
                            Err(e) => {
                                eprintln!("Error reading line: {}", e);
                                break;
                            }
                        }
                    }

                    for line in &new_lines {
                        line_count += 1;
                        if let Some(mut msg) = parse_chat_line(line) {
                            msg.line_number = line_count;
                            if let Ok(json) = serde_json::to_string(&msg) {
                                println!("{}", json);
                                // Flush stdout for immediate output
                                use std::io::Write;
                                let _ = io::stdout().flush();
                            }
                        }
                    }

                    last_pos = current_len;

                    // Update status
                    write_process_status(&wp_internal, "running", None);
                }
            }
            Ok(Err(e)) => {
                eprintln!("Watch error: {}", e);
                write_process_status(
                    &wp_internal,
                    "error",
                    Some(&format!("Watch error: {}", e)),
                );
            }
            Err(std::sync::mpsc::RecvTimeoutError::Timeout) => {
                // Normal timeout — continue loop
            }
            Err(e) => {
                eprintln!("Channel error: {}", e);
                break;
            }
        }
    }

    eprintln!("🛑 Workplace server shutting down");
    write_process_status(&wp_internal, "stopped", None);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_simple_message() {
        let line = "[coder-to-reviewer]: Please review the auth module";
        let msg = parse_chat_line(line).unwrap();
        assert_eq!(msg.sender, "coder");
        assert_eq!(msg.recipient, "reviewer");
        assert!(msg.broadcast.is_empty());
        assert_eq!(msg.message, "Please review the auth module");
    }

    #[test]
    fn test_parse_broadcast_message() {
        let line = "[reviewer-to-coder] @ [developer, manager]: Approved with minor changes";
        let msg = parse_chat_line(line).unwrap();
        assert_eq!(msg.sender, "reviewer");
        assert_eq!(msg.recipient, "coder");
        assert_eq!(msg.broadcast, vec!["developer", "manager"]);
        assert_eq!(msg.message, "Approved with minor changes");
    }

    #[test]
    fn test_parse_single_broadcast() {
        let line = "[coder-to-reviewer] @ [developer]: Done with implementation";
        let msg = parse_chat_line(line).unwrap();
        assert_eq!(msg.broadcast, vec!["developer"]);
    }

    #[test]
    fn test_parse_invalid_line() {
        assert!(parse_chat_line("just some random text").is_none());
        assert!(parse_chat_line("").is_none());
        assert!(parse_chat_line("# Header").is_none());
    }

    #[test]
    fn test_parse_with_special_chars_in_message() {
        let line = "[agent1-to-agent2]: Check `src/main.rs` — found 3 issues!";
        let msg = parse_chat_line(line).unwrap();
        assert_eq!(msg.message, "Check `src/main.rs` — found 3 issues!");
    }
}
