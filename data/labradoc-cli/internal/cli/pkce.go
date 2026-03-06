package cli

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"fmt"
	"net/url"
	"strings"
)

func GeneratePKCE() (verifier string, challenge string, err error) {
	buf := make([]byte, 64)
	if _, err = rand.Read(buf); err != nil {
		return "", "", err
	}
	verifier = base64.RawURLEncoding.EncodeToString(buf)
	sum := sha256.Sum256([]byte(verifier))
	challenge = base64.RawURLEncoding.EncodeToString(sum[:])
	return verifier, challenge, nil
}

func AuthURL(baseURL, realm, clientID, redirectURI, scope, state, codeChallenge string) (string, error) {
	if baseURL == "" || realm == "" || clientID == "" || redirectURI == "" {
		return "", fmt.Errorf("missing required auth url parameters")
	}
	base := strings.TrimRight(baseURL, "/")
	u, err := url.Parse(base + "/realms/" + realm + "/protocol/openid-connect/auth")
	if err != nil {
		return "", err
	}
	q := u.Query()
	q.Set("client_id", clientID)
	q.Set("response_type", "code")
	q.Set("redirect_uri", redirectURI)
	if scope != "" {
		q.Set("scope", scope)
	}
	if state != "" {
		q.Set("state", state)
	}
	if codeChallenge != "" {
		q.Set("code_challenge_method", "S256")
		q.Set("code_challenge", codeChallenge)
	}
	u.RawQuery = q.Encode()
	return u.String(), nil
}

func TokenEndpoint(baseURL, realm string) (string, error) {
	if baseURL == "" || realm == "" {
		return "", fmt.Errorf("missing required token endpoint parameters")
	}
	base := strings.TrimRight(baseURL, "/")
	u, err := url.Parse(base + "/realms/" + realm + "/protocol/openid-connect/token")
	if err != nil {
		return "", err
	}
	return u.String(), nil
}
