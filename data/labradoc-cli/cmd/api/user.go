package api

import (
	"bytes"
	"encoding/json"
	"fmt"

	"github.com/spf13/cobra"
)

var userCmd = &cobra.Command{
	Use:   "user",
	Short: "User operations via the API",
}

var userCreditsCmd = &cobra.Command{
	Use:   "credits",
	Short: "Get AI credit balance",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simpleGet(cmd, "/api/user/ai/credits", "")
	},
}

var userStatsCmd = &cobra.Command{
	Use:   "stats",
	Short: "Get user statistics",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simpleGet(cmd, "/api/user/stats", "")
	},
}

var userLanguageCmd = &cobra.Command{
	Use:   "language",
	Short: "User language preference",
}

var userLanguageGetCmd = &cobra.Command{
	Use:   "get",
	Short: "Get user language",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simpleGet(cmd, "/api/user/preference/language", "")
	},
}

var (
	userLanguage string
)

var userLanguageSetCmd = &cobra.Command{
	Use:   "set",
	Short: "Set user language",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if userLanguage == "" {
			return fmt.Errorf("missing --language")
		}
		body, err := json.Marshal(map[string]string{"language": userLanguage})
		if err != nil {
			return err
		}
		return simplePost(cmd, "/api/user/preference/language", bytes.NewReader(body), "application/json", "")
	},
}

func init() {
	userCmd.AddCommand(userCreditsCmd)
	userCmd.AddCommand(userStatsCmd)
	userCmd.AddCommand(userLanguageCmd)

	userLanguageCmd.AddCommand(userLanguageGetCmd)
	userLanguageCmd.AddCommand(userLanguageSetCmd)

	userLanguageSetCmd.Flags().StringVar(&userLanguage, "language", "", "Language value")
}
