use anyhow::Result;

use crate::daemon;

pub async fn run(interval: u64, _foreground: bool, _json: bool) -> Result<()> {
    daemon::run(interval).await
}
