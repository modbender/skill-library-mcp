#!/bin/bash
# Shopify Admin API Helper
# Usage: ./shopify-admin.sh <command> [args]

set -e

# Use SHOPIFY_STORE_DOMAIN and SHOPIFY_ACCESS_TOKEN from the process environment only.
# Do not source any env file; set these where the agent/gateway runs (e.g. export or gateway env).
if [ -z "${SHOPIFY_STORE_DOMAIN}" ] || [ -z "${SHOPIFY_ACCESS_TOKEN}" ]; then
  echo "Error: SHOPIFY_STORE_DOMAIN and SHOPIFY_ACCESS_TOKEN must be set in the environment." >&2
  exit 1
fi

API_BASE="https://${SHOPIFY_STORE_DOMAIN}/admin/api/2026-01"
AUTH_HEADER="X-Shopify-Access-Token: ${SHOPIFY_ACCESS_TOKEN}"

case "$1" in
  orders)
    curl -s "${API_BASE}/orders.json?status=any&limit=${2:-10}" \
      -H "${AUTH_HEADER}" -H "Content-Type: application/json" | jq '.'
    ;;
  
  order)
    [ -z "$2" ] && echo "Usage: $0 order <order_id>" && exit 1
    curl -s "${API_BASE}/orders/$2.json" \
      -H "${AUTH_HEADER}" -H "Content-Type: application/json" | jq '.'
    ;;
  
  products)
    curl -s "${API_BASE}/products.json?limit=${2:-50}" \
      -H "${AUTH_HEADER}" -H "Content-Type: application/json" | jq '.products'
    ;;
  
  product)
    [ -z "$2" ] && echo "Usage: $0 product <product_id>" && exit 1
    curl -s "${API_BASE}/products/$2.json" \
      -H "${AUTH_HEADER}" -H "Content-Type: application/json" | jq '.'
    ;;
  
  delete-product)
    [ -z "$2" ] && echo "Usage: $0 delete-product <product_id>" && exit 1
    curl -s -X DELETE "${API_BASE}/products/$2.json" \
      -H "${AUTH_HEADER}" \
      -w "\nHTTP Status: %{http_code}\n"
    ;;
  
  customers)
    curl -s "${API_BASE}/customers.json?limit=${2:-50}" \
      -H "${AUTH_HEADER}" -H "Content-Type: application/json" | jq '.customers'
    ;;
  
  customer)
    [ -z "$2" ] && echo "Usage: $0 customer <customer_id>" && exit 1
    curl -s "${API_BASE}/customers/$2.json" \
      -H "${AUTH_HEADER}" -H "Content-Type: application/json" | jq '.'
    ;;
  
  shop)
    curl -s "${API_BASE}/shop.json" \
      -H "${AUTH_HEADER}" -H "Content-Type: application/json" | jq '.'
    ;;

  marketing-events)
    curl -s "${API_BASE}/marketing_events.json?limit=${2:-50}" \
      -H "${AUTH_HEADER}" -H "Content-Type: application/json" | jq '.marketing_events'
    ;;

  marketing-event)
    [ -z "$2" ] && echo "Usage: $0 marketing-event <event_id>" && exit 1
    curl -s "${API_BASE}/marketing_events/$2.json" \
      -H "${AUTH_HEADER}" -H "Content-Type: application/json" | jq '.'
    ;;

  reports)
    curl -s "${API_BASE}/reports.json" \
      -H "${AUTH_HEADER}" -H "Content-Type: application/json" | jq '.reports'
    ;;

  report)
    [ -z "$2" ] && echo "Usage: $0 report <report_id>" && exit 1
    curl -s "${API_BASE}/reports/$2.json" \
      -H "${AUTH_HEADER}" -H "Content-Type: application/json" | jq '.'
    ;;

  customer-events)
    [ -z "$2" ] && echo "Usage: $0 customer-events <customer_id>" && exit 1
    curl -s "${API_BASE}/customers/$2/events.json" \
      -H "${AUTH_HEADER}" -H "Content-Type: application/json" | jq '.events'
    ;;

  analytics-orders)
    # Get orders with attribution data (referring site, UTM)
    curl -s "${API_BASE}/orders.json?status=any&limit=${2:-50}" \
      -H "${AUTH_HEADER}" -H "Content-Type: application/json" | jq '.orders | map({id, name, referring_site, landing_site, source_name, created_at})'
    ;;

  *)
    echo "Shopify Admin API Helper"
    echo ""
    echo "Usage: $0 <command> [args]"
    echo ""
    echo "Orders & Products:"
    echo "  orders [limit]              List orders"
    echo "  order <id>                  Get specific order"
    echo "  products [limit]            List products"
    echo "  product <id>                Get specific product"
    echo "  delete-product <id>         Delete a product"
    echo ""
    echo "Customers:"
    echo "  customers [limit]           List customers"
    echo "  customer <id>               Get specific customer"
    echo "  customer-events <id>        Get customer behavior events"
    echo ""
    echo "Marketing & Analytics:"
    echo "  marketing-events [limit]    List marketing campaigns"
    echo "  marketing-event <id>        Get specific campaign"
    echo "  reports                     List available reports"
    echo "  report <id>                 Get report data"
    echo "  analytics-orders [limit]    Orders with UTM/referral data"
    echo ""
    echo "Shop:"
    echo "  shop                        Get shop info"
    echo ""
    echo "Requires SHOPIFY_STORE_DOMAIN and SHOPIFY_ACCESS_TOKEN env vars"
    ;;
esac
