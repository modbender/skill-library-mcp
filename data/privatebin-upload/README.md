# privatebin-upload-skill

<p align="center">
  A skill that uploads content to any <a href="https://privatebin.info/">PrivateBin</a> instance and returns a shareable link.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://github.com/gearnode/privatebin"><img src="https://img.shields.io/badge/requires-privatebin--cli-orange" alt="requires: privatebin-cli"></a>
  <a href="https://github.com/KafCoppelia/privatebin-upload-skill"><img src="https://img.shields.io/badge/npx_skills_add-KafCoppelia%2Fprivatebin--upload--skill-brightgreen" alt="Install with skills"></a>
</p>

---

## Install Skill

```bash
npx skills add KafCoppelia/privatebin-upload-skill
```

## Requirements

- `privatebin` CLI — see [Install CLI](#install-cli) below
- A PrivateBin instance (default: `https://privatebin.net`, or self-hosted)

## Install CLI

| OS | Command |
|---|---|
| **macOS** | `brew install privatebin-cli` |
| **Arch Linux** | `yay -Sy privatebin-cli` (or `privatebin-cli-bin`) |
| **Ubuntu / Debian** | `apt install privatebin-cli` |
| **Prebuilt** | [Download from releases](https://github.com/gearnode/privatebin/releases/latest) |
| **Source** | `git clone https://github.com/gearnode/privatebin.git && cd privatebin && make && make install` |

### Configure

```bash
privatebin init                                        # default: privatebin.net
privatebin init --host https://bin.example.com         # custom host
privatebin init --host https://bin.example.com --force # overwrite existing
```

Config file (`~/.config/privatebin/config.json`):

```json
{
  "bin": [{ "name": "", "host": "https://bin.example.com" }],
  "expire": "1day",
  "formatter": "plaintext",
  "gzip": true
}
```

**Multiple instances** — define named entries, select with `--bin=<name>`:

```json
{
  "bin": [
    { "name": "",     "host": "https://privatebin.net" },
    { "name": "work", "host": "https://bin.example.com" }
  ]
}
```

Verify: `privatebin --version`

## Usage

Trigger naturally in conversation:

```
"Upload the report I just generated to paste"
"Upload this script and get a shareable link"
"Share this file with my colleague, expire in one week"
"Upload the report, burn after reading"
"Upload this code with password protection"
"Upload this file to my work instance"
```

## Options

| Option | Values | Default |
|---|---|---|
| `--expire` | 5min, 10min, 1hour, 1day, 1week, 1month, 1year, never | 1day |
| `--formatter` | plaintext, markdown, syntaxhighlighting | plaintext |
| `--burn-after-reading` | — | off |
| `--open-discussion` | — | off |
| `--password` | any string | none |
| `--gzip` | — | off |
| `--attachment` | — | off |
| `--bin` *(global)* | named instance from config | default |
| `--proxy` *(global)* | http/https/socks5 URL | none |

## Skill Definition

Agent instructions are in [SKILL.md](SKILL.md).

## License

MIT
