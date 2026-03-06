package main

import (
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"
)

const userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

// ANSI color codes
const (
	reset   = "\033[0m"
	bold    = "\033[1m"
	dim     = "\033[2m"
	red     = "\033[31m"
	green   = "\033[32m"
	yellow  = "\033[33m"
	blue    = "\033[34m"
	magenta = "\033[35m"
	cyan    = "\033[36m"
	white   = "\033[37m"
)

func printBanner() {
	fmt.Println()
	fmt.Printf("%s%s  LinkedIn Video Downloader%s\n", bold, cyan, reset)
	fmt.Printf("%s  =========================%s\n", dim, reset)
	fmt.Println()
}

func printStep(step int, total int, msg string) {
	fmt.Printf("  %s[%d/%d]%s %s\n", blue, step, total, reset, msg)
}

func printSuccess(msg string) {
	fmt.Printf("\n  %s%s  %s%s\n\n", green, bold, msg, reset)
}

func printError(msg string) {
	fmt.Fprintf(os.Stderr, "\n  %s%s  Error: %s%s\n\n", red, bold, msg, reset)
}

func printInfo(msg string) {
	fmt.Fprintf(os.Stderr, "  %s%s%s\n", dim, msg, reset)
}

func main() {
	if len(os.Args) < 2 {
		printBanner()
		fmt.Fprintf(os.Stderr, "  %sUsage:%s linkedin-video-dl %s<post-url>%s\n", bold, reset, yellow, reset)
		fmt.Fprintf(os.Stderr, "  %sExample:%s linkedin-video-dl %s\"https://www.linkedin.com/posts/user_slug-activity-123\"%s\n\n", bold, reset, dim, reset)
		os.Exit(1)
	}

	postURL := os.Args[1]

	printBanner()

	if !strings.Contains(postURL, "linkedin.com") {
		printError("The URL does not appear to be from LinkedIn")
		os.Exit(1)
	}

	// Step 1: Fetch page
	printStep(1, 3, "Fetching post page...")

	html, err := fetchPage(postURL)
	if err != nil {
		printError(fmt.Sprintf("Failed to fetch page: %v", err))
		os.Exit(1)
	}

	// Step 2: Extract video URLs
	printStep(2, 3, "Searching for video URLs...")

	videoURLs := extractVideoURLs(html)
	if len(videoURLs) == 0 {
		printError("No videos found in this post")
		fmt.Fprintf(os.Stderr, "  %sPossible reasons:%s\n", yellow, reset)
		fmt.Fprintf(os.Stderr, "  %s- The post does not contain a video%s\n", dim, reset)
		fmt.Fprintf(os.Stderr, "  %s- The post is private or requires authentication%s\n", dim, reset)
		fmt.Fprintf(os.Stderr, "  %s- LinkedIn blocked the request%s\n\n", dim, reset)
		os.Exit(1)
	}

	videoURL := pickBestVideo(videoURLs)
	truncated := videoURL[:min(60, len(videoURL))]
	printInfo(fmt.Sprintf("Found: %s...", truncated))

	// Step 3: Download
	filename := buildFilename(postURL)
	printStep(3, 3, fmt.Sprintf("Downloading to %s%s%s", yellow, filename, reset))
	fmt.Println()

	err = downloadFile(videoURL, filename)
	if err != nil {
		printError(fmt.Sprintf("Download failed: %v", err))
		os.Exit(1)
	}

	printSuccess(fmt.Sprintf("Done! Saved as %s", filename))
}

func fetchPage(pageURL string) (string, error) {
	client := &http.Client{
		Timeout: 30 * time.Second,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			req.Header.Set("User-Agent", userAgent)
			return nil
		},
	}

	req, err := http.NewRequest("GET", pageURL, nil)
	if err != nil {
		return "", err
	}

	req.Header.Set("User-Agent", userAgent)
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
	req.Header.Set("Accept-Language", "en-US,en;q=0.5")
	req.Header.Set("Connection", "keep-alive")

	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("HTTP %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	return string(body), nil
}

