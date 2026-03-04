package cmd

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

// configCmd represents the config command
var configCmd = &cobra.Command{
	Use:   "config",
	Short: "Manage API configuration",
	Long:  `Manage API configuration settings, such as API keys and secrets.`,
}

var setCmd = &cobra.Command{
	Use:   "set",
	Short: "Set a configuration value",
	Long:  `Set a configuration value, such as the API key or secret.`,
	Run: func(cmd *cobra.Command, args []string) {
		home, err := os.UserHomeDir()
		cobra.CheckErr(err)
		configPath := filepath.Join(home, ".config", "hotel-pricer")
		configFilePath := filepath.Join(configPath, "config.yaml")

		// Ensure the config directory exists
		if _, err := os.Stat(configPath); os.IsNotExist(err) {
			os.MkdirAll(configPath, 0755)
		}

		// Read existing config or create new
		viper.SetConfigFile(configFilePath)

		apiKey, _ := cmd.Flags().GetString("api-key")
		apiSecret, _ := cmd.Flags().GetString("api-secret")

		if apiKey != "" {
			viper.Set("amadeus.api_key", apiKey)
			fmt.Println("API Key has been set.")
		}

		if apiSecret != "" {
			viper.Set("amadeus.api_secret", apiSecret)
			fmt.Println("API Secret has been set.")
		}

		if err := viper.WriteConfigAs(configFilePath); err != nil {
			cobra.CheckErr(err)
		}
	},
}

func init() {
	rootCmd.AddCommand(configCmd)
	configCmd.AddCommand(setCmd)

	setCmd.Flags().String("api-key", "", "Amadeus API Key")
	setCmd.Flags().String("api-secret", "", "Amadeus API Secret")
}
