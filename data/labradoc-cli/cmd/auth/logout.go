package auth

import (
	"fmt"
	"os"

	"github.com/zamedic/labradoc-cli/internal/cli"

	"github.com/spf13/cobra"
)

var logoutCmd = &cobra.Command{
	Use:   "logout",
	Short: "Delete the stored token",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if err := cli.ClearToken(); err != nil {
			return err
		}
		fmt.Fprintln(os.Stdout, "Token removed.")
		return nil
	},
}
