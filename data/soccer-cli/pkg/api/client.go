package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

const BaseURL = "https://v3.football.api-sports.io"

type Client struct {
	ApiKey     string
	HttpClient *http.Client
}

func NewClient(apiKey string) *Client {
	return &Client{
		ApiKey:     apiKey,
		HttpClient: &http.Client{Timeout: 10 * time.Second},
	}
}

func (c *Client) sendRequest(endpoint string, target interface{}) error {
	req, err := http.NewRequest("GET", fmt.Sprintf("%s%s", BaseURL, endpoint), nil)
	if err != nil {
		return err
	}

	req.Header.Set("x-apisports-key", c.ApiKey)
	req.Header.Set("Content-Type", "application/json")

	res, err := c.HttpClient.Do(req)
	if err != nil {
		return err
	}
	defer res.Body.Close()

	if res.StatusCode != http.StatusOK {
		return fmt.Errorf("API request failed with status: %s", res.Status)
	}
	
	// Use a generic wrapper to decode the top-level structure
	var apiResp APIResponse
	apiResp.Response = target // Point the generic response field to our specific target struct
	
	return json.NewDecoder(res.Body).Decode(&apiResp)
}

func (c *Client) GetTeam(teamName string) ([]TeamResponse, error) {
	var teams []TeamResponse
	endpoint := fmt.Sprintf("/teams?search=%s", teamName)
	err := c.sendRequest(endpoint, &teams)
	return teams, err
}

func (c *Client) GetLatestFixturesForTeam(teamID int, limit int) ([]FixtureResponse, error) {
	var fixtures []FixtureResponse
	endpoint := fmt.Sprintf("/fixtures?team=%d&last=%d", teamID, limit)
	err := c.sendRequest(endpoint, &fixtures)
	return fixtures, err
}

func (c *Client) GetFixtureDetails(fixtureID int) ([]FixtureResponse, error) {
	var fixtureDetails []FixtureResponse
	endpoint := fmt.Sprintf("/fixtures?id=%d", fixtureID)
	err := c.sendRequest(endpoint, &fixtureDetails)
	return fixtureDetails, err
}

func (c *Client) GetPlayerStatsForFixture(fixtureID int) ([]PlayerStatsParent, error) {
	var playerStats []PlayerStatsParent
	endpoint := fmt.Sprintf("/fixtures/players?fixture=%d", fixtureID)
	err := c.sendRequest(endpoint, &playerStats)
	return playerStats, err
}
