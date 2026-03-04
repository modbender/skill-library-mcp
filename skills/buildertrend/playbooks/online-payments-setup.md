# Buildertrend Payments Setup & Management
> Setting up BT Payments, accepting client payments, paying subs

## Trigger
- the user says "set up payments", "accept credit cards", "pay subs through BT"
- New project needs client payment collection enabled
- Sub/vendor payment method setup needed

## Error Handling
| Issue | Resolution |
|---|---|
| Application rejected | Review submitted info for errors, contact BT support |
| Payment processing failed | Check card/ACH details, retry, contact payment provider |
| Client cannot see payment option | Verify client portal permissions include invoice payments |
| ACH transfer delayed | Standard ACH takes 3-5 business days — inform the user |
| BT session expired | Stop, notify the user to re-login |

---

## Overview
Buildertrend Payments allows builders to:
1. **Receive client payments** on invoices via credit card, ACH, or digital wallets
2. **Pay subcontractors/vendors** via ACH or check (printed/mailed)
3. All processed through Adyen (PCI compliant)

---

## PART 1: Initial Setup

### Applying for Buildertrend Payments
1. Navigate to **Additional Services** tab in your BT account
2. Provide required information:
   - Company legal name and DBA
   - Legal structure (LLC, Inc., etc.)
   - Physical address
   - Beneficial owner information
   - Deposit account details
3. May need additional docs: P&L, Articles of Incorporation, driver's license, tax returns, bank statements
4. Review takes **2-4 business days**
5. Team will notify of approval and processing limits

### Adding Bank Accounts
1. Navigate to **Online Payments Settings** (Company Settings)
2. Under "Pay" click **Add Bank Account**
3. Verify via Plaid instant verification (or micro deposits if bank not supported)
4. No limit on number of bank accounts
5. Set starting check number per bank account

### Configuring Payment Settings
- **Check expiration:** Choose 30, 60, 90, or 180 days
- **Trusted Payment Users:** Define who can send payments and edit sub/vendor contact info
  - Org Owners have automatic access
  - Add additional trusted users from Company Settings
- **Credit card toggle:** Can disable credit cards as payment method
- **Monthly processing limit:** Set during underwriting; track via Invoices page banner

---

## PART 2: Receiving Client Payments

### Payment Methods Accepted
| Method | Fee | Notes |
|--------|-----|-------|
| Credit/Debit (Visa, MC, Discover) | 2.99% | Can pass fees to clients. AmEx NOT accepted |
| ACH Bank Transfer | $15.00 flat | Per transaction |
| Apple Pay / Google Pay | 2.99% | Same as card (AmEx still not accepted) |

### Sending an Invoice for Payment
1. Create invoice in BT (see create-invoice playbook)
2. Release invoice to client
3. Client receives email with **"View and pay"** button
4. Client can also pay from:
   - Client Portal dashboard (Next Payment banner)
   - Client Portal Pending Invoices
   - BT Mobile App (Unpaid Invoices > Action Items)

### Client Payment Setup (from Client Portal)
Clients save payment methods at: **Settings > Payments > Add payment method**
- Add credit card or bank account
- Set preferred payment method for auto-apply

### Payment Limits
- **Per transaction:** $120,000 max
- **Monthly:** Custom limit per builder (set during underwriting)
- **Monitoring:** Banner on Invoices page shows utilization
- **Alerts:** Email at 50% and 100% monthly utilization
- When limit reached: online pay disabled; client sees message to contact builder

### Payout Timing
- Payments settle within **2-4 business days**
- After-hours payments start processing next business day

---

## PART 3: Paying Subcontractors & Vendors

### Fees (Paid by Builder)
| Method | Cost |
|--------|------|
| ACH | $1 per transaction |
| Printed check | $2 per transaction |
| Mailed check | $2 per transaction |

Fees billed monthly (even if subscription is annual). View on Subscription Management page.

### Making Individual Payments
1. Navigate to the Bill
2. Click **Pay > Pay Online**
3. Select bank account
4. Edit memo if needed
5. Confirm payment

### Making Bulk Payments
1. Go to **Bills** page
2. Select multiple bills via checkboxes
3. Use **checked actions** to pay
4. System sums bills by sub and sends single payment to each

### Sub/Vendor Requirements
- **No BT account needed** — just email + job assignment
- ACH: sub prompted to set up bank info securely
- Check: no action required from sub

### Payment Delivery
| Method | Timeline |
|--------|----------|
| ACH | 3-5 business days |
| Self-printed check | Immediate (varies by bank) |
| Mailed check (USPS) | 3-14 days |

### Check Details
- **Limit:** $150,000 per check
- **Memo:** 2,054 chars (e-check), 180 chars (printed; URL added if longer)
- **Custom numbering:** Set starting number per bank account
- **Expiration:** Configurable (30/60/90/180 days)

### Payment Email to Sub
- From: info@buildertrend.com
- Subject: "(Your company name) has sent you a payment"
- Contains deposit options for sub to choose

---

## PART 4: Handling Disputes

### ACH Returns
- **Timeline:** Up to 60 days after payment
- **Cannot be directly disputed** by builder
- BT debits builder's account within 2-4 business days
- Common causes: incorrect account details, insufficient funds
- **Resolution:** Work with client to reinitiate or find alternative payment
- Invoice returns to "Pending/Released" — client can repay

### Credit Card Chargebacks
- **Timeline:** Up to 120 days after transaction
- Funds immediately withdrawn from builder's account
- **To dispute:**
  1. Reply to chargeback notification email
  2. Provide ALL evidence in single submission (cannot add later)
  3. Resolution takes 45-60 days average
  4. Final decision made by client's card issuer, not BT
- **No fees** for chargebacks currently
- If integrated with QuickBooks: paid invoice auto-deleted on chargeback

### After Any Return/Chargeback
1. Invoice returns to "Pending/Released"
2. Client can repay via same method
3. Leave comment on invoice or resend to notify client

---

## PART 5: Reporting & Reconciliation

### Online Payments Report
Found under Bills tab. Includes:
- Check number
- Direct link to bill
- Payment history

### Bill Payment Details
For each bill:
- Check number
- Recipient info (name, email, phone)
- Internal user who sent payment
- Bank account used
- Memo/description
- Full payment history

### Bank Statement Format
**ACH:**
- Builder view: (Payment ID) BT Bill Pay
- Sub view: (Builder Name) Payment

**Printed Checks:** Standard check format

### 1099-K
- Issued by Adyen, shipped 3rd week of January
- Threshold: $20,000 gross volume + 200 transactions
- Reports gross volume (before fees, chargebacks, refunds)
- Contact BT support if not received by 2nd week of February

---

## Quick Reference: Company-Specific Notes
- Currently NOT enrolled in BT Payments (evaluate during BT setup)
- If enrolled, configure Trusted Payment Users for the user + authorized staff
- Set up bank accounts for both sending and receiving
- Consider passing credit card fees to clients for large invoices
