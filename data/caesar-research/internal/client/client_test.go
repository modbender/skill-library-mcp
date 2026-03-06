package client

import (
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func testClient(t *testing.T, handler http.Handler) (*Client, *httptest.Server) {
	t.Helper()
	srv := httptest.NewServer(handler)
	t.Cleanup(srv.Close)
	c := NewWithOptions(Options{
		BaseURL: srv.URL,
		APIKey:  "test-key-12345",
	})
	return c, srv
}

func TestDo_SetsAuthHeader(t *testing.T) {
	var gotAuth string
	c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotAuth = r.Header.Get("Authorization")
		w.WriteHeader(200)
	}))

	c.do("GET", "/test", nil)

	want := "Bearer test-key-12345"
	if gotAuth != want {
		t.Errorf("Authorization = %q, want %q", gotAuth, want)
	}
}

func TestDo_SetsContentTypeForBody(t *testing.T) {
	var gotCT string
	c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotCT = r.Header.Get("Content-Type")
		w.WriteHeader(200)
	}))

	c.do("POST", "/test", map[string]string{"key": "val"})

	if gotCT != "application/json" {
		t.Errorf("Content-Type = %q, want %q", gotCT, "application/json")
	}
}

func TestDo_NoContentTypeForNilBody(t *testing.T) {
	var gotCT string
	c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotCT = r.Header.Get("Content-Type")
		w.WriteHeader(200)
	}))

	c.do("GET", "/test", nil)

	if gotCT != "" {
		t.Errorf("Content-Type = %q, want empty for nil body", gotCT)
	}
}

func TestDo_HTTPError(t *testing.T) {
	tests := []struct {
		name   string
		status int
		body   string
	}{
		{"bad request", 400, "invalid input"},
		{"unauthorized", 401, "bad key"},
		{"server error", 500, "internal error"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(tt.status)
				w.Write([]byte(tt.body))
			}))

			_, err := c.do("GET", "/test", nil)
			if err == nil {
				t.Fatal("expected error for status", tt.status)
			}
			if !strings.Contains(err.Error(), tt.body) {
				t.Errorf("error %q should contain body %q", err.Error(), tt.body)
			}
		})
	}
}

func TestCreateResearch(t *testing.T) {
	var gotReq CreateResearchRequest
	var gotMethod, gotPath string

	c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotMethod = r.Method
		gotPath = r.URL.Path
		json.NewDecoder(r.Body).Decode(&gotReq)
		json.NewEncoder(w).Encode(CreateResearchResponse{ID: "res-123", Status: "queued"})
	}))

	resp, err := c.CreateResearch(&CreateResearchRequest{
		Query:          "test query",
		ReasoningLoops: 3,
		Model:          "claude-opus-4.5",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if gotMethod != "POST" {
		t.Errorf("method = %s, want POST", gotMethod)
	}
	if gotPath != "/research" {
		t.Errorf("path = %s, want /research", gotPath)
	}
	if gotReq.Query != "test query" {
		t.Errorf("request query = %q, want %q", gotReq.Query, "test query")
	}
	if gotReq.ReasoningLoops != 3 {
		t.Errorf("request loops = %d, want 3", gotReq.ReasoningLoops)
	}
	if gotReq.Model != "claude-opus-4.5" {
		t.Errorf("request model = %q, want %q", gotReq.Model, "claude-opus-4.5")
	}
	if resp.ID != "res-123" {
		t.Errorf("response ID = %q, want %q", resp.ID, "res-123")
	}
	if resp.Status != "queued" {
		t.Errorf("response status = %q, want %q", resp.Status, "queued")
	}
}

func TestGetResearch(t *testing.T) {
	content := "Here is the answer with [1] citations."
	c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "GET" {
			t.Errorf("method = %s, want GET", r.Method)
		}
		if r.URL.Path != "/research/abc-123" {
			t.Errorf("path = %s, want /research/abc-123", r.URL.Path)
		}
		json.NewEncoder(w).Encode(ResearchObject{
			ID:        "abc-123",
			Status:    "completed",
			Query:     "test",
			Content:   &content,
			CreatedAt: time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC),
			Results: []ResearchResult{
				{ID: "r1", Title: "Source 1", URL: "https://example.com", CitationIndex: 1},
			},
		})
	}))

	res, err := c.GetResearch("abc-123")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if res.ID != "abc-123" {
		t.Errorf("ID = %q, want %q", res.ID, "abc-123")
	}
	if res.Status != "completed" {
		t.Errorf("status = %q, want %q", res.Status, "completed")
	}
	if res.Content == nil || *res.Content != content {
		t.Errorf("content = %v, want %q", res.Content, content)
	}
	if len(res.Results) != 1 {
		t.Fatalf("results count = %d, want 1", len(res.Results))
	}
	if res.Results[0].CitationIndex != 1 {
		t.Errorf("citation index = %d, want 1", res.Results[0].CitationIndex)
	}
}

