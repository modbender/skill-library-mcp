# People Search & OSINT Resources

## Free Services (Actually Useful)

### TruePeopleSearch (truepeoplesearch.com)
- **Cost:** Free
- **Data:** Name, age, addresses, phone numbers, relatives, associates
- **Quality:** Good for basic info, addresses are usually current
- **Tip:** Sometimes works with web_fetch, otherwise browser tool

### FastPeopleSearch (fastpeoplesearch.com)
- **Cost:** Free
- **Data:** Similar to TruePeopleSearch
- **Quality:** Good backup when TPS doesn't have results

### ClustrMaps (clustrmaps.com)
- **Cost:** Free previews
- **Data:** Address history, property records, neighbors
- **Tip:** Good for address history and connecting family members via shared addresses

### FEC (fec.gov)
- **Cost:** Free API (DEMO_KEY works, rate-limited)
- **Data:** Political donations with employer, occupation, address
- **Tip:** Use the API script at `scripts/fec-lookup.sh` for structured results
- **Goldmine:** Donations include self-reported employer and occupation — sometimes the ONLY source for career info

### Florida Sunbiz (search.sunbiz.org)
- **Cost:** Free
- **Data:** All FL corporations, LLCs, nonprofits — officers, registered agents, addresses
- **Tip:** Officer search reveals every business a person is affiliated with in FL

### CourtListener (courtlistener.com)
- **Cost:** Free
- **Data:** Federal court opinions + RECAP PACER docket archive
- **Quality:** Comprehensive for federal; state coverage varies

## Paid Services (Sometimes Worth It)

### Spokeo
- **Cost:** $13.95/mo (or per-report)
- **Data:** Deep records — social media profiles, dating profiles, Amazon wishlists, etc.
- **Quality:** Mixes up people with same name constantly. Verify everything.

### BeenVerified
- **Cost:** $26.89/mo
- **Data:** Background checks, criminal records, property, vehicles
- **Quality:** More thorough than free options

### Intelius
- **Cost:** Per-report pricing
- **Data:** Criminal records, financial, professional licenses
- **Quality:** Good for professional license verification

## Reverse Lookup Tools

### Phone Number
1. Google the number in quotes: `"555-123-4567"`
2. TruePeopleSearch reverse phone
3. Spokeo reverse phone (paid)
4. CallerID apps (Hiya, TrueCaller) — sometimes cached data appears in web results

### Email Address
1. Google the email in quotes: `"john_doe@example.com"`
2. Hunter.io — shows email patterns for companies
3. Have I Been Pwned (haveibeenpwned.com) — shows if email was in breaches (doesn't reveal data, just breach names)
4. Gravatar — `https://www.gravatar.com/[md5hash]` — sometimes has profile photo + bio

### Address
1. Property appraiser (county-specific)
2. Zillow/Redfin/Realtor.com — shows ownership history, sale prices
3. Google Maps Street View — visual confirmation
4. ClustrMaps — who else has lived there

## Social Media OSINT

### Username Enumeration
If you find one username, check it across platforms:
- `https://twitter.com/[username]`
- `https://instagram.com/[username]`
- `https://github.com/[username]`
- `https://reddit.com/user/[username]`
- `https://linkedin.com/in/[username]`

### Photo Reverse Search
- Google Images reverse search
- TinEye (tineye.com)
- Yandex Images (often better than Google for faces)

### Archived Content
- Wayback Machine: `https://web.archive.org/web/*/[url]`
- Google Cache: `cache:[url]`
- Archive.today: `https://archive.ph/[url]`

## Pro Tips

1. **State bid documents** are goldmines — government RFPs list company reps with direct phone/email
2. **University/school donor pages** often list people who don't appear anywhere else online
3. **Wedding registries** (The Knot, Zola) can reveal partner names and dates
4. **Marathon/race results** — many runners use real names, reveal age and city
5. **Fishing/hunting license databases** — some states make these public
6. **Voter registration** — FL voter rolls are public (request from Supervisor of Elections)
7. **Professional licenses** — FL DBPR (myfloridalicense.com) for RE agents, contractors, etc.
