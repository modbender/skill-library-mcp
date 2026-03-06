package cmd

import (
	"github.com/alexrudloff/caesar-cli/internal/output"
	"github.com/spf13/cobra"
)

func init() {
	rootCmd.AddCommand(collectionsCmd)
	collectionsCmd.AddCommand(collectionsCreateCmd)

	collectionsCreateCmd.Flags().String("description", "", "Collection description")
}

var collectionsCmd = &cobra.Command{
	Use:   "collections",
	Short: "Manage file collections",
}

var collectionsCreateCmd = &cobra.Command{
	Use:   "create [name]",
	Short: "Create a new collection",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		c, err := newClient()
		if err != nil {
			output.Error("%v", err)
		}

		desc, _ := cmd.Flags().GetString("description")
		coll, err := c.CreateCollection(args[0], desc)
		if err != nil {
			output.Error("%v", err)
		}

		output.JSON(coll)
	},
}
