package cmd

import (
	"fmt"
	"log"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

// configCmd represents the config command
var configCmd = &cobra.Command{
	Use:   "config",
	Short: "Manage CLI configuration",
	Long:  `Set or view configuration parameters like username and token.`,
}

var setCmd = &cobra.Command{
	Use:   "set",
	Short: "Set a configuration value",
	Long:  `Sets configuration values like the Discogs username and token and saves them to the config file.`,
	Run: func(cmd *cobra.Command, args []string) {
		token, _ := cmd.Flags().GetString("token")
		username, _ := cmd.Flags().GetString("username")

		if token != "" {
			viper.Set("token", token)
			fmt.Println("Set 'token' in config.")
		}
		if username != "" {
			viper.Set("username", username)
			fmt.Println("Set 'username' in config.")
		}

		if err := viper.WriteConfig(); err != nil {
			log.Fatalf("Error writing config file: %s", err)
		}
		fmt.Println("Configuration saved to:", viper.ConfigFileUsed())
	},
}

func init() {
	rootCmd.AddCommand(configCmd)
	configCmd.AddCommand(setCmd)

	setCmd.Flags().StringP("token", "t", "", "Discogs Personal Access Token")
	setCmd.Flags().StringP("username", "u", "", "Discogs Username")
}
