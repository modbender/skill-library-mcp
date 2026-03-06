package api

import (
	"fmt"
	"net/url"

	"github.com/spf13/cobra"
)

var googleCmd = &cobra.Command{
	Use:   "google",
	Short: "Google integration endpoints",
}

var googleDriveCmd = &cobra.Command{
	Use:   "drive",
	Short: "Google Drive integration",
}

var googleDriveStatusCmd = &cobra.Command{
	Use:   "status",
	Short: "Has Google Drive scope",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simpleGet(cmd, "/api/google/drive", "")
	},
}

var (
	googleDriveScope string
)

var googleDriveTokenCmd = &cobra.Command{
	Use:   "token",
	Short: "Request Google OAuth token",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if googleDriveScope == "" {
			return fmt.Errorf("missing --scope")
		}
		query := url.Values{}
		query.Set("scope", googleDriveScope)
		path := "/api/google/drive/token?" + query.Encode()
		return simpleGet(cmd, path, "")
	},
}

var (
	googleDriveCode string
)

var googleDriveCodeCmd = &cobra.Command{
	Use:   "code",
	Short: "Google OAuth callback",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if googleDriveCode == "" {
			return fmt.Errorf("missing --code")
		}
		query := url.Values{}
		query.Set("code", googleDriveCode)
		path := "/api/google/drive/code?" + query.Encode()
		return simpleGet(cmd, path, "")
	},
}

var googleDriveRefreshCmd = &cobra.Command{
	Use:   "refresh",
	Short: "Refresh Google Drive Files",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simpleGet(cmd, "/api/google/drive/refresh", "")
	},
}

var googleDriveRevokeCmd = &cobra.Command{
	Use:   "revoke",
	Short: "Revoke Google OAuth token",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simpleDelete(cmd, "/api/google/drive/token", "")
	},
}

var googleGmailCmd = &cobra.Command{
	Use:   "gmail",
	Short: "Gmail integration",
}

var googleGmailStatusCmd = &cobra.Command{
	Use:   "status",
	Short: "Has Gmail token",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simpleGet(cmd, "/api/google/gmail", "")
	},
}

var googleGmailTokenCmd = &cobra.Command{
	Use:   "token",
	Short: "Request Gmail OAuth token",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simpleGet(cmd, "/api/google/gmail/token", "")
	},
}

var (
	googleGmailCode string
)

var googleGmailCodeCmd = &cobra.Command{
	Use:   "code",
	Short: "Gmail OAuth callback",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if googleGmailCode == "" {
			return fmt.Errorf("missing --code")
		}
		query := url.Values{}
		query.Set("code", googleGmailCode)
		path := "/api/google/gmail/code?" + query.Encode()
		return simpleGet(cmd, path, "")
	},
}

var googleGmailRevokeCmd = &cobra.Command{
	Use:   "revoke",
	Short: "Revoke Gmail token",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simpleGet(cmd, "/api/google/gmail/revoke", "")
	},
}

func init() {
	googleCmd.AddCommand(googleDriveCmd)
	googleCmd.AddCommand(googleGmailCmd)

	googleDriveCmd.AddCommand(googleDriveStatusCmd)
	googleDriveCmd.AddCommand(googleDriveTokenCmd)
	googleDriveCmd.AddCommand(googleDriveCodeCmd)
	googleDriveCmd.AddCommand(googleDriveRefreshCmd)
	googleDriveCmd.AddCommand(googleDriveRevokeCmd)

	googleDriveTokenCmd.Flags().StringVar(&googleDriveScope, "scope", "", "OAuth scope")
	googleDriveCodeCmd.Flags().StringVar(&googleDriveCode, "code", "", "OAuth code")

	googleGmailCmd.AddCommand(googleGmailStatusCmd)
	googleGmailCmd.AddCommand(googleGmailTokenCmd)
	googleGmailCmd.AddCommand(googleGmailCodeCmd)
	googleGmailCmd.AddCommand(googleGmailRevokeCmd)

	googleGmailCodeCmd.Flags().StringVar(&googleGmailCode, "code", "", "OAuth code")
}
