# Booking Flow

## End-to-End: Search → Book → Manage

### 1. Search (Offer Request)

```
POST /air/offer_requests
{
  "data": {
    "slices": [
      {"origin": "MIA", "destination": "LHR", "departure_date": "2026-04-15"},
      {"origin": "LHR", "destination": "MIA", "departure_date": "2026-04-22"}  // optional return
    ],
    "passengers": [{"type": "adult"}],
    "cabin_class": "economy",
    "max_connections": 0  // optional, 0 = nonstop
  }
}
```

Returns: offer_request with embedded `offers[]`. Each offer has an `id`, price, slices with segments.

### 2. Inspect Offer

```
GET /air/offers/{offer_id}?return_available_services=true
```

Shows: fare conditions (refundable? changeable?), baggage allowance, available extras (bags, seats).

### 3. Book (Create Order)

```
POST /air/orders
{
  "data": {
    "selected_offers": ["off_XXXXX"],
    "passengers": [
      {
        "id": "pas_XXXXX",  // from offer request
        "title": "mr",
        "given_name": "FABIO",
        "family_name": "RIBEIRO",
        "born_on": "1977-01-31",
        "email": "fabio@ribei.ro",
        "phone_number": "+13059159687",
        "gender": "m",
        "type": "adult"
      }
    ],
    "type": "instant",
    "payments": [
      {"type": "balance", "amount": "359.07", "currency": "USD"}
    ]
  }
}
```

Returns: order with `id`, `booking_reference` (PNR), slices, passengers, documents.

### 4. Manage Order

```
GET /air/orders/{order_id}
```

Check status, available actions (cancel, change, update).

### 5. Cancel

Two-step process:
1. **Quote**: `POST /air/order_cancellations` with `{"data": {"order_id": "ord_XXX"}}` → returns refund amount and cancellation ID
2. **Confirm**: `POST /air/order_cancellations/{cancel_id}/actions/confirm` → executes cancellation

## Passenger Data Requirements

| Field | Required | Notes |
|-------|----------|-------|
| given_name | Yes | First name, as on passport |
| family_name | Yes | Last name |
| title | Yes | mr, mrs, ms, miss, dr |
| born_on | Yes | YYYY-MM-DD |
| email | Yes | Contact email |
| phone_number | Yes | With country code (+1...) |
| gender | Yes | m or f |
| type | Yes | adult, child, infant_without_seat |
| nationality | No | 2-letter country code (BR, US, etc.) |
| id | Yes for booking | Passenger ID from offer request |
