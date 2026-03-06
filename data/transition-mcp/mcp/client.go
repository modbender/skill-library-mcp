package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

// TransitionClient wraps the Transition public API
type TransitionClient struct {
	baseURL    string
	apiKey     string
	httpClient *http.Client
}

// NewTransitionClient creates a new API client
func NewTransitionClient(baseURL, apiKey string) *TransitionClient {
	return &TransitionClient{
		baseURL: strings.TrimRight(baseURL, "/"),
		apiKey:  apiKey,
		httpClient: &http.Client{
			Timeout: 60 * time.Second,
		},
	}
}

func (tc *TransitionClient) doRequest(method, path string, body io.Reader) (*http.Response, error) {
	url := tc.baseURL + path
	req, err := http.NewRequest(method, url, body)
	if err != nil {
		return nil, err
	}

	if tc.apiKey != "" {
		req.Header.Set("X-API-Key", tc.apiKey)
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")

	return tc.httpClient.Do(req)
}

// Get performs a GET request and returns the JSON response as a string
func (tc *TransitionClient) Get(path string) (string, error) {
	resp, err := tc.doRequest("GET", path, nil)
	if err != nil {
		return "", fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode >= 400 {
		return "", fmt.Errorf("API error %d: %s", resp.StatusCode, string(data))
	}

	return string(data), nil
}

// Post performs a POST request and returns the JSON response as a string
func (tc *TransitionClient) Post(path string, body interface{}) (string, error) {
	var reader io.Reader
	if body != nil {
		jsonData, err := json.Marshal(body)
		if err != nil {
			return "", fmt.Errorf("failed to marshal body: %w", err)
		}
		reader = strings.NewReader(string(jsonData))
	}

	resp, err := tc.doRequest("POST", path, reader)
	if err != nil {
		return "", fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode >= 400 {
		return "", fmt.Errorf("API error %d: %s", resp.StatusCode, string(data))
	}

	return string(data), nil
}

// PostSSE performs a POST request that returns a Server-Sent Events stream,
// collects all data chunks, and returns the concatenated text
func (tc *TransitionClient) PostSSE(path string, body interface{}) (string, error) {
	var reader io.Reader
	if body != nil {
		jsonData, err := json.Marshal(body)
		if err != nil {
			return "", fmt.Errorf("failed to marshal body: %w", err)
		}
		reader = strings.NewReader(string(jsonData))
	}

	resp, err := tc.doRequest("POST", path, reader)
	if err != nil {
		return "", fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		data, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("API error %d: %s", resp.StatusCode, string(data))
	}

	// Check if this is actually an SSE response
	contentType := resp.Header.Get("Content-Type")
	if !strings.Contains(contentType, "text/event-stream") {
		// Not SSE, just read the whole body
		data, err := io.ReadAll(resp.Body)
		if err != nil {
			return "", fmt.Errorf("failed to read response: %w", err)
		}
		return string(data), nil
	}

	// Parse SSE stream
	var result strings.Builder
	scanner := bufio.NewScanner(resp.Body)
	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "data: ") {
			chunk := strings.TrimPrefix(line, "data: ")
			if chunk == "[DONE]" {
				break
			}
			result.WriteString(chunk)
		}
	}

	return result.String(), scanner.Err()
}
