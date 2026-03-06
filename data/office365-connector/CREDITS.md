# Credits & Attribution

## Original Skill

This skill is an enhanced version of the **Office 365 Connector** skill originally published on ClawHub.

- **Original Skill**: office365-connector v1.0.0
- **Original Author**: ClawHub Community
- **Source**: https://clawhub.com
- **Installed From**: ClawHub Registry

## Enhancements by Matt Gordon

**Version**: 2.0.0 (Multi-Account Enhanced)  
**Date**: February 2026  
**Author**: Matt Gordon (matt@workandthrive.ai)

### What's New in 2.0.0

This enhanced version adds comprehensive multi-account support, allowing users to manage multiple Microsoft 365 identities from a single skill installation.

**Major Additions:**
- Multi-account management system (`accounts.js`)
- Per-account token storage and isolation
- Account switching with `--account=` flag across all operations
- Default account selection
- Legacy single-account import
- Backward compatibility with environment-based configuration

**Enhanced Scripts:**
- `auth.js` - Multi-account authentication
- `email.js` - Multi-account email operations
- `calendar.js` - Multi-account calendar operations
- `send-email.js` - Send from specific accounts
- `cancel-event.js` - Cancel events from specific accounts

**New Documentation:**
- `MULTI-ACCOUNT.md` - Complete multi-account usage guide
- `CREDITS.md` - This file

### Original Code Preserved

All original functionality remains intact and fully compatible. Single-account users can continue using the skill exactly as before, with multi-account features available as optional enhancements.

## License

This enhanced version maintains compatibility with the original skill's licensing and adds no additional restrictions. All enhancements are provided as-is for the OpenClaw community.

## Acknowledgments

Thanks to the original skill creator for providing the foundation for Microsoft Graph API integration with OpenClaw, making this multi-account enhancement possible.
