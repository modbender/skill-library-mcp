package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
)

// releaseCmd represents the release command
var releaseCmd = &cobra.Command{
	Use:   "release",
	Short: "Get details for a specific release.",
	Long:  `The release command provides subcommands to get information about a specific Discogs release, such as its details or album art.`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Release command requires a subcommand. See --help for details.")
	},
}

func init() {
	rootCmd.AddCommand(releaseCmd)
}