func extractVideoURLs(html string) []string {
	seen := make(map[string]bool)
	var urls []string

	// Pattern 1: dms.licdn.com video URLs (main CDN)
	patterns := []*regexp.Regexp{
		regexp.MustCompile(`https?://dms\.licdn\.com/playlist/[^\s"'\\]+\.mp4[^\s"'\\]*`),
		regexp.MustCompile(`https?://dms\.licdn\.com/playlist/vid/[^\s"'\\]+`),
		regexp.MustCompile(`https?://[a-z0-9-]+\.licdn\.com/[^\s"'\\]*video[^\s"'\\]*\.mp4[^\s"'\\]*`),
	}

	for _, pattern := range patterns {
		matches := pattern.FindAllString(html, -1)
		for _, m := range matches {
			cleaned := cleanURL(m)
			if cleaned != "" && !seen[cleaned] {
				seen[cleaned] = true
				urls = append(urls, cleaned)
			}
		}
	}

	// Pattern 2: Encoded URLs (LinkedIn often HTML-encodes or unicode-escapes URLs)
	encodedPattern := regexp.MustCompile(`https?:%2F%2Fdms\.licdn\.com%2F[^\s"'\\]+`)
	for _, m := range encodedPattern.FindAllString(html, -1) {
		decoded, err := url.QueryUnescape(m)
		if err == nil {
			cleaned := cleanURL(decoded)
			if cleaned != "" && !seen[cleaned] {
				seen[cleaned] = true
				urls = append(urls, cleaned)
			}
		}
	}

	// Pattern 3: Unicode-escaped URLs (\u002F = /)
	unescaped := strings.ReplaceAll(html, `\u002F`, `/`)
	unescaped = strings.ReplaceAll(unescaped, `\/`, `/`)
	for _, pattern := range patterns {
		matches := pattern.FindAllString(unescaped, -1)
		for _, m := range matches {
			cleaned := cleanURL(m)
			if cleaned != "" && !seen[cleaned] {
				seen[cleaned] = true
				urls = append(urls, cleaned)
			}
		}
	}

	// Pattern 4: Look for video src in data attributes or JSON
	videoSrcPattern := regexp.MustCompile(`"src"\s*:\s*"(https?://[^"]*licdn\.com[^"]*)"`)
	for _, match := range videoSrcPattern.FindAllStringSubmatch(html, -1) {
		if len(match) > 1 {
			cleaned := cleanURL(match[1])
			if cleaned != "" && !seen[cleaned] {
				seen[cleaned] = true
				urls = append(urls, cleaned)
			}
		}
	}

	// Pattern 5: contentUrl in JSON-LD
	contentURLPattern := regexp.MustCompile(`"contentUrl"\s*:\s*"(https?://[^"]+)"`)
	for _, match := range contentURLPattern.FindAllStringSubmatch(html, -1) {
		if len(match) > 1 {
			cleaned := cleanURL(match[1])
			if cleaned != "" && !seen[cleaned] {
				seen[cleaned] = true
				urls = append(urls, cleaned)
			}
		}
	}

	return urls
}

func cleanURL(rawURL string) string {
	// Remove trailing punctuation/quotes
	rawURL = strings.TrimRight(rawURL, `"'\;,)>]}`)

	// Unescape common HTML entities
	rawURL = strings.ReplaceAll(rawURL, "&amp;", "&")

	// Unescape unicode forward slashes
	rawURL = strings.ReplaceAll(rawURL, `\u002F`, `/`)
	rawURL = strings.ReplaceAll(rawURL, `\/`, `/`)

	// Validate it's a proper URL
	_, err := url.Parse(rawURL)
	if err != nil {
		return ""
	}

	return rawURL
}

