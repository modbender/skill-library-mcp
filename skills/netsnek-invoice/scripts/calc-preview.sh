#!/bin/bash
# Calculate invoice totals and generate a Telegram-formatted preview.
# Usage: calc-preview.sh '<JSON_CONTENT>'
# The JSON must follow the invoice schema (items with qty, unitPrice, discountPercent).
# Output: Telegram-compatible text (no Markdown tables, no code blocks).

set -e

JSON_CONTENT="$1"

if [ -z "$JSON_CONTENT" ]; then
  echo "Usage: calc-preview.sh '<JSON_CONTENT>'"
  echo "Reads invoice JSON and outputs a formatted Telegram preview with calculated totals."
  exit 1
fi

printf '%s' "$JSON_CONTENT" | python3 -c '
import sys, json, re, math

data = json.load(sys.stdin)

meta = data.get("meta", {})
intro = data.get("intro", {})
items = data.get("items", [])
totals_obj = data.get("totals", {})
payment = data.get("payment", {})
sender = data.get("sender", {})
recipient = data.get("recipient", [])

doc_id = meta.get("id", "???")
title = meta.get("title", "").replace("{id}", doc_id)
date_str = meta.get("date", "")
due_date = meta.get("deliveryDate", "")
service_period = meta.get("servicePeriod", "")
reference = meta.get("reference", "").replace("{id}", doc_id)
customer_id = meta.get("customerId", "")
contact_person = meta.get("contactPerson", "")
tax_note = totals_obj.get("taxNote", "")

def fmt_euro(amount):
    """Format number as German EUR string (comma decimal, period thousands)."""
    rounded = math.floor(amount * 100 + 0.5) / 100
    s = f"{rounded:.2f}"
    integer_part, decimal_part = s.split(".")
    # Add thousands separator
    if integer_part.startswith("-"):
        sign = "-"
        integer_part = integer_part[1:]
    else:
        sign = ""
    groups = []
    while len(integer_part) > 3:
        groups.insert(0, integer_part[-3:])
        integer_part = integer_part[:-3]
    groups.insert(0, integer_part)
    return sign + ".".join(groups) + "," + decimal_part + " EUR"

def parse_qty(raw_qty):
    """Parse quantity: returns (calc_qty, display_qty)."""
    if isinstance(raw_qty, (int, float)):
        return raw_qty, str(raw_qty).replace(".", ",")
    qty_str = str(raw_qty)
    m = re.match(r"^([\d.,]+)\s*(.*)", qty_str)
    if m:
        num_str = m.group(1).replace(",", ".")
        try:
            calc = float(num_str)
        except ValueError:
            calc = 1
        unit_str = m.group(2)
        disp = num_str.replace(".", ",")
        if unit_str:
            disp = disp + " " + unit_str
        return calc, disp
    return 1, qty_str

# Calculate line items
sum_net = 0
item_lines = []
for i, item in enumerate(items, 1):
    unit_price = float(item.get("unitPrice", 0))
    discount_pct = float(item.get("discountPercent", 0))
    raw_qty = item.get("qty", 1)

    calc_qty, disp_qty = parse_qty(raw_qty)

    line_raw = calc_qty * unit_price
    disc_abs = line_raw * (discount_pct / 100)
    line_final = line_raw - disc_abs
    sum_net += line_final

    item_title = item.get("title", "Position")

    line = f"{i}. {item_title}\n"
    line += f"   {disp_qty} x {fmt_euro(unit_price)}"
    if discount_pct > 0:
        line += f"\n   Rabatt {discount_pct:g}%: -{fmt_euro(disc_abs)}"
    line += f"\n   = {fmt_euro(line_final)}"
    item_lines.append(line)

sum_gross = sum_net  # invoice.sty: gross = net (Kleinunternehmerregelung)

# Build output
out = []

# Determine icon based on document type
is_offer = doc_id.startswith("AN")
icon = "\U0001f4c4" if is_offer else "\U0001f9fe"  # page or receipt
doc_label = "Angebot" if is_offer else "Rechnung"

out.append(f"{icon} *{doc_label} {doc_id}*")
out.append("")

if date_str:
    date_label = "Angebotsdatum" if is_offer else "Rechnungsdatum"
    out.append(f"\U0001f4c5 {date_label}: {date_str}")
if due_date:
    out.append(f"\U0001f4c5 Lieferdatum: {due_date}")
if service_period:
    out.append(f"\U0001f4c5 Leistungszeitraum: {service_period}")
if reference:
    out.append(f"\U0001f4c5 Referenz: {reference}")

out.append("")

# Recipient
if recipient:
    out.append("\U0001f464 *Kunde:*")
    for line in recipient:
        out.append(line)
    out.append("")

# Items
out.append("\U0001f4cb *Positionen:*")
out.append("")
for il in item_lines:
    out.append(il)
    out.append("")

# Totals
out.append("\U0001f4b0 *Zusammenfassung:*")
out.append(f"Netto: {fmt_euro(sum_net)}")
if tax_note:
    out.append(f"_{tax_note}_")
out.append(f"*Gesamt: {fmt_euro(sum_gross)}*")
out.append("")

# Payment
pay_terms = payment.get("terms", "")
pay_status = payment.get("status", "")
if pay_terms:
    out.append(f"\U0001f4dd {pay_terms}")
if pay_status:
    out.append(pay_status)

out.append("")
action = "Soll ich das Angebot hochladen?" if is_offer else "Soll ich die Rechnung hochladen?"
out.append(action)

print("\n".join(out))
'
