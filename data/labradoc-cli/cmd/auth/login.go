package auth

import (
	"context"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os"
	"time"

	"github.com/zamedic/labradoc-cli/internal/cli"

	"github.com/google/uuid"
	"github.com/spf13/cobra"
)

var (
	loginTimeout time.Duration
	loginJSON    bool
)

var loginCmd = &cobra.Command{
	Use:   "login",
	Short: "Login via OAuth PKCE using a local callback",
	RunE: func(cmd *cobra.Command, _ []string) error {
		authURL, realm, clientID, scope, err := resolveAuthConfig()
		if err != nil {
			return err
		}

		codeVerifier, codeChallenge, err := cli.GeneratePKCE()
		if err != nil {
			return err
		}

		state := uuid.NewString()
		listener, err := net.Listen("tcp", "127.0.0.1:0")
		if err != nil {
			return err
		}
		defer listener.Close()

		port := listener.Addr().(*net.TCPAddr).Port
		redirectURI := fmt.Sprintf("http://127.0.0.1:%d/callback", port)

		authURLString, err := cli.AuthURL(authURL, realm, clientID, redirectURI, scope, state, codeChallenge)
		if err != nil {
			return err
		}

		if loginJSON {
			fmt.Fprintf(os.Stderr, "Open this URL to authenticate:\n%s\n", authURLString)
		} else {
			fmt.Fprintf(os.Stdout, "Open this URL to authenticate:\n%s\n", authURLString)
		}

		codeCh := make(chan string, 1)
		errCh := make(chan error, 1)

		server := &http.Server{
			Handler: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				if r.URL.Path != "/callback" {
					w.WriteHeader(http.StatusNotFound)
					return
				}
				q := r.URL.Query()
				code := q.Get("code")
				if code == "" {
					w.WriteHeader(http.StatusBadRequest)
					_, _ = w.Write([]byte("Missing code"))
					return
				}
				if s := q.Get("state"); s != "" && s != state {
					w.WriteHeader(http.StatusBadRequest)
					_, _ = w.Write([]byte("State mismatch"))
					return
				}
				_, _ = w.Write([]byte("Authentication complete. You can close this window."))
				codeCh <- code
			}),
		}

		go func() {
			if err := server.Serve(listener); err != nil && err != http.ErrServerClosed {
				errCh <- err
			}
		}()

		ctx, cancel := context.WithTimeout(cmd.Context(), loginTimeout)
		defer cancel()

		var code string
		select {
		case <-ctx.Done():
			_ = server.Shutdown(context.Background())
			return fmt.Errorf("timed out waiting for authentication")
		case err := <-errCh:
			_ = server.Shutdown(context.Background())
			return err
		case code = <-codeCh:
		}

		_ = server.Shutdown(context.Background())

		token, err := cli.ExchangeCode(ctx, authURL, realm, clientID, code, redirectURI, codeVerifier)
		if err != nil {
			return err
		}
		if apiURL, err := resolveAPIURL(); err == nil {
			token.APIURL = apiURL
		}
		if err := cli.SaveToken(*token); err != nil {
			return err
		}

		if loginJSON {
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
	loginCmd.Flags().DurationVar(&loginTimeout, "timeout", 2*time.Minute, "Wait timeout for callback")
	loginCmd.Flags().BoolVar(&loginJSON, "json", false, "Output machine-readable JSON")
}
