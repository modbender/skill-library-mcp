package telegram

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func overrideBaseURL(t *testing.T, url string) {
	t.Helper()
	orig := BaseURL
	BaseURL = url
	t.Cleanup(func() { BaseURL = orig })
}

func overrideHTTPClient(t *testing.T, client *http.Client) {
	t.Helper()
	orig := HTTPClient
	HTTPClient = client
	t.Cleanup(func() { HTTPClient = orig })
}

func TestSendMessage_Success(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			t.Errorf("expected POST, got %s", r.Method)
		}
		if err := r.ParseForm(); err != nil {
			t.Fatalf("parse form: %v", err)
		}
		if r.FormValue("chat_id") != "123" {
			t.Errorf("chat_id = %q", r.FormValue("chat_id"))
		}
		if r.FormValue("text") != "hello" {
			t.Errorf("text = %q", r.FormValue("text"))
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{"ok": true})
	}))
	defer srv.Close()
	overrideBaseURL(t, srv.URL)
	overrideHTTPClient(t, srv.Client())

	if err := SendMessage("mytoken", "123", "hello"); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestSendMessage_APIError(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{"ok": false, "description": "Unauthorized"})
	}))
	defer srv.Close()
	overrideBaseURL(t, srv.URL)
	overrideHTTPClient(t, srv.Client())

	err := SendMessage("badtoken", "123", "hi")
	if err == nil {
		t.Fatal("expected error")
	}
	if !strings.Contains(err.Error(), "Unauthorized") {
		t.Errorf("error = %q, want 'Unauthorized'", err.Error())
	}
}

func TestSendMessage_NonOKHTTPStatus(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "internal error", http.StatusInternalServerError)
	}))
	defer srv.Close()
	overrideBaseURL(t, srv.URL)
	overrideHTTPClient(t, srv.Client())

	err := SendMessage("token", "123", "hi")
	if err == nil {
		t.Fatal("expected error")
	}
	if !strings.Contains(err.Error(), "500") {
		t.Errorf("error = %q, want 500", err.Error())
	}
}

func TestSendMessage_EmptyBotToken(t *testing.T) {
	if err := SendMessage("", "123", "hi"); err == nil {
		t.Fatal("expected error for empty bot token")
	}
}

func TestSendMessage_EmptyChatID(t *testing.T) {
	if err := SendMessage("token", "", "hi"); err == nil {
		t.Fatal("expected error for empty chat ID")
	}
}

func TestSendMessage_NetworkError(t *testing.T) {
	// Point to a server that is already closed
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {}))
	srv.Close()
	overrideBaseURL(t, srv.URL)

	err := SendMessage("token", "123", "hi")
	if err == nil {
		t.Fatal("expected error for network failure")
	}
}
