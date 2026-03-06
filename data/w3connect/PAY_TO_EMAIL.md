## Pay to email in PUSDC

The tool allow to send `USDC` without knowing the receipt address.
We need an on-chain call and then an API call to PUSDC.

Parameters:
    
    code: Authenticator code in 6 digits. It will be valided for 5 minutes giving enough processing time for LLM, but can only be used for once.
    
    chain: Current support `base` only.
    
    token: Current support `USDC` only.
    
    amount: In decimal like `1.1` USDC stand for 1100000 in int with 6 decemal places.
    
    to_email: The email address we are sending to.
    
    
The on-chain call deposit fund with a txNo return in curl json
```bash
curl http://127.0.0.1:5333/pay2email?code=[code]&chain=[chain]&token=[token]&amount=[amount]&to_email=[to_email]
```
    