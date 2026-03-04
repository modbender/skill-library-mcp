# Meta Ads Analytics Bundle

This bundle provides two skills to help you monitor your Meta (Facebook/Instagram) Ads performance directly from OpenClaw.

1.  **Analytics (`meta_ads_analytics`):** Reports Spend, Conversions, and CAC for a specific period.
2.  **Event Finder (`list_meta_events`):** Lists all raw event names so you can configure the correct conversion metric.

---

## 🛠️ Setup Guide

To use this skill, you need to get your **Access Token** and **Ad Account ID** and save them in your `.env` file.

### Step 1: Get Access Token
1.  Go to [Meta for Developers - Graph API Explorer](https://developers.facebook.com/tools/explorer/).
2.  Select your App in the "Meta App" dropdown.
3.  In "User or Page", select **"User Token"**.
4.  Under "Permissions", add the following:
    * `ads_read`
    * `read_insights`
5.  Click **Generate Access Token**.
6.  Copy the long string generated in the top field.

### Step 2: Get Ad Account ID
1.  Go to [Facebook Ads Manager](https://adsmanager.facebook.com/).
2.  Look at the URL in your browser.
3.  Find `act=123456789`. The number part is your ID.
4.  **Important:** You must add `act_` before the number (e.g., `act_123456789`).

### Step 3: Configure `.env`
Create or edit the `.env` file in your OpenClaw root directory and add:

```ini
META_ACCESS_TOKEN=YOUR_LONG_ACCESS_TOKEN_HERE
META_AD_ACCOUNT_ID=act_YOUR_ACCOUNT_ID_HERE

# (Optional) The event you want to count as a "Conversion"
# Default is: offsite_conversion.fb_pixel_custom
META_EVENT_NAME=offsite_conversion.fb_pixel_custom
