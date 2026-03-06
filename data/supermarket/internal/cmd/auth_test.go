package cmd

import (
	"bufio"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/blanxlait/krocli/internal/telegram"
)

func TestAuthCredentialsSetCmd_Run(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	// Write a valid creds file
	credsFile := filepath.Join(tmp, "creds.json")
	data, _ := json.Marshal(map[string]string{
		"client_id":     "test-id",
		"client_secret": "test-secret",
	})
	if err := os.WriteFile(credsFile, data, 0o600); err != nil {
		t.Fatalf("write creds: %v", err)
	}

	cmd := &AuthCredentialsSetCmd{Path: credsFile}
	flags := &RootFlags{}
	if err := cmd.Run(flags); err != nil {
		t.Fatalf("Run: %v", err)
	}

	// Verify saved
	saved, err := os.ReadFile(filepath.Join(tmp, ".config", "krocli", "credentials.json"))
	if err != nil {
		t.Fatalf("read saved: %v", err)
	}
	var creds map[string]string
	if err := json.Unmarshal(saved, &creds); err != nil {
		t.Fatalf("unmarshal saved: %v", err)
	}
	if creds["client_id"] != "test-id" {
		t.Errorf("client_id = %q", creds["client_id"])
	}
}

func TestAuthCredentialsSetCmd_MissingFields(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	credsFile := filepath.Join(tmp, "creds.json")
	if err := os.WriteFile(credsFile, []byte(`{"client_id":"only-id"}`), 0o600); err != nil {
		t.Fatalf("write creds: %v", err)
	}

	cmd := &AuthCredentialsSetCmd{Path: credsFile}
	flags := &RootFlags{}
	if err := cmd.Run(flags); err == nil {
		t.Fatal("expected error for missing client_secret")
	}
}

func TestAuthCredentialsSetCmd_BadPath(t *testing.T) {
	cmd := &AuthCredentialsSetCmd{Path: "/nonexistent/creds.json"}
	flags := &RootFlags{}
	if err := cmd.Run(flags); err == nil {
		t.Fatal("expected error for missing file")
	}
}

func TestSendViaTelegram_WithSavedConfig(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	// Pre-write a valid telegram config
	dir := filepath.Join(tmp, ".config", "krocli")
	_ = os.MkdirAll(dir, 0o700)
	cfg := map[string]string{"bot_token": "validtoken", "chat_id": "111"}
	data, _ := json.Marshal(cfg)
	_ = os.WriteFile(filepath.Join(dir, "telegram.json"), data, 0o600)

	var receivedText string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = r.ParseForm()
		receivedText = r.FormValue("text")
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"ok":true}`))
	}))
	defer srv.Close()

	origClient := telegram.HTTPClient
	telegram.HTTPClient = srv.Client()
	t.Cleanup(func() { telegram.HTTPClient = origClient })

	origBase := telegram.BaseURL
	telegram.BaseURL = srv.URL
	t.Cleanup(func() { telegram.BaseURL = origBase })

	if err := sendViaTelegram("https://example.com/login"); err != nil {
		t.Fatalf("sendViaTelegram: %v", err)
	}
	if !strings.Contains(receivedText, "https://example.com/login") {
		t.Errorf("message = %q, want login URL", receivedText)
	}
}

func TestSendViaTelegram_PromptsWhenNoConfig(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	// Mock the Telegram API server
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"ok":true}`))
	}))
	defer srv.Close()

	origClient := telegram.HTTPClient
	telegram.HTTPClient = srv.Client()
	t.Cleanup(func() { telegram.HTTPClient = origClient })

	origBase := telegram.BaseURL
	telegram.BaseURL = srv.URL
	t.Cleanup(func() { telegram.BaseURL = origBase })

	// Provide bot token and chat ID via stdin
	input := "mybot:token\n12345\n"
	origStdinReader := stdinReader
	stdinReader = func() *bufio.Reader { return bufio.NewReader(strings.NewReader(input)) }
	t.Cleanup(func() { stdinReader = origStdinReader })

	if err := sendViaTelegram("https://example.com/login"); err != nil {
		t.Fatalf("sendViaTelegram: %v", err)
	}
}

