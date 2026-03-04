# hex-vetter

Physical-layer hex auditing skill for AI agents. Detects hidden binary data, control characters, and encoding-based attacks.

## Features

- **Hex Dump Analysis** - View file contents in hexadecimal
- **Hidden Data Detection** - Scan for embedded payloads, magic bytes, steganography
- **Encoding Analysis** - Detect non-printable chars, null bytes, weird encodings
- **Self-Integrity** - Built-in tamper detection

## Installation

### Prerequisites

- Node.js 18+
- npm or pnpm

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/Matrix-Meta/hex-vetter.git
   cd hex-vetter
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   pnpm install
   ```

3. Verify installation:
   ```bash
   node -e "const { scanFile } = require('./vet.js'); console.log('OK');"
   ```

### As OpenClaw Skill

If using with OpenClaw, the skill is typically installed via:
```bash
clawhub install hex-vetter
# or copy to skills directory
```

## Usage

```javascript
const { scanFile } = require('./vet.js');
const result = await scanFile('/path/to/file.bin');
```

## Architecture

```
hex-vetter/
├── starfragment.js       # Core module
├── scan_all.js          # Recursive directory scanner
├── verify.js            # Integrity verification
├── vet.js               # Main entry
├── .gitignore
├── LICENSE              # GPLv3
├── README.md
└── SKILL.md            # Skill documentation
```

## How It Works

The module uses self-modifying storage - reading and writing data from/to its own file at runtime. Constants are encoded and stored as valid JavaScript comments at the end of the source file.

## License

GNU General Public License v3 (GPLv3)
