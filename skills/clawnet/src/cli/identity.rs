use anyhow::Result;

use crate::identity;
use crate::output::{self, IdentityOutput};

pub fn run(json: bool) -> Result<()> {
    let key_path = crate::config::data_dir()?.join("identity.key");
    let created = !key_path.exists();
    let secret_key = identity::load_or_generate()?;
    let node_id = secret_key.public();

    output::print(
        &IdentityOutput {
            node_id: node_id.to_string(),
            created,
        },
        json,
    );
    Ok(())
}
