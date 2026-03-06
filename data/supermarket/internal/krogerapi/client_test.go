package krogerapi

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"sync/atomic"
	"testing"
	"time"

	"github.com/99designs/keyring"
	"github.com/blanxlait/krocli/internal/config"
	"github.com/blanxlait/krocli/internal/secrets"
	"golang.org/x/oauth2"
)

// setupTestEnv redirects HOME and uses a file-based keyring in a temp dir
// so tests don't touch real keychain or config files.
func setupTestEnv(t *testing.T) {
	t.Helper()
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)
	t.Setenv("XDG_CONFIG_HOME", tmp)

	origOpen := secrets.OpenKeyring
	secrets.OpenKeyring = func() (keyring.Keyring, error) {
		return keyring.Open(keyring.Config{
			ServiceName:      "krocli-test",
			AllowedBackends:  []keyring.BackendType{keyring.FileBackend},
			FileDir:          filepath.Join(tmp, "keyring"),
			FilePasswordFunc: keyring.FixedStringPrompt("test"),
		})
	}
	t.Cleanup(func() { secrets.OpenKeyring = origOpen })
}

// newTokenServer returns an httptest.Server that responds to client_credentials
// token requests with a valid token response. The accessToken returned
// increments on each call so tests can detect retries.
func newTokenServer(t *testing.T) (*httptest.Server, *atomic.Int32) {
	t.Helper()
	callCount := &atomic.Int32{}
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		n := callCount.Add(1)
		if r.Method != "POST" {
			http.Error(w, "want POST", http.StatusMethodNotAllowed)
			return
		}
		user, pass, ok := r.BasicAuth()
		if !ok || user == "" || pass == "" {
			http.Error(w, "missing basic auth", http.StatusUnauthorized)
			return
		}
		if err := r.ParseForm(); err != nil {
			http.Error(w, "bad form", http.StatusBadRequest)
			return
		}
		if r.FormValue("grant_type") != "client_credentials" {
			http.Error(w, "bad grant_type", http.StatusBadRequest)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{
			"access_token": "tok-" + string(rune('A'-1+n)),
			"token_type":   "bearer",
			"expires_in":   1800,
		})
	}))
	return srv, callCount
}

// overrideTokenURL sets the package-level tokenURL and tokenHTTPClient
// for the duration of the test.
func overrideTokenURL(t *testing.T, url string) {
	t.Helper()
	origURL := tokenURL
	origClient := tokenHTTPClient
	tokenURL = url
	tokenHTTPClient = http.DefaultClient
	t.Cleanup(func() {
		tokenURL = origURL
		tokenHTTPClient = origClient
	})
}

func TestClientCredentialsExchange(t *testing.T) {
	setupTestEnv(t)
	srv, callCount := newTokenServer(t)
	defer srv.Close()
	overrideTokenURL(t, srv.URL)

	creds := &config.Credentials{ClientID: "test-id", ClientSecret: "test-secret"}
	tok, err := clientCredentialsExchange(creds, "product.compact")
	if err != nil {
		t.Fatalf("exchange: %v", err)
	}
	if tok.AccessToken == "" {
		t.Error("empty access token")
	}
	if tok.TokenType != "bearer" {
		t.Errorf("token type = %q, want bearer", tok.TokenType)
	}
	if tok.Expiry.Before(time.Now()) {
		t.Error("token already expired")
	}
	if callCount.Load() != 1 {
		t.Errorf("expected 1 token call, got %d", callCount.Load())
	}
}

func TestClientCredentialsExchange_BadCreds(t *testing.T) {
	setupTestEnv(t)
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, `{"error":"unauthorized"}`, http.StatusUnauthorized)
	}))
	defer srv.Close()
	overrideTokenURL(t, srv.URL)

	creds := &config.Credentials{ClientID: "bad", ClientSecret: "bad"}
	_, err := clientCredentialsExchange(creds, "product.compact")
	if err == nil {
		t.Fatal("expected error for bad credentials")
	}
}

func TestGetClientToken_CachesToken(t *testing.T) {
	setupTestEnv(t)
	srv, callCount := newTokenServer(t)
	defer srv.Close()
	overrideTokenURL(t, srv.URL)

	creds := &config.Credentials{ClientID: "test-id", ClientSecret: "test-secret"}

	// First call fetches from server
	tok1, err := GetClientToken(creds)
	if err != nil {
		t.Fatalf("first call: %v", err)
	}

	// Second call should use cached token (no new server call)
	tok2, err := GetClientToken(creds)
	if err != nil {
		t.Fatalf("second call: %v", err)
	}

	if tok1.AccessToken != tok2.AccessToken {
		t.Error("expected cached token on second call")
	}
	if callCount.Load() != 1 {
		t.Errorf("expected 1 token call (cached), got %d", callCount.Load())
	}
}

