package cli

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"time"
)

const (
	tokenFileName = "token.json"
	pkceFileName  = "pkce.json"
)

type Token struct {
	AccessToken      string    `json:"access_token"`
	RefreshToken     string    `json:"refresh_token,omitempty"`
	TokenType        string    `json:"token_type,omitempty"`
	ExpiresIn        int64     `json:"expires_in,omitempty"`
	RefreshExpiresIn int64     `json:"refresh_expires_in,omitempty"`
	IDToken          string    `json:"id_token,omitempty"`
	Scope            string    `json:"scope,omitempty"`
	Expiry           time.Time `json:"expiry,omitempty"`
	ObtainedAt       time.Time `json:"obtained_at,omitempty"`
	AuthURL          string    `json:"auth_url,omitempty"`
	Realm            string    `json:"realm,omitempty"`
	ClientID         string    `json:"client_id,omitempty"`
	APIURL           string    `json:"api_url,omitempty"`
}

type PKCEState struct {
	CodeVerifier  string    `json:"code_verifier"`
	CodeChallenge string    `json:"code_challenge"`
	State         string    `json:"state"`
	RedirectURI   string    `json:"redirect_uri"`
	Scope         string    `json:"scope"`
	CreatedAt     time.Time `json:"created_at"`
}

func configDir() (string, error) {
	base, err := os.UserConfigDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(base, "labradoc", "cli"), nil
}

func tokenPath() (string, error) {
	dir, err := configDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(dir, tokenFileName), nil
}

func pkcePath() (string, error) {
	dir, err := configDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(dir, pkceFileName), nil
}

func ensureDir(path string) error {
	dir := filepath.Dir(path)
	return os.MkdirAll(dir, 0o700)
}

func LoadToken() (*Token, error) {
	path, err := tokenPath()
	if err != nil {
		return nil, err
	}
	b, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var t Token
	if err := json.Unmarshal(b, &t); err != nil {
		return nil, err
	}
	if t.AccessToken == "" {
		return nil, errors.New("token file missing access_token")
	}
	return &t, nil
}

func SaveToken(t Token) error {
	path, err := tokenPath()
	if err != nil {
		return err
	}
	if err := ensureDir(path); err != nil {
		return err
	}
	if t.ObtainedAt.IsZero() {
		t.ObtainedAt = time.Now().UTC()
	}
	if t.Expiry.IsZero() && t.ExpiresIn > 0 {
		t.Expiry = t.ObtainedAt.Add(time.Duration(t.ExpiresIn) * time.Second)
	}
	b, err := json.MarshalIndent(t, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, b, 0o600)
}

func ClearToken() error {
	path, err := tokenPath()
	if err != nil {
		return err
	}
	if err := os.Remove(path); err != nil && !os.IsNotExist(err) {
		return err
	}
	return nil
}

func LoadPKCEState() (*PKCEState, error) {
	path, err := pkcePath()
	if err != nil {
		return nil, err
	}
	b, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var s PKCEState
	if err := json.Unmarshal(b, &s); err != nil {
		return nil, err
	}
	if s.CodeVerifier == "" || s.RedirectURI == "" {
		return nil, errors.New("pkce state missing required fields")
	}
	return &s, nil
}

func SavePKCEState(s PKCEState) error {
	path, err := pkcePath()
	if err != nil {
		return err
	}
	if err := ensureDir(path); err != nil {
		return err
	}
	if s.CreatedAt.IsZero() {
		s.CreatedAt = time.Now().UTC()
	}
	b, err := json.MarshalIndent(s, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, b, 0o600)
}

func ClearPKCEState() error {
	path, err := pkcePath()
	if err != nil {
		return err
	}
	if err := os.Remove(path); err != nil && !os.IsNotExist(err) {
		return err
	}
	return nil
}
