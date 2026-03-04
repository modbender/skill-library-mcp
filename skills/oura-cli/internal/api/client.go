package api

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"

	"golang.org/x/oauth2"
)

const BaseURL = "https://api.ouraring.com/v2/usercollection/"

type Client struct {
	httpClient *http.Client
	baseURL    string
}

func NewClient(ctx context.Context, tokenSource oauth2.TokenSource) *Client {
	return &Client{
		httpClient: oauth2.NewClient(ctx, tokenSource),
		baseURL:    BaseURL,
	}
}

func (c *Client) get(endpoint string, params url.Values, v interface{}) error {
	u, err := url.Parse(c.baseURL + endpoint)
	if err != nil {
		return err
	}

	if params != nil {
		u.RawQuery = params.Encode()
	}

	req, err := http.NewRequest("GET", u.String(), nil)
	if err != nil {
		return err
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("API request failed with status %d: %s", resp.StatusCode, string(body))
	}

	if v != nil {
		if err := json.NewDecoder(resp.Body).Decode(v); err != nil {
			return err
		}
	}

	return nil
}
