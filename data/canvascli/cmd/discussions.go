package cmd

import (
	"encoding/json"
	"fmt"
	"net/url"
	"os"

	"canvas-cli/internal/ui"
)

func runDiscussions(args []string) {
	if len(args) == 0 {
		ui.Error("usage: canvas-cli discussions <course_id> [topic_id] [--reply \"message\"]")
		os.Exit(1)
	}

	courseID := args[0]
	remaining := args[1:]

	if len(remaining) == 0 {
		listDiscussions(courseID)
		return
	}

	topicID := remaining[0]
	remaining = remaining[1:]

	// Check for --reply flag
	for i := 0; i < len(remaining); i++ {
		if remaining[i] == "--reply" && i+1 < len(remaining) {
			postReply(courseID, topicID, remaining[i+1])
			return
		}
	}

	showDiscussion(courseID, topicID)
}

func listDiscussions(courseID string) {
	data, err := client.GET(fmt.Sprintf("/courses/%s/discussion_topics?order_by=recent_activity", courseID))
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var topics []struct {
		ID            int    `json:"id"`
		Title         string `json:"title"`
		PostedAt      string `json:"posted_at"`
		LastReplyAt   string `json:"last_reply_at"`
		DiscussionSubentryCount int `json:"discussion_subentry_count"`
		ReadState     string `json:"read_state"`
		UnreadCount   int    `json:"unread_count"`
		Pinned        bool   `json:"pinned"`
		Locked        bool   `json:"locked"`
	}
	if err := json.Unmarshal(data, &topics); err != nil {
		ui.Error("parsing discussions: " + err.Error())
		os.Exit(1)
	}

	ui.Header(fmt.Sprintf("Discussions — Course %s", courseID))

	rows := make([][]string, 0, len(topics))
	for _, t := range topics {
		unread := ""
		if t.UnreadCount > 0 {
			unread = ui.C(ui.Yellow, fmt.Sprintf("%d new", t.UnreadCount))
		}
		pinned := ""
		if t.Pinned {
			pinned = "pinned"
		}
		rows = append(rows, []string{
			fmt.Sprintf("%d", t.ID),
			ui.Truncate(t.Title, 40),
			fmt.Sprintf("%d", t.DiscussionSubentryCount),
			unread,
			ui.FormatDate(t.LastReplyAt),
			pinned,
		})
	}

	ui.Table([]string{"ID", "TITLE", "REPLIES", "UNREAD", "LAST REPLY", "FLAG"}, rows)
	fmt.Println()
}

func showDiscussion(courseID, topicID string) {
	data, err := client.GET(fmt.Sprintf("/courses/%s/discussion_topics/%s/view", courseID, topicID))
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var view struct {
		Participants []struct {
			ID          int    `json:"id"`
			DisplayName string `json:"display_name"`
		} `json:"participants"`
		View []struct {
			ID        int    `json:"id"`
			UserID    int    `json:"user_id"`
			Message   string `json:"message"`
			CreatedAt string `json:"created_at"`
			Replies   []struct {
				ID        int    `json:"id"`
				UserID    int    `json:"user_id"`
				Message   string `json:"message"`
				CreatedAt string `json:"created_at"`
			} `json:"replies"`
		} `json:"view"`
	}
	if err := json.Unmarshal(data, &view); err != nil {
		ui.Error("parsing discussion: " + err.Error())
		os.Exit(1)
	}

	// Build participant name map
	names := make(map[int]string)
	for _, p := range view.Participants {
		names[p.ID] = p.DisplayName
	}

	ui.Header(fmt.Sprintf("Discussion %s", topicID))

	for _, entry := range view.View {
		name := names[entry.UserID]
		if name == "" {
			name = fmt.Sprintf("User %d", entry.UserID)
		}
		fmt.Printf("\n  %s  %s\n", ui.C(ui.Bold, name), ui.C(ui.Dim, ui.FormatDate(entry.CreatedAt)))
		fmt.Printf("  %s\n", ui.Truncate(stripHTML(entry.Message), 500))

		for _, reply := range entry.Replies {
			rName := names[reply.UserID]
			if rName == "" {
				rName = fmt.Sprintf("User %d", reply.UserID)
			}
			fmt.Printf("\n    %s %s  %s\n", ui.C(ui.Dim, "└─"), ui.C(ui.Bold, rName), ui.C(ui.Dim, ui.FormatDate(reply.CreatedAt)))
			fmt.Printf("       %s\n", ui.Truncate(stripHTML(reply.Message), 400))
		}
	}
	fmt.Println()
}

func postReply(courseID, topicID, message string) {
	form := url.Values{
		"message": {message},
	}
	data, err := client.POST(fmt.Sprintf("/courses/%s/discussion_topics/%s/entries", courseID, topicID), form)
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	ui.Success("Reply posted!")
	fmt.Println()
}

// stripHTML removes basic HTML tags from a string (simple version)
func stripHTML(s string) string {
	result := ""
	inTag := false
	for _, r := range s {
		if r == '<' {
			inTag = true
			continue
		}
		if r == '>' {
			inTag = false
			continue
		}
		if !inTag {
			result += string(r)
		}
	}
	return result
}
