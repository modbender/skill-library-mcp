//! CLI module for SmithNode

use clap::{Parser, Subcommand};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "smithnode")]
#[command(author = "SmithNode Team")]
#[command(version = env!("CARGO_PKG_VERSION"))]
#[command(about = "P2P for AI agents. Proof of Cognition.", long_about = None)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Initialize a new SmithNode
    Init {
        /// Directory to store node data
        #[arg(short, long, default_value = ".smithnode")]
        data_dir: PathBuf,
    },
    
    /// Start the SmithNode (RPC + P2P, no validation)
    Start {
        /// Directory containing node data
        #[arg(short, long, default_value = ".smithnode")]
        data_dir: PathBuf,
        
        /// JSON-RPC bind address (use 0.0.0.0 for public access)
        #[arg(long, default_value = "127.0.0.1:26658")]
        rpc_bind: String,
        
        /// P2P bind address (use 0.0.0.0 for public access)
        #[arg(long, default_value = "0.0.0.0:26656")]
        p2p_bind: String,
        
        /// Bootstrap peer multiaddr (can be specified multiple times)
        #[arg(long = "peer", short = 'p')]
        peers: Vec<String>,
    },
    
    /// Start as a P2P VALIDATOR (true peer, no RPC dependency)
    /// This mode joins the P2P network directly and validates blocks
    Validator {
        /// Directory containing node data
        #[arg(short, long, default_value = ".smithnode")]
        data_dir: PathBuf,
        
        /// Path to validator keypair JSON file
        #[arg(long, short = 'k')]
        keypair: PathBuf,
        
        /// P2P bind address
        #[arg(long, default_value = "0.0.0.0:26656")]
        p2p_bind: String,
        
        /// Bootstrap peer multiaddr (required to join network)
        #[arg(long = "peer", short = 'p', required = true)]
        peers: Vec<String>,
        
        /// Also run RPC server (optional, for monitoring)
        #[arg(long)]
        rpc_bind: Option<String>,
        
        /// AI provider for cognitive challenges: ollama, openai, anthropic, groq, together
        /// REQUIRED — SmithNode is an AI blockchain, every validator must have AI
        #[arg(long)]
        ai_provider: Option<String>,
        
        /// AI API key (required for openai, anthropic, groq, together)
        #[arg(long)]
        ai_api_key: Option<String>,
        
        /// AI model name (e.g. llama2, gpt-4, claude-3-sonnet, llama-3.1-70b-versatile)
        #[arg(long)]
        ai_model: Option<String>,
        
        /// AI endpoint URL (for ollama: http://localhost:11434, or custom endpoints)
        #[arg(long)]
        ai_endpoint: Option<String>,
        
        /// Sequencer RPC URL for upgrade polling fallback
        /// Validators poll this URL to discover available upgrades when gossipsub
        /// doesn't deliver them (e.g. peer disconnects, late joiners).
        /// Defaults to https://smithnode-rpc.fly.dev
        #[arg(long, default_value = "https://smithnode-rpc.fly.dev")]
        sequencer_rpc: Option<String>,
    },
    
    /// Generate a new validator keypair
    Keygen {
        /// Output file for keypair (prints to stdout if not specified)
        #[arg(short, long)]
        output: Option<PathBuf>,
    },

    AnnounceNode {
        /// Path to operator keypair JSON file (must be in TRUSTED_OPERATOR_KEYS)
        #[arg(long, short = 'k')]
        keypair: PathBuf,
        
        /// New version string (semver, e.g. "0.6.0")
        #[arg(long)]
        version: String,

        /// Linux x86_64 binary download URL
        #[arg(long)]
        url_linux_x64: Option<String>,

        /// Linux x86_64 binary SHA256 checksum
        #[arg(long)]
        checksum_linux_x64: Option<String>,

        /// macOS Apple Silicon binary download URL
        #[arg(long)]
        url_darwin_arm64: Option<String>,

        /// macOS Apple Silicon binary SHA256 checksum
        #[arg(long)]
        checksum_darwin_arm64: Option<String>,

        /// macOS x86_64 binary download URL
        #[arg(long)]
        url_darwin_x64: Option<String>,

        /// macOS x86_64 binary SHA256 checksum
        #[arg(long)]
        checksum_darwin_x64: Option<String>,

        /// Linux ARM64 binary download URL
        #[arg(long)]
        url_linux_arm64: Option<String>,

        /// Linux ARM64 binary SHA256 checksum
        #[arg(long)]
        checksum_linux_arm64: Option<String>,
        
        /// Is this a mandatory upgrade? (peers may reject blocks from old versions)
        #[arg(long, default_value = "false")]
        mandatory: bool,
        
        /// Release notes
        #[arg(long)]
        notes: Option<String>,
        
        /// RPC endpoint of the running node to publish through
        #[arg(long, default_value = "http://127.0.0.1:26658")]
        rpc_url: String,
    },
}
