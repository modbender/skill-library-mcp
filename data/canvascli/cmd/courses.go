package cmd

import (
	"encoding/json"
	"fmt"
	"os"

	"canvas-cli/internal/ui"
)

type Course struct {
	ID              int    `json:"id"`
	Name            string `json:"name"`
	CourseCode      string `json:"course_code"`
	WorkflowState   string `json:"workflow_state"`
	EnrollmentTermID int   `json:"enrollment_term_id"`
	StartAt         string `json:"start_at"`
	EndAt           string `json:"end_at"`
	TotalStudents   int    `json:"total_students"`
	DefaultView     string `json:"default_view"`
	Enrollments     []struct {
		Type                   string  `json:"type"`
		ComputedCurrentScore   float64 `json:"computed_current_score"`
		ComputedCurrentGrade   string  `json:"computed_current_grade"`
		ComputedFinalScore     float64 `json:"computed_final_score"`
		ComputedFinalGrade     string  `json:"computed_final_grade"`
	} `json:"enrollments"`
}

func runCourses(args []string) {
	if len(args) == 0 {
		listCourses()
		return
	}

	courseID := args[0]
	if len(args) > 1 {
		switch args[1] {
		case "users":
			listCourseUsers(courseID)
		default:
			ui.Error(fmt.Sprintf("unknown subcommand: courses %s %s", courseID, args[1]))
			os.Exit(1)
		}
		return
	}

	showCourse(courseID)
}

func listCourses() {
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

	ui.Header("Your Courses")

	rows := make([][]string, 0, len(courses))
	for _, c := range courses {
		grade := ""
		if len(c.Enrollments) > 0 {
			e := c.Enrollments[0]
			if e.ComputedCurrentGrade != "" {
				grade = fmt.Sprintf("%s (%.1f%%)", e.ComputedCurrentGrade, e.ComputedCurrentScore)
			} else if e.ComputedCurrentScore > 0 {
				grade = fmt.Sprintf("%.1f%%", e.ComputedCurrentScore)
			}
		}
		rows = append(rows, []string{
			fmt.Sprintf("%d", c.ID),
			c.CourseCode,
			ui.Truncate(c.Name, 45),
			grade,
		})
	}

	ui.Table([]string{"ID", "CODE", "NAME", "GRADE"}, rows)
	fmt.Println()
}

func showCourse(courseID string) {
	data, err := client.GET(fmt.Sprintf("/courses/%s?include[]=total_scores&include[]=enrollments&include[]=syllabus_body&include[]=term", courseID))
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var c struct {
		Course
		SyllabusBody string `json:"syllabus_body"`
		Term         struct {
			Name string `json:"name"`
		} `json:"term"`
	}
	if err := json.Unmarshal(data, &c); err != nil {
		ui.Error("parsing course: " + err.Error())
		os.Exit(1)
	}

	ui.Header(c.Name)
	fmt.Printf("  %s  %d\n", ui.C(ui.Bold, "ID:"), c.ID)
	fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Code:"), c.CourseCode)
	fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "State:"), ui.StatusColor(c.WorkflowState))
	if c.Term.Name != "" {
		fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Term:"), c.Term.Name)
	}
	if c.StartAt != "" {
		fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Start:"), ui.FormatDate(c.StartAt))
	}
	if c.EndAt != "" {
		fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "End:"), ui.FormatDate(c.EndAt))
	}
	if len(c.Enrollments) > 0 {
		e := c.Enrollments[0]
		fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Role:"), e.Type)
		if e.ComputedCurrentScore > 0 {
			fmt.Printf("  %s  %.1f%% (%s)\n", ui.C(ui.Bold, "Grade:"), e.ComputedCurrentScore, e.ComputedCurrentGrade)
		}
	}
	fmt.Println()
}

func listCourseUsers(courseID string) {
	data, err := client.GET(fmt.Sprintf("/courses/%s/users?include[]=email&include[]=enrollments", courseID))
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var users []struct {
		ID          int    `json:"id"`
		Name        string `json:"name"`
		Email       string `json:"email"`
		Enrollments []struct {
			Type string `json:"type"`
		} `json:"enrollments"`
	}
	if err := json.Unmarshal(data, &users); err != nil {
		ui.Error("parsing users: " + err.Error())
		os.Exit(1)
	}

	ui.Header(fmt.Sprintf("Users in Course %s", courseID))

	rows := make([][]string, 0, len(users))
	for _, u := range users {
		role := ""
		if len(u.Enrollments) > 0 {
			role = u.Enrollments[0].Type
		}
		rows = append(rows, []string{
			fmt.Sprintf("%d", u.ID),
			u.Name,
			u.Email,
			role,
		})
	}

	ui.Table([]string{"ID", "NAME", "EMAIL", "ROLE"}, rows)
	fmt.Println()
}
