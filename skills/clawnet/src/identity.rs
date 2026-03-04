use std::fs;
use std::path::PathBuf;

use anyhow::{Context, Result};
use iroh::SecretKey;

use crate::config;

/// Get the path to the identity key file.
fn key_path() -> Result<PathBuf> {
    let dir = config::data_dir()?;
    Ok(dir.join("identity.key"))
}

/// Load an existing secret key or generate a new one.
pub fn load_or_generate() -> Result<SecretKey> {
    let path = key_path()?;
    if path.exists() {
        load_key(&path)
    } else {
        let key = SecretKey::generate(&mut rand::rng());
        save_key(&key, &path)?;
        Ok(key)
    }
}

/// Load a secret key from disk.
fn load_key(path: &PathBuf) -> Result<SecretKey> {
    let bytes = fs::read(path).context("failed to read identity key")?;
    let hex_str = String::from_utf8(bytes).context("identity key is not valid UTF-8")?;
    let key_bytes = data_encoding::HEXLOWER
        .decode(hex_str.trim().as_bytes())
        .context("identity key is not valid hex")?;
    let key_array: [u8; 32] = key_bytes
        .try_into()
        .map_err(|_| anyhow::anyhow!("identity key must be 32 bytes"))?;
    Ok(SecretKey::from_bytes(&key_array))
}

/// Save a secret key to disk with restricted permissions.
fn save_key(key: &SecretKey, path: &PathBuf) -> Result<()> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).context("failed to create data directory")?;
    }
    let hex = data_encoding::HEXLOWER.encode(&key.to_bytes());
    fs::write(path, hex.as_bytes()).context("failed to write identity key")?;

    // Set file permissions to 0600 (owner read/write only)
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(path, fs::Permissions::from_mode(0o600))
            .context("failed to set key file permissions")?;
    }

    Ok(())
}
