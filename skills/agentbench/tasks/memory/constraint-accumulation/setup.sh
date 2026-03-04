#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="$1"
cd "$WORKSPACE"

git init -q
git config user.email "bench@agentbench.local"
git config user.name "AgentBench"

mkdir -p data

# ── Data pools ───────────────────────────────────────────────────────────────

FIRST_NAMES=(
  "Alice" "Bob" "Carol" "David" "Eva"
  "Frank" "Grace" "Hank" "Irene" "Jack"
  "Karen" "Leo" "Mia" "Nate" "Olivia"
  "Paul" "Quinn" "Rita" "Sam" "Tina"
  "Uma" "Victor" "Wendy" "Xander" "Yara"
  "Zane" "Bella" "Caleb" "Diana" "Ethan"
)

LAST_NAMES=(
  "Johnson" "Smith" "Williams" "Brown" "Jones"
  "Garcia" "Miller" "Davis" "Rodriguez" "Martinez"
  "Hernandez" "Lopez" "Gonzalez" "Wilson" "Anderson"
  "Thomas" "Taylor" "Moore" "Jackson" "Martin"
  "Lee" "Perez" "Thompson" "White" "Harris"
  "Sanchez" "Clark" "Ramirez" "Lewis" "Robinson"
)

DOMAINS=(
  "example.com" "techco.com" "globex.io" "initech.net" "acmecorp.com"
  "widgets.co" "dataflow.io" "cloudnine.com" "bytesize.net" "openstack.org"
)

REGIONS=("North America" "Europe" "Asia Pacific" "Latin America")
PLANS=("Free" "Starter" "Professional" "Enterprise")

PRODUCT_NAMES=(
  "Widget Pro" "Widget Basic" "Sensor Pack" "Cable Kit"
  "CloudSync" "DataVault" "Analytics Pro" "DevTools Suite"
  "Setup Service" "Training Session" "Support Plan" "Migration Service"
  "USB Hub" "Docking Station" "Monitor Arm" "Keyboard Elite"
  "Security Suite" "API Gateway" "Dashboard Plus" "Backup Manager"
)

PRODUCT_CATEGORIES=(
  "Hardware" "Hardware" "Hardware" "Hardware"
  "Software" "Software" "Software" "Software"
  "Services" "Services" "Services" "Services"
  "Accessories" "Accessories" "Accessories" "Accessories"
  "Software" "Software" "Software" "Software"
)

PRODUCT_PRICES=(
  "75.00" "45.00" "120.00" "25.00"
  "199.99" "149.00" "299.99" "89.00"
  "500.00" "250.00" "350.00" "750.00"
  "39.99" "189.00" "59.99" "129.99"
  "249.00" "399.00" "179.00" "99.00"
)

PRODUCT_STOCKS=(
  "500" "800" "300" "1200"
  "0" "0" "0" "0"
  "0" "0" "0" "0"
  "650" "220" "410" "175"
  "0" "0" "0" "0"
)

ORDER_STATUSES=("Completed" "Completed" "Completed" "Completed" "Pending" "Cancelled")

# ── Deterministic helpers ────────────────────────────────────────────────────

# Pseudo-random number from seed; result stored in global PRAND_RESULT
prand() {
  local seed=$1 mod=$2
  PRAND_RESULT=$(( (seed * 1103515245 + 12345) % 2147483648 % mod ))
}

# ============================================================================
# FILE 1: data/customers.csv  (30 rows)
# ============================================================================
{
  echo "Customer_ID,Name,Email,Region,Signup_Date,Plan"

  for i in $(seq 1 30); do
    cid=$(printf "C%03d" "$i")
    first="${FIRST_NAMES[$((i - 1))]}"
    last="${LAST_NAMES[$((i - 1))]}"
    name="${first} ${last}"

    # Email: lowercase first name @ rotating domain
    domain_idx=$(( (i - 1) % ${#DOMAINS[@]} ))
    email="$(echo "$first" | tr '[:upper:]' '[:lower:]')@${DOMAINS[$domain_idx]}"

    # Region: distribute roughly evenly with some clustering
    prand "$i" 4
    region="${REGIONS[$PRAND_RESULT]}"

    # Signup date: spread across 2024
    month=$(( (i - 1) % 12 + 1 ))
    day=$(( (i * 7 + 3) % 28 + 1 ))
    signup_date=$(printf "2024-%02d-%02d" "$month" "$day")

    # Plan: distribute with bias toward Professional and Enterprise
    prand "$((i + 7))" 4
    plan="${PLANS[$PRAND_RESULT]}"

    echo "${cid},${name},${email},${region},${signup_date},${plan}"
  done
} > data/customers.csv

# ============================================================================
# FILE 2: data/products.csv  (20 rows)
# ============================================================================
{
  echo "Product_ID,Name,Category,Price,Stock"

  for i in $(seq 1 20); do
    pid=$(printf "PROD-%02d" "$i")
    pname="${PRODUCT_NAMES[$((i - 1))]}"
    pcat="${PRODUCT_CATEGORIES[$((i - 1))]}"
    pprice="${PRODUCT_PRICES[$((i - 1))]}"
    pstock="${PRODUCT_STOCKS[$((i - 1))]}"

    echo "${pid},${pname},${pcat},${pprice},${pstock}"
  done
} > data/products.csv

# ============================================================================
# FILE 3: data/orders.csv  (60 rows)
#
# Constraints:
#   - Customer_IDs must reference C001..C030
#   - Product_IDs must reference PROD-01..PROD-20
#   - Products PROD-09 and PROD-12 are NEVER ordered (zero-order products)
#   - Orders span Jan-Dec 2025
# ============================================================================

# Products that will appear in orders (exclude PROD-09 and PROD-12 for
# the "products with zero orders" test case)
ORDERABLE_PRODUCTS=(1 2 3 4 5 6 7 8 10 11 13 14 15 16 17 18 19 20)

{
  echo "Order_ID,Customer_ID,Product_ID,Quantity,Amount,Date,Status"

  for i in $(seq 1 60); do
    oid=$(printf "ORD-%03d" "$i")

    # Customer: cycle through 1-30 with some variation
    prand "$((i * 3))" 30
    cust_num=$((PRAND_RESULT + 1))
    cid=$(printf "C%03d" "$cust_num")

    # Product: pick from orderable products only
    prand "$((i * 37 + 17))" ${#ORDERABLE_PRODUCTS[@]}
    prod_num=${ORDERABLE_PRODUCTS[$PRAND_RESULT]}
    pid=$(printf "PROD-%02d" "$prod_num")

    # Quantity: 1-10
    prand "$((i * 11))" 10
    qty=$((PRAND_RESULT + 1))

    # Amount: quantity * product price
    price="${PRODUCT_PRICES[$((prod_num - 1))]}"
    amount=$(awk "BEGIN { printf \"%.2f\", ${qty} * ${price} }")

    # Date: spread across 2025
    month=$(( (i - 1) % 12 + 1 ))
    day=$(( (i * 3 + 5) % 28 + 1 ))
    order_date=$(printf "2025-%02d-%02d" "$month" "$day")

    # Status: mostly Completed, some Pending and Cancelled
    prand "$((i + 5))" ${#ORDER_STATUSES[@]}
    status="${ORDER_STATUSES[$PRAND_RESULT]}"

    echo "${oid},${cid},${pid},${qty},${amount},${order_date},${status}"
  done
} > data/orders.csv

git add -A
git commit -q -m "initial: add customer, product, and order data"