func pickBestVideo(urls []string) string {
	// Prefer MP4 URLs, then longest URL (usually has quality params)
	best := urls[0]
	for _, u := range urls {
		if strings.Contains(u, ".mp4") && !strings.Contains(best, ".mp4") {
			best = u
			continue
		}
		if len(u) > len(best) {
			best = u
		}
	}
	return best
}

func buildFilename(postURL string) string {
	// Extract username and activity ID from URL
	parts := strings.Split(postURL, "/")
	name := "linkedin_video"

	for i, p := range parts {
		if p == "posts" && i+1 < len(parts) {
			slug := parts[i+1]
			// Remove query params
			slug = strings.Split(slug, "?")[0]
			name = slug
			break
		}
	}

	// Truncate if too long
	if len(name) > 80 {
		name = name[:80]
	}

	// Sanitize
	name = strings.Map(func(r rune) rune {
		if r == '/' || r == '\\' || r == ':' || r == '*' || r == '?' || r == '"' || r == '<' || r == '>' || r == '|' {
			return '_'
		}
		return r
	}, name)

	return name + ".mp4"
}

type progressWriter struct {
	total      int64
	downloaded int64
	lastPrint  time.Time
}

func (pw *progressWriter) Write(p []byte) (int, error) {
	n := len(p)
	pw.downloaded += int64(n)

	if time.Since(pw.lastPrint) > 100*time.Millisecond || pw.downloaded == pw.total {
		pw.lastPrint = time.Now()
		if pw.total > 0 {
			pct := float64(pw.downloaded) / float64(pw.total) * 100
			bar := buildProgressBar(pct, 30)
			fmt.Fprintf(os.Stderr, "\r  %s%s%s %s%.1f%%%s  %s%s / %s%s",
				green, bar, reset,
				bold, pct, reset,
				dim, formatBytes(pw.downloaded),
				formatBytes(pw.total), reset)
		} else {
			fmt.Fprintf(os.Stderr, "\r  %sDownloaded: %s%s",
				dim, formatBytes(pw.downloaded), reset)
		}
	}

	return n, nil
}

func buildProgressBar(pct float64, width int) string {
	filled := int(pct / 100 * float64(width))
	if filled > width {
		filled = width
	}
	empty := width - filled
	return "[" + strings.Repeat("=", filled) + ">" + strings.Repeat(" ", max(0, empty-1)) + "]"
}

func formatBytes(b int64) string {
	const unit = 1024
	if b < unit {
		return fmt.Sprintf("%d B", b)
	}
	div, exp := int64(unit), 0
	for n := b / unit; n >= unit; n /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.1f %cB", float64(b)/float64(div), "KMGTPE"[exp])
}

func downloadFile(videoURL, filename string) error {
	// Check if file already exists
	if _, err := os.Stat(filename); err == nil {
		return fmt.Errorf("file %s already exists", filename)
	}

	client := &http.Client{Timeout: 10 * time.Minute}

	req, err := http.NewRequest("GET", videoURL, nil)
	if err != nil {
		return err
	}
	req.Header.Set("User-Agent", userAgent)
	req.Header.Set("Referer", "https://www.linkedin.com/")

	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("HTTP %d while downloading video", resp.StatusCode)
	}

	// Verify it looks like a video
	ct := resp.Header.Get("Content-Type")
	if ct != "" && !strings.Contains(ct, "video") && !strings.Contains(ct, "octet-stream") && !strings.Contains(ct, "mp4") {
		return fmt.Errorf("response does not appear to be a video (Content-Type: %s)", ct)
	}

	tmpFile := filename + ".tmp"
	out, err := os.Create(tmpFile)
	if err != nil {
		return err
	}

	pw := &progressWriter{total: resp.ContentLength}

	_, err = io.Copy(out, io.TeeReader(resp.Body, pw))
	out.Close()
	if err != nil {
		os.Remove(tmpFile)
		return err
	}

	fmt.Fprintln(os.Stderr)

	return os.Rename(tmpFile, filepath.Clean(filename))
}
