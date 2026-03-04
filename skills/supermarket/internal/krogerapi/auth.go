package krogerapi

import (
	"bytes"
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/blanxlait/krocli/internal/config"
	"github.com/blanxlait/krocli/internal/secrets"
	"github.com/blanxlait/krocli/internal/ui"
	"golang.org/x/oauth2"
)

const (
	tokenKeyClient = "client_credentials"
	tokenKeyUser   = "authorization_code"
	authURL        = "https://api.kroger.com/v1/connect/oauth2/authorize"
)

// tokenURL is a var so tests can override it with httptest.Server URLs.
var tokenURL = "https://api.kroger.com/v1/connect/oauth2/token"

// tokenHTTPClient is the HTTP client used for token exchange. Tests override this.
var tokenHTTPClient = http.DefaultClient

func oauthConfig(creds *config.Credentials, redirectURL string, scopes ...string) *oauth2.Config {
	return &oauth2.Config{
		ClientID:     creds.ClientID,
		ClientSecret: creds.ClientSecret,
		Endpoint: oauth2.Endpoint{
			AuthURL:  authURL,
			TokenURL: tokenURL,
		},
		RedirectURL: redirectURL,
		Scopes:      scopes,
	}
}

func ClearClientToken() {
	_ = secrets.DeleteToken(tokenKeyClient)
}

func GetClientToken(creds *config.Credentials) (*oauth2.Token, error) {
	td, err := secrets.LoadToken(tokenKeyClient)
	if err == nil && td.Expiry.After(time.Now()) {
		return &oauth2.Token{
			AccessToken: td.AccessToken,
			TokenType:   td.TokenType,
			Expiry:      td.Expiry,
		}, nil
	}

	var tok *oauth2.Token
	if creds == nil {
		tok, err = hostedClientCredentialsExchange()
	} else {
		tok, err = clientCredentialsExchange(creds, "product.compact")
	}
	if err != nil {
		return nil, fmt.Errorf("client credentials exchange: %w", err)
	}

	_ = secrets.StoreToken(tokenKeyClient, &secrets.TokenData{
		AccessToken: tok.AccessToken,
		TokenType:   tok.TokenType,
		Expiry:      tok.Expiry,
	})
	return tok, nil
}

func clientCredentialsExchange(creds *config.Credentials, scope string) (*oauth2.Token, error) {
	data := url.Values{
		"grant_type": {"client_credentials"},
		"scope":      {scope},
	}
	req, err := http.NewRequest("POST", tokenURL, strings.NewReader(data.Encode()))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.SetBasicAuth(creds.ClientID, creds.ClientSecret)

	resp, err := tokenHTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer func() { _ = resp.Body.Close() }()

	body, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("token endpoint %d: %s", resp.StatusCode, string(body))
	}

	var tokenResp struct {
		AccessToken string `json:"access_token"`
		TokenType   string `json:"token_type"`
		ExpiresIn   int    `json:"expires_in"`
	}
	if err := json.Unmarshal(body, &tokenResp); err != nil {
		return nil, err
	}

	return &oauth2.Token{
		AccessToken: tokenResp.AccessToken,
		TokenType:   tokenResp.TokenType,
		Expiry:      time.Now().Add(time.Duration(tokenResp.ExpiresIn) * time.Second),
	}, nil
}

