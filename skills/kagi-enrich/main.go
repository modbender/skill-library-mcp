package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"html"
	"io"
	"net/http"
	"net/url"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"
)

var version = "dev" // injected via -ldflags "-X main.version=..."

const (
	enrichWebURL  = "https://kagi.com/api/v0/enrich/web"
	enrichNewsURL = "https://kagi.com/api/v0/enrich/news"
)

type apiMeta struct {
	ID         string   `json:"id,omitempty"`
	Node       string   `json:"node,omitempty"`
	MS         int      `json:"ms,omitempty"`
	APIBalance *float64 `json:"api_balance,omitempty"`
}

type apiItem struct {
	T         int     `json:"t"`
	Rank      int     `json:"rank,omitempty"`
	URL       string  `json:"url,omitempty"`
	Title     string  `json:"title,omitempty"`
	Snippet   *string `json:"snippet"`
	Published string  `json:"published,omitempty"`
}

type enrichResponse struct {
	Meta apiMeta   `json:"meta"`
	Data []apiItem `json:"data"`
}

type enrichResult struct {
	Rank      int    `json:"rank"`
	Title     string `json:"title"`
	URL       string `json:"url"`
	Snippet   string `json:"snippet,omitempty"`
	Published string `json:"published,omitempty"`
}

type enrichOutput struct {
	Query   string         `json:"query"`
	Index   string         `json:"index"`
	Meta    apiMeta        `json:"meta"`
	Results []enrichResult `json:"results"`
}

func main() {
	args := os.Args[1:]
	if len(args) == 0 {
		printGeneralUsage()
		os.Exit(1)
	}

	var err error
	switch args[0] {
	case "--version", "-v":
		fmt.Printf("kagi-enrich %s\n", version)
	case "web":
		err = runEnrich("web", args[1:])
	case "news":
		err = runEnrich("news", args[1:])
	case "-h", "--help":
		printGeneralUsage()
	default:
		// Convenience: no subcommand defaults to web
		err = runEnrich("web", args)
	}

	if err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
}

func printGeneralUsage() {
	fmt.Println("Usage:")
	fmt.Println("  kagi-enrich web  <query> [-n <num>] [--json]")
	fmt.Println("  kagi-enrich news <query> [-n <num>] [--json]")
	fmt.Println()
	fmt.Println("Indexes:")
	fmt.Println("  web   Teclis — non-commercial, independent web content (default)")
	fmt.Println("  news  TinyGem — non-mainstream news & discussions worth reading")
	fmt.Println()
	fmt.Println("Environment:")
	fmt.Println("  KAGI_API_KEY   Required. Your Kagi API key.")
}

func printIndexUsage(index string) {
	fmt.Printf("Usage: kagi-enrich %s <query> [-n <num>] [--json]\n", index)
	fmt.Println()
	fmt.Println("Options:")
	fmt.Println("  -n <num>         Max number of results to display (default: all)")
	fmt.Println("  --json           Emit JSON output")
	fmt.Println("  --timeout <sec>  HTTP timeout in seconds (default: 15)")
	fmt.Println()
	fmt.Println("Environment:")
	fmt.Println("  KAGI_API_KEY     Required. Your Kagi API key.")
}

