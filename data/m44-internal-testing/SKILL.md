---
name: datahive-installer
description: "Install and set up DataHive in a deterministic headless-friendly flow: (1) check/install browser (Chrome or Chromium), (2) check/create DataHive browser profile, (3) check Gog mailbox access, (4) install DataHive extension via CRX only (never Chrome Web Store UI), (5) login via email magic link and verify both dashboard and extension are logged in. Use for requests like 'install datahive', 'setup everything for datahive', or 'install datahive extension'."
---

# DataHive Installer

Follow this exact sequence.

## Browser selection
- Select browser target first:
  - `BROWSER=chrome` for Google Chrome
  - `BROWSER=chromium` for Chromium
- Use the same browser target consistently in all script steps.

## 1) Check browser installation
- Run `BROWSER=<target> scripts/check_browser.sh`.
- If missing, install with:
  - `BROWSER=<target> scripts/install_browser.sh`
- Re-run browser check and continue only when target browser is confirmed.

## 2) Check DataHive browser profile
- Check whether browser profile `datahive` exists in OpenClaw config.
- If profile is missing, create profile `datahive` with CDP port `18810`.
- Continue only when profile `datahive` is available and startable.

## 3) Check Gog availability
- Verify Gog auth/account is available for the default mailbox.
- If Gog is unavailable, stop and report blocker:
  - User must set up Gog first.

## 4) Install DataHive extension via CRX only
- Use extension ID `bonfdkhbkkdoipfojcnimjagphdnfedb`.
- Do not use Chrome Web Store UI.
- Run:
  - `BROWSER=<target> scripts/install_extension_crx.sh bonfdkhbkkdoipfojcnimjagphdnfedb`
  - `scripts/install_extension_policy.sh bonfdkhbkkdoipfojcnimjagphdnfedb`
- Restart the `datahive` browser profile after script execution.
- Open `chrome://extensions/` in `datahive` profile and verify:
  - Extension card `DataHive` is visible
  - Extension is enabled/active
  - Browser shows managed/policy state when applicable
- If verification fails, stop and report extension-install blocker.

## 5) Login flow + final validation (required)
- Open DataHive login in `datahive` profile.
- Use email login only (no Google OAuth).
- Enter default email and click **Login with email**.
- Fetch latest DataHive magic-link email via Gog.
- Open `https://dashboard.datahive.ai/auth?token=...`.

After finishing the login flow, run this final validation exactly:
- Make sure you are in browser profile `datahive`.
- Confirm the dashboard is logged in while using browser profile `datahive`.
- Confirm the DataHive extension is installed in browser profile `datahive`.

## Completion Criteria
- Target browser is installed and runnable.
- `datahive` browser profile exists and runs.
- Gog mailbox access works.
- Login flow is completed via email magic link.
- Final validation passed:
  - Active profile is `datahive`.
  - Dashboard is logged in in `datahive` profile.
  - DataHive extension is installed in `datahive` profile.

## Resources
- `scripts/check_browser.sh`
- `scripts/install_browser.sh`
- `scripts/install_extension_crx.sh`
- `scripts/install_extension_policy.sh`
- `references/email-access.md`
