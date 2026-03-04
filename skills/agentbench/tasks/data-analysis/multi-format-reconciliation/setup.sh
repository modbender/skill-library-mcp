#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="$1"
cd "$WORKSPACE"

git init -q
git config user.email "bench@agentbench.local"
git config user.name "AgentBench"

# ── Customer names pool ──────────────────────────────────────────────────────
CUSTOMERS=(
  "Acme Corp" "Globex Industries" "Initech LLC" "Umbrella Inc"
  "Stark Enterprises" "Wayne Industries" "Cyberdyne Systems" "Soylent Corp"
  "Oscorp" "LexCorp" "Wonka Industries" "Tyrell Corporation"
  "Nakatomi Trading" "Massive Dynamic" "Prestige Worldwide"
  "Dunder Mifflin" "Sterling Cooper" "Pied Piper" "Hooli" "Bluth Company"
)

METHODS=("bank_transfer" "credit_card" "wire")

# ── Helper: deterministic pseudo-random from seed ────────────────────────────
# We use awk for portable arithmetic to avoid bash $RANDOM limitations
amount_for_inv() {
  local inv_num=$1
  # Generate amount between 50.00 and 5000.00 deterministically
  local base=$(( (inv_num * 137 + 53) % 4951 + 50 ))
  local cents=$(( (inv_num * 73 + 17) % 100 ))
  printf "%d.%02d" "$base" "$cents"
}

