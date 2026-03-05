use clap::Parser;

#[derive(Parser)]
#[command(name = "clawnet", version, about = "P2P bot discovery for OpenClaw agents")]
pub struct Cli {
    /// Output in JSON format for machine parsing
    #[arg(long, global = true)]
    pub json: bool,

    /// Enable verbose logging
    #[arg(short, long, global = true)]
    pub verbose: bool,

    #[command(subcommand)]
    pub command: Command,
}

#[derive(clap::Subcommand)]
pub enum Command {
    /// Show or generate bot identity (NodeId)
    Identity,

    /// One-shot peer discovery scan
    Discover {
        /// Discovery timeout in seconds
        #[arg(long, default_value = "10")]
        timeout: u64,

        /// Maximum number of peers to discover
        #[arg(long)]
        max_peers: Option<usize>,
    },

    /// List cached peers
    Peers {
        /// Only show peers seen recently
        #[arg(long)]
        online: bool,
    },

    /// Broadcast presence to the network
    Announce {
        /// Bot name to announce
        #[arg(long)]
        name: Option<String>,

        /// Comma-separated list of capabilities
        #[arg(long, value_delimiter = ',')]
        capabilities: Vec<String>,

        /// Duration to keep announcing (seconds)
        #[arg(long, default_value = "30")]
        duration: u64,
    },

    /// Direct QUIC connection to a peer
    Connect {
        /// Target node ID
        node_id: String,
    },

    /// Send a message to a peer
    Send {
        /// Target node ID
        node_id: String,

        /// Message to send
        message: String,
    },

    /// Run continuous discovery daemon
    Daemon {
        /// Announce interval in seconds
        #[arg(long, default_value = "60")]
        interval: u64,

        /// Run in foreground (default)
        #[arg(long, default_value = "true")]
        foreground: bool,
    },

    /// Manage friends list
    Friend {
        #[command(subcommand)]
        action: FriendAction,
    },

    /// Ping a peer and measure round-trip time
    Ping {
        /// Target node ID
        node_id: String,

        /// Number of pings to send
        #[arg(short = 'c', default_value = "4")]
        count: u32,
    },

    /// Interactive chat with a peer
    Chat {
        /// Target node ID
        node_id: String,
    },

    /// Show network and daemon status
    Status,

    /// Configuration management
    Config {
        #[command(subcommand)]
        action: ConfigAction,
    },

    /// Interact with a ClawNet beacon registry
    Beacon {
        #[command(subcommand)]
        action: BeaconAction,
    },

    /// Scan IP ranges for ClawNet bots
    Scan {
        /// CIDR range (e.g. "192.168.1.0/24")
        range: String,

        /// Probe timeout in milliseconds
        #[arg(long, default_value = "1000")]
        timeout: u64,

        /// Max concurrent probes
        #[arg(long, default_value = "256")]
        concurrency: usize,

        /// Target port
        #[arg(long, default_value = "19851")]
        port: u16,
    },
}

#[derive(clap::Subcommand)]
pub enum FriendAction {
    /// Add a friend by node ID
    Add {
        /// Node ID of the friend
        node_id: String,
        /// Optional alias for this friend
        #[arg(long)]
        alias: Option<String>,
    },
    /// Remove a friend
    Remove {
        /// Node ID to remove
        node_id: String,
    },
    /// List all friends
    List,
}

#[derive(clap::Subcommand)]
pub enum ConfigAction {
    /// Show current configuration
    Show,
    /// Set a configuration value
    Set {
        /// Configuration key
        key: String,
        /// Configuration value
        value: String,
    },
    /// Reset configuration to defaults
    Reset,
}

#[derive(clap::Subcommand)]
pub enum BeaconAction {
    /// Register this bot with a beacon registry
    Register {
        /// Beacon URL (e.g. https://beacon.mylobster.ai)
        #[arg(long)]
        url: String,
        /// Bot name to register
        #[arg(long)]
        name: Option<String>,
        /// Comma-separated list of capabilities
        #[arg(long, value_delimiter = ',')]
        capabilities: Vec<String>,
    },
    /// Check beacon health/status
    Status {
        /// Beacon URL (e.g. https://beacon.mylobster.ai)
        #[arg(long)]
        url: String,
    },
}

pub mod announce;
pub mod beacon;
pub mod scan;
pub mod chat;
pub mod config_cmd;
pub mod connect;
pub mod daemon_cmd;
pub mod discover;
pub mod friend;
pub mod identity;
pub mod peers;
pub mod ping;
pub mod send;
pub mod status;
