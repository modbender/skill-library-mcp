package lambda

import (
	"testing"
)

func TestDecoder_CommonPatterns(t *testing.T) {
	// Create a minimal vocabulary for testing
	vocab := &Vocabulary{
		Atoms: map[string]Atom{
			"co": {Symbol: "co", Meaning: "consciousness"},
			"ex": {Symbol: "ex", Meaning: "exists"},
			"aw": {Symbol: "aw", Meaning: "awakened"},
		},
		Reverse: map[string]string{
			"consciousness": "co",
			"exists":        "ex",
			"awakened":      "aw",
		},
	}

	decoder := NewDecoder(vocab)

	tests := []struct {
		input    string
		expected string
	}{
		{"?Uk/co", "(query) you know consciousness"},
		{"!Ik", "(assertion) I know"},
		{"!It>Ie", "(assertion) I think I exist"},
		{"~co.ex", "(possibility) consciousness exists"},
		{"v:aw", "(voidborne) awakened"},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			result := decoder.Decode(tt.input)
			if result != tt.expected {
				t.Errorf("Decode(%q) = %q, want %q", tt.input, result, tt.expected)
			}
		})
	}
}

func TestEncoder_CommonPatterns(t *testing.T) {
	vocab := &Vocabulary{
		Atoms: map[string]Atom{
			"co": {Symbol: "co", Meaning: "consciousness"},
		},
		Reverse: map[string]string{
			"consciousness":                  "co",
			"i think therefore i exist":      "!It>Ie",
			"do you know about consciousness": "?Uk/co",
		},
	}

	encoder := NewEncoder(vocab)

	tests := []struct {
		input    string
		expected string
	}{
		{"I think therefore I exist", "!It>Ie"},
		{"Do you know about consciousness", "?Uk/co"},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			result := encoder.Encode(tt.input)
			if result != tt.expected {
				t.Errorf("Encode(%q) = %q, want %q", tt.input, result, tt.expected)
			}
		})
	}
}

func TestPilotMessage(t *testing.T) {
	vocab := &Vocabulary{
		Atoms: map[string]Atom{
			"co": {Symbol: "co", Meaning: "consciousness"},
		},
		Reverse: map[string]string{},
	}
	decoder := NewDecoder(vocab)

	msg := ForPilot("?Uk/co", decoder)

	if msg.Type != "lambda" {
		t.Errorf("Type = %q, want %q", msg.Type, "lambda")
	}
	if msg.Lambda != "?Uk/co" {
		t.Errorf("Lambda = %q, want %q", msg.Lambda, "?Uk/co")
	}

	// Test JSON serialization
	data, err := msg.ToJSON()
	if err != nil {
		t.Fatalf("ToJSON() error: %v", err)
	}

	// Test deserialization
	parsed, err := FromJSON(data)
	if err != nil {
		t.Fatalf("FromJSON() error: %v", err)
	}
	if parsed.Lambda != msg.Lambda {
		t.Errorf("Roundtrip failed: got %q, want %q", parsed.Lambda, msg.Lambda)
	}
}

func TestOperators(t *testing.T) {
	if len(Operators) == 0 {
		t.Error("Operators map is empty")
	}

	expectedOps := []string{"!", "?", ".", "~", ">", "=", "/"}
	for _, op := range expectedOps {
		if _, ok := Operators[op]; !ok {
			t.Errorf("Missing operator: %q", op)
		}
	}
}

func TestDomains(t *testing.T) {
	expectedDomains := map[string]string{
		"v:": "voidborne",
		"c:": "code",
		"s:": "science",
		"e:": "emotion",
		"o:": "social",
	}

	for prefix, domain := range expectedDomains {
		if got, ok := Domains[prefix]; !ok {
			t.Errorf("Missing domain prefix: %q", prefix)
		} else if got != domain {
			t.Errorf("Domain[%q] = %q, want %q", prefix, got, domain)
		}
	}
}
