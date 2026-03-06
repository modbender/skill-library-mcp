package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"canvas-cli/internal/ui"
)

type Assignment struct {
	ID                 int      `json:"id"`
	Name               string   `json:"name"`
	Description        string   `json:"description"`
	DueAt              string   `json:"due_at"`
	PointsPossible     float64  `json:"points_possible"`
	SubmissionTypes    []string `json:"submission_types"`
	HasSubmittedSubs   bool     `json:"has_submitted_submissions"`
	CourseID           int      `json:"course_id"`
	HTMLURL            string   `json:"html_url"`
	LockAt             string   `json:"lock_at"`
	UnlockAt           string   `json:"unlock_at"`
	Published          bool     `json:"published"`
	GradingType        string   `json:"grading_type"`
	AllowedAttempts    int      `json:"allowed_attempts"`
	Submission         *struct {
		Score         *float64 `json:"score"`
		Grade         string   `json:"grade"`
		WorkflowState string   `json:"workflow_state"`
		SubmittedAt   string   `json:"submitted_at"`
		Late          bool     `json:"late"`
		Missing       bool     `json:"missing"`
		Attempt       int      `json:"attempt"`
	} `json:"submission"`
}

func runAssignments(args []string) {
	if len(args) == 0 {
		ui.Error("usage: canvas-cli assignments <course_id> [assignment_id]")
		os.Exit(1)
	}

	courseID := args[0]

	if len(args) > 1 {
		showAssignment(courseID, args[1])
		return
	}

	listAssignments(courseID)
}

func listAssignments(courseID string) {
	data, err := client.GET(fmt.Sprintf("/courses/%s/assignments?include[]=submission&order_by=due_at", courseID))
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var assignments []Assignment
	if err := json.Unmarshal(data, &assignments); err != nil {
		ui.Error("parsing assignments: " + err.Error())
		os.Exit(1)
	}

	ui.Header(fmt.Sprintf("Assignments — Course %s", courseID))

	rows := make([][]string, 0, len(assignments))
	for _, a := range assignments {
		status := ""
		score := ""
		if a.Submission != nil {
			switch a.Submission.WorkflowState {
			case "submitted", "graded":
				status = ui.StatusColor("submitted")
			case "unsubmitted":
				if a.Submission.Missing {
					status = ui.StatusColor("missing")
				} else {
					status = ui.StatusColor("unsubmitted")
				}
			default:
				status = a.Submission.WorkflowState
			}
			if a.Submission.Score != nil {
				score = fmt.Sprintf("%.1f/%.1f", *a.Submission.Score, a.PointsPossible)
			}
		}

		rows = append(rows, []string{
			fmt.Sprintf("%d", a.ID),
			ui.Truncate(a.Name, 40),
			ui.FormatDate(a.DueAt),
			fmt.Sprintf("%.0f", a.PointsPossible),
			status,
			score,
		})
	}

	ui.Table([]string{"ID", "NAME", "DUE", "PTS", "STATUS", "SCORE"}, rows)
	fmt.Println()
}

func showAssignment(courseID, assignID string) {
	data, err := client.GET(fmt.Sprintf("/courses/%s/assignments/%s?include[]=submission", courseID, assignID))
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var a Assignment
	if err := json.Unmarshal(data, &a); err != nil {
		ui.Error("parsing assignment: " + err.Error())
		os.Exit(1)
	}

	ui.Header(a.Name)
	fmt.Printf("  %s  %d\n", ui.C(ui.Bold, "ID:"), a.ID)
	fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Due:"), ui.FormatDate(a.DueAt))
	fmt.Printf("  %s  %.1f\n", ui.C(ui.Bold, "Points:"), a.PointsPossible)
	fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Types:"), strings.Join(a.SubmissionTypes, ", "))
	fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Grading:"), a.GradingType)
	if a.AllowedAttempts > 0 {
		fmt.Printf("  %s  %d\n", ui.C(ui.Bold, "Attempts:"), a.AllowedAttempts)
	}
	if a.UnlockAt != "" {
		fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Unlocks:"), ui.FormatDate(a.UnlockAt))
	}
	if a.LockAt != "" {
		fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Locks:"), ui.FormatDate(a.LockAt))
	}
	fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "URL:"), a.HTMLURL)

	if a.Submission != nil {
		fmt.Println()
		fmt.Printf("  %s\n", ui.C(ui.Bold+ui.Cyan, "Submission"))
		fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Status:"), ui.StatusColor(a.Submission.WorkflowState))
		if a.Submission.Score != nil {
			fmt.Printf("  %s  %.1f / %.1f\n", ui.C(ui.Bold, "Score:"), *a.Submission.Score, a.PointsPossible)
		}
		if a.Submission.Grade != "" {
			fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Grade:"), a.Submission.Grade)
		}
		if a.Submission.SubmittedAt != "" {
			fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Submitted:"), ui.FormatDate(a.Submission.SubmittedAt))
		}
		if a.Submission.Late {
			fmt.Printf("  %s\n", ui.C(ui.Red, "  ⚠ Late submission"))
		}
	}
	fmt.Println()
}
