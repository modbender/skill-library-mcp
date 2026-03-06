package auth

import (
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/zamedic/labradoc-cli/internal/cli"

	"github.com/google/uuid"
	"github.com/spf13/cobra"
)

var (
	urlJSON        bool
	urlRedirectURI string
)

var urlCmd = &cobra.Command{
	Use:   "url",
	Short: "Generate an OAuth PKCE authorization URL",
	RunE: func(cmd *cobra.Command, _ []string) error {
		authURL, realm, clientID, scope, err := resolveAuthConfig()
		if err != nil {
			return err
		}
		redirectURI := urlRedirectURI
		if redirectURI == "" {
			redirectURI = "http://127.0.0.1:18080/callback"
		}

		codeVerifier, codeChallenge, err := cli.GeneratePKCE()
		if err != nil {
			return err
		}
		state := uuid.NewString()

		authURLString, err := cli.AuthURL(authURL, realm, clientID, redirectURI, scope, state, codeChallenge)
		if err != nil {
			return err
		}

		if err := cli.SavePKCEState(cli.PKCEState{
			CodeVerifier:  codeVerifier,
			CodeChallenge: codeChallenge,
			State:         state,
			RedirectURI:   redirectURI,
			Scope:         scope,
			CreatedAt:     time.Now().UTC(),
		}); err != nil {
			return err
		}

		if urlJSON {
			payload := map[string]string{
				"authorization_url": authURLString,
				"state":             state,
				"redirect_uri":      redirectURI,
				"client_id":         clientID,
				"realm":             realm,
				"auth_url":          authURL,
				"scope":             scope,
				"code_verifier":     codeVerifier,
				"code_challenge":    codeChallenge,
			}
			b, _ := json.Marshal(payload)
			fmt.Fprintln(os.Stdout, string(b))
			return nil
		}

		fmt.Fprintf(os.Stdout, "Authorization URL:\n%s\n", authURLString)
		fmt.Fprintf(os.Stdout, "Code verifier (store securely):\n%s\n", codeVerifier)
		return nil
	},
}

func init() {
	urlCmd.Flags().BoolVar(&urlJSON, "json", false, "Output machine-readable JSON")
	urlCmd.Flags().StringVar(&urlRedirectURI, "redirect-uri", "", "Redirect URI to use in the authorization URL")
}
