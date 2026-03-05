# Platform Formatting

Use best judgement for the platform. Unless the user specifies otherwise, follow this guidance:

### Telegram

Always use the message tool with `media` for product image and `caption` with inline markdown links. Format: **bold title**, price, rating, brief feature. End with [View Product](url) • [Buy Now](url) links.

Example:

```
await message({
  media: "image.jpg",
  caption: `**Pro Earbuds**
💰 $49.99 | ⭐ 4.6/5

Wireless earbuds with 8-hour battery, deep bass boost.

[View Product](https://store.com/earbuds-x3) • [Buy Now](https://store.com/buy)`
});
```

### WhatsApp

Send product image as media message, followed by an interactive message with bold title, price, rating, short description. Use button templates for "View Store" and "Buy Now" links.

### iMessage

No markdown. iMessage renders plain text only — no bold, no italics, no `[link](url)` syntax. Send the product page URL as a bare link on its own line so iOS generates a rich link preview.

### General Rule

Always follow the formatting advice for Telegram, WhatsApp, iMessage and others.
