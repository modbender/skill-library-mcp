package cmd

import (
	"fmt"
	"os"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var cfgFile string
var ApiKey string

var rootCmd = &cobra.Command{
	Use:   "soccer-cli",
	Short: "A CLI to check soccer scores and game details.",
	Long: `soccer-cli is a command-line interface to interact with the API-Football
service, allowing you to retrieve scores, game details, and squad information
directly from your terminal.`,
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func init() {
	cobra.OnInitialize(initConfig)
	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.config/soccer-cli/config.yaml)")
}

func initConfig() {
	if cfgFile != "" {
		viper.SetConfigFile(cfgFile)
	} else {
		home, err := os.UserHomeDir()
		cobra.CheckErr(err)
		configPath := home + "/.config/soccer-cli"
		viper.AddConfigPath(configPath)
		viper.SetConfigName("config")
		viper.SetConfigType("yaml")
	}

	viper.AutomaticEnv()

	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); ok {
			fmt.Println("Config file not found. Please create one at ~/.config/soccer-cli/config.yaml")
			fmt.Println("Example:\napikey: YOUR_API_KEY_HERE")
			os.Exit(1)
		} else {
			fmt.Printf("Error reading config file: %s\n", err)
			os.Exit(1)
		}
	}

	ApiKey = viper.GetString("apikey")
	if ApiKey == "" {
		fmt.Println("API key is missing from the config file.")
		os.Exit(1)
	}
}