func TestGetResearchEvents(t *testing.T) {
	c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/research/abc-123/events" {
			t.Errorf("path = %s, want /research/abc-123/events", r.URL.Path)
		}
		json.NewEncoder(w).Encode([]ResearchEvent{
			{Message: "Searching...", CreatedAt: time.Now()},
			{Message: "Analyzing...", CreatedAt: time.Now()},
		})
	}))

	events, err := c.GetResearchEvents("abc-123")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(events) != 2 {
		t.Fatalf("events count = %d, want 2", len(events))
	}
	if events[0].Message != "Searching..." {
		t.Errorf("event[0] message = %q, want %q", events[0].Message, "Searching...")
	}
}

func TestGetResultContent(t *testing.T) {
	t.Run("with format", func(t *testing.T) {
		c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			wantPath := "/research/r1/results/res1/content"
			if r.URL.Path != wantPath {
				t.Errorf("path = %s, want %s", r.URL.Path, wantPath)
			}
			if r.URL.Query().Get("format") != "markdown" {
				t.Errorf("format = %q, want %q", r.URL.Query().Get("format"), "markdown")
			}
			json.NewEncoder(w).Encode(ResultContent{Content: "# Hello"})
		}))

		rc, err := c.GetResultContent("r1", "res1", "markdown")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if rc.Content != "# Hello" {
			t.Errorf("content = %q, want %q", rc.Content, "# Hello")
		}
	})

	t.Run("without format", func(t *testing.T) {
		c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if r.URL.RawQuery != "" {
				t.Errorf("query string = %q, want empty", r.URL.RawQuery)
			}
			json.NewEncoder(w).Encode(ResultContent{Content: "raw content"})
		}))

		rc, err := c.GetResultContent("r1", "res1", "")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if rc.Content != "raw content" {
			t.Errorf("content = %q, want %q", rc.Content, "raw content")
		}
	})
}

func TestCreateBrainstorm(t *testing.T) {
	var gotBody map[string]string
	c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			t.Errorf("method = %s, want POST", r.Method)
		}
		if r.URL.Path != "/research/brainstorm" {
			t.Errorf("path = %s, want /research/brainstorm", r.URL.Path)
		}
		json.NewDecoder(r.Body).Decode(&gotBody)
		json.NewEncoder(w).Encode(BrainstormSession{
			ID:     "bs-1",
			Query:  "test query",
			Status: "ready",
			Questions: []BrainstormQuestion{
				{
					ID:       "q1",
					Question: "What scope?",
					Options:  map[string]string{"1": "Narrow", "2": "Broad"},
				},
			},
		})
	}))

	session, err := c.CreateBrainstorm("test query")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if gotBody["query"] != "test query" {
		t.Errorf("sent query = %q, want %q", gotBody["query"], "test query")
	}
	if session.ID != "bs-1" {
		t.Errorf("session ID = %q, want %q", session.ID, "bs-1")
	}
	if len(session.Questions) != 1 {
		t.Fatalf("questions count = %d, want 1", len(session.Questions))
	}
	if session.Questions[0].Question != "What scope?" {
		t.Errorf("question = %q, want %q", session.Questions[0].Question, "What scope?")
	}
}

func TestCreateChatMessage(t *testing.T) {
	var gotBody map[string]string
	c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			t.Errorf("method = %s, want POST", r.Method)
		}
		if r.URL.Path != "/research/r1/chat" {
			t.Errorf("path = %s, want /research/r1/chat", r.URL.Path)
		}
		json.NewDecoder(r.Body).Decode(&gotBody)
		json.NewEncoder(w).Encode(ChatMessage{ID: "msg-1", Status: "processing"})
	}))

	msg, err := c.CreateChatMessage("r1", "What about X?")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if gotBody["content"] != "What about X?" {
		t.Errorf("sent content = %q, want %q", gotBody["content"], "What about X?")
	}
	if msg.ID != "msg-1" {
		t.Errorf("message ID = %q, want %q", msg.ID, "msg-1")
	}
	if msg.Status != "processing" {
		t.Errorf("message status = %q, want %q", msg.Status, "processing")
	}
}