func TestSendViaTelegram_PromptEmptyInput(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	// Provide empty input
	origStdinReader := stdinReader
	stdinReader = func() *bufio.Reader { return bufio.NewReader(strings.NewReader("\n\n")) }
	t.Cleanup(func() { stdinReader = origStdinReader })

	if err := sendViaTelegram("https://example.com/login"); err == nil {
		t.Fatal("expected error for empty prompt input")
	}
}

func TestSendViaTelegram_TelegramAPIError(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	// Pre-write a valid telegram config
	dir := filepath.Join(tmp, ".config", "krocli")
	_ = os.MkdirAll(dir, 0o700)
	cfg := map[string]string{"bot_token": "badtoken", "chat_id": "999"}
	data, _ := json.Marshal(cfg)
	_ = os.WriteFile(filepath.Join(dir, "telegram.json"), data, 0o600)

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"ok":false,"description":"Forbidden: bot was blocked by the user"}`))
	}))
	defer srv.Close()

	origClient := telegram.HTTPClient
	telegram.HTTPClient = srv.Client()
	t.Cleanup(func() { telegram.HTTPClient = origClient })

	origBase := telegram.BaseURL
	telegram.BaseURL = srv.URL
	t.Cleanup(func() { telegram.BaseURL = origBase })

	err := sendViaTelegram("https://example.com/login")
	if err == nil {
		t.Fatal("expected error from Telegram API")
	}
	if !strings.Contains(err.Error(), "blocked") {
		t.Errorf("error = %q, want blocked message", err.Error())
	}
}

func TestSendViaTelegram_OpenClawIntegration(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)
	t.Setenv("OPENCLAW_BOT_TOKEN", "openclaw-bot:token")
	t.Setenv("OPENCLAW_CHAT_ID", "55555")

	var receivedToken, receivedText string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Extract bot token from path: /bot<token>/sendMessage
		parts := strings.Split(r.URL.Path, "/")
		for _, p := range parts {
			if strings.HasPrefix(p, "bot") {
				receivedToken = strings.TrimPrefix(p, "bot")
			}
		}
		_ = r.ParseForm()
		receivedText = r.FormValue("text")
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"ok":true}`))
	}))
	defer srv.Close()

	origClient := telegram.HTTPClient
	telegram.HTTPClient = srv.Client()
	t.Cleanup(func() { telegram.HTTPClient = origClient })

	origBase := telegram.BaseURL
	telegram.BaseURL = srv.URL
	t.Cleanup(func() { telegram.BaseURL = origBase })

	if err := sendViaTelegram("https://example.com/login"); err != nil {
		t.Fatalf("sendViaTelegram: %v", err)
	}
	if receivedToken != "openclaw-bot:token" {
		t.Errorf("bot token = %q, want %q", receivedToken, "openclaw-bot:token")
	}
	if !strings.Contains(receivedText, "https://example.com/login") {
		t.Errorf("message = %q, want login URL", receivedText)
	}
}

func TestSendViaTelegram_OpenClawFallsBackToFile(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)
	// No OpenClaw env vars set
	t.Setenv("OPENCLAW_BOT_TOKEN", "")
	t.Setenv("OPENCLAW_CHAT_ID", "")

	// Pre-write a valid telegram config file
	dir := filepath.Join(tmp, ".config", "krocli")
	_ = os.MkdirAll(dir, 0o700)
	cfg := map[string]string{"bot_token": "file-token", "chat_id": "22222"}
	data, _ := json.Marshal(cfg)
	_ = os.WriteFile(filepath.Join(dir, "telegram.json"), data, 0o600)

	var receivedToken string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		parts := strings.Split(r.URL.Path, "/")
		for _, p := range parts {
			if strings.HasPrefix(p, "bot") {
				receivedToken = strings.TrimPrefix(p, "bot")
			}
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"ok":true}`))
	}))
	defer srv.Close()

	origClient := telegram.HTTPClient
	telegram.HTTPClient = srv.Client()
	t.Cleanup(func() { telegram.HTTPClient = origClient })

	origBase := telegram.BaseURL
	telegram.BaseURL = srv.URL
	t.Cleanup(func() { telegram.BaseURL = origBase })

	if err := sendViaTelegram("https://example.com/login"); err != nil {
		t.Fatalf("sendViaTelegram: %v", err)
	}
	if receivedToken != "file-token" {
		t.Errorf("bot token = %q, want %q", receivedToken, "file-token")
	}
}
