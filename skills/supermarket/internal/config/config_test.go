package config

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"testing"
)

func TestSaveAndLoadCredentials(t *testing.T) {
	// Use a temp dir as config home
	tmp := t.TempDir()
	origHome := os.Getenv("HOME")
	t.Setenv("HOME", tmp)
	defer func() { _ = os.Setenv("HOME", origHome) }()

	creds := &Credentials{
		ClientID:     "test-id",
		ClientSecret: "test-secret",
	}

	if err := SaveCredentials(creds); err != nil {
		t.Fatalf("SaveCredentials: %v", err)
	}

	loaded, err := LoadCredentials()
	if err != nil {
		t.Fatalf("LoadCredentials: %v", err)
	}

	if loaded.ClientID != creds.ClientID {
		t.Errorf("ClientID = %q, want %q", loaded.ClientID, creds.ClientID)
	}
	if loaded.ClientSecret != creds.ClientSecret {
		t.Errorf("ClientSecret = %q, want %q", loaded.ClientSecret, creds.ClientSecret)
	}
}

func TestLoadCredentials_NotFound(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	_, err := LoadCredentials()
	if err == nil {
		t.Fatal("expected error for missing credentials")
	}
}

func TestLoadCredentials_InvalidJSON(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	dir := filepath.Join(tmp, ".config", "krocli")
	_ = os.MkdirAll(dir, 0o700)
	_ = os.WriteFile(filepath.Join(dir, "credentials.json"), []byte("{not json"), 0o600)

	_, err := LoadCredentials()
	if err == nil {
		t.Fatal("expected error for invalid JSON")
	}
}

func TestLoadCredentials_MissingFields(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	dir := filepath.Join(tmp, ".config", "krocli")
	_ = os.MkdirAll(dir, 0o700)
	data, _ := json.Marshal(Credentials{ClientID: "id-only"})
	_ = os.WriteFile(filepath.Join(dir, "credentials.json"), data, 0o600)

	_, err := LoadCredentials()
	if err == nil {
		t.Fatal("expected error for missing client_secret")
	}
}

func TestDir_CreatesDirectory(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	dir, err := Dir()
	if err != nil {
		t.Fatalf("Dir: %v", err)
	}

	info, err := os.Stat(dir)
	if err != nil {
		t.Fatalf("dir not created: %v", err)
	}
	if !info.IsDir() {
		t.Error("expected directory")
	}
}

func TestSaveAndLoadTelegramConfig(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	cfg := &TelegramConfig{BotToken: "bot123:token", ChatID: "456789"}
	if err := SaveTelegramConfig(cfg); err != nil {
		t.Fatalf("SaveTelegramConfig: %v", err)
	}

	loaded, err := LoadTelegramConfig()
	if err != nil {
		t.Fatalf("LoadTelegramConfig: %v", err)
	}
	if loaded.BotToken != cfg.BotToken {
		t.Errorf("BotToken = %q, want %q", loaded.BotToken, cfg.BotToken)
	}
	if loaded.ChatID != cfg.ChatID {
		t.Errorf("ChatID = %q, want %q", loaded.ChatID, cfg.ChatID)
	}
}

func TestLoadTelegramConfig_NotFound(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	_, err := LoadTelegramConfig()
	if err == nil {
		t.Fatal("expected error for missing telegram config")
	}
	if !errors.Is(err, ErrNoTelegramConfig) {
		t.Errorf("expected ErrNoTelegramConfig, got %v", err)
	}
}

func TestLoadTelegramConfig_MissingFields(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	dir := filepath.Join(tmp, ".config", "krocli")
	_ = os.MkdirAll(dir, 0o700)
	data, _ := json.Marshal(TelegramConfig{BotToken: "token-only"})
	_ = os.WriteFile(filepath.Join(dir, "telegram.json"), data, 0o600)

	_, err := LoadTelegramConfig()
	if err == nil {
		t.Fatal("expected error for missing chat_id")
	}
}

func TestLoadTelegramConfig_InvalidJSON(t *testing.T) {
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)

	dir := filepath.Join(tmp, ".config", "krocli")
	_ = os.MkdirAll(dir, 0o700)
	_ = os.WriteFile(filepath.Join(dir, "telegram.json"), []byte("{not json"), 0o600)

	_, err := LoadTelegramConfig()
	if err == nil {
		t.Fatal("expected error for invalid JSON")
	}
}

func TestOpenClawIntegration_BothSet(t *testing.T) {
	t.Setenv("OPENCLAW_BOT_TOKEN", "openclaw-bot:token")
	t.Setenv("OPENCLAW_CHAT_ID", "99999")

	cfg := OpenClawIntegration()
	if cfg == nil {
		t.Fatal("expected non-nil config when both env vars are set")
	}
	if cfg.BotToken != "openclaw-bot:token" {
		t.Errorf("BotToken = %q, want %q", cfg.BotToken, "openclaw-bot:token")
	}
	if cfg.ChatID != "99999" {
		t.Errorf("ChatID = %q, want %q", cfg.ChatID, "99999")
	}
}

func TestOpenClawIntegration_OnlyTokenSet(t *testing.T) {
	t.Setenv("OPENCLAW_BOT_TOKEN", "openclaw-bot:token")
	t.Setenv("OPENCLAW_CHAT_ID", "")

	cfg := OpenClawIntegration()
	if cfg != nil {
		t.Error("expected nil config when only OPENCLAW_BOT_TOKEN is set")
	}
}

func TestOpenClawIntegration_OnlyChatIDSet(t *testing.T) {
	t.Setenv("OPENCLAW_BOT_TOKEN", "")
	t.Setenv("OPENCLAW_CHAT_ID", "99999")

	cfg := OpenClawIntegration()
	if cfg != nil {
		t.Error("expected nil config when only OPENCLAW_CHAT_ID is set")
	}
}

func TestOpenClawIntegration_NoneSet(t *testing.T) {
	t.Setenv("OPENCLAW_BOT_TOKEN", "")
	t.Setenv("OPENCLAW_CHAT_ID", "")

	cfg := OpenClawIntegration()
	if cfg != nil {
		t.Error("expected nil config when no env vars are set")
	}
}
