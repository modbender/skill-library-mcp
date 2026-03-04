package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/alexrudloff/caesar-cli/internal/config"
)

type Client struct {
	httpClient *http.Client
	baseURL    string
	apiKey     string
}

// Options allows creating a Client with explicit dependencies (used in tests).
type Options struct {
	HTTPClient *http.Client
	BaseURL    string
	APIKey     string
}

func New() (*Client, error) {
	apiKey, err := config.GetAPIKey()
	if err != nil {
		return nil, err
	}
	return &Client{
		httpClient: &http.Client{Timeout: 120 * time.Second},
		baseURL:    config.BaseURL,
		apiKey:     apiKey,
	}, nil
}

// NewWithOptions creates a Client with explicit dependencies.
func NewWithOptions(opts Options) *Client {
	httpClient := opts.HTTPClient
	if httpClient == nil {
		httpClient = &http.Client{Timeout: 120 * time.Second}
	}
	baseURL := opts.BaseURL
	if baseURL == "" {
		baseURL = config.BaseURL
	}
	return &Client{
		httpClient: httpClient,
		baseURL:    baseURL,
		apiKey:     opts.APIKey,
	}
}

func (c *Client) do(method, path string, body any) (*http.Response, error) {
	var reqBody io.Reader
	if body != nil {
		b, err := json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("marshal request: %w", err)
		}
		reqBody = bytes.NewReader(b)
	}

	req, err := http.NewRequest(method, c.baseURL+path, reqBody)
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}

	if resp.StatusCode >= 400 {
		defer resp.Body.Close()
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(respBody))
	}

	return resp, nil
}

// CreateResearch starts a new research job.
func (c *Client) CreateResearch(req *CreateResearchRequest) (*CreateResearchResponse, error) {
	resp, err := c.do("POST", "/research", req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result CreateResearchResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &result, nil
}

// GetResearch retrieves a research job by ID.
func (c *Client) GetResearch(id string) (*ResearchObject, error) {
	resp, err := c.do("GET", "/research/"+id, nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result ResearchObject
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &result, nil
}

// GetResearchEvents retrieves events/reasoning steps for a research job.
func (c *Client) GetResearchEvents(id string) ([]ResearchEvent, error) {
	resp, err := c.do("GET", "/research/"+id+"/events", nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result []ResearchEvent
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return result, nil
}

// GetResultContent retrieves content for a specific source result.
func (c *Client) GetResultContent(researchID, resultID, format string) (*ResultContent, error) {
	path := fmt.Sprintf("/research/%s/results/%s/content", researchID, resultID)
	if format != "" {
		path += "?format=" + format
	}
	resp, err := c.do("GET", path, nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result ResultContent
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &result, nil
}

// CreateBrainstorm starts a brainstorm session.
func (c *Client) CreateBrainstorm(query string) (*BrainstormSession, error) {
	resp, err := c.do("POST", "/research/brainstorm", map[string]string{"query": query})
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result BrainstormSession
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &result, nil
}

// CreateChatMessage sends a follow-up chat message on a research job.
func (c *Client) CreateChatMessage(researchID string, content string) (*ChatMessage, error) {
	resp, err := c.do("POST", "/research/"+researchID+"/chat", map[string]string{"content": content})
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result ChatMessage
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &result, nil
}

// GetChatHistory retrieves chat messages for a research job.
func (c *Client) GetChatHistory(researchID string) ([]ChatMessage, error) {
	resp, err := c.do("GET", "/research/"+researchID+"/chat", nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result []ChatMessage
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return result, nil
}

// GetChatMessage polls a single chat message by ID.
func (c *Client) GetChatMessage(researchID, messageID string) (*ChatMessage, error) {
	path := fmt.Sprintf("/research/%s/chat/%s", researchID, messageID)
	resp, err := c.do("GET", path, nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result ChatMessage
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &result, nil
}

// StreamChatMessage returns the raw SSE response for streaming a chat message.
func (c *Client) StreamChatMessage(researchID, messageID string) (*http.Response, error) {
	path := fmt.Sprintf("/research/%s/chat/%s/stream", researchID, messageID)
	return c.do("GET", path, nil)
}

// CreateCollection creates a new file collection.
func (c *Client) CreateCollection(name, description string) (*Collection, error) {
	body := map[string]string{"name": name}
	if description != "" {
		body["description"] = description
	}
	resp, err := c.do("POST", "/research/collections", body)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result Collection
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &result, nil
}
