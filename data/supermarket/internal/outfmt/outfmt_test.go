package outfmt

import (
	"bytes"
	"encoding/json"
	"io"
	"os"
	"testing"
)

func TestPrintJSON(t *testing.T) {
	// Capture stdout
	old := os.Stdout
	r, w, _ := os.Pipe()
	os.Stdout = w

	data := map[string]string{"key": "value"}
	if err := PrintJSON(data); err != nil {
		t.Fatalf("PrintJSON: %v", err)
	}

	_ = w.Close()
	os.Stdout = old

	var buf bytes.Buffer
	_, _ = io.Copy(&buf, r)

	var result map[string]string
	if err := json.Unmarshal(buf.Bytes(), &result); err != nil {
		t.Fatalf("output not valid JSON: %v", err)
	}
	if result["key"] != "value" {
		t.Errorf("got %q, want %q", result["key"], "value")
	}
}

func TestPrintPlain(t *testing.T) {
	old := os.Stdout
	r, w, _ := os.Pipe()
	os.Stdout = w

	rows := [][]string{
		{"a", "b", "c"},
		{"1", "2", "3"},
	}
	PrintPlain(rows)

	_ = w.Close()
	os.Stdout = old

	var buf bytes.Buffer
	_, _ = io.Copy(&buf, r)

	expected := "a\tb\tc\n1\t2\t3\n"
	if buf.String() != expected {
		t.Errorf("got %q, want %q", buf.String(), expected)
	}
}
