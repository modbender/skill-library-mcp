package auth

import (
	"fmt"
	"io"
	"os"
	"time"

	"github.com/zamedic/labradoc-cli/internal/cli"

	"github.com/spf13/cobra"
)

var statusCmd = &cobra.Command{
	Use:   "status",
	Short: "Validate the stored token against the API",
	RunE: func(cmd *cobra.Command, _ []string) error {
		apiURL, err := resolveAPIURL()
		if err != nil {
			return err
		}
		tok, err := cli.LoadToken()
		if err != nil {
			return err
		}

		resp, err := cli.DoRequest(
			cmd.Context(),
			"GET",
			"/api/validate",
			nil,
			cli.RequestOptions{
				BaseURL: apiURL,
				Token:   tok.AccessToken,
				Timeout: 30 * time.Second,
			},
		)
		if err != nil {
			return err
		}
		defer resp.Body.Close()

		body, _ := io.ReadAll(resp.Body)
		if resp.StatusCode >= 400 {
			fmt.Fprintln(os.Stdout, string(body))
			return fmt.Errorf("token invalid: %s", resp.Status)
		}
		fmt.Fprintln(os.Stdout, "ok")
		return nil
	},
}
