# Fluora Setup Skill - Update Summary

## Version 1.1.0 - GitHub Integration

### Changes Made

#### 1. Repository Source
- **Old:** Uses npm package `fluora-mcp@0.1.38`
- **New:** Clones from GitHub https://github.com/fluora-ai/fluora-mcp
- **Why:** npm version has parameter parsing bug; GitHub version (v0.1.39+) is fixed

#### 2. Installation Method
- **Old:** `npm install -g fluora-mcp` or `npx fluora-mcp`
- **New:** Clone → `npm install` → `npm run build` locally
- **Why:** Full control over version, dependencies, and build

#### 3. mcporter Configuration
- **Old:** 
  ```json
  {
    "command": "npx",
    "args": ["fluora-mcp"]
  }
  ```
- **New:**
  ```json
  {
    "command": "node",
    "args": ["/Users/USERNAME/.openclaw/workspace/fluora-mcp/build/index.js"]
  }
  ```
- **Why:** Points to local build with working parameter parsing

#### 4. Wallet Requirements
- **Old:** Only mentioned USDC
- **New:** Emphasizes USDC + ETH requirement
- **Why:** Users need ETH for gas fees (~$0.50 recommended)

#### 5. Setup Script (setup.js)
- Added `cloneFluoraMcp()` - clones from GitHub
- Added `installAndBuild()` - npm install + build
- Updated `configureMcporter()` - uses local path
- Enhanced error handling and verification

### Bug Fixed

**Issue:** `useService` always returns "Missing required parameters"

**Root Cause:** npm package v0.1.38 has incorrect schema definition:
```javascript
// Broken (npm)
const UseServiceSchema = {
  serviceId: z.string(),
  serverUrl: z.string(),
  ...
};
```

**Solution:** GitHub v0.1.39+ has correct schema that works with MCP SDK

**Impact:** All paid Fluora services now work correctly with payment confirmation

### Testing

Verified working:
- ✅ `exploreServices()` - Browse marketplace
- ✅ `useService()` - Execute services with payment
- ✅ PDF conversion ($0.02) - Success
- ✅ Screenshot (free testnet) - Success

### Installation

```bash
# For users
clawhub install chetan-guevara/fluora-setup

# Or run directly
cd ~/.openclaw/workspace/skills/fluora-setup
node setup.js
```

### Files Modified

1. `SKILL.md` - Complete rewrite with GitHub instructions
2. `setup.js` - New implementation with GitHub cloning
3. `package.json` - Updated dependencies and metadata
4. Published to ClawHub as v1.1.0

### Next Steps for Users

After running the updated setup:

1. **Fund wallet:**
   - $5-10 USDC (for services)
   - $0.50 ETH (for gas fees)
   - Network: Base

2. **Test connection:**
   ```bash
   mcporter call 'fluora-registry.exploreServices()'
   ```

3. **Use a service:**
   ```bash
   mcporter call 'fluora-registry.useService' --args '{
     "serviceId": "zyte-screenshot",
     "serverUrl": "https://pi5fcuvxfb.us-west-2.awsapprunner.com",
     "serverId": "c2b7baa1-771c-4662-8be4-4fd676168ad6",
     "params": {"url": "https://example.com"}
   }'
   ```

### Support

- GitHub Issues: https://github.com/fluora-ai/fluora-mcp/issues
- ClawHub: https://clawhub.ai/chetan-guevara/fluora-setup
- Fluora: https://fluora.ai
