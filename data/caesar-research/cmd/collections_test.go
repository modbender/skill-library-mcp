package cmd

import (
	"encoding/json"
	"net/http"
	"strings"
	"testing"

	"github.com/alexrudloff/caesar-cli/internal/client"
)

func TestCollectionsCreateCmd(t *testing.T) {
	stdout, _ := captureOutput(t)

	var gotBody map[string]string
	setupTestServer(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		json.NewDecoder(r.Body).Decode(&gotBody)
		json.NewEncoder(w).Encode(client.Collection{ID: "col-1", Name: "My Docs"})
	}))

	rootCmd.SetArgs([]string{"collections", "create", "My Docs"})
	rootCmd.Execute()

	if gotBody["name"] != "My Docs" {
		t.Errorf("sent name = %q, want %q", gotBody["name"], "My Docs")
	}

	out := stdout.String()
	if !strings.Contains(out, "col-1") {
		t.Errorf("output should contain collection ID, got %q", out)
	}
}

func TestCollectionsCreateCmd_WithDescription(t *testing.T) {
	stdout, _ := captureOutput(t)

	var gotBody map[string]string
	setupTestServer(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		json.NewDecoder(r.Body).Decode(&gotBody)
		json.NewEncoder(w).Encode(client.Collection{ID: "col-2", Name: "Named", Description: "A desc"})
	}))

	rootCmd.SetArgs([]string{"collections", "create", "Named", "--description", "A desc"})
	rootCmd.Execute()

	if gotBody["description"] != "A desc" {
		t.Errorf("sent description = %q, want %q", gotBody["description"], "A desc")
	}

	out := stdout.String()
	if !strings.Contains(out, "col-2") {
		t.Errorf("output should contain collection ID, got %q", out)
	}
}
