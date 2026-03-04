package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

var version = "dev" // injected via -ldflags "-X main.version=..."

const summarizerURL = "https://kagi.com/api/v0/summarize"

type summarizeRequest struct {
	URL            string `json:"url,omitempty"`
	Text           string `json:"text,omitempty"`
	Engine         string `json:"engine,omitempty"`
	SummaryType    string `json:"summary_type,omitempty"`
	TargetLanguage string `json:"target_language,omitempty"`
	Cache          *bool  `json:"cache,omitempty"`
}

type apiMeta struct {
	ID         string   `json:"id,omitempty"`
	Node       string   `json:"node,omitempty"`
	MS         int      `json:"ms,omitempty"`
	APIBalance *float64 `json:"api_balance,omitempty"`
}

type summarizeData struct {
	Output string `json:"output"`
	Tokens int    `json:"tokens"`
}

type summarizeResponse struct {
	Meta apiMeta       `json:"meta"`
	Data summarizeData `json:"data"`
}

type outputJSON struct {
	Input  string  `json:"input"`
	Output string  `json:"output"`
	Tokens int     `json:"tokens"`
	Engine string  `json:"engine,omitempty"`
	Type   string  `json:"type,omitempty"`
	Meta   apiMeta `json:"meta"`
}

var validEngines = map[string]bool{
	"cecil":  true,
	"agnes":  true,
	"daphne": true,
	"muriel": true,
}

var validTypes = map[string]bool{
	"summary":  true,
	"takeaway": true,
}

func main() {
	args := os.Args[1:]
	if len(args) == 0 {
		// Check if stdin has data
		stat, err := os.Stdin.Stat()
		if err != nil || (stat.Mode()&os.ModeCharDevice) != 0 {
			printUsage()
			os.Exit(1)
		}
	}

	if len(args) > 0 && (args[0] == "--version" || args[0] == "-v") {
		fmt.Printf("kagi-summarizer %s\n", version)
		return
	}

	if err := run(args); err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Println("Usage: kagi-summarizer <url> [options]")
	fmt.Println("       kagi-summarizer --text <text> [options]")
	fmt.Println("       echo <text> | kagi-summarizer [options]")
	fmt.Println()
	fmt.Println("Options:")
	fmt.Println("  --text <text>        Summarize raw text instead of a URL")
	fmt.Println("  --engine <name>      Summarization engine: cecil (default), agnes, muriel")
	fmt.Println("  --type <type>        Output type: summary (default), takeaway")
	fmt.Println("  --lang <code>        Target language code (e.g. EN, DE, FR, JA)")
	fmt.Println("  --json               Emit JSON output")
	fmt.Println("  --no-cache           Bypass cached responses")
	fmt.Println("  --timeout <sec>      HTTP timeout in seconds (default: 120)")
	fmt.Println()
	fmt.Println("Engines:")
	fmt.Println("  cecil    Friendly, descriptive, fast summary (default)")
	fmt.Println("  agnes    Formal, technical, analytical summary")
	fmt.Println("  muriel   Best-in-class, enterprise-grade summary")
	fmt.Println()
	fmt.Println("Summary types:")
	fmt.Println("  summary   Paragraph(s) of prose (default)")
	fmt.Println("  takeaway  Bulleted list of key points")
	fmt.Println()
	fmt.Println("Environment:")
	fmt.Println("  KAGI_API_KEY   Required. Your Kagi API key.")
	fmt.Println()
	fmt.Println("Examples:")
	fmt.Println("  kagi-summarizer https://en.wikipedia.org/wiki/Go_(programming_language)")
	fmt.Println("  kagi-summarizer https://arxiv.org/abs/1706.03762 --engine muriel --type takeaway")
	fmt.Println("  kagi-summarizer https://example.com/article --lang DE")
	fmt.Println("  cat paper.txt | kagi-summarizer --type takeaway")
	fmt.Println("  kagi-summarizer --text \"Long article text here...\" --json")
}

