package auth

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/zamedic/labradoc-cli/internal/cli"

	"github.com/spf13/cobra"
)

var tokenJSON bool

var tokenCmd = &cobra.Command{
	Use:   "token",
	Short: "Print the stored access token",
	RunE: func(cmd *cobra.Command, _ []string) error {
		tok, err := cli.LoadToken()
		if err != nil {
			return err
		}
		if tokenJSON {
			out := map[string]any{
				"access_token": tok.AccessToken,
				"token_type":   tok.TokenType,
				"expires_at":   tok.Expiry,
				"scope":        tok.Scope,
			}
			b, _ := json.Marshal(out)
			fmt.Fprintln(os.Stdout, string(b))
			return nil
		}
		fmt.Fprintln(os.Stdout, tok.AccessToken)
		return nil
	},
}

func init() {
	tokenCmd.Flags().BoolVar(&tokenJSON, "json", false, "Output machine-readable JSON")
}
