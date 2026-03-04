package cli

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"
)

func ExchangeCode(ctx context.Context, baseURL, realm, clientID, code, redirectURI, codeVerifier string) (*Token, error) {
	if code == "" || redirectURI == "" || codeVerifier == "" {
		return nil, fmt.Errorf("missing code, redirect_uri, or code_verifier")
	}
	endpoint, err := TokenEndpoint(baseURL, realm)
	if err != nil {
		return nil, err
	}
	form := url.Values{}
	form.Set("grant_type", "authorization_code")
	form.Set("client_id", clientID)
	form.Set("code", code)
	form.Set("redirect_uri", redirectURI)
	form.Set("code_verifier", codeVerifier)

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint, strings.NewReader(form.Encode()))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Accept", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("token exchange failed: %s", strings.TrimSpace(string(body)))
	}
	var tok Token
	if err := json.Unmarshal(body, &tok); err != nil {
		return nil, err
	}
	if tok.ObtainedAt.IsZero() {
		tok.ObtainedAt = time.Now().UTC()
	}
	if tok.Expiry.IsZero() && tok.ExpiresIn > 0 {
		tok.Expiry = tok.ObtainedAt.Add(time.Duration(tok.ExpiresIn) * time.Second)
	}
	tok.AuthURL = baseURL
	tok.Realm = realm
	tok.ClientID = clientID
	return &tok, nil
}

func RefreshToken(ctx context.Context, baseURL, realm, clientID, refreshToken string) (*Token, error) {
	if refreshToken == "" {
		return nil, fmt.Errorf("missing refresh_token")
	}
	endpoint, err := TokenEndpoint(baseURL, realm)
	if err != nil {
		return nil, err
	}
	form := url.Values{}
	form.Set("grant_type", "refresh_token")
	form.Set("client_id", clientID)
	form.Set("refresh_token", refreshToken)

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint, strings.NewReader(form.Encode()))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Accept", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("token refresh failed: %s", strings.TrimSpace(string(body)))
	}
	var tok Token
	if err := json.Unmarshal(body, &tok); err != nil {
		return nil, err
	}
	if tok.ObtainedAt.IsZero() {
		tok.ObtainedAt = time.Now().UTC()
	}
	if tok.Expiry.IsZero() && tok.ExpiresIn > 0 {
		tok.Expiry = tok.ObtainedAt.Add(time.Duration(tok.ExpiresIn) * time.Second)
	}
	tok.AuthURL = baseURL
	tok.Realm = realm
	tok.ClientID = clientID
	return &tok, nil
}
