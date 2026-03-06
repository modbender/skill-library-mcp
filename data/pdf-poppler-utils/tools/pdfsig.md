---
description: Verify digital signatures in PDF documents.
---
# pdfsig

Verify digital signatures in PDF documents.

## Synopsis

```
pdfsig [options] [PDF-file]
```

## Description

Pdfsig verifies digital signatures in PDF documents and prints information about them.

## When to Use

- To verify if a PDF is digitally signed
- To check signature validity
- To see who signed the document
- To validate timestamp information

## Common Options

| Option | Description |
|--------|-------------|
| `-nssdir [prefix]directory` | NSS database directory |
| `-nss-pwd password` | Password for NSS database |
| `-nocert` | Don't validate the certificate |
| `-no-ocsp` | Disable online OCSP certificate revocation check |
| `-no-appearance` | Don't add appearance info when signing |
| `-aia` | Enable Authority Information Access to fetch missing certificates |
| `-dump` | Dump all signatures to current directory |
| `-add-signature` | Add a new signature to the document |
| `-new-signature-field-name name` | Field name for new signature |
| `-sign field` | Sign in specified signature field |
| `-nick nickname` | Certificate nickname for signing |
| `-backend backend` | Specify cryptographic backend |
| `-kpw password` | Password for signing key |
| `-digest algorithm` | Digest algorithm (default: SHA256) |
| `-reason reason` | Reason string for signature |
| `-etsi` | Create ETSI.CAdES.detached signature |
| `-list-nicks` | List available nicknames in NSS database |
| `-list-backends` | List available cryptographic backends |
| `-opw password` | Owner password |
| `-upw password` | User password |
| `-v` | Print version information |
| `-h` | Print help information |

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | No error |
| 1 | Error opening PDF file |
| 2 | Error opening output file |
| 3 | PDF permissions error |
| 99 | Other error |

## Examples

```bash
# Check signatures
pdfsig document.pdf

# Verbose output
pdfsig -verbose document.pdf

# Without certificate details
pdfsig -nocert document.pdf
```
