package cli

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

type RequestOptions struct {
	BaseURL string
	Token   string
	APIKey  string
	Timeout time.Duration
	Headers map[string]string
}

func DoRequest(ctx context.Context, method, path string, body io.Reader, opts RequestOptions) (*http.Response, error) {
	if opts.BaseURL == "" {
		return nil, fmt.Errorf("missing base url")
	}
	base := strings.TrimRight(opts.BaseURL, "/")
	if !strings.HasPrefix(path, "/") {
		path = "/" + path
	}
	req, err := http.NewRequestWithContext(ctx, method, base+path, body)
	if err != nil {
		return nil, err
	}
	if opts.APIKey != "" {
		req.Header.Set("X-API-Key", opts.APIKey)
	} else if opts.Token != "" {
		req.Header.Set("Authorization", "Bearer "+opts.Token)
	}
	for k, v := range opts.Headers {
		if v != "" {
			req.Header.Set(k, v)
		}
	}
	client := http.Client{
		Timeout: opts.Timeout,
	}
	return client.Do(req)
}
