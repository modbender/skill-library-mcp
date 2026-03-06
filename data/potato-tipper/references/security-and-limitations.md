# Security + limitations (current posture)

## Status

- Contract is marked **experimental** and not formally audited by an external third party auditor.
- The repo contains AI-tool audit outputs under `audits/`.

## Key security design choices

- **Spoof resistance**: `universalReceiverDelegate` requires `sender == LSP26 Follower Registry` and re-validates follow/unfollow state against the registry.
- **EOA rejection**: only LSP0 accounts (🆙) are eligible to receive tips.
- **No revert strategy**: LSP26 notification flow should not be broken; contract returns user-friendly status bytes instead of reverting.
- **Transfer failure handling**: LSP7 transfer is wrapped in `try/catch`; if it fails, state is reverted (tipped flag cleared) and an event emitted.

## Known limitations (product-level)

- Existing followers (before install) are not eligible for tips; unfollow/refollow should not allow gaming.
- If a user tips someone, that recipient might unfollow later; the protocol does not “claw back” tips.

## Practical review checklist (when modifying)

- Any change touching `_tippedFollowers` / `_postInstallFollowers` / `_existingFollowersUnfollowedPostInstall` → re-run the whole follow/unfollow test matrix.
- Any change touching settings decoding → add explicit negative tests for malformed bytes.
- Any change touching token transfer path → re-check `try/catch` + emitted events and non-revert behavior.

