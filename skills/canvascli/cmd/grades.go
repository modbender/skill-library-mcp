package cmd

import (
	"encoding/json"
	"fmt"
	"os"

	"canvas-cli/internal/ui"
)

func runGrades(args []string) {
	if len(args) > 0 {
		showCourseGrades(args[0])
		return
	}
	showAllGrades()
}

func showAllGrades() {
	data, err := client.GET("/courses?enrollment_state=active&include[]=total_scores&include[]=enrollments")
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var courses []Course
	if err := json.Unmarshal(data, &courses); err != nil {
		ui.Error("parsing courses: " + err.Error())
		os.Exit(1)
	}

	ui.Header("Grades Overview")

	rows := make([][]string, 0, len(courses))
	for _, c := range courses {
		currentScore := ""
		currentGrade := ""
		finalScore := ""
		if len(c.Enrollments) > 0 {
			e := c.Enrollments[0]
			if e.ComputedCurrentScore > 0 {
				currentScore = fmt.Sprintf("%.1f%%", e.ComputedCurrentScore)
			}
			if e.ComputedCurrentGrade != "" {
				currentGrade = e.ComputedCurrentGrade
			}
			if e.ComputedFinalScore > 0 {
				finalScore = fmt.Sprintf("%.1f%%", e.ComputedFinalScore)
			}
		}

		// Color the grade
		gradeDisplay := currentGrade
		if currentGrade != "" {
			switch currentGrade[0] {
			case 'A':
				gradeDisplay = ui.C(ui.Green, currentGrade)
			case 'B':
				gradeDisplay = ui.C(ui.Cyan, currentGrade)
			case 'C':
				gradeDisplay = ui.C(ui.Yellow, currentGrade)
			case 'D', 'F':
				gradeDisplay = ui.C(ui.Red, currentGrade)
			}
		}

		rows = append(rows, []string{
			fmt.Sprintf("%d", c.ID),
			ui.Truncate(c.Name, 35),
			currentScore,
			gradeDisplay,
			finalScore,
		})
	}

	ui.Table([]string{"ID", "COURSE", "CURRENT %", "GRADE", "FINAL %"}, rows)
	fmt.Println()
}

func showCourseGrades(courseID string) {
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

	ui.Header(fmt.Sprintf("Grades — Course %s", courseID))

	var totalEarned, totalPossible float64
	rows := make([][]string, 0, len(assignments))

	for _, a := range assignments {
		score := ""
		pct := ""
		if a.Submission != nil && a.Submission.Score != nil {
			score = fmt.Sprintf("%.1f/%.1f", *a.Submission.Score, a.PointsPossible)
			if a.PointsPossible > 0 {
				p := (*a.Submission.Score / a.PointsPossible) * 100
				if p >= 90 {
					pct = ui.C(ui.Green, fmt.Sprintf("%.0f%%", p))
				} else if p >= 70 {
					pct = ui.C(ui.Yellow, fmt.Sprintf("%.0f%%", p))
				} else {
					pct = ui.C(ui.Red, fmt.Sprintf("%.0f%%", p))
				}
			}
			totalEarned += *a.Submission.Score
			totalPossible += a.PointsPossible
		} else if a.PointsPossible > 0 {
			score = fmt.Sprintf("—/%.1f", a.PointsPossible)
		}

		rows = append(rows, []string{
			ui.Truncate(a.Name, 40),
			ui.FormatDate(a.DueAt),
			score,
			pct,
		})
	}

	ui.Table([]string{"ASSIGNMENT", "DUE", "SCORE", "%"}, rows)

	if totalPossible > 0 {
		overallPct := (totalEarned / totalPossible) * 100
		fmt.Println()
		fmt.Printf("  %s  %.1f / %.1f (%.1f%%)\n",
			ui.C(ui.Bold, "Overall:"),
			totalEarned, totalPossible, overallPct)
	}
	fmt.Println()
}
