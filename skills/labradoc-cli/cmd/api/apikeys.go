package api

import (
	"bytes"
	"encoding/json"
	"fmt"

	"github.com/spf13/cobra"
)

var apikeysCmd = &cobra.Command{
	Use:   "apikeys",
	Short: "API key operations via the API",
}

var apikeysListCmd = &cobra.Command{
	Use:   "list",
	Short: "List API keys",
	Long:  "Returns all API keys for the authenticated user.",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simpleGet(cmd, "/api/user/apikeys", "")
	},
}

var (
	apiKeyName      string
	apiKeyExpiresAt string
)

var apikeysCreateCmd = &cobra.Command{
	Use:   "create",
	Short: "Create API key",
	Long:  "Creates a new API key for the authenticated user.",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if apiKeyName == "" {
			return fmt.Errorf("missing --name")
		}
		payload := map[string]string{
			"name": apiKeyName,
		}
		if apiKeyExpiresAt != "" {
			payload["expiresAt"] = apiKeyExpiresAt
		}
		body, err := json.Marshal(payload)
		if err != nil {
			return err
		}
		return simplePost(cmd, "/api/user/apikeys", bytes.NewReader(body), "application/json", "")
	},
}

var (
	apiKeyID string
)

var apikeysRevokeCmd = &cobra.Command{
	Use:   "revoke",
	Short: "Revoke API key",
	Long:  "Revokes an API key for the authenticated user.",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if apiKeyID == "" {
			return fmt.Errorf("missing --id")
		}
		return simpleDelete(cmd, fmt.Sprintf("/api/user/apikeys/%s", apiKeyID), "")
	},
}

func init() {
	apikeysCmd.AddCommand(apikeysListCmd)
	apikeysCmd.AddCommand(apikeysCreateCmd)
	apikeysCmd.AddCommand(apikeysRevokeCmd)

	apikeysCreateCmd.Flags().StringVar(&apiKeyName, "name", "", "A descriptive name for the API key")
	apikeysCreateCmd.Flags().StringVar(&apiKeyExpiresAt, "expires-at", "", "Optional expiration date for the API key (RFC 3339)")
	apikeysRevokeCmd.Flags().StringVar(&apiKeyID, "id", "", "API key ID")
}
