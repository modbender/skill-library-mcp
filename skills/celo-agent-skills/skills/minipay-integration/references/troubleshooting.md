# MiniPay Troubleshooting

## Common Errors

### "Cannot read property of undefined"

**Cause:** Accessing `window.ethereum` before checking if it exists.

**Solution:** Always check for browser environment first:
```typescript
if (typeof window !== "undefined" && window.ethereum) {
  // Safe to use window.ethereum
}
```

### Transaction Fails Silently

**Cause:** MiniPay uses legacy transactions, EIP-1559 properties are ignored.

**Solution:** Don't include `maxFeePerGas` or `maxPriorityFeePerGas` in transactions. Viem handles this automatically when using Celo chains.

### "eth_sendTransaction not implemented"

**Cause:** Using HTTP transport instead of injected provider.

**Solution:** Use `custom(window.ethereum)` transport for wallet operations:
```typescript
// Wrong
const client = createWalletClient({
  chain: celo,
  transport: http("https://forno.celo.org"),
});

// Correct
const client = createWalletClient({
  chain: celo,
  transport: custom(window.ethereum),
});
```

### App Not Loading in MiniPay

**Possible causes:**
1. ngrok tunnel expired or restarted
2. Using HTTP instead of HTTPS
3. Mixed content errors

**Solutions:**
- Restart ngrok and get new URL
- Always use the HTTPS URL from ngrok
- Check browser console for mixed content warnings

### Gas Estimation Errors

**Cause:** Insufficient funds or invalid transaction parameters.

**Solutions:**
- Ensure account has sufficient balance for gas
- For fee currency transactions, ensure account has enough USDm
- Verify recipient address is valid
- Check token decimals (USDm uses 18, USDC/USDT use 6)

### Wallet Not Detected

**Cause:** App not running inside MiniPay webview.

**Solution:** Verify you're testing within MiniPay:
```typescript
console.log("Is MiniPay:", window.ethereum?.isMiniPay);
console.log("Provider exists:", !!window.ethereum);
```

### Transaction Pending Forever

**Cause:** Gas price too low or network congestion.

**Solutions:**
- Wait for network conditions to improve
- Increase gas price if setting manually
- Check transaction on Celoscan

### CORS Errors

**Cause:** Cross-origin requests blocked.

**Solution:** Configure your server to allow cross-origin requests or use appropriate headers in your framework configuration.

### Message Signing Not Working

**Note:** Message signing is not currently supported in MiniPay.

### EIP-1559 Errors

**Cause:** MiniPay only supports legacy transactions.

**Solution:** Don't pass `maxFeePerGas` or `maxPriorityFeePerGas`. Viem handles this automatically for Celo chains.

## Debugging Tips

### Check MiniPay Detection

```typescript
console.log("Is MiniPay:", window.ethereum?.isMiniPay);
console.log("Provider:", window.ethereum);
console.log("Accounts:", await window.ethereum?.request({
  method: "eth_accounts"
}));
```

### Remote Debugging with Chrome

1. Connect phone via USB
2. Enable USB debugging on phone
3. Open `chrome://inspect` in Chrome
4. Find your app's webview and click "inspect"

### Monitor ngrok Traffic

ngrok provides a local dashboard at `http://localhost:4040` where you can:
- See all incoming requests
- Inspect request/response headers
- Replay requests for debugging

## Testing Checklist

### Basic Functionality
- [ ] App loads in MiniPay webview
- [ ] Wallet address detected automatically
- [ ] Connect button hidden when in MiniPay
- [ ] Balance reads correctly

### Transactions
- [ ] Transactions submit successfully
- [ ] Transaction confirmation works
- [ ] Error handling displays properly
- [ ] Correct decimals for each token type

### Edge Cases
- [ ] Handle network errors gracefully
- [ ] Handle insufficient balance
- [ ] Handle user rejection
- [ ] Handle invalid addresses
