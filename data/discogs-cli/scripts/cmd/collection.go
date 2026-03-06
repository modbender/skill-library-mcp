package cmd

import (
	"github.com/spf13/cobra"
)

// collectionCmd represents the collection command
var collectionCmd = &cobra.Command{
	Use:   "collection",
	Short: "Work with your Discogs collection",
	Long:  `Provides subcommands to interact with your record collection, such as listing releases or folders.`,
}

func init() {
	rootCmd.AddCommand(collectionCmd)
}