func GetUserToken(creds *config.Credentials) (*oauth2.Token, error) {
	td, err := secrets.LoadToken(tokenKeyUser)
	if err != nil {
		return nil, fmt.Errorf("not logged in; run: krocli auth login")
	}
	if td.Expiry.After(time.Now()) {
		return &oauth2.Token{
			AccessToken:  td.AccessToken,
			RefreshToken: td.RefreshToken,
			TokenType:    td.TokenType,
			Expiry:       td.Expiry,
		}, nil
	}
	if td.RefreshToken == "" {
		return nil, fmt.Errorf("token expired and no refresh token; run: krocli auth login")
	}

	var tok *oauth2.Token
	if creds == nil {
		tok, err = hostedRefreshToken(td.RefreshToken)
	} else {
		cfg := oauthConfig(creds, "", "cart.basic:write", "profile.compact")
		tok, err = cfg.TokenSource(context.Background(), &oauth2.Token{RefreshToken: td.RefreshToken}).Token()
	}
	if err != nil {
		return nil, fmt.Errorf("token refresh failed: %w; run: krocli auth login", err)
	}

	_ = secrets.StoreToken(tokenKeyUser, &secrets.TokenData{
		AccessToken:  tok.AccessToken,
		RefreshToken: tok.RefreshToken,
		TokenType:    tok.TokenType,
		Expiry:       tok.Expiry,
	})
	return tok, nil
}

func LoginFlow(creds *config.Credentials, openURL func(string) error) error {
	if creds == nil {
		return hostedLoginFlow(openURL)
	}
	const callbackPort = 8080
	redirectURL := fmt.Sprintf("http://localhost:%d/callback", callbackPort)

	listener, err := net.Listen("tcp", fmt.Sprintf("127.0.0.1:%d", callbackPort))
	if err != nil {
		return fmt.Errorf("listen on port %d (is something else using it?): %w", callbackPort, err)
	}

	cfg := oauthConfig(creds, redirectURL, "cart.basic:write", "profile.compact")

	stateBytes := make([]byte, 16)
	_, _ = rand.Read(stateBytes)
	state := hex.EncodeToString(stateBytes)

	url := cfg.AuthCodeURL(state, oauth2.AccessTypeOffline)
	ui.Info("Opening browser for Kroger login...")
	if err := openURL(url); err != nil {
		ui.Warn("Could not open browser. Visit this URL:\n%s", url)
	}

	codeCh := make(chan string, 1)
	errCh := make(chan error, 1)

	mux := http.NewServeMux()
	mux.HandleFunc("/callback", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Query().Get("state") != state {
			errCh <- fmt.Errorf("state mismatch")
			http.Error(w, "state mismatch", http.StatusBadRequest)
			return
		}
		code := r.URL.Query().Get("code")
		if code == "" {
			errCh <- fmt.Errorf("no code in callback")
			http.Error(w, "no code", http.StatusBadRequest)
			return
		}
		_, _ = fmt.Fprintf(w, "<html><body><h1>Success!</h1><p>You can close this tab.</p></body></html>")
		codeCh <- code
	})

	srv := &http.Server{Handler: mux}
	go func() { _ = srv.Serve(listener) }()

	var code string
	select {
	case code = <-codeCh:
	case err := <-errCh:
		_ = srv.Close()
		return err
	case <-time.After(2 * time.Minute):
		_ = srv.Close()
		return fmt.Errorf("login timed out")
	}
	_ = srv.Close()

	tok, err := cfg.Exchange(context.Background(), code)
	if err != nil {
		return fmt.Errorf("token exchange: %w", err)
	}

	return secrets.StoreToken(tokenKeyUser, &secrets.TokenData{
		AccessToken:  tok.AccessToken,
		RefreshToken: tok.RefreshToken,
		TokenType:    tok.TokenType,
		Expiry:       tok.Expiry,
	})
}

// --- hosted mode functions ---

func hostedClientCredentialsExchange() (*oauth2.Token, error) {
	resp, err := tokenHTTPClient.Post(config.ProxyBaseURL+"/tokenClient", "application/json", nil)
	if err != nil {
		return nil, err
	}
	defer func() { _ = resp.Body.Close() }()

	body, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("hosted token endpoint %d: %s", resp.StatusCode, string(body))
	}

	var tokenResp struct {
		AccessToken string `json:"access_token"`
		TokenType   string `json:"token_type"`
		ExpiresIn   int    `json:"expires_in"`
	}
	if err := json.Unmarshal(body, &tokenResp); err != nil {
		return nil, err
	}
	return &oauth2.Token{
		AccessToken: tokenResp.AccessToken,
		TokenType:   tokenResp.TokenType,
		Expiry:      time.Now().Add(time.Duration(tokenResp.ExpiresIn) * time.Second),
	}, nil
}

