package api

import (
	"fmt"
	"net/url"

	"github.com/spf13/cobra"
)

var microsoftCmd = &cobra.Command{
	Use:   "microsoft",
	Short: "Microsoft integration endpoints",
}

var outlookCmd = &cobra.Command{
	Use:   "outlook",
	Short: "Outlook integration",
}

var outlookTokenCmd = &cobra.Command{
	Use:   "token",
	Short: "Request Outlook OAuth token",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simpleGet(cmd, "/api/microsoft/outlook/token", "")
	},
}

var (
	outlookCode string
)

var outlookCodeCmd = &cobra.Command{
	Use:   "code",
	Short: "Outlook OAuth callback",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if outlookCode == "" {
			return fmt.Errorf("missing --code")
		}
		query := url.Values{}
		query.Set("code", outlookCode)
		path := "/api/microsoft/outlook/code?" + query.Encode()
		return simpleGet(cmd, path, "")
	},
}

func init() {
	microsoftCmd.AddCommand(outlookCmd)
	outlookCmd.AddCommand(outlookTokenCmd)
	outlookCmd.AddCommand(outlookCodeCmd)

	outlookCodeCmd.Flags().StringVar(&outlookCode, "code", "", "OAuth code")
}
