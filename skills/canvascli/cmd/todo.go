package cmd

import (
	"encoding/json"
	"fmt"
	"os"

	"canvas-cli/internal/ui"
)

func runTodo() {
	data, err := client.GET("/users/self/todo")
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var items []struct {
		Type       string `json:"type"`
		Assignment struct {
			ID             int     `json:"id"`
			Name           string  `json:"name"`
			DueAt          string  `json:"due_at"`
			PointsPossible float64 `json:"points_possible"`
			CourseID       int     `json:"course_id"`
			HTMLURL        string  `json:"html_url"`
		} `json:"assignment"`
		ContextName string `json:"context_name"`
		HTMLURL     string `json:"html_url"`
	}
	if err := json.Unmarshal(data, &items); err != nil {
		ui.Error("parsing todo: " + err.Error())
		os.Exit(1)
	}

	ui.Header("To-Do Items")

	if len(items) == 0 {
		fmt.Println(ui.C(ui.Green, "  All caught up! Nothing to do."))
		fmt.Println()
		return
	}

	rows := make([][]string, 0, len(items))
	for _, item := range items {
		rows = append(rows, []string{
			item.Type,
			ui.Truncate(item.ContextName, 25),
			ui.Truncate(item.Assignment.Name, 35),
			ui.FormatDate(item.Assignment.DueAt),
			fmt.Sprintf("%.0f pts", item.Assignment.PointsPossible),
		})
	}

	ui.Table([]string{"TYPE", "COURSE", "ASSIGNMENT", "DUE", "POINTS"}, rows)
	fmt.Println()
}

func runUpcoming() {
	data, err := client.GET("/users/self/upcoming_events")
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var events []struct {
		ID        int    `json:"id"`
		Title     string `json:"title"`
		StartAt   string `json:"start_at"`
		EndAt     string `json:"end_at"`
		Type      string `json:"type"`
		HTMLURL   string `json:"html_url"`
		ContextCode string `json:"context_code"`
		Assignment *struct {
			ID             int     `json:"id"`
			Name           string  `json:"name"`
			DueAt          string  `json:"due_at"`
			PointsPossible float64 `json:"points_possible"`
		} `json:"assignment"`
	}
	if err := json.Unmarshal(data, &events); err != nil {
		ui.Error("parsing events: " + err.Error())
		os.Exit(1)
	}

	ui.Header("Upcoming Events & Assignments")

	if len(events) == 0 {
		fmt.Println(ui.C(ui.Green, "  Nothing upcoming!"))
		fmt.Println()
		return
	}

	rows := make([][]string, 0, len(events))
	for _, e := range events {
		title := e.Title
		date := ui.FormatDate(e.StartAt)
		eventType := e.Type
		if e.Assignment != nil {
			title = e.Assignment.Name
			date = ui.FormatDate(e.Assignment.DueAt)
			eventType = "assignment"
		}
		rows = append(rows, []string{
			eventType,
			ui.Truncate(title, 45),
			date,
		})
	}

	ui.Table([]string{"TYPE", "TITLE", "DATE"}, rows)
	fmt.Println()
}

func runMissing() {
	data, err := client.GET("/users/self/missing_submissions?include[]=course")
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var assignments []struct {
		ID             int     `json:"id"`
		Name           string  `json:"name"`
		DueAt          string  `json:"due_at"`
		PointsPossible float64 `json:"points_possible"`
		CourseID       int     `json:"course_id"`
		HTMLURL        string  `json:"html_url"`
		Course         *struct {
			Name string `json:"name"`
		} `json:"course"`
	}
	if err := json.Unmarshal(data, &assignments); err != nil {
		ui.Error("parsing missing: " + err.Error())
		os.Exit(1)
	}

	ui.Header("Missing Submissions")

	if len(assignments) == 0 {
		fmt.Println(ui.C(ui.Green, "  No missing submissions!"))
		fmt.Println()
		return
	}

	rows := make([][]string, 0, len(assignments))
	for _, a := range assignments {
		courseName := fmt.Sprintf("%d", a.CourseID)
		if a.Course != nil {
			courseName = a.Course.Name
		}
		rows = append(rows, []string{
			fmt.Sprintf("%d", a.ID),
			ui.Truncate(courseName, 25),
			ui.Truncate(a.Name, 35),
			ui.FormatDate(a.DueAt),
			ui.C(ui.Red, fmt.Sprintf("%.0f pts", a.PointsPossible)),
		})
	}

	ui.Table([]string{"ID", "COURSE", "ASSIGNMENT", "DUE", "POINTS"}, rows)
	fmt.Printf("\n  %s %d missing submission(s)\n\n", ui.C(ui.Red, "!"), len(assignments))
}