func run(args []string) error {
	var (
		inputURL   string
		inputText  string
		engine     string
		summType   string
		targetLang string
		jsonOut    bool
		noCache    bool
		timeoutSec = 120
	)

	positionals := make([]string, 0, len(args))
	for i := 0; i < len(args); i++ {
		arg := args[i]
		switch arg {
		case "-h", "--help":
			printUsage()
			return nil
		case "--":
			positionals = append(positionals, args[i+1:]...)
			i = len(args)
		case "--text":
			if i+1 >= len(args) {
				return errors.New("missing value for --text")
			}
			i++
			inputText = args[i]
		case "--engine":
			if i+1 >= len(args) {
				return errors.New("missing value for --engine")
			}
			i++
			engine = strings.ToLower(args[i])
			if !validEngines[engine] {
				return fmt.Errorf("unknown engine %q — valid: cecil, agnes, muriel", engine)
			}
		case "--type":
			if i+1 >= len(args) {
				return errors.New("missing value for --type")
			}
			i++
			summType = strings.ToLower(args[i])
			if !validTypes[summType] {
				return fmt.Errorf("unknown type %q — valid: summary, takeaway", summType)
			}
		case "--lang":
			if i+1 >= len(args) {
				return errors.New("missing value for --lang")
			}
			i++
			targetLang = strings.ToUpper(args[i])
		case "--json":
			jsonOut = true
		case "--no-cache":
			noCache = true
		case "--timeout":
			if i+1 >= len(args) {
				return errors.New("missing value for --timeout")
			}
			i++
			var n int
			if _, err := fmt.Sscanf(args[i], "%d", &n); err != nil {
				return fmt.Errorf("invalid value for --timeout: %s", args[i])
			}
			timeoutSec = n
		default:
			if strings.HasPrefix(arg, "-") {
				return fmt.Errorf("unknown option: %s", arg)
			}
			positionals = append(positionals, arg)
		}
	}

	// Resolve URL from positional args
	if len(positionals) == 1 {
		inputURL = strings.TrimSpace(positionals[0])
	} else if len(positionals) > 1 {
		return errors.New("too many positional arguments — provide a single URL or use --text")
	}

	// Check stdin if no URL and no --text
	if inputURL == "" && inputText == "" {
		stat, err := os.Stdin.Stat()
		if err == nil && (stat.Mode()&os.ModeCharDevice) == 0 {
			stdinBytes, err := io.ReadAll(io.LimitReader(os.Stdin, 4<<20))
			if err != nil {
				return fmt.Errorf("reading stdin: %w", err)
			}
			inputText = strings.TrimSpace(string(stdinBytes))
		}
	}

	if inputURL == "" && inputText == "" {
		printUsage()
		return errors.New("a URL or text input is required")
	}
	if inputURL != "" && inputText != "" {
		return errors.New("--text and a URL are mutually exclusive")
	}

	apiKey := strings.TrimSpace(os.Getenv("KAGI_API_KEY"))
	if apiKey == "" {
		return errors.New("KAGI_API_KEY environment variable is required (https://kagi.com/settings/api)")
	}

	if timeoutSec < 1 {
		timeoutSec = 1
	}

	client := &http.Client{Timeout: time.Duration(timeoutSec) * time.Second}

	resp, err := callSummarizer(client, apiKey, inputURL, inputText, engine, summType, targetLang, !noCache)
	if err != nil {
		return err
	}

	// Determine the display label for input
	inputLabel := inputURL
	if inputLabel == "" {
		runes := []rune(inputText)
		if len(runes) > 80 {
			inputLabel = string(runes[:80]) + "..."
		} else {
			inputLabel = inputText
		}
	}

	if jsonOut {
		out := outputJSON{
			Input:  inputLabel,
			Output: resp.Data.Output,
			Tokens: resp.Data.Tokens,
			Engine: engine,
			Type:   summType,
			Meta:   resp.Meta,
		}
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		return enc.Encode(out)
	}

	fmt.Println(resp.Data.Output)

	if resp.Meta.APIBalance != nil {
		fmt.Fprintf(os.Stderr, "[API Balance: $%.4f | tokens: %d]\n", *resp.Meta.APIBalance, resp.Data.Tokens)
	} else {
		fmt.Fprintf(os.Stderr, "[tokens: %d]\n", resp.Data.Tokens)
	}

	return nil
}

func callSummarizer(
	client *http.Client,
	apiKey, inputURL, inputText, engine, summType, targetLang string,
	cache bool,
) (*summarizeResponse, error) {
	reqBody := summarizeRequest{
		URL:            inputURL,
		Text:           inputText,
		Engine:         engine,
		SummaryType:    summType,
		TargetLanguage: targetLang,
	}
	if !cache {
		reqBody.Cache = new(bool)
	}

	bodyBytes, err := json.Marshal(reqBody)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequestWithContext(context.Background(), http.MethodPost, summarizerURL, bytes.NewReader(bodyBytes))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bot "+apiKey)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(io.LimitReader(resp.Body, 4<<20))
	if err != nil {
		return nil, err
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		var errResp struct {
			Error []struct {
				Code int    `json:"code"`
				Msg  string `json:"msg"`
			} `json:"error"`
		}
		if json.Unmarshal(respBody, &errResp) == nil && len(errResp.Error) > 0 {
			return nil, fmt.Errorf("HTTP %d: %s", resp.StatusCode, errResp.Error[0].Msg)
		}
		text := strings.TrimSpace(string(respBody))
		if len(text) > 500 {
			text = text[:500] + "..."
		}
		return nil, fmt.Errorf("HTTP %d: %s", resp.StatusCode, text)
	}

	var out summarizeResponse
	if err := json.Unmarshal(respBody, &out); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	if out.Data.Output == "" {
		return nil, errors.New("empty response from Summarizer API")
	}

	return &out, nil
}