func runEnrich(index string, args []string) error {
	limit := 0 // 0 = no limit (show all returned results)
	jsonOut := false
	timeoutSec := 15

	queryParts := make([]string, 0, len(args))
	for i := 0; i < len(args); i++ {
		arg := args[i]
		switch arg {
		case "-h", "--help":
			printIndexUsage(index)
			return nil
		case "--":
			queryParts = append(queryParts, args[i+1:]...)
			i = len(args)
		case "-n":
			if i+1 >= len(args) {
				return errors.New("missing value for -n")
			}
			i++
			n, err := strconv.Atoi(args[i])
			if err != nil || n < 1 {
				return fmt.Errorf("invalid value for -n: %s", args[i])
			}
			limit = n
		case "--json":
			jsonOut = true
		case "--timeout":
			if i+1 >= len(args) {
				return errors.New("missing value for --timeout")
			}
			i++
			n, err := strconv.Atoi(args[i])
			if err != nil || n < 1 {
				return fmt.Errorf("invalid value for --timeout: %s", args[i])
			}
			timeoutSec = n
		default:
			if strings.HasPrefix(arg, "-") {
				return fmt.Errorf("unknown option: %s", arg)
			}
			queryParts = append(queryParts, arg)
		}
	}

	query := strings.TrimSpace(strings.Join(queryParts, " "))
	if query == "" {
		printIndexUsage(index)
		return errors.New("query is required")
	}

	apiKey := strings.TrimSpace(os.Getenv("KAGI_API_KEY"))
	if apiKey == "" {
		return errors.New("KAGI_API_KEY environment variable is required (https://kagi.com/settings/api)")
	}

	endpoint := enrichWebURL
	if index == "news" {
		endpoint = enrichNewsURL
	}

	client := &http.Client{Timeout: time.Duration(timeoutSec) * time.Second}
	resp, err := fetchEnrich(client, apiKey, endpoint, query)
	if err != nil {
		return err
	}

	// Build result list, filtering to type-0 items only
	results := make([]enrichResult, 0, len(resp.Data))
	for _, item := range resp.Data {
		if item.T != 0 {
			continue
		}
		r := enrichResult{
			Rank:      item.Rank,
			Title:     html.UnescapeString(item.Title),
			URL:       item.URL,
			Published: item.Published,
		}
		if item.Snippet != nil {
			r.Snippet = html.UnescapeString(*item.Snippet)
		}
		results = append(results, r)
	}

	// Sort by rank
	sort.Slice(results, func(i, j int) bool {
		return results[i].Rank < results[j].Rank
	})

	// Apply -n limit
	if limit > 0 && len(results) > limit {
		results = results[:limit]
	}

	out := enrichOutput{
		Query:   query,
		Index:   index,
		Meta:    resp.Meta,
		Results: results,
	}

	if jsonOut {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		return enc.Encode(out)
	}

	if len(results) == 0 {
		fmt.Fprintln(os.Stderr, "No results found.")
		if resp.Meta.APIBalance != nil {
			fmt.Fprintf(os.Stderr, "[API Balance: $%.4f]\n", *resp.Meta.APIBalance)
		}
		return nil
	}

	for i, r := range results {
		fmt.Printf("--- Result %d ---\n", i+1)
		fmt.Printf("Title: %s\n", r.Title)
		fmt.Printf("URL:   %s\n", r.URL)
		if r.Published != "" {
			fmt.Printf("Date:  %s\n", r.Published)
		}
		if r.Snippet != "" {
			fmt.Printf("       %s\n", r.Snippet)
		}
		fmt.Println()
	}

	if resp.Meta.APIBalance != nil {
		fmt.Fprintf(os.Stderr, "[API Balance: $%.4f | results: %d]\n", *resp.Meta.APIBalance, len(results))
	} else {
		fmt.Fprintf(os.Stderr, "[results: %d]\n", len(results))
	}

	return nil
}

func fetchEnrich(client *http.Client, apiKey, endpoint, query string) (*enrichResponse, error) {
	params := url.Values{}
	params.Set("q", query)

	req, err := http.NewRequestWithContext(context.Background(), http.MethodGet, endpoint+"?"+params.Encode(), nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bot "+apiKey)
	req.Header.Set("Accept", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(io.LimitReader(resp.Body, 4<<20))
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
		if json.Unmarshal(body, &errResp) == nil && len(errResp.Error) > 0 {
			return nil, fmt.Errorf("HTTP %d: %s", resp.StatusCode, errResp.Error[0].Msg)
		}
		text := strings.TrimSpace(string(body))
		if len(text) > 500 {
			text = text[:500] + "..."
		}
		return nil, fmt.Errorf("HTTP %d: %s", resp.StatusCode, text)
	}

	var out enrichResponse
	if err := json.Unmarshal(body, &out); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	return &out, nil
}
