package cmd

import (
	"github.com/zamedic/labradoc-cli/cmd/api"
	"github.com/zamedic/labradoc-cli/cmd/auth"

	"github.com/spf13/cobra"
)

var RootCmd = cobra.Command{
	Use: "labradoc-cli",
}

func Execute() {
	cobra.CheckErr(RootCmd.Execute())
}

func init() {
	RootCmd.AddCommand(auth.RootCmd)
	RootCmd.AddCommand(api.RootCmd)
}
