package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"time"

	"canvas-cli/internal/ui"
)

func runAnnouncements(args []string) {
	if len(args) > 0 {
		listCourseAnnouncements(args[0])
		return
	}
	listAllAnnouncements()
}

func listAllAnnouncements() {
	// First get active courses to build context_codes
	coursesData, err := client.GET("/courses?enrollment_state=active")
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	var courses []struct {
		ID int `json:"id"`
	}
	json.Unmarshal(coursesData, &courses)

	if len(courses) == 0 {
		ui.Header("Announcements")
		fmt.Println(ui.C(ui.Dim, "  No active courses found."))
		fmt.Println()
		return
	}

	// Build context_codes parameter
	var codes []string
	for _, c := range courses {
		codes = append(codes, fmt.Sprintf("context_codes[]=course_%d", c.ID))
	}

	startDate := time.Now().AddDate(0, 0, -30).Format("2006-01-02")
	endpoint := fmt.Sprintf("/announcements?%s&start_date=%s&latest_only=false", strings.Join(codes, "&"), startDate)

	data, err := client.GET(endpoint)
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	displayAnnouncements(data, "Recent Announcements")
}

func listCourseAnnouncements(courseID string) {
	startDate := time.Now().AddDate(0, 0, -60).Format("2006-01-02")
	endpoint := fmt.Sprintf("/announcements?context_codes[]=course_%s&start_date=%s", courseID, startDate)

	data, err := client.GET(endpoint)
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	displayAnnouncements(data, fmt.Sprintf("Announcements — Course %s", courseID))
}

func displayAnnouncements(data []byte, title string) {
	var announcements []struct {
		ID          int    `json:"id"`
		Title       string `json:"title"`
		Message     string `json:"message"`
		PostedAt    string `json:"posted_at"`
		ContextCode string `json:"context_code"`
		AuthorName  string `json:"author"`
		Author      struct {
			DisplayName string `json:"display_name"`
		} `json:"author"`
		ReadState   string `json:"read_state"`
	}
	if err := json.Unmarshal(data, &announcements); err != nil {
		ui.Error("parsing announcements: " + err.Error())
		os.Exit(1)
	}

	ui.Header(title)

	if len(announcements) == 0 {
		fmt.Println(ui.C(ui.Dim, "  No announcements."))
		fmt.Println()
		return
	}

	for _, a := range announcements {
		unread := ""
		if a.ReadState == "unread" {
			unread = ui.C(ui.Yellow, " [NEW]")
		}
		author := a.Author.DisplayName
		if author == "" {
			author = a.AuthorName
		}

		fmt.Printf("\n  %s%s\n", ui.C(ui.Bold, a.Title), unread)
		fmt.Printf("  %s  %s\n", ui.C(ui.Dim, ui.FormatDate(a.PostedAt)), ui.C(ui.Cyan, author))
		msg := stripHTML(a.Message)
		if len(msg) > 200 {
			msg = msg[:197] + "..."
		}
		fmt.Printf("  %s\n", msg)
	}
	fmt.Println()
}
