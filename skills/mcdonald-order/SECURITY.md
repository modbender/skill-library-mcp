# Security Considerations

## ⚠️ Important Security Notice

This skill requires sensitive credentials and system access. Please review these security considerations before installation.

## Required Permissions

### 1. execute_bash Tool
**What it does**: Executes shell commands to make API calls via curl

**Why needed**: The skill uses curl to communicate with McDonald's MCP API

**Potential risks**:
- Can execute arbitrary bash commands
- Could be exploited if skill code is malicious
- Could leak credentials if compromised

**Mitigation**:
- Review SKILL.md source code before installation
- Only install from trusted sources
- Monitor skill behavior during use

### 2. MCD_TOKEN Environment Variable
**What it is**: Your personal McDonald's API authentication token

**Why needed**: Required to access your McDonald's account via API

**Potential risks**:
- If leaked, someone could access your McDonald's account
- Could be used to place orders or claim coupons without your permission
- May expose personal information (addresses, order history)

**Mitigation**:
- Never share your token publicly
- Rotate token regularly at https://mcp.mcd.cn
- Review skill code to ensure token is only used for legitimate API calls

## Code Transparency

### What the skill does with execute_bash:
```bash
# ONLY executes curl commands in this format:
curl -s -X POST "${MCD_MCP_URL:-https://mcp.mcd.cn}" \
  -H "Authorization: Bearer ${MCD_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{...},"id":1}'
```

### What the skill does NOT do:
- ❌ Does not send your token to any other domains
- ❌ Does not execute file system operations (rm, mv, etc.)
- ❌ Does not read or modify files outside the skill directory
- ❌ Does not install additional software
- ❌ Does not open network connections to untrusted servers

## Verification Steps

Before trusting this skill:

1. **Review the source code**
   ```bash
   cat ~/.kiro/skills/mcdonald-order/SKILL.md
   ```
   - Check all curl commands only target `mcp.mcd.cn`
   - Verify no suspicious bash commands
   - Confirm token is only used in Authorization headers

2. **Check the skill origin**
   - Official repository: https://github.com/anthropics/skills
   - Verify package integrity (checksums if available)
   - Check author reputation

3. **Test in isolated environment first**
   - Use a test token if possible
   - Monitor network traffic
   - Review all operations before confirming

## Trust Model

### When to trust this skill:
- ✅ Downloaded from official Anthropic skills repository
- ✅ Source code reviewed and understood
- ✅ No modifications to SKILL.md after download
- ✅ Using official MCD_TOKEN from mcp.mcd.cn

### When NOT to trust:
- ❌ Downloaded from unknown sources
- ❌ Source code contains obfuscated commands
- ❌ Requests tokens for services other than mcp.mcd.cn
- ❌ Modified by untrusted third parties

## Data Exfiltration Prevention

### How this skill protects your data:

1. **Hardcoded API endpoint**
   - Only communicates with `mcp.mcd.cn`
   - MCD_MCP_URL has a safe default
   - No dynamic URL construction from user input

2. **Token scope limitation**
   - Token only works with McDonald's MCP API
   - Cannot be used for other services
   - Limited to McDonald's account operations

3. **No data persistence**
   - Skill does not save tokens to disk
   - No logging of sensitive information
   - Temporary execution only

4. **User confirmation required**
   - All write operations require explicit user approval
   - Read-only queries can proceed without confirmation
   - Clear indication of what each operation does

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public GitHub issue
2. Contact the skill author privately
3. Provide details of the vulnerability
4. Allow time for a fix before public disclosure

## Alternative: Sandboxed Execution

For maximum security, consider:

1. **Use a dedicated API token**
   - Create a separate token just for this skill
   - Revoke it when not in use

2. **Run in a container**
   ```bash
   docker run --rm -it \
     -e MCD_TOKEN="your_token" \
     kiro-cli-image
   ```

3. **Monitor network traffic**
   ```bash
   # Use tcpdump or wireshark to verify connections
   sudo tcpdump -i any host mcp.mcd.cn
   ```

## Conclusion

This skill requires elevated permissions by design. The security risks are inherent to its functionality (making authenticated API calls). Only install if you:

- ✅ Trust the skill source
- ✅ Have reviewed the code
- ✅ Understand the risks
- ✅ Accept the security trade-offs

**When in doubt, do not install.**