func hostedLoginFlow(openURL func(string) error) error {
	sessionID := generateSessionID()

	loginURL := config.ProxyBaseURL + "/authorize?session_id=" + sessionID

	ui.Info("Opening browser for Kroger login...")
	if err := openURL(loginURL); err != nil {
		ui.Warn("Could not open browser. Visit this URL:\n%s", loginURL)
	}

	deadline := time.After(2 * time.Minute)
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-deadline:
			return fmt.Errorf("login timed out")
		case <-ticker.C:
			tok, err := pollForUserToken(sessionID)
			if err != nil {
				continue // still pending
			}
			return secrets.StoreToken(tokenKeyUser, &secrets.TokenData{
				AccessToken:  tok.AccessToken,
				RefreshToken: tok.RefreshToken,
				TokenType:    tok.TokenType,
				Expiry:       tok.Expiry,
			})
		}
	}
}

func pollForUserToken(sessionID string) (*oauth2.Token, error) {
	resp, err := tokenHTTPClient.Get(config.ProxyBaseURL + "/tokenUser?session_id=" + sessionID)
	if err != nil {
		return nil, err
	}
	defer func() { _ = resp.Body.Close() }()

	if resp.StatusCode == 202 {
		return nil, fmt.Errorf("pending")
	}

	body, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("hosted user token %d: %s", resp.StatusCode, string(body))
	}

	var tokenResp struct {
		AccessToken  string `json:"access_token"`
		RefreshToken string `json:"refresh_token"`
		TokenType    string `json:"token_type"`
		ExpiresIn    int    `json:"expires_in"`
	}
	if err := json.Unmarshal(body, &tokenResp); err != nil {
		return nil, err
	}
	return &oauth2.Token{
		AccessToken:  tokenResp.AccessToken,
		RefreshToken: tokenResp.RefreshToken,
		TokenType:    tokenResp.TokenType,
		Expiry:       time.Now().Add(time.Duration(tokenResp.ExpiresIn) * time.Second),
	}, nil
}

func hostedRefreshToken(refreshToken string) (*oauth2.Token, error) {
	payload, _ := json.Marshal(map[string]string{"refresh_token": refreshToken})
	resp, err := tokenHTTPClient.Post(config.ProxyBaseURL+"/tokenRefresh", "application/json", bytes.NewReader(payload))
	if err != nil {
		return nil, err
	}
	defer func() { _ = resp.Body.Close() }()

	body, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("hosted refresh %d: %s", resp.StatusCode, string(body))
	}

	var tokenResp struct {
		AccessToken  string `json:"access_token"`
		RefreshToken string `json:"refresh_token"`
		TokenType    string `json:"token_type"`
		ExpiresIn    int    `json:"expires_in"`
	}
	if err := json.Unmarshal(body, &tokenResp); err != nil {
		return nil, err
	}
	return &oauth2.Token{
		AccessToken:  tokenResp.AccessToken,
		RefreshToken: tokenResp.RefreshToken,
		TokenType:    tokenResp.TokenType,
		Expiry:       time.Now().Add(time.Duration(tokenResp.ExpiresIn) * time.Second),
	}, nil
}

func generateSessionID() string {
	b := make([]byte, 16)
	_, _ = rand.Read(b)
	return hex.EncodeToString(b)
}

func AuthStatus() (clientOK, userOK bool) {
	if td, err := secrets.LoadToken(tokenKeyClient); err == nil && td.Expiry.After(time.Now()) {
		clientOK = true
	}
	if td, err := secrets.LoadToken(tokenKeyUser); err == nil && (td.Expiry.After(time.Now()) || td.RefreshToken != "") {
		userOK = true
	}
	return
}
