## Send

The tool to send `ETH` or `USDC` on chain from the ETH address within web3b0x.

Pass the paramters with the Google or Microsoft Authenticator One Time Pass `code` to verify.

Parameters:
    
    code: Authenticator code in 6 digits. It will be valided for 5 minutes giving enough processing time for LLM, but can only be used for once.
    
    chain: Current support `base` only.
    
    token: Current support `ETH` and `USDC`.
    
    to_address: The ETH address we are sending to.
    
    amount: In decimal like `1.1` USDC stand for 1100000 in int with 6 decemal places. ETH has 18 decemals.
    
Quick one-liner
```bash
curl http://127.0.0.1:5333/send?code=[code]&chain=[chain]&to_address=[to_address]&token=[token]&amount=[amount]
```
    
    