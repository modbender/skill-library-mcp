package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"time"

	"canvas-cli/internal/ui"
)

func runCalendar(args []string) {
	startDate := time.Now().Format("2006-01-02")
	endDate := time.Now().AddDate(0, 0, 30).Format("2006-01-02")

	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "--start":
			if i+1 < len(args) {
				startDate = args[i+1]
				i++
			}
		case "--end":
			if i+1 < len(args) {
				endDate = args[i+1]
				i++
			}
		}
	}

	endpoint := fmt.Sprintf("/calendar_events?type=event&start_date=%s&end_date=%s&all_events=true", startDate, endDate)
	data, err := client.GET(endpoint)
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	// Also fetch assignments in calendar
	assignEndpoint := fmt.Sprintf("/calendar_events?type=assignment&start_date=%s&end_date=%s&all_events=true", startDate, endDate)
	assignData, _ := client.GET(assignEndpoint)

	if jsonOutput {
		fmt.Printf("[%s,%s]\n", string(data), string(assignData))
		return
	}

	var events []struct {
		ID          int    `json:"id"`
		Title       string `json:"title"`
		StartAt     string `json:"start_at"`
		EndAt       string `json:"end_at"`
		Description string `json:"description"`
		ContextCode string `json:"context_code"`
		ContextName string `json:"context_name"`
		Type        string `json:"type"`
		HTMLURL     string `json:"html_url"`
		Assignment  *struct {
			Name  string `json:"name"`
			DueAt string `json:"due_at"`
		} `json:"assignment"`
	}
	json.Unmarshal(data, &events)

	var assignEvents []struct {
		ID          int    `json:"id"`
		Title       string `json:"title"`
		StartAt     string `json:"start_at"`
		ContextName string `json:"context_name"`
		Type        string `json:"type"`
		Assignment  *struct {
			Name  string `json:"name"`
			DueAt string `json:"due_at"`
		} `json:"assignment"`
	}
	json.Unmarshal(assignData, &assignEvents)

	ui.Header(fmt.Sprintf("Calendar  %s → %s", startDate, endDate))

	rows := make([][]string, 0)

	for _, e := range events {
		rows = append(rows, []string{
			"event",
			ui.Truncate(e.ContextName, 20),
			ui.Truncate(e.Title, 35),
			ui.FormatDate(e.StartAt),
		})
	}

	for _, e := range assignEvents {
		title := e.Title
		date := e.StartAt
		if e.Assignment != nil {
			title = e.Assignment.Name
			date = e.Assignment.DueAt
		}
		rows = append(rows, []string{
			ui.C(ui.Magenta, "assign"),
			ui.Truncate(e.ContextName, 20),
			ui.Truncate(title, 35),
			ui.FormatDate(date),
		})
	}

	if len(rows) == 0 {
		fmt.Println(ui.C(ui.Dim, "  No events in this period."))
	} else {
		ui.Table([]string{"TYPE", "COURSE", "TITLE", "DATE"}, rows)
	}
	fmt.Println()
}