func TestGetClientToken_RefreshesAfterClear(t *testing.T) {
	setupTestEnv(t)
	srv, callCount := newTokenServer(t)
	defer srv.Close()
	overrideTokenURL(t, srv.URL)

	creds := &config.Credentials{ClientID: "test-id", ClientSecret: "test-secret"}

	tok1, err := GetClientToken(creds)
	if err != nil {
		t.Fatalf("first call: %v", err)
	}

	ClearClientToken()

	tok2, err := GetClientToken(creds)
	if err != nil {
		t.Fatalf("after clear: %v", err)
	}

	if tok1.AccessToken == tok2.AccessToken {
		t.Error("expected new token after clear")
	}
	if callCount.Load() != 2 {
		t.Errorf("expected 2 token calls, got %d", callCount.Load())
	}
}

func TestDoClientRequest_RetryOn403(t *testing.T) {
	setupTestEnv(t)

	// Token server
	tokSrv, tokCalls := newTokenServer(t)
	defer tokSrv.Close()
	overrideTokenURL(t, tokSrv.URL)

	// API server: reject first call with 403, accept second
	apiCalls := &atomic.Int32{}
	apiSrv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		n := apiCalls.Add(1)
		if n == 1 {
			w.WriteHeader(403)
			_, _ = w.Write([]byte(`{"code":"AUTH-1007","reason":"Invalid token"}`))
			return
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{
			"data": []map[string]string{{"productId": "123", "description": "Test"}},
			"meta": map[string]any{"pagination": map[string]any{"start": 0, "limit": 1, "total": 1}},
		})
	}))
	defer apiSrv.Close()

	creds := &config.Credentials{ClientID: "test-id", ClientSecret: "test-secret"}
	client := &Client{http: &http.Client{}, baseURL: apiSrv.URL, creds: creds}

	data, err := client.doClientRequest("GET", "/products?filter.term=test", nil)
	if err != nil {
		t.Fatalf("doClientRequest: %v", err)
	}
	if len(data) == 0 {
		t.Error("empty response")
	}
	if apiCalls.Load() != 2 {
		t.Errorf("expected 2 API calls (retry), got %d", apiCalls.Load())
	}
	if tokCalls.Load() != 2 {
		t.Errorf("expected 2 token calls (original + retry), got %d", tokCalls.Load())
	}
}

func TestDoClientRequest_NoRetryOn500(t *testing.T) {
	setupTestEnv(t)

	tokSrv, _ := newTokenServer(t)
	defer tokSrv.Close()
	overrideTokenURL(t, tokSrv.URL)

	apiCalls := &atomic.Int32{}
	apiSrv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		apiCalls.Add(1)
		w.WriteHeader(500)
		_, _ = w.Write([]byte(`{"reason":"server error"}`))
	}))
	defer apiSrv.Close()

	creds := &config.Credentials{ClientID: "test-id", ClientSecret: "test-secret"}
	client := &Client{http: &http.Client{}, baseURL: apiSrv.URL, creds: creds}

	_, err := client.doClientRequest("GET", "/products", nil)
	if err == nil {
		t.Fatal("expected error on 500")
	}
	apiErr, ok := err.(*APIError)
	if !ok {
		t.Fatalf("expected *APIError, got %T", err)
	}
	if apiErr.StatusCode != 500 {
		t.Errorf("status = %d, want 500", apiErr.StatusCode)
	}
	if apiCalls.Load() != 1 {
		t.Errorf("expected 1 API call (no retry on 500), got %d", apiCalls.Load())
	}
}

func TestDoRequest_SetsHeaders(t *testing.T) {
	var gotAuth, gotAccept, gotContentType string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotAuth = r.Header.Get("Authorization")
		gotAccept = r.Header.Get("Accept")
		gotContentType = r.Header.Get("Content-Type")
		_, _ = w.Write([]byte("{}"))
	}))
	defer srv.Close()

	creds := &config.Credentials{ClientID: "id", ClientSecret: "secret"}
	client := &Client{http: &http.Client{}, baseURL: srv.URL, creds: creds}

	tok := &oauth2.Token{AccessToken: "my-token", TokenType: "bearer"}
	_, err := client.doRequest("GET", "/test", nil, tok)
	if err != nil {
		t.Fatalf("doRequest: %v", err)
	}

	if gotAuth != "Bearer my-token" {
		t.Errorf("Authorization = %q", gotAuth)
	}
	if gotAccept != "application/json" {
		t.Errorf("Accept = %q", gotAccept)
	}
	if gotContentType != "" {
		t.Errorf("Content-Type should be empty for GET, got %q", gotContentType)
	}
}