func TestGetChatMessage(t *testing.T) {
	c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/research/r1/chat/msg-1" {
			t.Errorf("path = %s, want /research/r1/chat/msg-1", r.URL.Path)
		}
		json.NewEncoder(w).Encode(ChatMessage{
			ID:      "msg-1",
			Status:  "completed",
			Content: "The answer is 42.",
			Results: []ResearchResult{{ID: "r1", Title: "Source", URL: "https://example.com", CitationIndex: 1}},
		})
	}))

	msg, err := c.GetChatMessage("r1", "msg-1")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if msg.Content != "The answer is 42." {
		t.Errorf("content = %q, want %q", msg.Content, "The answer is 42.")
	}
	if len(msg.Results) != 1 {
		t.Fatalf("results count = %d, want 1", len(msg.Results))
	}
}

func TestGetChatHistory(t *testing.T) {
	c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/research/r1/chat" {
			t.Errorf("path = %s, want /research/r1/chat", r.URL.Path)
		}
		if r.Method != "GET" {
			t.Errorf("method = %s, want GET", r.Method)
		}
		json.NewEncoder(w).Encode([]ChatMessage{
			{ID: "msg-1", Content: "first"},
			{ID: "msg-2", Content: "second"},
		})
	}))

	msgs, err := c.GetChatHistory("r1")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(msgs) != 2 {
		t.Fatalf("messages count = %d, want 2", len(msgs))
	}
	if msgs[0].ID != "msg-1" {
		t.Errorf("msgs[0].ID = %q, want %q", msgs[0].ID, "msg-1")
	}
}

func TestStreamChatMessage(t *testing.T) {
	c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/research/r1/chat/msg-1/stream" {
			t.Errorf("path = %s, want /research/r1/chat/msg-1/stream", r.URL.Path)
		}
		w.Header().Set("Content-Type", "text/event-stream")
		w.Write([]byte("data: hello\n\n"))
	}))

	resp, err := c.StreamChatMessage("r1", "msg-1")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	if !strings.Contains(string(body), "hello") {
		t.Errorf("stream body = %q, want to contain %q", string(body), "hello")
	}
}

func TestCreateCollection(t *testing.T) {
	t.Run("with description", func(t *testing.T) {
		var gotBody map[string]string
		c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if r.Method != "POST" {
				t.Errorf("method = %s, want POST", r.Method)
			}
			if r.URL.Path != "/research/collections" {
				t.Errorf("path = %s, want /research/collections", r.URL.Path)
			}
			json.NewDecoder(r.Body).Decode(&gotBody)
			json.NewEncoder(w).Encode(Collection{
				ID:   "col-1",
				Name: "My Collection",
			})
		}))

		coll, err := c.CreateCollection("My Collection", "A description")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if gotBody["name"] != "My Collection" {
			t.Errorf("sent name = %q, want %q", gotBody["name"], "My Collection")
		}
		if gotBody["description"] != "A description" {
			t.Errorf("sent description = %q, want %q", gotBody["description"], "A description")
		}
		if coll.ID != "col-1" {
			t.Errorf("collection ID = %q, want %q", coll.ID, "col-1")
		}
	})

	t.Run("without description", func(t *testing.T) {
		var gotBody map[string]string
		c, _ := testClient(t, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			json.NewDecoder(r.Body).Decode(&gotBody)
			json.NewEncoder(w).Encode(Collection{ID: "col-2", Name: "Bare"})
		}))

		_, err := c.CreateCollection("Bare", "")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if _, ok := gotBody["description"]; ok {
			t.Errorf("description should not be sent when empty, got %q", gotBody["description"])
		}
	})
}

func TestNewWithOptions_Defaults(t *testing.T) {
	c := NewWithOptions(Options{APIKey: "key"})
	if c.httpClient == nil {
		t.Error("httpClient should not be nil")
	}
	if c.baseURL == "" {
		t.Error("baseURL should default to config.BaseURL")
	}
	if c.apiKey != "key" {
		t.Errorf("apiKey = %q, want %q", c.apiKey, "key")
	}
}

func TestNew_MissingKey(t *testing.T) {
	t.Setenv("CAESAR_API_KEY", "")
	_, err := New()
	if err == nil {
		t.Fatal("expected error when CAESAR_API_KEY is not set")
	}
}

func TestNew_WithKey(t *testing.T) {
	t.Setenv("CAESAR_API_KEY", "real-key")
	c, err := New()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if c.apiKey != "real-key" {
		t.Errorf("apiKey = %q, want %q", c.apiKey, "real-key")
	}
}
