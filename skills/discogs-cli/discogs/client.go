// Package discogs provides a client for interacting with the Discogs API.
package discogs

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"github.com/irlndts/go-discogs"
	"github.com/spf13/viper"
)

// --- Custom Client for Wantlist ---

// Client manages requests to the Discogs API, including the wantlist.
type Client struct {
	LegacyClient discogs.Discogs // For existing collection/search calls
	HTTPClient   *http.Client
	Token        string
}

// NewClient creates a new configured Discogs API client.
func NewClient() *Client {
	token := viper.GetString("token")
	username := viper.GetString("username")

	if token == "" || username == "" {
		log.Fatalf("Error: 'token' and 'username' not set in config file.")
	}

	legacyClient, err := discogs.New(&discogs.Options{
		UserAgent: "OpenClawDiscogsSkill/1.3",
		Token:     token,
	})
	if err != nil {
		log.Fatalf("Error creating Discogs legacy client: %v", err)
	}

	return &Client{
		LegacyClient: legacyClient,
		HTTPClient:   &http.Client{},
		Token:        token,
	}
}

// WantlistRequest performs a raw HTTP request to a given Discogs API endpoint.
// It is used for wantlist operations not covered by the legacy client.
func (c *Client) WantlistRequest(method, url string, target interface{}) error {
	req, err := http.NewRequest(method, url, nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	// Set the required headers for authentication and user-agent.
	req.Header.Set("User-Agent", "OpenClawDiscogsSkill/1.3")
	req.Header.Set("Authorization", fmt.Sprintf("Discogs token=%s", c.Token))

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	// Check for non-successful status codes.
	if resp.StatusCode >= 300 {
		return fmt.Errorf("API request failed with status: %s", resp.Status)
	}

	// If a target struct is provided, unmarshal the response body into it.
	if target != nil {
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			return fmt.Errorf("failed to read response body: %w", err)
		}
		if err := json.Unmarshal(body, target); err != nil {
			return fmt.Errorf("failed to unmarshal response: %w", err)
		}
	}

	return nil
}


// --- API Response Types ---

type Artist struct {
	Name string `json:"name"`
}

type Image struct {
	Type        string `json:"type"`
	URI         string `json:"uri"`
	ResourceURL string `json:"resource_url"`
	URI150      string `json:"uri150"`
	Width       int    `json:"width"`
	Height      int    `json:"height"`
}

type Release struct {
	Title   string   `json:"title"`
	Artists []Artist `json:"artists"`
	Images  []Image  `json:"images"`
}

// Wantlist defines the structure for the entire wantlist response from Discogs.
type Wantlist struct {
	Wants []Want `json:"wants"`
}

// Want represents a single item in the user's wantlist.
type Want struct {
	ID               int              `json:"id"`
	BasicInformation BasicInformation `json:"basic_information"`
}

// BasicInformation contains the core details about a release.
type BasicInformation struct {
	Artists []Artist `json:"artists"`
	Title   string   `json:"title"`
	Year    int      `json:"year"`
}