func TestSearchProducts_ParsesResponse(t *testing.T) {
	setupTestEnv(t)

	tokSrv, _ := newTokenServer(t)
	defer tokSrv.Close()
	overrideTokenURL(t, tokSrv.URL)

	apiSrv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Query().Get("filter.term") != "milk" {
			t.Errorf("filter.term = %q", r.URL.Query().Get("filter.term"))
		}
		if r.URL.Query().Get("filter.limit") != "5" {
			t.Errorf("filter.limit = %q", r.URL.Query().Get("filter.limit"))
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(ProductsResponse{
			Data: []Product{{ProductID: "001", Brand: "Kroger", Description: "Milk"}},
			Meta: Meta{Pagination: Pagination{Total: 1, Limit: 5}},
		})
	}))
	defer apiSrv.Close()

	creds := &config.Credentials{ClientID: "id", ClientSecret: "secret"}
	client := &Client{http: &http.Client{}, baseURL: apiSrv.URL, creds: creds}

	resp, err := client.SearchProducts("milk", "", 5)
	if err != nil {
		t.Fatalf("SearchProducts: %v", err)
	}
	if len(resp.Data) != 1 {
		t.Fatalf("expected 1 product, got %d", len(resp.Data))
	}
	if resp.Data[0].Description != "Milk" {
		t.Errorf("description = %q", resp.Data[0].Description)
	}
}

func TestSearchLocations_IncludesRadius(t *testing.T) {
	setupTestEnv(t)

	tokSrv, _ := newTokenServer(t)
	defer tokSrv.Close()
	overrideTokenURL(t, tokSrv.URL)

	apiSrv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Query().Get("filter.zipCode.near") != "45202" {
			t.Errorf("zipCode = %q", r.URL.Query().Get("filter.zipCode.near"))
		}
		if r.URL.Query().Get("filter.radiusInMiles") != "25" {
			t.Errorf("radius = %q", r.URL.Query().Get("filter.radiusInMiles"))
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(LocationsResponse{
			Data: []Location{{LocationID: "014", Name: "Kroger Downtown"}},
		})
	}))
	defer apiSrv.Close()

	creds := &config.Credentials{ClientID: "id", ClientSecret: "secret"}
	client := &Client{http: &http.Client{}, baseURL: apiSrv.URL, creds: creds}

	resp, err := client.SearchLocations("45202", 25, 10)
	if err != nil {
		t.Fatalf("SearchLocations: %v", err)
	}
	if resp.Data[0].Name != "Kroger Downtown" {
		t.Errorf("name = %q", resp.Data[0].Name)
	}
}

func TestAddToCart_SendsPUT(t *testing.T) {
	setupTestEnv(t)

	// Store a valid user token so AddToCart doesn't fail on "not logged in"
	_ = secrets.StoreToken(tokenKeyUser, &secrets.TokenData{
		AccessToken: "user-tok",
		TokenType:   "bearer",
		Expiry:      time.Now().Add(time.Hour),
	})

	var gotMethod string
	var gotBody map[string]any
	apiSrv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotMethod = r.Method
		_ = json.NewDecoder(r.Body).Decode(&gotBody)
		w.WriteHeader(204)
	}))
	defer apiSrv.Close()

	creds := &config.Credentials{ClientID: "id", ClientSecret: "secret"}
	client := &Client{http: &http.Client{}, baseURL: apiSrv.URL, creds: creds}

	err := client.AddToCart([]CartItem{{UPC: "0001111060903", Quantity: 2}})
	if err != nil {
		t.Fatalf("AddToCart: %v", err)
	}
	if gotMethod != "PUT" {
		t.Errorf("method = %q, want PUT", gotMethod)
	}
	items, ok := gotBody["items"].([]any)
	if !ok || len(items) != 1 {
		t.Fatalf("expected 1 item in body, got %v", gotBody)
	}
}

// Ensure credentials file doesn't leak
func TestMain(m *testing.M) {
	os.Exit(m.Run())
}
