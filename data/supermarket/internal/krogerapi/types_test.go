package krogerapi

import (
	"encoding/json"
	"testing"
)

func TestProductsResponse_Unmarshal(t *testing.T) {
	raw := `{
		"data": [{
			"productId": "0011110838049",
			"upc": "0011110838049",
			"brand": "Kroger",
			"description": "2% Milk",
			"items": [{"itemId": "123", "size": "1 gal", "price": {"regular": 3.99, "promo": 2.99}}],
			"images": [{"perspective": "front", "sizes": [{"size": "large", "url": "https://example.com/img.jpg"}]}]
		}],
		"meta": {"pagination": {"start": 0, "limit": 10, "total": 1}}
	}`

	var resp ProductsResponse
	if err := json.Unmarshal([]byte(raw), &resp); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if len(resp.Data) != 1 {
		t.Fatalf("expected 1 product, got %d", len(resp.Data))
	}
	p := resp.Data[0]
	if p.ProductID != "0011110838049" {
		t.Errorf("ProductID = %q", p.ProductID)
	}
	if p.Items[0].Price.Regular != 3.99 {
		t.Errorf("Price.Regular = %v", p.Items[0].Price.Regular)
	}
	if resp.Meta.Pagination.Total != 1 {
		t.Errorf("Total = %d", resp.Meta.Pagination.Total)
	}
}

func TestLocationsResponse_Unmarshal(t *testing.T) {
	raw := `{
		"data": [{
			"locationId": "01400376",
			"chain": "Kroger",
			"name": "Kroger Downtown",
			"address": {"addressLine1": "100 Main St", "city": "Cincinnati", "state": "OH", "zipCode": "45202"},
			"phone": "513-555-0100"
		}],
		"meta": {"pagination": {"start": 0, "limit": 10, "total": 1}}
	}`

	var resp LocationsResponse
	if err := json.Unmarshal([]byte(raw), &resp); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if resp.Data[0].LocationID != "01400376" {
		t.Errorf("LocationID = %q", resp.Data[0].LocationID)
	}
	if resp.Data[0].Address.City != "Cincinnati" {
		t.Errorf("City = %q", resp.Data[0].Address.City)
	}
}

func TestCartRequest_Marshal(t *testing.T) {
	req := CartRequest{
		Items: []CartItem{{UPC: "0011110838049", Quantity: 2}},
	}
	data, err := json.Marshal(req)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	var back CartRequest
	if err := json.Unmarshal(data, &back); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if back.Items[0].UPC != "0011110838049" || back.Items[0].Quantity != 2 {
		t.Errorf("round-trip failed: %+v", back)
	}
}

func TestIdentityResponse_Unmarshal(t *testing.T) {
	raw := `{"data": {"id": "user-123"}}`
	var resp IdentityResponse
	if err := json.Unmarshal([]byte(raw), &resp); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if resp.Data.ID != "user-123" {
		t.Errorf("ID = %q", resp.Data.ID)
	}
}
