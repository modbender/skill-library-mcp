//! Build script to load operator keys from Cargo.toml metadata

use std::fs;

fn main() {
    // Read Cargo.toml
    let cargo_toml = fs::read_to_string("Cargo.toml")
        .expect("Failed to read Cargo.toml");
    
    let parsed: toml::Value = cargo_toml.parse()
        .expect("Failed to parse Cargo.toml");
    
    // Extract operator_keys from [package.metadata.smithnode]
    let keys = parsed
        .get("package")
        .and_then(|p| p.get("metadata"))
        .and_then(|m| m.get("smithnode"))
        .and_then(|s| s.get("operator_keys"))
        .and_then(|k| k.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|v| v.as_str())
                .collect::<Vec<_>>()
                .join(",")
        })
        .unwrap_or_default();
    
    // Output as compile-time environment variable
    println!("cargo:rustc-env=SMITHNODE_OPERATOR_KEYS_BUILTIN={}", keys);
    
    // Rerun if Cargo.toml changes
    println!("cargo:rerun-if-changed=Cargo.toml");
}
