package cmd

import (
	"encoding/json"
	"net/http"
	"strings"
	"sync/atomic"
	"testing"

	"github.com/alexrudloff/caesar-cli/internal/client"
)

func TestChatSendCmd_NoWait(t *testing.T) {
	stdout, _ := captureOutput(t)

	setupTestServer(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		json.NewEncoder(w).Encode(client.ChatMessage{ID: "msg-1", Status: "processing"})
	}))

	rootCmd.SetArgs([]string{"chat", "send", "r1", "What about X?", "--wait=false"})
	rootCmd.Execute()

	out := stdout.String()
	if !strings.Contains(out, "msg-1") {
		t.Errorf("output should contain message ID, got %q", out)
	}
}

func TestChatSendCmd_PollUntilComplete(t *testing.T) {
	origInterval := chatPollInterval
	chatPollInterval = 0
	t.Cleanup(func() { chatPollInterval = origInterval })

	var callCount atomic.Int32
	setupTestServer(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		n := callCount.Add(1)
		if r.Method == "POST" {
			json.NewEncoder(w).Encode(client.ChatMessage{ID: "msg-1", Status: "processing"})
			return
		}
		// GET polls
		if n <= 3 {
			json.NewEncoder(w).Encode(client.ChatMessage{ID: "msg-1", Status: "processing"})
		} else {
			json.NewEncoder(w).Encode(client.ChatMessage{
				ID:      "msg-1",
				Status:  "completed",
				Content: "The answer is 42.",
				Results: []client.ResearchResult{
					{CitationIndex: 1, Title: "Source A", URL: "https://example.com/a"},
				},
			})
		}
	}))

	var cmdOut strings.Builder
	chatSendCmd.SetOut(&cmdOut)
	t.Cleanup(func() { chatSendCmd.SetOut(nil) })

	rootCmd.SetArgs([]string{"chat", "send", "r1", "question", "--wait"})
	rootCmd.Execute()

	out := cmdOut.String()
	if !strings.Contains(out, "The answer is 42.") {
		t.Errorf("output should contain answer, got %q", out)
	}
	if !strings.Contains(out, "Sources:") {
		t.Errorf("output should contain sources header, got %q", out)
	}
	if !strings.Contains(out, "Source A") {
		t.Errorf("output should contain source title, got %q", out)
	}
}

func TestChatSendCmd_NoSources(t *testing.T) {
	origInterval := chatPollInterval
	chatPollInterval = 0
	t.Cleanup(func() { chatPollInterval = origInterval })

	setupTestServer(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "POST" {
			json.NewEncoder(w).Encode(client.ChatMessage{ID: "msg-1", Status: "completed", Content: "No sources needed."})
			return
		}
		json.NewEncoder(w).Encode(client.ChatMessage{ID: "msg-1", Status: "completed", Content: "No sources needed."})
	}))

	var cmdOut strings.Builder
	chatSendCmd.SetOut(&cmdOut)
	t.Cleanup(func() { chatSendCmd.SetOut(nil) })

	rootCmd.SetArgs([]string{"chat", "send", "r1", "simple question", "--wait"})
	rootCmd.Execute()

	out := cmdOut.String()
	if strings.Contains(out, "Sources:") {
		t.Errorf("output should not contain sources when none exist, got %q", out)
	}
}

func TestChatHistoryCmd(t *testing.T) {
	stdout, _ := captureOutput(t)

	setupTestServer(t, jsonHandler(t, []client.ChatMessage{
		{ID: "msg-1", Content: "first"},
		{ID: "msg-2", Content: "second"},
	}))

	rootCmd.SetArgs([]string{"chat", "history", "r1"})
	rootCmd.Execute()

	out := stdout.String()
	if !strings.Contains(out, "msg-1") {
		t.Errorf("output should contain first message ID, got %q", out)
	}
	if !strings.Contains(out, "msg-2") {
		t.Errorf("output should contain second message ID, got %q", out)
	}
}
