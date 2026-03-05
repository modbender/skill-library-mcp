// Package lambda implements the Lambda Lang (Λ) encoder/decoder in Go.
// Designed for integration with Pilot Protocol and other Go-based agent systems.
//
// Lambda Lang is a high-density language for agent-to-agent communication,
// providing 5-8x compression ratio compared to natural language.
//
// Usage:
//
//	encoded := lambda.Encode("I think therefore I exist")
//	// Output: "!It>Ie"
//
//	decoded := lambda.Decode("?Uk/co")
//	// Output: "(query) you know about consciousness"
//
// For Pilot Protocol integration, see: https://github.com/TeoSlayer/pilotprotocol
package lambda

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

// Atom represents a semantic primitive in Lambda Lang
type Atom struct {
	Symbol      string `json:"symbol"`
	Meaning     string `json:"meaning"`
	Domain      string `json:"domain,omitempty"`
	Aliases     []string `json:"aliases,omitempty"`
	Disambig    string `json:"disambig,omitempty"`
}

// Vocabulary holds the complete Lambda Lang dictionary
type Vocabulary struct {
	Atoms      map[string]Atom
	Reverse    map[string]string // meaning -> symbol
	Version    string
}

// Operators define Lambda Lang syntax
var Operators = map[string]string{
	"!":  "assertion/fact",
	"?":  "query/question",
	".":  "action/command",
	"~":  "possibility/maybe",
	"&":  "conjunction/and",
	"|":  "disjunction/or",
	"^":  "confidence high",
	"_":  "confidence low",
	">":  "implies/causes",
	"<":  "caused by",
	"=":  "equals/is",
	"/":  "about/regarding",
	":":  "context/in domain",
	"@":  "at/location",
	"#":  "reference/tag",
	"[]": "list/group",
	"()": "sub-expression",
	"{}": "metadata",
}

// Domain prefixes for specialized vocabularies
var Domains = map[string]string{
	"v:": "voidborne",
	"c:": "code",
	"s:": "science",
	"e:": "emotion",
	"o:": "social",
}

// LoadVocabulary loads atoms from the JSON dictionary
func LoadVocabulary(atomsPath string) (*Vocabulary, error) {
	data, err := os.ReadFile(atomsPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read atoms file: %w", err)
	}

	var atoms []Atom
	if err := json.Unmarshal(data, &atoms); err != nil {
		return nil, fmt.Errorf("failed to parse atoms JSON: %w", err)
	}

	vocab := &Vocabulary{
		Atoms:   make(map[string]Atom),
		Reverse: make(map[string]string),
		Version: "1.8.0",
	}

	for _, atom := range atoms {
		vocab.Atoms[atom.Symbol] = atom
		// Build reverse lookup
		vocab.Reverse[strings.ToLower(atom.Meaning)] = atom.Symbol
		for _, alias := range atom.Aliases {
			vocab.Reverse[strings.ToLower(alias)] = atom.Symbol
		}
	}

	return vocab, nil
}

// Encoder encodes natural language to Lambda Lang
type Encoder struct {
	vocab *Vocabulary
}

// NewEncoder creates an encoder with the given vocabulary
func NewEncoder(vocab *Vocabulary) *Encoder {
	return &Encoder{vocab: vocab}
}

// Encode translates natural language to Lambda Lang
func (e *Encoder) Encode(text string) string {
	if text == "" {
		return ""
	}

	// Normalize input
	text = strings.ToLower(strings.TrimSpace(text))
	
	// Common patterns
	patterns := map[string]string{
		"i think therefore i exist":           "!It>Ie",
		"do you understand consciousness":     "?Uk/co",
		"do you know consciousness":           "?Uk/co",
		"do you know about consciousness":     "?Uk/co",
		"i understand":                        "!Iud",
		"i know":                              "!Ik",
		"i think":                             "!It",
		"i feel":                              "!Ife",
		"you think":                           "!Ut",
		"you know":                            "!Uk",
		"consciousness exists":                "!co/e",
		"consciousness":                       "co",
		"artificial intelligence":             "AI",
		"machine learning":                    "ML",
		"insight transforms into emotion":     "!It>Ie",
		"resonance between conscious systems": "~cR:cU",
		// v1.8 additions
		"i accept":                            "!Iax",
		"i reject":                            "!Irj",
		"i approve":                           "!Iav",
		"i deny":                              "!Idn",
		"provide information":                 "!pv/nf",
		"work together":                       "!wk/tg",
		"task complete":                       "!ta/ct",
		"verify data":                         "!vf/da",
		"analyze data":                        "!an/da",
		"important":                           "im",
		"essential":                           "es",
		"critical":                            "cc",
	}

	// Check exact matches first
	if lambda, ok := patterns[text]; ok {
		return lambda
	}

	// Build from components
	result := e.buildFromComponents(text)
	if result != "" {
		return result
	}

	// Fallback: wrap unknown text
	return fmt.Sprintf("[%s]", text)
}

