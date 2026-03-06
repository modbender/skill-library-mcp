# Certificate Format Conversions

## Common Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| PEM | .pem, .crt, .cer | Base64 encoded, most common for Linux/Unix |
| DER | .der, .cer | Binary format, common for Java/Windows |
| PKCS#12 | .p12, .pfx | Bundle with key + cert, password protected |
| PKCS#7 | .p7b | Certificate chain without private key |

## Conversion Commands

**PEM to DER:**
```bash
openssl x509 -outform der -in cert.pem -out cert.der
```

**DER to PEM:**
```bash
openssl x509 -inform der -in cert.der -out cert.pem
```

**PEM to PKCS#12 (for Windows/Java):**
```bash
openssl pkcs12 -export -out cert.pfx -inkey privkey.pem -in cert.pem -certfile chain.pem
```

**PKCS#12 to PEM:**
```bash
# Extract certificate
openssl pkcs12 -in cert.pfx -clcerts -nokeys -out cert.pem

# Extract private key
openssl pkcs12 -in cert.pfx -nocerts -out privkey.pem
```

**Extract from PKCS#7:**
```bash
openssl pkcs7 -print_certs -in cert.p7b -out cert.pem
```

## Combining Files

**Create full chain (for nginx):**
```bash
cat cert.pem intermediate.pem > fullchain.pem
```

**Verify key matches certificate:**
```bash
# These should output the same hash
openssl x509 -noout -modulus -in cert.pem | openssl md5
openssl rsa -noout -modulus -in privkey.pem | openssl md5
```
