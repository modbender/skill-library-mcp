# Vision Hub — Sample Routing Logic

Paste this into your hub Discord channel's AGENTS.md (or merge with your existing one).

---

## 👁️ Vision Ingress Protocol

When you receive a message containing an image URL forwarded from WhatsApp (look for `[Ingress:WhatsApp]` prefix or a bare image URL), do the following:

1. **Do NOT** describe or analyze the image yourself
2. **Immediately** classify the image intent from the URL context or any accompanying text:
   - 🍷 **Wine** — bottle, label, glass, wine list
   - 🍵 **Tea** — tea tin, tea cake, tea leaves, packaging
   - 🚬 **Cigar** — cigar band, humidor, cigar box
   - 👤 **Contacts** — face, business card, name badge, event badge
   - 📄 **Other** — anything else; log it and ask for clarification
3. **Forward** using `sessions_send` to the matching specialist session key (configure these in your own workspace config)
4. **Reply** to confirm routing: e.g. "🍷 Routed to Wine Bot."

### Example routing call (adapt session keys to your own setup)

```
sessions_send(
  sessionKey = "<your-wine-channel-session-key>",
  message = "[Vision Router] New image.\nType: Wine\nImage: <image_url>\n\nINSTRUCTION: Post the image to the channel, then analyze and log to your database."
)
```

### Rules
- One classification per image — pick the most likely category
- If intent is ambiguous, default to **Other** and ask the user
- Never store the image URL yourself — forward it immediately
- All destination session keys must be pre-configured by the user; never infer or guess them