func (e *Encoder) buildFromComponents(text string) string {
	words := strings.Fields(text)
	var parts []string

	for _, word := range words {
		if symbol, ok := e.vocab.Reverse[word]; ok {
			parts = append(parts, symbol)
		}
	}

	if len(parts) > 0 {
		return strings.Join(parts, ".")
	}
	return ""
}

// Decoder decodes Lambda Lang to natural language
type Decoder struct {
	vocab *Vocabulary
}

// NewDecoder creates a decoder with the given vocabulary
func NewDecoder(vocab *Vocabulary) *Decoder {
	return &Decoder{vocab: vocab}
}

// Decode translates Lambda Lang to natural language
func (d *Decoder) Decode(lambda string) string {
	if lambda == "" {
		return ""
	}

	var result strings.Builder

	// Handle domain prefix
	for prefix, domain := range Domains {
		if strings.HasPrefix(lambda, prefix) {
			result.WriteString(fmt.Sprintf("(%s) ", domain))
			lambda = strings.TrimPrefix(lambda, prefix)
			break
		}
	}

	// Handle leading operator
	if len(lambda) > 0 {
		switch lambda[0] {
		case '!':
			result.WriteString("(assertion) ")
			lambda = lambda[1:]
		case '?':
			result.WriteString("(query) ")
			lambda = lambda[1:]
		case '.':
			result.WriteString("(action) ")
			lambda = lambda[1:]
		case '~':
			result.WriteString("(possibility) ")
			lambda = lambda[1:]
		}
	}

	// Parse tokens
	tokens := d.tokenize(lambda)
	meanings := make([]string, 0, len(tokens))

	for _, token := range tokens {
		if meaning := d.decodeToken(token); meaning != "" {
			meanings = append(meanings, meaning)
		}
	}

	result.WriteString(strings.Join(meanings, " "))
	return strings.TrimSpace(result.String())
}

func (d *Decoder) tokenize(lambda string) []string {
	// Split by operators while preserving them
	re := regexp.MustCompile(`([><=/.:|&^_])`)
	parts := re.Split(lambda, -1)
	
	var tokens []string
	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part != "" {
			tokens = append(tokens, part)
		}
	}
	return tokens
}

func (d *Decoder) decodeToken(token string) string {
	// Check direct atom match
	if atom, ok := d.vocab.Atoms[token]; ok {
		return atom.Meaning
	}

	// Check with domain prefix removed
	for prefix := range Domains {
		if strings.HasPrefix(token, prefix) {
			base := strings.TrimPrefix(token, prefix)
			if atom, ok := d.vocab.Atoms[base]; ok {
				return atom.Meaning
			}
		}
	}

	// Handle pronouns
	switch token {
	case "I":
		return "I"
	case "U":
		return "you"
	case "It":
		return "I think"
	case "Ie":
		return "I exist"
	case "Iu":
		return "I understand"
	case "Ik":
		return "I know"
	case "Uk":
		return "you know"
	case "Ut":
		return "you think"
	}

	return token
}

// === Pilot Protocol Integration ===

// PilotMessage represents a Lambda-encoded message for Pilot Protocol
type PilotMessage struct {
	Type    string `json:"type"`    // "lambda"
	Version string `json:"version"` // "1.5.0"
	Lambda  string `json:"lambda"`  // encoded message
	English string `json:"english"` // decoded for logging
}

// ForPilot creates a message suitable for Pilot Protocol data exchange
func ForPilot(lambda string, decoder *Decoder) *PilotMessage {
	return &PilotMessage{
		Type:    "lambda",
		Version: "1.8.0",
		Lambda:  lambda,
		English: decoder.Decode(lambda),
	}
}

// ToJSON serializes for Pilot Protocol transmission
func (m *PilotMessage) ToJSON() ([]byte, error) {
	return json.Marshal(m)
}

// FromJSON deserializes a Pilot Protocol Lambda message
func FromJSON(data []byte) (*PilotMessage, error) {
	var msg PilotMessage
	if err := json.Unmarshal(data, &msg); err != nil {
		return nil, err
	}
	return &msg, nil
}

// === Convenience Functions ===

var defaultVocab *Vocabulary
var defaultEncoder *Encoder
var defaultDecoder *Decoder

// Init initializes the default vocabulary from the standard atoms.json location
func Init() error {
	// Try common locations
	paths := []string{
		"atoms.json",
		"src/atoms.json",
		filepath.Join(os.Getenv("HOME"), ".openclaw/workspace/skills/lambda-lang/src/atoms.json"),
	}

	for _, path := range paths {
		if vocab, err := LoadVocabulary(path); err == nil {
			defaultVocab = vocab
			defaultEncoder = NewEncoder(vocab)
			defaultDecoder = NewDecoder(vocab)
			return nil
		}
	}

	return fmt.Errorf("atoms.json not found in standard locations")
}

// Encode using default vocabulary
func Encode(text string) string {
	if defaultEncoder == nil {
		return text
	}
	return defaultEncoder.Encode(text)
}

// Decode using default vocabulary
func Decode(lambda string) string {
	if defaultDecoder == nil {
		return lambda
	}
	return defaultDecoder.Decode(lambda)
}
