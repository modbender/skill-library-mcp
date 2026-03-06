# Stegstr (ClawHub Skill)

Embed and decode hidden messages in PNG images. Steganographic Nostr client—works offline, no registration.

## Quick install

Requires [Rust](https://rustup.rs) and git.

```bash
git clone https://github.com/brunkstr/Stegstr.git
cd Stegstr/src-tauri && cargo build --release --bin stegstr-cli
```

Binary: `target/release/stegstr-cli` (Windows: `stegstr-cli.exe`)

Or use the optional `install.sh` script for a one-step install to `~/.local/bin`.

## Usage

| Command | Description |
|---------|-------------|
| `stegstr-cli decode image.png` | Extract raw payload from image |
| `stegstr-cli detect image.png` | Decode + decrypt, print bundle JSON |
| `stegstr-cli embed cover.png -o out.png --payload @bundle.json --encrypt` | Hide payload in image |
| `stegstr-cli post "message" --output bundle.json` | Create Nostr note bundle |

See [SKILL.md](./SKILL.md) for full documentation and examples.

## Links

- [stegstr.com](https://stegstr.com)
- [GitHub](https://github.com/brunkstr/Stegstr)
- [CLI docs](https://www.stegstr.com/wiki/cli.html)
- [For AI agents](https://www.stegstr.com/wiki/for-agents.html)
