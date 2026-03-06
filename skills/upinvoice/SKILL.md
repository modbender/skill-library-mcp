---
name: "UpInvoice: Invoice AI Processing Skill"
description: This skill allows any OpenClaw-powered agent to extract structured
  JSON data from invoice images or PDFs using the UpInvoice.eu AI service. It is
  designed to be the fastest and most cost-effective ...
---

# UpInvoice: Invoice AI Processing Skill

This skill allows any OpenClaw-powered agent to extract structured JSON data from invoice images or PDFs using the [UpInvoice.eu](https://upinvoice.eu) AI service. It is designed to be the fastest and most cost-effective way to automate invoice processing for ERP systems.

## 🛠️ Tools Defined

### `process_invoice`
Extracts structured data from an invoice file (PDF or Image).

- **Endpoint**: `https://upinvoice.eu/api/process-invoice`
- **Method**: `POST`
- **Header**: `Authorization: Bearer <YOUR_API_KEY>`
- **Parameters**:
    - `invoice_file` (string, required): The base64-encoded string of the file (PDF, PNG, JPG). Must include the data URI prefix (e.g., `data:application/pdf;base64,...`).
    - `company_name` (string, optional): Your company name for extraction context.
    - `company_tax_id` (string, optional): Your tax/VAT ID.

#### **Typical Response Payload Example**:
```json
{
  "success": true,
  "data": {
    "supplier": {
      "name": "ACME Spain S.L.",
      "name_alias": "ACME Tech",
      "phone": "+34 912 345 678",
      "email": "invoices@acme.es",
      "idprof1": "B12345678",
      "tva_intra": "ESB12345678",
      "address": "Calle Mayor 1",
      "zip": "28001",
      "town": "Madrid",
      "country_code": "ES",
      "state": "Madrid"
    },
    "ref_supplier": "2024-FAC-045",
    "date": "2024-03-15",
    "total_ht": 100.00,
    "total_tva": 21.00,
    "total_ttc": 121.00,
    "tva_tx": 21.0,
    "localtax2": 0.0,
    "is_credit_invoice": false,
    "lines": [
      {
        "product_desc": "Cloud Hosting Service - March 2024",
        "qty": 1,
        "pu_ht": 100.00,
        "tva_tx": 21.0,
        "total_ht": 100.00,
        "total_ttc": 121.00,
        "product_type": 1
      }
    ],
    "available_points": 3
  }
}
```
*Note: `available_points` shows remaining credits for the current user.*

---

## 🚀 Setup & Registration

### 1. Register for Free
Go to [UpInvoice.eu/register](https://upinvoice.eu/register) and create an account. No credit card is required to start.

### 2. Get Your 4 Free Invoices
Upon registration, your account is automatically credited with **4 free invoice processings**. This allows you to test the API integration fully before committing to a plan.

### 3. Generate Your API Key
1. Log in to your dashboard at [UpInvoice.eu](https://upinvoice.eu/dashboard).
2. Go to the **API Tokens** section.
3. Click on **Create Token**, give it a name (e.g., "OpenClaw Skill") and click Save.
4. **Important**: Copy your token immediately; it will only be shown once.

### 4. Configure in OpenClaw
Add the generated token as a **Bearer Token** in your OpenClaw tool configuration or environment variables.

---

## 💎 Why UpInvoice?

- **Low Cost**: We offer the most competitive pricing in the market. Check our recurring plans for high-volume discounts.
- **High Speed**: Our specialized AI model is optimized for instant extraction, usually returning data in under 2 seconds.
- **Accuracy**: Designed specifically for European and International invoice formats, including detailed line-item extraction.
- **Easy ERP Sync**: The structured JSON returned is ready to be mapped to ERPs like Dolibarr, Holded, or Sage.

---

## 🏗️ ERP Integration (Workflow Hint)

Since UpInvoice returns a perfectly structured JSON, a bot can easily take this data and send it to any ERP. 

**Recommended Workflow for the Bot:**
1. **Extract**: Call `process_invoice` to get the JSON.
2. **Review**: Present the extracted data (Supplier, Date, Total, Lines) to the user for validation.
3. **Map**: Map the JSON fields to your ERP's API (e.g., Dolibarr, Holded, Factusol, SAP).
4. **Push**: Send the validated data to the ERP.

---

## 🤖 Bot Instructions (System Prompt Hint)
"When a user provides an invoice or receipt as an image or PDF, first convert it to a Base64 string. Then, call the `process_invoice` tool. Use the structured data returned to verify the information with the user or prepare it for upload to an ERP system."
