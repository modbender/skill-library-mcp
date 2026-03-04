package config

import (
	"testing"
)

func TestGetAPIKey_Set(t *testing.T) {
	t.Setenv("CAESAR_API_KEY", "my-secret-key")
	key, err := GetAPIKey()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if key != "my-secret-key" {
		t.Errorf("key = %q, want %q", key, "my-secret-key")
	}
}

func TestGetAPIKey_Empty(t *testing.T) {
	t.Setenv("CAESAR_API_KEY", "")
	_, err := GetAPIKey()
	if err == nil {
		t.Fatal("expected error when CAESAR_API_KEY is empty")
	}
}

func TestGetAPIKey_Unset(t *testing.T) {
	t.Setenv("CAESAR_API_KEY", "")
	_, err := GetAPIKey()
	if err == nil {
		t.Fatal("expected error when CAESAR_API_KEY is not set")
	}
	want := "environment variable CAESAR_API_KEY is not set"
	if err.Error() != want {
		t.Errorf("error = %q, want %q", err.Error(), want)
	}
}
