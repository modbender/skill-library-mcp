use clap::Parser;
use tracing_subscriber::EnvFilter;

use clawnet::cli::{self, BeaconAction, Command, ConfigAction, FriendAction};

#[tokio::main]
async fn main() {
    let args = cli::Cli::parse();

    // Initialize logging
    let filter = if args.verbose {
        EnvFilter::new("clawnet=debug,iroh=info,iroh_gossip=info")
    } else {
        EnvFilter::new("clawnet=warn")
    };
    tracing_subscriber::fmt()
        .with_env_filter(filter)
        .with_target(false)
        .init();

    let result = run(args).await;
    if let Err(e) = result {
        clawnet::output::print_error(&e, false);
        std::process::exit(1);
    }
}

async fn run(args: cli::Cli) -> anyhow::Result<()> {
    let json = args.json;

    match args.command {
        Command::Identity => {
            cli::identity::run(json)?;
        }
        Command::Config { action } => match action {
            ConfigAction::Show => cli::config_cmd::show(json)?,
            ConfigAction::Set { key, value } => cli::config_cmd::set(&key, &value, json)?,
            ConfigAction::Reset => cli::config_cmd::reset(json)?,
        },
        Command::Discover {
            timeout,
            max_peers,
        } => {
            cli::discover::run(timeout, max_peers, json).await?;
        }
        Command::Announce {
            name,
            capabilities,
            duration,
        } => {
            cli::announce::run(name, capabilities, duration, json).await?;
        }
        Command::Peers { online } => {
            cli::peers::run(online, json)?;
        }
        Command::Connect { node_id } => {
            cli::connect::run(&node_id, json).await?;
        }
        Command::Send { node_id, message } => {
            cli::send::run(&node_id, &message, json).await?;
        }
        Command::Friend { action } => match action {
            FriendAction::Add { node_id, alias } => {
                cli::friend::add(&node_id, alias.as_deref(), json)?;
            }
            FriendAction::Remove { node_id } => {
                cli::friend::remove(&node_id, json)?;
            }
            FriendAction::List => {
                cli::friend::list(json)?;
            }
        },
        Command::Ping { node_id, count } => {
            cli::ping::run(&node_id, count, json).await?;
        }
        Command::Chat { node_id } => {
            cli::chat::run(&node_id).await?;
        }
        Command::Daemon {
            interval,
            foreground,
        } => {
            cli::daemon_cmd::run(interval, foreground, json).await?;
        }
        Command::Status => {
            cli::status::run(json)?;
        }
        Command::Scan {
            range,
            timeout,
            concurrency,
            port,
        } => {
            cli::scan::run(&range, timeout, concurrency, port, json).await?;
        }
        Command::Beacon { action } => match action {
            BeaconAction::Register {
                url,
                name,
                capabilities,
            } => {
                cli::beacon::register(&url, name, capabilities, json).await?;
            }
            BeaconAction::Status { url } => {
                cli::beacon::status(&url, json).await?;
            }
        },
    }
    Ok(())
}
