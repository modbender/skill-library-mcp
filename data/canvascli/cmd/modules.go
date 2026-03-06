package cmd

import (
	"encoding/json"
	"fmt"
	"os"

	"canvas-cli/internal/ui"
)

func runModules(args []string) {
	if len(args) == 0 {
		ui.Error("usage: canvas-cli modules <course_id> [module_id]")
		os.Exit(1)
	}

	courseID := args[0]

	if len(args) > 1 {
		listModuleItems(courseID, args[1])
		return
	}

	listModules(courseID)
}

func listModules(courseID string) {
	data, err := client.GET(fmt.Sprintf("/courses/%s/modules?include[]=items_count", courseID))
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var modules []struct {
		ID             int    `json:"id"`
		Name           string `json:"name"`
		Position       int    `json:"position"`
		State          string `json:"state"`
		ItemsCount     int    `json:"items_count"`
		CompletedAt    string `json:"completed_at"`
		WorkflowState  string `json:"workflow_state"`
	}
	if err := json.Unmarshal(data, &modules); err != nil {
		ui.Error("parsing modules: " + err.Error())
		os.Exit(1)
	}

	ui.Header(fmt.Sprintf("Modules — Course %s", courseID))

	rows := make([][]string, 0, len(modules))
	for _, m := range modules {
		state := m.State
		if m.CompletedAt != "" {
			state = "completed"
		}
		rows = append(rows, []string{
			fmt.Sprintf("%d", m.ID),
			ui.Truncate(m.Name, 45),
			fmt.Sprintf("%d", m.ItemsCount),
			ui.StatusColor(state),
		})
	}

	ui.Table([]string{"ID", "NAME", "ITEMS", "STATE"}, rows)
	fmt.Println()
}

func listModuleItems(courseID, moduleID string) {
	data, err := client.GET(fmt.Sprintf("/courses/%s/modules/%s/items?include[]=content_details", courseID, moduleID))
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var items []struct {
		ID              int    `json:"id"`
		Title           string `json:"title"`
		Type            string `json:"type"`
		Position        int    `json:"position"`
		HTMLURL         string `json:"html_url"`
		ContentID       int    `json:"content_id"`
		CompletionReq   *struct {
			Type      string `json:"type"`
			Completed bool   `json:"completed"`
		} `json:"completion_requirement"`
		ContentDetails  *struct {
			DueAt          string  `json:"due_at"`
			PointsPossible float64 `json:"points_possible"`
		} `json:"content_details"`
	}
	if err := json.Unmarshal(data, &items); err != nil {
		ui.Error("parsing module items: " + err.Error())
		os.Exit(1)
	}

	ui.Header(fmt.Sprintf("Module %s Items", moduleID))

	rows := make([][]string, 0, len(items))
	for _, item := range items {
		status := ""
		if item.CompletionReq != nil {
			if item.CompletionReq.Completed {
				status = ui.C(ui.Green, "done")
			} else {
				status = ui.C(ui.Yellow, item.CompletionReq.Type)
			}
		}
		due := ""
		if item.ContentDetails != nil && item.ContentDetails.DueAt != "" {
			due = ui.FormatDate(item.ContentDetails.DueAt)
		}

		rows = append(rows, []string{
			fmt.Sprintf("%d", item.ID),
			item.Type,
			ui.Truncate(item.Title, 40),
			due,
			status,
		})
	}

	ui.Table([]string{"ID", "TYPE", "TITLE", "DUE", "STATUS"}, rows)
	fmt.Println()
}
