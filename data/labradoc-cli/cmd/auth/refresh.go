package auth

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/zamedic/labradoc-cli/internal/cli"

	"github.com/spf13/cobra"
)

var refreshJSON bool

var refreshCmd = &cobra.Command{
	Use:   "refresh",
	Short: "Refresh the stored access token",
	RunE: func(cmd *cobra.Command, _ []string) error {
		authURL, realm, clientID, _, err := resolveAuthConfig()
		if err != nil {
			return err
		}
		tok, err := cli.LoadToken()
		if err != nil {
			return err
		}
		if tok.RefreshToken == "" {
			return fmt.Errorf("no refresh_token available")
		}

		ctx, cancel := context.WithTimeout(cmd.Context(), 30*time.Second)
		defer cancel()

		newTok, err := cli.RefreshToken(ctx, authURL, realm, clientID, tok.RefreshToken)
		if err != nil {
			return err
		}
		if newTok.RefreshToken == "" {
			newTok.RefreshToken = tok.RefreshToken
		}
		newTok.APIURL = tok.APIURL
		if err := cli.SaveToken(*newTok); err != nil {
			return err
		}

		if refreshJSON {
			out := map[string]any{
				"status":     "ok",
				"expires_at": newTok.Expiry,
				"scope":      newTok.Scope,
			}
			b, _ := json.Marshal(out)
			fmt.Fprintln(os.Stdout, string(b))
			return nil
		}

		fmt.Fprintln(os.Stdout, "Token refreshed.")
		return nil
	},
}

func init() {
	refreshCmd.Flags().BoolVar(&refreshJSON, "json", false, "Output machine-readable JSON")
}
