package krogerapi

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"

	"github.com/blanxlait/krocli/internal/config"
	"golang.org/x/oauth2"
)

const BaseURL = "https://api.kroger.com/v1"

type Client struct {
	http    *http.Client
	baseURL string
	creds   *config.Credentials
}

func NewClient(creds *config.Credentials) *Client {
	return &Client{
		http:    &http.Client{},
		baseURL: BaseURL,
		creds:   creds,
	}
}

func (c *Client) doRequest(method, path string, body io.Reader, tok *oauth2.Token) ([]byte, error) {
	u := c.baseURL + path
	req, err := http.NewRequest(method, u, body)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+tok.AccessToken)
	req.Header.Set("Accept", "application/json")
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	resp, err := c.http.Do(req)
	if err != nil {
		return nil, err
	}
	defer func() { _ = resp.Body.Close() }()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode >= 400 {
		return nil, &APIError{StatusCode: resp.StatusCode, Body: string(data)}
	}
	return data, nil
}

type APIError struct {
	StatusCode int
	Body       string
}

func (e *APIError) Error() string {
	return fmt.Sprintf("API %d: %s", e.StatusCode, e.Body)
}

func (c *Client) doClientRequest(method, path string, body io.Reader) ([]byte, error) {
	tok, err := GetClientToken(c.creds)
	if err != nil {
		return nil, err
	}
	data, err := c.doRequest(method, path, body, tok)
	if err != nil {
		if apiErr, ok := err.(*APIError); ok && (apiErr.StatusCode == 401 || apiErr.StatusCode == 403) {
			ClearClientToken()
			tok, err = GetClientToken(c.creds)
			if err != nil {
				return nil, err
			}
			return c.doRequest(method, path, body, tok)
		}
	}
	return data, err
}

func (c *Client) SearchProducts(term string, locationID string, limit int) (*ProductsResponse, error) {
	params := url.Values{"filter.term": {term}, "filter.limit": {fmt.Sprint(limit)}}
	if locationID != "" {
		params.Set("filter.locationId", locationID)
	}
	data, err := c.doClientRequest("GET", "/products?"+params.Encode(), nil)
	if err != nil {
		return nil, err
	}
	var resp ProductsResponse
	return &resp, json.Unmarshal(data, &resp)
}

func (c *Client) GetProduct(id string) (*ProductsResponse, error) {
	data, err := c.doClientRequest("GET", "/products/"+id, nil)
	if err != nil {
		return nil, err
	}
	var resp ProductsResponse
	return &resp, json.Unmarshal(data, &resp)
}

func (c *Client) SearchLocations(zipCode string, radiusMiles int, limit int) (*LocationsResponse, error) {
	params := url.Values{
		"filter.zipCode.near": {zipCode},
		"filter.limit":        {fmt.Sprint(limit)},
	}
	if radiusMiles > 0 {
		params.Set("filter.radiusInMiles", fmt.Sprint(radiusMiles))
	}
	data, err := c.doClientRequest("GET", "/locations?"+params.Encode(), nil)
	if err != nil {
		return nil, err
	}
	var resp LocationsResponse
	return &resp, json.Unmarshal(data, &resp)
}

func (c *Client) GetLocation(id string) (*LocationsResponse, error) {
	data, err := c.doClientRequest("GET", "/locations/"+id, nil)
	if err != nil {
		return nil, err
	}
	var resp LocationsResponse
	return &resp, json.Unmarshal(data, &resp)
}

func (c *Client) GetChains() (*ChainsResponse, error) {
	data, err := c.doClientRequest("GET", "/chains", nil)
	if err != nil {
		return nil, err
	}
	var resp ChainsResponse
	return &resp, json.Unmarshal(data, &resp)
}

func (c *Client) GetDepartments() (*DepartmentsResponse, error) {
	data, err := c.doClientRequest("GET", "/departments", nil)
	if err != nil {
		return nil, err
	}
	var resp DepartmentsResponse
	return &resp, json.Unmarshal(data, &resp)
}

func (c *Client) AddToCart(items []CartItem) error {
	tok, err := GetUserToken(c.creds)
	if err != nil {
		return err
	}
	body := CartRequest{Items: items}
	b, err := json.Marshal(body)
	if err != nil {
		return err
	}
	_, err = c.doRequest("PUT", "/cart/add", strings.NewReader(string(b)), tok)
	return err
}

func (c *Client) GetProfile() (*IdentityResponse, error) {
	tok, err := GetUserToken(c.creds)
	if err != nil {
		return nil, err
	}
	data, err := c.doRequest("GET", "/identity/profile", nil, tok)
	if err != nil {
		return nil, err
	}
	var resp IdentityResponse
	return &resp, json.Unmarshal(data, &resp)
}
