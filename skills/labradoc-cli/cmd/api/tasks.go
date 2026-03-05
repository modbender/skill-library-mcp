package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/zamedic/labradoc-cli/internal/cli"

	"github.com/spf13/cobra"
)

var tasksCmd = &cobra.Command{
	Use:   "tasks",
	Short: "Task operations via the API",
}

var tasksListCmd = &cobra.Command{
	Use:   "list",
	Short: "List tasks",
	RunE: func(cmd *cobra.Command, _ []string) error {
		opts, err := resolveAPIConfig()
		if err != nil {
			return err
		}
		if opts.APIKey == "" && opts.Token == "" {
			return fmt.Errorf("missing api token (use --api-token, --token, api_token, or --use-auth-token)")
		}
		resp, err := cli.DoRequest(cmd.Context(), "GET", "/api/tasks", nil, opts)
		if err != nil {
			return err
		}
		defer resp.Body.Close()
		if _, err := io.Copy(os.Stdout, resp.Body); err != nil {
			return err
		}
		if resp.StatusCode >= 400 {
			return fmt.Errorf("request failed: %s", resp.Status)
		}
		return nil
	},
}

var (
	taskID   string
	taskIDs  []string
	tasksOut string
)

var tasksCloseCmd = &cobra.Command{
	Use:   "close",
	Short: "Close tasks",
	Long:  "Close multiple tasks or a single task when --id is provided.",
	RunE: func(cmd *cobra.Command, _ []string) error {
		opts, err := resolveAPIConfig()
		if err != nil {
			return err
		}
		if opts.APIKey == "" && opts.Token == "" {
			return fmt.Errorf("missing api token (use --api-token, --token, api_token, or --use-auth-token)")
		}

		if taskID != "" {
			resp, err := cli.DoRequest(cmd.Context(), "POST", fmt.Sprintf("/api/tasks/%s/close", taskID), nil, opts)
			if err != nil {
				return err
			}
			defer resp.Body.Close()
			return writeResponse(resp, tasksOut)
		}

		ids := make([]string, 0, len(taskIDs))
		for _, id := range taskIDs {
			if strings.TrimSpace(id) != "" {
				ids = append(ids, strings.TrimSpace(id))
			}
		}
		if len(ids) == 0 {
			return fmt.Errorf("missing --id or --ids")
		}
		body, err := json.Marshal(map[string]any{"id": ids})
		if err != nil {
			return err
		}
		opts.Headers = map[string]string{
			"Content-Type": "application/json",
		}
		resp, err := cli.DoRequest(cmd.Context(), "POST", "/api/tasks/close", bytes.NewReader(body), opts)
		if err != nil {
			return err
		}
		defer resp.Body.Close()
		return writeResponse(resp, tasksOut)
	},
}

func init() {
	tasksCmd.AddCommand(tasksListCmd)
	tasksCmd.AddCommand(tasksCloseCmd)

	tasksCloseCmd.Flags().StringVar(&taskID, "id", "", "Task ID to close")
	tasksCloseCmd.Flags().StringSliceVar(&taskIDs, "ids", nil, "Task IDs to close (repeatable)")
	tasksCloseCmd.Flags().StringVar(&tasksOut, "out", "", "Write response to file instead of stdout")
}
