package cmd

import (
	"encoding/json"
	"fmt"
	"os"

	"canvas-cli/internal/ui"
)

func runNotifications() {
	data, err := client.GET("/users/self/activity_stream?only_active_courses=true")
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var items []struct {
		ID          int    `json:"id"`
		Title       string `json:"title"`
		Message     string `json:"message"`
		Type        string `json:"type"`
		ReadState   bool   `json:"read_state"`
		CreatedAt   string `json:"created_at"`
		UpdatedAt   string `json:"updated_at"`
		ContextType string `json:"context_type"`
		CourseName  string `json:"course_name,omitempty"`
		HTMLURL     string `json:"html_url"`
	}
	if err := json.Unmarshal(data, &items); err != nil {
		ui.Error("parsing activity stream: " + err.Error())
		os.Exit(1)
	}

	ui.Header("Activity Stream")

	if len(items) == 0 {
		fmt.Println(ui.C(ui.Dim, "  No recent activity."))
		fmt.Println()
		return
	}

	for _, item := range items {
		unread := ""
		if !item.ReadState {
			unread = ui.C(ui.Yellow, " [NEW]")
		}

		typeLabel := item.Type
		switch item.Type {
		case "Announcement":
			typeLabel = ui.C(ui.Magenta, "ANNOUNCE")
		case "DiscussionTopic":
			typeLabel = ui.C(ui.Cyan, "DISCUSS")
		case "Submission":
			typeLabel = ui.C(ui.Green, "SUBMIT")
		case "Conversation":
			typeLabel = ui.C(ui.Blue, "MESSAGE")
		case "Message":
			typeLabel = ui.C(ui.Blue, "MESSAGE")
		}

		fmt.Printf("\n  %s  %s%s\n", typeLabel, ui.C(ui.Bold, item.Title), unread)
		if item.CourseName != "" {
			fmt.Printf("  %s  %s\n", ui.C(ui.Dim, item.CourseName), ui.C(ui.Dim, ui.FormatDate(item.CreatedAt)))
		} else {
			fmt.Printf("  %s\n", ui.C(ui.Dim, ui.FormatDate(item.CreatedAt)))
		}
		if item.Message != "" {
			msg := stripHTML(item.Message)
			if len(msg) > 150 {
				msg = msg[:147] + "..."
			}
			fmt.Printf("  %s\n", msg)
		}
	}
	fmt.Println()
}
