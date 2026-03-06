package cmd

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/alexrudloff/caesar-cli/internal/client"
	"github.com/alexrudloff/caesar-cli/internal/output"
)

// setupTestServer creates an httptest.Server and injects a test client into newClient.
// Returns the server (for handler access) and a restore function.
func setupTestServer(t *testing.T, handler http.Handler) *httptest.Server {
	t.Helper()
	srv := httptest.NewServer(handler)
	t.Cleanup(srv.Close)

	origNewClient := newClient
	newClient = func() (*client.Client, error) {
		return client.NewWithOptions(client.Options{
			BaseURL: srv.URL,
			APIKey:  "test-key",
		}), nil
	}
	t.Cleanup(func() { newClient = origNewClient })

	return srv
}

// captureOutput replaces output.Stdout and output.Stderr with buffers.
// Returns the buffers. Restores originals on test cleanup.
func captureOutput(t *testing.T) (stdout, stderr *bytes.Buffer) {
	t.Helper()
	var outBuf, errBuf bytes.Buffer
	origOut, origErr, origExit := output.Stdout, output.Stderr, output.ExitFunc
	output.Stdout = &outBuf
	output.Stderr = &errBuf
	output.ExitFunc = func(int) {} // prevent os.Exit in tests
	t.Cleanup(func() {
		output.Stdout = origOut
		output.Stderr = origErr
		output.ExitFunc = origExit
	})
	return &outBuf, &errBuf
}

// jsonHandler returns an http.HandlerFunc that responds with the given value as JSON.
func jsonHandler(t *testing.T, v any) http.HandlerFunc {
	t.Helper()
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(v)
	}
}
