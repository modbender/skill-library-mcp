# OAuth Pages for Whoop Integration

These HTML files are required when creating a Whoop Developer Application.

## Files

- **privacy.html** - Privacy policy page (required by Whoop)
- **redirect.html** - OAuth callback/redirect page (receives authorization code)

## How to Use

### Option 1: GitHub Pages (Recommended)

1. Create a new public GitHub repository (e.g., `whoop-oauth`)
2. Upload both HTML files to the repository
3. Go to Settings → Pages
4. Enable GitHub Pages (source: main branch, root folder)
5. Your URLs will be:
   - Privacy: `https://yourusername.github.io/whoop-oauth/privacy.html`
   - Redirect: `https://yourusername.github.io/whoop-oauth/redirect.html`

### Option 2: Your Own Domain

1. Upload both files to your web server
2. Make them publicly accessible
3. Use your domain URLs (must be HTTPS)

### Option 3: Netlify/Vercel (Free hosting)

1. Create account on Netlify or Vercel
2. Upload files or connect GitHub repo
3. Use the provided URLs

## Using in Whoop App

When creating your Whoop Developer Application at https://app.whoop.com/settings/developer:

- **Privacy Policy URL**: Your `privacy.html` URL
- **Redirect URI**: Your `redirect.html` URL

## Customization

Feel free to customize the HTML files:
- Update branding/colors
- Add your own contact info
- Modify the privacy policy text (while keeping it accurate)

The redirect page automatically:
- Extracts the authorization code from the URL
- Displays it to the user
- Auto-copies it to clipboard
- Handles OAuth errors
