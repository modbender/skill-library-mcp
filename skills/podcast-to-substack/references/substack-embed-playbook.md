# Substack Embed Playbook

## Goal
Publish a post where the podcast player is an actual embed block, not plain link text.

## Rule 1: Never type Markdown embed code
Do not use iframe HTML or markdown links for the player.

## Rule 2: Use one of these two reliable methods

Method A (recommended): Duplicate the prepared Substack draft that already contains a working embed block.
- Open draft: `https://danielfoch.substack.com/publish/post/187957196`
- Duplicate it.
- Replace title/body content.
- Keep the existing embed block in place.

Method B: Insert a fresh embed block.
- In editor, add a new block (`+` menu or `/embed`).
- Paste the top-level Apple Podcasts show URL on its own.
- Press Enter and wait for unfurl.
- Confirm the block renders a player card (not plain URL text).

## URL to use for stable fallback
Use the show-level URL so it always plays the latest episode:
`https://podcasts.apple.com/ca/podcast/the-canadian-real-estate-investor/id1634197127`

## Verification checklist
- Player card is visible in editor before publish.
- URL is not inside a paragraph block.
- Publish preview still shows player card.
- Email distribution toggle is enabled.
