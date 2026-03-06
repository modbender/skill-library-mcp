package cmd

import (
	"strings"
	"testing"

	"github.com/alexrudloff/caesar-cli/internal/client"
)

func TestBrainstormCmd(t *testing.T) {
	captureOutput(t)

	setupTestServer(t, jsonHandler(t, client.BrainstormSession{
		ID:    "bs-1",
		Query: "test query",
		Questions: []client.BrainstormQuestion{
			{
				ID:       "q1",
				Question: "What scope?",
				Options:  map[string]string{"1": "Narrow", "2": "Broad"},
			},
		},
		Status: "ready",
	}))

	var cmdOut strings.Builder
	brainstormCmd.SetOut(&cmdOut)
	t.Cleanup(func() { brainstormCmd.SetOut(nil) })

	rootCmd.SetArgs([]string{"brainstorm", "test query"})
	rootCmd.Execute()

	out := cmdOut.String()
	if !strings.Contains(out, "bs-1") {
		t.Errorf("output should contain session ID, got %q", out)
	}
	if !strings.Contains(out, "What scope?") {
		t.Errorf("output should contain question, got %q", out)
	}
	if !strings.Contains(out, "--brainstorm") {
		t.Errorf("output should contain usage hint, got %q", out)
	}
}
