package krogerapi

type ProductsResponse struct {
	Data []Product `json:"data"`
	Meta Meta      `json:"meta"`
}

type Product struct {
	ProductID   string       `json:"productId"`
	UPC         string       `json:"upc"`
	Brand       string       `json:"brand"`
	Description string       `json:"description"`
	Items       []ProductItem `json:"items"`
	Images      []Image      `json:"images"`
}

type ProductItem struct {
	ItemID string `json:"itemId"`
	Size   string `json:"size"`
	Price  *Price `json:"price,omitempty"`
}

type Price struct {
	Regular float64 `json:"regular"`
	Promo   float64 `json:"promo"`
}

type Image struct {
	Perspective string     `json:"perspective"`
	Sizes       []ImageSize `json:"sizes"`
}

type ImageSize struct {
	Size string `json:"size"`
	URL  string `json:"url"`
}

type LocationsResponse struct {
	Data []Location `json:"data"`
	Meta Meta       `json:"meta"`
}

type Location struct {
	LocationID string  `json:"locationId"`
	Chain      string  `json:"chain"`
	Name       string  `json:"name"`
	Address    Address `json:"address"`
	Phone      string  `json:"phone"`
}

type Address struct {
	AddressLine1 string `json:"addressLine1"`
	City         string `json:"city"`
	State        string `json:"state"`
	ZipCode      string `json:"zipCode"`
}

type Meta struct {
	Pagination Pagination `json:"pagination"`
}

type Pagination struct {
	Start int `json:"start"`
	Limit int `json:"limit"`
	Total int `json:"total"`
}

type CartRequest struct {
	Items []CartItem `json:"items"`
}

type CartItem struct {
	UPC      string `json:"upc"`
	Quantity int    `json:"quantity"`
}

type IdentityResponse struct {
	Data IdentityData `json:"data"`
}

type IdentityData struct {
	ID string `json:"id"`
}

type ChainsResponse struct {
	Data []Chain `json:"data"`
}

type Chain struct {
	Name string `json:"name"`
}

type DepartmentsResponse struct {
	Data []Department `json:"data"`
}

type Department struct {
	DepartmentID string `json:"departmentId"`
	Name         string `json:"name"`
}
