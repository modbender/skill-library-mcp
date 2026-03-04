package cmd

import (
	"fmt"
	"os"

	"github.com/alexrudloff/caesar-cli/internal/client"
	"github.com/spf13/cobra"
)

// newClient is the function used to create API clients. Tests can replace it.
var newClient = func() (*client.Client, error) {
	return client.New()
}

var rootCmd = &cobra.Command{
	Use:   "caesar",
	Short: "CLI for the Caesar research API",
	Long:  "A command-line interface for caesar.org's research API. Set CAESAR_API_KEY to authenticate.",
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
