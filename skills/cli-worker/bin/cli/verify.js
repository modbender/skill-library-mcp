import { getConfig } from "../config.js";
import { getProviderFromConfig, isValidProviderId, VALID_PROVIDER_IDS, } from "../providers/index.js";
export async function runVerify(cliFlag) {
    // Validate provider flag if provided
    if (cliFlag && !isValidProviderId(cliFlag)) {
        console.error(`✗ Unknown provider: ${cliFlag}`);
        console.error(`\nValid providers: ${VALID_PROVIDER_IDS.join(", ")}`);
        return 1;
    }
    const config = getConfig();
    const provider = getProviderFromConfig(config, cliFlag);
    const result = await Promise.resolve(provider.verify());
    if (result.ok) {
        console.log(`✓ ${provider.displayName} is installed and authenticated.`);
        return 0;
    }
    console.error("✗ Verification failed:", result.reason);
    if (result.detail)
        console.error("\n", result.detail);
    // Provider-specific help messages
    if (provider.id === "kimi") {
        console.error("\nTo fix:\n  1. Run: kimi\n  2. Type: /login\n  3. Complete browser OAuth\n  4. Verify with: cli-worker verify");
    }
    else if (provider.id === "claude") {
        console.error("\nTo fix:\n  1. Install Claude CLI: npm install -g @anthropic-ai/claude-code\n  2. Set API key: export ANTHROPIC_API_KEY=your_key\n  3. Verify with: cli-worker verify --provider claude");
    }
    else if (provider.id === "opencode") {
        console.error("\nTo fix:\n  1. Install OpenCode CLI\n  2. Authenticate: opencode auth login\n  3. Verify with: cli-worker verify --provider opencode");
    }
    return 1;
}
//# sourceMappingURL=verify.js.map