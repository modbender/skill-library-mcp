# Example: Single Contact Lookup

## User Request
"What's the email for Sarah Chen, VP of Product at Figma?"

## What the Agent Does

1. **Matches prospect**: Uses full_name + company_name
2. **Enriches**: Gets contact information (emails, phone)
3. **Presents**: Contact details in structured format

## Match Payload
```json
[{"full_name": "Sarah Chen", "company_name": "Figma"}]
```

## Enrichments Used
- `contacts_information` — emails and phones
- `profiles` — current title verification, LinkedIn

## Expected Output
```
Sarah Chen — VP of Product at Figma
- Email: sarah.chen@figma.com
- Phone: +1 (415) 555-1234
- LinkedIn: linkedin.com/in/sarahchen
- Department: Product
- Seniority: Vice President
```
