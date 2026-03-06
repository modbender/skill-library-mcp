# Security guidance for the zotero skill

- Store your Zotero API key in an environment variable named ZOTERO_API_KEY. Avoid storing the key in plaintext files or committing to version control.
- Recommended (bash):
  export ZOTERO_API_KEY="<your_key_here>"

- For long-term automation, prefer OS keyrings (macOS Keychain, Windows Credential Manager, or a secrets manager).
- Logs should never include the value of ZOTERO_API_KEY or full contents of uploaded PDFs. Enable debug logging only when necessary and with awareness of sensitive data exposure.
- When sharing skill packages, remove any files that accidentally contain credentials.
