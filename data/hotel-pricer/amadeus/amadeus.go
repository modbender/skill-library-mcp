// Package amadeus handles interactions with the Amadeus Self-Service APIs.
package amadeus

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/spf13/viper"
)

const (
	// APIBaseURL is the base URL for the Amadeus test environment.
	APIBaseURL = "https://test.api.amadeus.com"
	// tokenURL is the endpoint for obtaining an OAuth2 access token.
	tokenURL = APIBaseURL + "/v1/security/oauth2/token"
)

// TokenResponse defines the structure of the JSON response from the Amadeus token endpoint.
type TokenResponse struct {
	AccessToken string `json:"access_token"`
	ExpiresIn   int    `json:"expires_in"`
}

// GetAmadeusToken performs the OAuth2 client credentials grant flow to obtain an access token.
// It implements a caching mechanism to reuse tokens until they expire.
func GetAmadeusToken(apiKey, apiSecret string) (string, error) {
	// 1. Check for an existing, non-expired token in the config.
	cachedToken := viper.GetString("amadeus.auth.token")
	tokenExpiryStr := viper.GetString("amadeus.auth.expiry")

	if cachedToken != "" && tokenExpiryStr != "" {
		tokenExpiry, err := time.Parse(time.RFC3339, tokenExpiryStr)
		// If the token is valid and expires more than 60 seconds in the future, reuse it.
		if err == nil && tokenExpiry.After(time.Now().Add(60*time.Second)) {
			return cachedToken, nil
		}
	}

	// 2. If no valid token is found, request a new one.
	fmt.Println("No valid token found, requesting a new one from Amadeus...")
	client := &http.Client{}

	// Prepare the request body.
	data := url.Values{}
	data.Set("grant_type", "client_credentials")
	data.Set("client_id", apiKey)
	data.Set("client_secret", apiSecret)

	// Create and execute the POST request.
	req, err := http.NewRequest("POST", tokenURL, strings.NewReader(data.Encode()))
	if err != nil {
		return "", fmt.Errorf("failed to create token request: %w", err)
	}
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")

	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("failed to execute token request: %w", err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read token response body: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("token request failed with status %d: %s", resp.StatusCode, string(body))
	}

	// Unmarshal the JSON response.
	var tokenResponse TokenResponse
	if err := json.Unmarshal(body, &tokenResponse); err != nil {
		return "", fmt.Errorf("failed to parse token response: %w", err)
	}

	// 3. Save the new token and its calculated expiry time to the config file.
	newExpiry := time.Now().Add(time.Duration(tokenResponse.ExpiresIn) * time.Second)
	viper.Set("amadeus.auth.token", tokenResponse.AccessToken)
	viper.Set("amadeus.auth.expiry", newExpiry.Format(time.RFC3339))

	if err := viper.WriteConfig(); err != nil {
		// Log the error but don't fail the operation, as we still have a valid token in memory.
		fmt.Printf("Warning: failed to write token to config file: %v\n", err)
	}

	return tokenResponse.AccessToken, nil
}
