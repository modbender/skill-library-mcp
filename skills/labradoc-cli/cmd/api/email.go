package api

import (
	"bytes"
	"encoding/json"
	"fmt"

	"github.com/spf13/cobra"
)

var emailCmd = &cobra.Command{
	Use:   "email",
	Short: "Email operations via the API",
}

var emailAddressesCmd = &cobra.Command{
	Use:   "addresses",
	Short: "List email addresses",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simpleGet(cmd, "/api/emailAddresses", "")
	},
}

var (
	emailDescription string
)

var emailRequestCmd = &cobra.Command{
	Use:   "request",
	Short: "Request new email address",
	RunE: func(cmd *cobra.Command, _ []string) error {
		payload := map[string]string{}
		if emailDescription != "" {
			payload["description"] = emailDescription
		}
		body, err := json.Marshal(payload)
		if err != nil {
			return err
		}
		return simplePost(cmd, "/api/emailAddress", bytes.NewReader(body), "application/json", "")
	},
}

var emailListCmd = &cobra.Command{
	Use:   "list",
	Short: "List emails",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simpleGet(cmd, "/api/emails", "")
	},
}

var (
	emailID    string
	emailIndex int
	emailOut   string
)

var emailBodyCmd = &cobra.Command{
	Use:   "body",
	Short: "Get email body",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if emailID == "" {
			return fmt.Errorf("missing --id")
		}
		if emailIndex <= 0 {
			return fmt.Errorf("missing or invalid --index")
		}
		path := fmt.Sprintf("/api/email/%s/%d", emailID, emailIndex)
		return simpleGet(cmd, path, emailOut)
	},
}

func init() {
	emailCmd.AddCommand(emailAddressesCmd)
	emailCmd.AddCommand(emailRequestCmd)
	emailCmd.AddCommand(emailListCmd)
	emailCmd.AddCommand(emailBodyCmd)

	emailRequestCmd.Flags().StringVar(&emailDescription, "description", "", "Optional description for the email address")
	emailBodyCmd.Flags().StringVar(&emailID, "id", "", "Email ID")
	emailBodyCmd.Flags().IntVar(&emailIndex, "index", 0, "Email index")
	emailBodyCmd.Flags().StringVar(&emailOut, "out", "", "Write response to file instead of stdout")
}
