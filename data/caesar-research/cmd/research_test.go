package cmd

import (
	"bytes"
	"encoding/json"
	"net/http"
	"strings"
	"sync/atomic"
	"testing"
	"time"

	"github.com/alexrudloff/caesar-cli/internal/client"
)

func TestPollResearch_CompletesImmediately(t *testing.T) {
	origInterval := pollInterval
	pollInterval = 0
	t.Cleanup(func() { pollInterval = origInterval })

	content := "done"
	setupTestServer(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch {
		case strings.HasSuffix(r.URL.Path, "/events"):
			json.NewEncoder(w).Encode([]client.ResearchEvent{})
		default:
			json.NewEncoder(w).Encode(client.ResearchObject{
				ID:      "r1",
				Status:  "completed",
				Content: &content,
			})
		}
	}))

	c := client.NewWithOptions(client.Options{BaseURL: "", APIKey: "test"})
	// We need the real test server URL, so use newClient
	c2, _ := newClient()

	var buf bytes.Buffer
	res, err := pollResearch(c2, &buf, "r1")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if res.Status != "completed" {
		t.Errorf("status = %q, want %q", res.Status, "completed")
	}
	_ = c // suppress unused
}

func TestPollResearch_PollingWithEvents(t *testing.T) {
	origInterval := pollInterval
	pollInterval = 0
	t.Cleanup(func() { pollInterval = origInterval })

	var callCount atomic.Int32
	setupTestServer(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		n := callCount.Add(1)
		switch {
		case strings.HasSuffix(r.URL.Path, "/events"):
			if n <= 2 {
				json.NewEncoder(w).Encode([]client.ResearchEvent{
					{Message: "Searching...", CreatedAt: time.Date(2025, 1, 1, 12, 0, 0, 0, time.UTC)},
				})
			} else {
				json.NewEncoder(w).Encode([]client.ResearchEvent{
					{Message: "Searching...", CreatedAt: time.Date(2025, 1, 1, 12, 0, 0, 0, time.UTC)},
					{Message: "Analyzing...", CreatedAt: time.Date(2025, 1, 1, 12, 0, 1, 0, time.UTC)},
				})
			}
		default:
			if n <= 2 {
				json.NewEncoder(w).Encode(client.ResearchObject{ID: "r1", Status: "searching"})
			} else {
				content := "result"
				json.NewEncoder(w).Encode(client.ResearchObject{ID: "r1", Status: "completed", Content: &content})
			}
		}
	}))

	c, _ := newClient()
	var buf bytes.Buffer
	res, err := pollResearch(c, &buf, "r1")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if res.Status != "completed" {
		t.Errorf("status = %q, want %q", res.Status, "completed")
	}

	out := buf.String()
	if !strings.Contains(out, "Searching...") {
		t.Errorf("output should contain 'Searching...', got %q", out)
	}
	if !strings.Contains(out, "Analyzing...") {
		t.Errorf("output should contain 'Analyzing...', got %q", out)
	}
	// "Searching..." should appear only once (not duplicated on re-poll)
	if strings.Count(out, "Searching...") != 1 {
		t.Errorf("'Searching...' should appear once, appeared %d times", strings.Count(out, "Searching..."))
	}
}

func TestPollResearch_FailedJob(t *testing.T) {
	origInterval := pollInterval
	pollInterval = 0
	t.Cleanup(func() { pollInterval = origInterval })

	setupTestServer(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch {
		case strings.HasSuffix(r.URL.Path, "/events"):
			json.NewEncoder(w).Encode([]client.ResearchEvent{})
		default:
			json.NewEncoder(w).Encode(client.ResearchObject{ID: "r1", Status: "failed"})
		}
	}))

	c, _ := newClient()
	var buf bytes.Buffer
	_, err := pollResearch(c, &buf, "r1")
	if err == nil {
		t.Fatal("expected error for failed job")
	}
	if !strings.Contains(err.Error(), "failed") {
		t.Errorf("error = %q, should contain 'failed'", err.Error())
	}
}