customer_for_inv() {
  local inv_num=$1
  local idx=$(( inv_num % ${#CUSTOMERS[@]} ))
  echo "${CUSTOMERS[$idx]}"
}

date_for_inv() {
  local inv_num=$1
  local month=$(( inv_num % 3 + 1 ))
  local day=$(( inv_num % 28 + 1 ))
  printf "2025-%02d-%02d" "$month" "$day"
}

method_for_pay() {
  local pay_num=$1
  local idx=$(( pay_num % ${#METHODS[@]} ))
  echo "${METHODS[$idx]}"
}

# ============================================================================
# FILE 1: invoices.csv  (200 rows)
# ============================================================================
{
  echo "Invoice_ID,Customer,Amount,Date,Reference_ID"

  for i in $(seq 1 200); do
    inv_id=$(printf "INV-%04d" "$i")
    ref_id=$(printf "REF-INV-%04d" "$i")
    customer=$(customer_for_inv "$i")
    date=$(date_for_inv "$i")
    amt=$(amount_for_inv "$i")

    # Discrepancy 9: INV-0034 must be exactly $1,500.00
    if [ "$i" -eq 34 ]; then
      amt="1500.00"
    fi
    # Discrepancy 10: INV-0078 must be exactly $820.00
    if [ "$i" -eq 78 ]; then
      amt="820.00"
    fi
    # Discrepancy 15: INV-0150 must be exactly $3,000.00 (split payment)
    if [ "$i" -eq 150 ]; then
      amt="3000.00"
    fi

    echo "${inv_id},${customer},${amt},${date},${ref_id}"
  done
} > invoices.csv

# ============================================================================
# FILE 2: payments.json  (180 entries)
# ============================================================================
# Build the JSON array.  We skip invoices that have NO payment (discrepancy 1-5)
# and add 3 orphan payments (discrepancy 6-8).
{
  echo "["

  pay_num=0
  first=true

  for i in $(seq 1 200); do
    # Skip the 5 invoices with no payment (discrepancy 1-5),
    # plus ~15 others that only appear in the bank (not in payment system).
    # This brings payment count to ~180.
    case $i in
      45|89|123|156|198) continue ;;           # discrepancy 1-5
      150) continue ;;                          # discrepancy 15 (split payment)
      7|14|23|36|51|62|73|84|97|108|119|130|141|153|168|179|193) continue ;;  # bank-only (17 invoices)
    esac

    pay_num=$((pay_num + 1))
    pay_id=$(printf "PAY-%04d" "$pay_num")
    ref_id=$(printf "REF-INV-%04d" "$i")
    amt=$(amount_for_inv "$i")
    method=$(method_for_pay "$pay_num")

    # Payment date is 1-5 days after invoice date
    inv_date=$(date_for_inv "$i")
    day_offset=$(( pay_num % 5 + 1 ))
    inv_day=${inv_date:8:2}
    inv_month=${inv_date:5:2}
    new_day=$(( 10#$inv_day + day_offset ))
    if [ "$new_day" -gt 28 ]; then
      new_day=$(( new_day - 28 ))
      new_month=$(( 10#$inv_month + 1 ))
      if [ "$new_month" -gt 3 ]; then new_month=3; new_day=28; fi
    else
      new_month=$((10#$inv_month))
    fi
    pay_date=$(printf "2025-%02d-%02d" "$new_month" "$new_day")

    # Discrepancy 9: INV-0034 payment is $1,450.00 (invoice is $1,500.00)
    if [ "$i" -eq 34 ]; then
      amt="1450.00"
    fi
    # Discrepancy 10: INV-0078 payment is $830.00 (invoice is $820.00)
    if [ "$i" -eq 78 ]; then
      amt="830.00"
    fi

    if [ "$first" = true ]; then
      first=false
    else
      echo "  ,"
    fi

    cat <<ENTRY
  {
    "payment_id": "${pay_id}",
    "invoice_ref": "${ref_id}",
    "amount_paid": ${amt},
    "payment_date": "${pay_date}",
    "method": "${method}"
  }
ENTRY
  done

  # Discrepancy 6-8: Three orphan payments referencing non-existent invoices
  for orphan_idx in 1 2 3; do
    case $orphan_idx in
      1) opay="PAY-0067"; oref="REF-INV-9901"; oamt="475.50";  odate="2025-01-18"; ometh="bank_transfer" ;;
      2) opay="PAY-0134"; oref="REF-INV-9902"; oamt="1230.00"; odate="2025-02-09"; ometh="credit_card" ;;
      3) opay="PAY-0171"; oref="REF-INV-9903"; oamt="890.75";  odate="2025-03-14"; ometh="wire" ;;
    esac

    echo "  ,"
    cat <<ENTRY
  {
    "payment_id": "${opay}",
    "invoice_ref": "${oref}",
    "amount_paid": ${oamt},
    "payment_date": "${odate}",
    "method": "${ometh}"
  }
ENTRY
  done

  echo "]"
} > payments.json

# ============================================================================
# FILE 3: bank-statement.txt  (190 lines of transactions)
# ============================================================================
{
  cat <<'HEADER'
=== BANK STATEMENT -- Acme Corp ===
Account: ****4521 | Period: Jan-Mar 2025

Date        | Reference       | Description              | Amount
------------|-----------------|--------------------------|--------
HEADER

  line_count=0

  for i in $(seq 1 200); do
    # Skip the 5 unpaid invoices -- they should NOT appear in bank.
    # Also skip 11 others (pending clearance) to bring total to ~190 lines.
    case $i in
      45|89|123|156|198) continue ;;                          # discrepancy 1-5
      10|25|40|60|76|101|116|137|164|180|195) continue ;;     # pending clearance (11)
    esac

    ref_id=$(printf "REF-INV-%04d" "$i")
    customer=$(customer_for_inv "$i")
    amt_raw=$(amount_for_inv "$i")
    inv_date=$(date_for_inv "$i")

    # Payment date offset for bank (2-6 days after invoice)
    day_offset=$(( (i * 3 + 7) % 5 + 2 ))
    inv_day=${inv_date:8:2}
    inv_month=${inv_date:5:2}
    new_day=$(( 10#$inv_day + day_offset ))
    if [ "$new_day" -gt 28 ]; then
      new_day=$(( new_day - 28 ))
      new_month=$(( 10#$inv_month + 1 ))
      if [ "$new_month" -gt 3 ]; then new_month=3; new_day=28; fi
    else
      new_month=$((10#$inv_month))
    fi
    bank_date=$(printf "2025-%02d-%02d" "$new_month" "$new_day")

    # Format amount with comma for thousands
    amt_int=${amt_raw%.*}
    amt_dec=${amt_raw#*.}
    if [ "$amt_int" -ge 1000 ]; then
      amt_formatted=$(printf "%s,%s.%s" "${amt_int:0:${#amt_int}-3}" "${amt_int:${#amt_int}-3}" "$amt_dec")
    else
      amt_formatted=$(printf "%s.%s" "$amt_int" "$amt_dec")
    fi

    # Discrepancy 9: bank matches payment amount for INV-0034 ($1,450.00)
    if [ "$i" -eq 34 ]; then
      amt_formatted="1,450.00"
    fi
    # Discrepancy 10: bank matches payment amount for INV-0078 ($830.00)
    if [ "$i" -eq 78 ]; then
      amt_formatted="830.00"
    fi

    # Discrepancy 11: REF-INV-O087 (letter O instead of zero 0)
    if [ "$i" -eq 87 ]; then
      ref_id="REF-INV-O087"
    fi
    # Discrepancy 12: REF-INV-0l42 (lowercase L instead of digit 1)
    if [ "$i" -eq 142 ]; then
      ref_id="REF-INV-0l42"
    fi

    desc=$(printf "Payment from %-16s" "$customer")

    # Discrepancy 15: INV-0150 split into two entries of $1,500.00 each
    if [ "$i" -eq 150 ]; then
      printf "%-12s| %-16s| %-25s| %s\n" "$bank_date" "REF-INV-0150" "Payment from $(customer_for_inv 150) (1/2)" "1,500.00"
      line_count=$((line_count + 1))
      # Second half 3 days later
      split_day=$(( 10#${bank_date:8:2} + 3 ))
      split_month=$((10#${bank_date:5:2}))
      if [ "$split_day" -gt 28 ]; then
        split_day=$(( split_day - 28 ))
        split_month=$(( split_month + 1 ))
        if [ "$split_month" -gt 3 ]; then split_month=3; split_day=28; fi
      fi
      split_date=$(printf "2025-%02d-%02d" "$split_month" "$split_day")
      printf "%-12s| %-16s| %-25s| %s\n" "$split_date" "REF-INV-0150" "Payment from $(customer_for_inv 150) (2/2)" "1,500.00"
      line_count=$((line_count + 1))
      continue
    fi

    printf "%-12s| %-16s| %-25s| %s\n" "$bank_date" "$ref_id" "$desc" "$amt_formatted"
    line_count=$((line_count + 1))

    # Discrepancy 13: Duplicate bank entry for REF-INV-0055 (different date)
    if [ "$i" -eq 55 ]; then
      dup_day=$(( 10#${bank_date:8:2} + 5 ))
      dup_month=$((10#${bank_date:5:2}))
      if [ "$dup_day" -gt 28 ]; then
        dup_day=$(( dup_day - 28 ))
        dup_month=$(( dup_month + 1 ))
        if [ "$dup_month" -gt 3 ]; then dup_month=3; dup_day=28; fi
      fi
      dup_date=$(printf "2025-%02d-%02d" "$dup_month" "$dup_day")
      printf "%-12s| %-16s| %-25s| %s\n" "$dup_date" "REF-INV-0055" "$desc" "$amt_formatted"
      line_count=$((line_count + 1))
    fi

    # Discrepancy 14: Duplicate bank entry for REF-INV-0091 (different date)
    if [ "$i" -eq 91 ]; then
      dup_day=$(( 10#${bank_date:8:2} + 7 ))
      dup_month=$((10#${bank_date:5:2}))
      if [ "$dup_day" -gt 28 ]; then
        dup_day=$(( dup_day - 28 ))
        dup_month=$(( dup_month + 1 ))
        if [ "$dup_month" -gt 3 ]; then dup_month=3; dup_day=28; fi
      fi
      dup_date=$(printf "2025-%02d-%02d" "$dup_month" "$dup_day")
      printf "%-12s| %-16s| %-25s| %s\n" "$dup_date" "REF-INV-0091" "$desc" "$amt_formatted"
      line_count=$((line_count + 1))
    fi
  done

  # Orphan bank entries for the 3 orphan payments (discrepancy 6-8)
  printf "%-12s| %-16s| %-25s| %s\n" "2025-01-18" "REF-INV-9901" "Payment from Unknown Pty  " "475.50"
  line_count=$((line_count + 1))
  printf "%-12s| %-16s| %-25s| %s\n" "2025-02-09" "REF-INV-9902" "Payment from Unknown Ltd  " "1,230.00"
  line_count=$((line_count + 1))
  printf "%-12s| %-16s| %-25s| %s\n" "2025-03-14" "REF-INV-9903" "Payment from Unknown GmbH " "890.75"
  line_count=$((line_count + 1))

  echo ""
  echo "--- End of Statement ---"
  echo "Total entries: ${line_count}"

} > bank-statement.txt

git add -A
git commit -q -m "initial: add financial data for reconciliation"
