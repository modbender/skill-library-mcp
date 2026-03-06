package ui

import (
	"fmt"
	"os"
	"strings"
	"time"
)

// ANSI color codes
const (
	Reset   = "\033[0m"
	Bold    = "\033[1m"
	Dim     = "\033[2m"
	Red     = "\033[31m"
	Green   = "\033[32m"
	Yellow  = "\033[33m"
	Blue    = "\033[34m"
	Magenta = "\033[35m"
	Cyan    = "\033[36m"
	White   = "\033[37m"
)

var noColor bool

func init() {
	// Disable colors if not a terminal or NO_COLOR is set
	if os.Getenv("NO_COLOR") != "" {
		noColor = true
	}
	fi, _ := os.Stdout.Stat()
	if fi != nil && (fi.Mode()&os.ModeCharDevice) == 0 {
		noColor = true
	}
}

func C(color, text string) string {
	if noColor {
		return text
	}
	return color + text + Reset
}

func Header(text string) {
	fmt.Println()
	fmt.Println(C(Bold+Cyan, "  "+text))
	fmt.Println(C(Dim, "  "+strings.Repeat("─", len(text)+2)))
}

func Error(msg string) {
	fmt.Fprintf(os.Stderr, "%s %s\n", C(Red, "Error:"), msg)
}

func Success(msg string) {
	fmt.Printf("%s %s\n", C(Green, "✓"), msg)
}

func Info(msg string) {
	fmt.Printf("%s %s\n", C(Cyan, "→"), msg)
}

func Warning(msg string) {
	fmt.Printf("%s %s\n", C(Yellow, "!"), msg)
}

// Table prints a formatted table
func Table(headers []string, rows [][]string) {
	if len(rows) == 0 {
		fmt.Println(C(Dim, "  No results."))
		return
	}

	// Calculate column widths
	widths := make([]int, len(headers))
	for i, h := range headers {
		widths[i] = len(h)
	}
	for _, row := range rows {
		for i, col := range row {
			if i < len(widths) && len(col) > widths[i] {
				widths[i] = len(col)
			}
		}
	}

	// Cap max width
	for i := range widths {
		if widths[i] > 60 {
			widths[i] = 60
		}
	}

	// Print header
	headerLine := "  "
	sepLine := "  "
	for i, h := range headers {
		headerLine += C(Bold, padRight(h, widths[i])) + "  "
		sepLine += C(Dim, strings.Repeat("─", widths[i])) + "  "
	}
	fmt.Println(headerLine)
	fmt.Println(sepLine)

	// Print rows
	for _, row := range rows {
		line := "  "
		for i := range headers {
			val := ""
			if i < len(row) {
				val = row[i]
			}
			if len(val) > 60 {
				val = val[:57] + "..."
			}
			line += padRight(val, widths[i]) + "  "
		}
		fmt.Println(line)
	}
}

func padRight(s string, length int) string {
	if len(s) >= length {
		return s
	}
	return s + strings.Repeat(" ", length-len(s))
}

// FormatDate formats an ISO 8601 date string into a human-readable format
func FormatDate(isoDate string) string {
	if isoDate == "" {
		return C(Dim, "—")
	}
	t, err := time.Parse(time.RFC3339, isoDate)
	if err != nil {
		return isoDate
	}
	diff := time.Until(t)

	formatted := t.Format("Jan 02 15:04")

	if diff < 0 {
		return C(Red, formatted+" (overdue)")
	} else if diff < 48*time.Hour {
		return C(Yellow, formatted+" (soon)")
	}
	return formatted
}

// StatusColor returns a colored status string
func StatusColor(status string) string {
	switch strings.ToLower(status) {
	case "submitted", "graded", "complete", "completed", "active":
		return C(Green, status)
	case "missing", "overdue", "late":
		return C(Red, status)
	case "pending", "unsubmitted", "not_submitted":
		return C(Yellow, status)
	default:
		return status
	}
}

func Truncate(s string, max int) string {
	if len(s) <= max {
		return s
	}
	return s[:max-3] + "..."
}