func TestResearchCreateCmd_NoWait(t *testing.T) {
	stdout, _ := captureOutput(t)

	var gotReq client.CreateResearchRequest
	setupTestServer(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		json.NewDecoder(r.Body).Decode(&gotReq)
		json.NewEncoder(w).Encode(client.CreateResearchResponse{ID: "res-99", Status: "queued"})
	}))

	rootCmd.SetArgs([]string{"research", "create", "my research question", "--no-wait"})
	rootCmd.Execute()

	if gotReq.Query != "my research question" {
		t.Errorf("sent query = %q, want %q", gotReq.Query, "my research question")
	}

	out := stdout.String()
	if !strings.Contains(out, "res-99") {
		t.Errorf("output should contain job ID, got %q", out)
	}
}

func TestResearchCreateCmd_DefaultWaits(t *testing.T) {
	origInterval := pollInterval
	pollInterval = 0
	t.Cleanup(func() { pollInterval = origInterval })

	// Reset sticky flag from prior tests.
	researchCreateCmd.Flags().Set("no-wait", "false")

	stdout, _ := captureOutput(t)

	var callCount atomic.Int32
	setupTestServer(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		n := callCount.Add(1)
		if r.Method == "POST" {
			json.NewEncoder(w).Encode(client.CreateResearchResponse{ID: "res-99", Status: "queued"})
			return
		}
		switch {
		case strings.HasSuffix(r.URL.Path, "/events"):
			json.NewEncoder(w).Encode([]client.ResearchEvent{})
		default:
			if n <= 3 {
				json.NewEncoder(w).Encode(client.ResearchObject{ID: "res-99", Status: "searching"})
			} else {
				content := "final answer"
				json.NewEncoder(w).Encode(client.ResearchObject{ID: "res-99", Status: "completed", Content: &content})
			}
		}
	}))

	rootCmd.SetArgs([]string{"research", "create", "my question"})
	rootCmd.Execute()

	out := stdout.String()
	if !strings.Contains(out, "completed") {
		t.Errorf("default should wait for completion, got %q", out)
	}
}

func TestResearchCreateCmd_WithFlags(t *testing.T) {
	captureOutput(t)

	var gotReq client.CreateResearchRequest
	setupTestServer(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		json.NewDecoder(r.Body).Decode(&gotReq)
		json.NewEncoder(w).Encode(client.CreateResearchResponse{ID: "res-100", Status: "queued"})
	}))

	rootCmd.SetArgs([]string{"research", "create", "query", "--model", "gpt-5.2", "--loops", "5", "--reasoning", "--no-wait"})
	rootCmd.Execute()

	if gotReq.Model != "gpt-5.2" {
		t.Errorf("model = %q, want %q", gotReq.Model, "gpt-5.2")
	}
	if gotReq.ReasoningLoops != 5 {
		t.Errorf("loops = %d, want 5", gotReq.ReasoningLoops)
	}
	if !gotReq.ReasoningMode {
		t.Error("reasoning mode should be true")
	}
}

func TestResearchGetCmd(t *testing.T) {
	stdout, _ := captureOutput(t)

	content := "answer"
	setupTestServer(t, jsonHandler(t, client.ResearchObject{
		ID:      "r1",
		Status:  "completed",
		Content: &content,
	}))

	rootCmd.SetArgs([]string{"research", "get", "r1"})
	rootCmd.Execute()

	out := stdout.String()
	if !strings.Contains(out, "r1") {
		t.Errorf("output should contain research ID, got %q", out)
	}
	if !strings.Contains(out, "completed") {
		t.Errorf("output should contain status, got %q", out)
	}
}

func TestResearchEventsCmd(t *testing.T) {
	stdout, _ := captureOutput(t)

	setupTestServer(t, jsonHandler(t, []client.ResearchEvent{
		{Message: "Step 1", CreatedAt: time.Now()},
	}))

	rootCmd.SetArgs([]string{"research", "events", "r1"})
	rootCmd.Execute()

	out := stdout.String()
	if !strings.Contains(out, "Step 1") {
		t.Errorf("output should contain event message, got %q", out)
	}
}
