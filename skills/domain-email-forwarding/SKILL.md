---
name: domain-email-forwarding
description: Set up email forwarding for custom domains to receive verification codes, password resets, and other emails at a domain you own but don't actively use for email. Covers GoDaddy, Namecheap, Cloudflare Email Routing, and ImprovMX. Use when recovering accounts linked to inactive domain emails, setting up catch-all forwarding, or routing domain email to Gmail/Outlook without paying for email hosting.
---

# Domain Email Forwarding

Route email from custom domains to accessible inboxes. Essential for account recovery when the original email is on a domain you own but don't actively host email for.

## When to Use

- Account recovery: target platform sent codes to `user@yourdomain.com` but email hosting is inactive
- Catch-all: forward ALL email for a domain to one inbox
- Cost savings: route domain email to Gmail without paying for email hosting
- Temporary: just need to receive one verification code, then revert

## Decision Matrix

| Registrar/DNS | Free Forwarding? | Setup Time | Notes |
|---|---|---|---|
| **GoDaddy** | ✅ Built-in | 5 min | Requires "Forwarding Status" toggle ON |
| **Cloudflare** | ✅ Email Routing | 10 min | DNS must be on Cloudflare |
| **Namecheap** | ✅ Built-in | 5 min | Up to 100 forwards free |
| **ImprovMX** | ✅ Free tier | 15 min | Works with any registrar, MX record change |
| **Google Workspace** | ❌ Paid | 30 min | Overkill for forwarding only |

## GoDaddy

### If Email Account Already Exists (e.g., Email Essentials plan)

1. Log into GoDaddy → `productivity.godaddy.com`
2. Go to **Admin → Email Forwarding** (sidebar)
3. Find domain section → click **edit** (pencil icon) on existing rule
4. Change "Forward mail to" → your Gmail/accessible email
5. Click **Save**
6. **CRITICAL:** Click **"Forwarding Status"** button → select domain → verify toggle is **ON**

### If No Email Account Exists (domain-only forwarding)

1. Log into GoDaddy → `account.godaddy.com/products`
2. Find domain → **Manage DNS**
3. GoDaddy may offer free email forwarding without a full email plan
4. Go to **Email Forwarding** section → Add rule

### Gotchas
- The per-user forwarding dialog (Manage → Forwarding) often gets stuck in a loading spinner. Use the **admin-level** forwarding page instead (`/#/admin/email/forwarding`)
- **Forwarding Status must be ON** for external addresses — this is a separate toggle, not automatic
- Changes take effect within 1-5 minutes (no DNS propagation needed since email account exists)

## Cloudflare Email Routing

Best option if your domain's DNS is already on Cloudflare.

### Setup
1. Cloudflare dashboard → select domain → **Email Routing**
2. Click **Enable Email Routing**
3. Cloudflare will add required MX and TXT records automatically
4. **Create routing rule:**
   - Custom address: `user@yourdomain.com`
   - Forward to: `your@gmail.com`
5. Cloudflare sends a verification email to the destination — click the link
6. Rule is active

### Catch-all
- Enable "Catch-all" to forward ALL addresses at the domain to one inbox
- Useful when you don't know the exact address that'll receive the code

### Gotchas
- Requires DNS to be on Cloudflare (nameservers)
- Destination email must be verified (click link in verification email)
- If MX records conflict with existing email hosting, Cloudflare will warn

## Namecheap

1. Log into Namecheap → Domain List → select domain
2. Click **"Email Forwarding"** tab (or Manage → Mail Settings)
3. Select "Email Forwarding" from dropdown
4. Add rule: `user` → `destination@gmail.com`
5. Save

### Gotchas
- Namecheap free forwarding handles up to 100 forwards
- MX records are auto-configured when you select Email Forwarding

## ImprovMX (Any Registrar)

Works with any domain registrar. Free tier: 25 forwards/day.

### Setup
1. Go to `improvmx.com` → enter your domain
2. Add forwarding alias: `user@yourdomain.com` → `destination@gmail.com`
3. ImprovMX provides MX records to add at your registrar:
   ```
   MX mx1.improvmx.com (priority 10)
   MX mx2.improvmx.com (priority 20)
   ```
4. Add MX records at your registrar's DNS settings
5. Wait for DNS propagation (5 min - 48 hours, usually fast)

### Gotchas
- Free tier: 25 emails/day, no sending (receive-only)
- DNS propagation can delay first email by minutes to hours
- Remove old MX records that conflict

## Verification Steps

After setting up forwarding, always verify before relying on it:

1. **Send a test email** from another account to `user@yourdomain.com`
2. Check destination inbox (and spam folder)
3. If test arrives → forwarding works → proceed with account recovery
4. If test doesn't arrive after 5 min:
   - Check Forwarding Status toggle (GoDaddy)
   - Check MX records are correct (`dig MX yourdomain.com`)
   - Check spam/junk folder at destination
   - Wait for DNS propagation if MX records were just changed

## Post-Recovery Cleanup

After recovering the target account:
- **Update the account's email** to your primary email (Gmail) so you don't need forwarding again
- **Decide on forwarding:** Keep it (useful for future emails to that domain) or revert to original settings
- **Document** the account's email and login method for future reference
