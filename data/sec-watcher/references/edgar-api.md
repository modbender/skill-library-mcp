# EDGAR Full-Text Search API Reference

## Endpoint

```
GET https://efts.sec.gov/LATEST/search-index?q=QUERY&dateRange=custom&startdt=YYYY-MM-DD&enddt=YYYY-MM-DD&forms=FORM_TYPE
```

## Base URL

```
https://efts.sec.gov/LATEST/search-index
```

## Query Parameters

| Parameter   | Required | Description                                                      |
|-------------|----------|------------------------------------------------------------------|
| `q`         | Yes      | Search query — company name, ticker, CIK, or keyword            |
| `forms`     | No       | Comma-separated form types: `8-K`, `10-K`, `10-Q`, `S-1`, `425` |
| `dateRange` | No       | `custom` to use startdt/enddt                                    |
| `startdt`   | No       | Start date `YYYY-MM-DD`                                          |
| `enddt`     | No       | End date `YYYY-MM-DD`                                            |
| `from`      | No       | Pagination offset (default 0)                                    |
| `size`      | No       | Results per page (default 10, max 100)                           |

## Required Headers

SEC requires a `User-Agent` header identifying the requester:

```
User-Agent: SignalReport sec-watcher@signal-report.com
```

Failure to include a proper User-Agent results in 403 errors.

## Rate Limits

- **10 requests per second** per IP
- No API key required
- Fair use policy — avoid hammering during market hours peak

## Response Shape

```json
{
  "hits": {
    "hits": [
      {
        "_id": "filing-id",
        "_source": {
          "file_date": "2026-02-18",
          "form_type": "8-K",
          "entity_name": "NVIDIA CORP",
          "file_num": "0-12345",
          "period_of_report": "2026-02-18",
          "items": "1.01, 5.02",
          "file_description": "Current report",
          "display_names": ["NVIDIA CORP"],
          "display_date_filed": "2026-02-18",
          "biz_locations": ["Santa Clara, CA"],
          "biz_phone": "408-555-1234",
          "inc_states": ["DE"]
        }
      }
    ],
    "total": { "value": 42 }
  }
}
```

## 8-K Item Code Reference

### High Signal (leadership, M&A, material events)

| Item | Description                                              | Signal Level |
|------|----------------------------------------------------------|-------------|
| 1.01 | Entry into a material definitive agreement               | HIGH        |
| 1.02 | Termination of a material definitive agreement           | HIGH        |
| 2.01 | Completion of acquisition or disposition of assets       | HIGH        |
| 2.05 | Costs associated with exit or disposal activities        | MEDIUM      |
| 4.02 | Non-reliance on previously issued financial statements   | CRITICAL    |
| 5.02 | Departure/election of directors or principal officers    | HIGH        |

### Medium Signal (financial, governance)

| Item | Description                                              | Signal Level |
|------|----------------------------------------------------------|-------------|
| 2.02 | Results of operations and financial condition             | MEDIUM      |
| 2.03 | Creation of direct financial obligation                   | MEDIUM      |
| 2.04 | Triggering events — accelerate/increase obligations       | MEDIUM      |
| 3.01 | Notice of delisting or transfer                          | MEDIUM      |
| 5.01 | Changes in control of registrant                         | HIGH        |
| 5.03 | Amendments to articles of incorporation or bylaws        | LOW         |

### Routine / Low Signal

| Item | Description                                              | Signal Level |
|------|----------------------------------------------------------|-------------|
| 7.01 | Regulation FD disclosure                                 | MEDIUM      |
| 8.01 | Other events                                             | LOW         |
| 9.01 | Financial statements and exhibits                        | LOW         |

## Form Type Reference

| Form   | Description                        | Frequency   |
|--------|------------------------------------|-------------|
| 8-K    | Current report (material events)   | As needed   |
| 10-K   | Annual report                      | Yearly      |
| 10-Q   | Quarterly report                   | Quarterly   |
| S-1    | IPO registration statement         | One-time    |
| 425    | M&A proxy/prospectus materials     | As needed   |
| DEF14A | Proxy statement (board votes)      | Yearly      |
| SC 13D | Beneficial ownership >5%           | As needed   |
| Form 4 | Insider trading                    | As needed   |

## EDGAR Filing URL Pattern

Direct link to a filing:

```
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=ENTITY_CIK&type=FORM_TYPE&dateb=&owner=include&count=40
```

Or from search results, use the `_id` to construct:

```
https://www.sec.gov/Archives/edgar/data/CIK/ACCESSION_NUMBER
```
