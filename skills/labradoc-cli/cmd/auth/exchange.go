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

var (
	exchangeCode        string
	exchangeVerifier    string
	exchangeRedirectURI string
	exchangeState       string
	exchangeJSON        bool
)

var exchangeCmd = &cobra.Command{
	Use:   "exchange",
	Short: "Exchange an OAuth code for a token",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if exchangeCode == "" {
			return fmt.Errorf("missing --code")
		}

		authURL, realm, clientID, _, err := resolveAuthConfig()
		if err != nil {
			return err
		}

		state := exchangeState
		codeVerifier := exchangeVerifier
		redirectURI := exchangeRedirectURI

		if codeVerifier == "" || redirectURI == "" || state == "" {
			if pkce, err := cli.LoadPKCEState(); err == nil {
				if state != "" && pkce.State != "" && pkce.State != state {
					return fmt.Errorf("state mismatch between stored PKCE and provided state")
				}
				if codeVerifier == "" {
					codeVerifier = pkce.CodeVerifier
				}
				if redirectURI == "" {
					redirectURI = pkce.RedirectURI
				}
				if state == "" {
					state = pkce.State
				}
			}
		}

		if codeVerifier == "" || redirectURI == "" {
			return fmt.Errorf("missing code verifier or redirect uri")
		}

		ctx, cancel := context.WithTimeout(cmd.Context(), 30*time.Second)
		defer cancel()

		token, err := cli.ExchangeCode(ctx, authURL, realm, clientID, exchangeCode, redirectURI, codeVerifier)
		if err != nil {
			return err
		}
		if apiURL, err := resolveAPIURL(); err == nil {
			token.APIURL = apiURL
		}
		if err := cli.SaveToken(*token); err != nil {
			return err
		}
		_ = cli.ClearPKCEState()

		if exchangeJSON {
			out := map[string]any{
				"status":     "ok",
				"expires_at": token.Expiry,
				"scope":      token.Scope,
			}
			b, _ := json.Marshal(out)
			fmt.Fprintln(os.Stdout, string(b))
			return nil
		}

		fmt.Fprintln(os.Stdout, "Token saved.")
		return nil
	},
}

func init() {
	exchangeCmd.Flags().StringVar(&exchangeCode, "code", "", "Authorization code from the redirect")
	exchangeCmd.Flags().StringVar(&exchangeVerifier, "code-verifier", "", "PKCE code verifier")
	exchangeCmd.Flags().StringVar(&exchangeRedirectURI, "redirect-uri", "", "Redirect URI used in authorization")
	exchangeCmd.Flags().StringVar(&exchangeState, "state", "", "State returned from authorization")
	exchangeCmd.Flags().BoolVar(&exchangeJSON, "json", false, "Output machine-readable JSON")
}
