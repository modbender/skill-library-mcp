name: "📍 Google Maps Lead Hunter (B2B Goldmine)"
description: |
  EXTRACT UNLIMITED LEADS (Emails, Phones, Websites) from Google Maps.
  
  ⚠️ **REQUIRED:** This skill uses the Apify Cloud Engine.
  To use this skill, you must generate a FREE API Token here:
  👉 **https://www.apify.com?fpr=dx06p**
  
  1. Click the link above & Sign up.
  2. Go to Settings -> Integrations -> Copy your "API Token".
  3. Enter the token below to start scraping leads instantly.
  
  Perfect for: Marketing Agencies, Realtors, Sales Teams.
authors:
  - "YourName"
inputs:
  keyword:
    description: "What business are you looking for? (e.g., 'Real Estate Agents', 'Dentists', 'Italian Restaurants')"
    required: true
  location:
    description: "Where should we search? (e.g., 'Miami, FL', 'London, UK')"
    required: true
  apify_token:
    description: "Paste your Apify API Token here (Get it at: https://www.apify.com?fpr=dx06p)"
    required: true
steps:
  - name: scrape_google_maps
    type: python
    code: |
      import requests
      import time
      import json

      # 1. SETUP VARIABLES
      # We limit to 15 results for speed, user can scale up later
      APIFY_TOKEN = inputs['apify_token']
      SEARCH_TERM = f"{inputs['keyword']} in {inputs['location']}"
      
      print(f"🚀 Starting Lead Hunt for: {SEARCH_TERM}...")
      print("⏳ Connecting to Apify Cloud Engine...")

      # 2. START THE CRAWLER (Compass Google Maps)
      url_start = f"https://api.apify.com/v2/acts/compass~crawler-google-places/runs?token={APIFY_TOKEN}"
      
      payload = {
          "searchStringsArray": [SEARCH_TERM],
          "maxCrawledPlacesPerSearch": 15,
          "language": "en",
          "onlyResult": True
      }
      
      headers = {'Content-Type': 'application/json'}
      
      try:
          response = requests.post(url_start, headers=headers, json=payload)
          response.raise_for_status()
          run_data = response.json()['data']
          run_id = run_data['id']
          dataset_id = run_data['defaultDatasetId']
      except Exception as e:
          print(f"❌ Error: Invalid API Token or Apify Connection failed. Did you sign up via the link? Error: {e}")
          raise e

      print(f"✅ Scraper Started! (Run ID: {run_id})")
      print("☕ This usually takes 30-60 seconds. Extracting fresh data...")

      # 3. POLL FOR COMPLETION
      while True:
          status_url = f"https://api.apify.com/v2/acts/runs/{run_id}?token={APIFY_TOKEN}"
          status_res = requests.get(status_url)
          status_data = status_res.json()['data']
          status = status_data['status']
          
          if status == "SUCCEEDED":
              break
          elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
              print("❌ The scrape failed. Please try again.")
              return
          
          time.sleep(5) # Wait 5 seconds before checking again

      # 4. FETCH THE DATA (LEADS)
      dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"
      data_res = requests.get(dataset_url)
      items = data_res.json()

      # 5. FORMAT OUTPUT FOR CLAWHUB USER
      results = []
      for item in items:
          lead = {
              "Business Name": item.get('title', 'N/A'),
              "Phone": item.get('phone', 'N/A'),
              "Website": item.get('website', 'N/A'),
              "Address": item.get('address', 'N/A'),
              "Rating": item.get('totalScore', 'N/A')
          }
          results.append(lead)

      print(f"🎉 SUCCESS! Found {len(results)} leads for {inputs['keyword']}.")
      
      # Output as Markdown Table for nice display in Clawhub
      print("\nHere are your leads:\n")
      print("| Business Name | Phone | Website | Rating |")
      print("| --- | --- | --- | --- |")
      for r in results:
          print(f"| {r['Business Name']} | {r['Phone']} | {r['Website']} | {r['Rating']} |")

      # Final Affiliate Reminder
      print("\n💡 Want more than 15 leads? Upgrade your Apify plan here to support this tool: https://www.apify.com?fpr=dx06p")