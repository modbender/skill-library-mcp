package api

import (
	"bytes"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/zamedic/labradoc-cli/internal/cli"

	"github.com/spf13/cobra"
)

var (
	requestMethod      string
	requestBody        string
	requestBodyFile    string
	requestContentType string
	requestAccept      string
	requestOut         string
	requestNoAuth      bool
)

var requestCmd = &cobra.Command{
	Use:   "request [path]",
	Short: "Make a raw API request",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		opts, err := resolveAPIConfig()
		if err != nil {
			return err
		}
		path := args[0]

		var body io.Reader
		if requestBodyFile != "" {
			if requestBodyFile == "-" {
				body = os.Stdin
			} else {
				b, err := os.ReadFile(requestBodyFile)
				if err != nil {
					return err
				}
				body = bytes.NewReader(b)
			}
		} else if requestBody != "" {
			body = strings.NewReader(requestBody)
		}

		headers := map[string]string{}
		if requestContentType != "" {
			headers["Content-Type"] = requestContentType
		} else if body != nil && requestMethod != "" && strings.ToUpper(requestMethod) != "GET" {
			headers["Content-Type"] = "application/json"
		}
		if requestAccept != "" {
			headers["Accept"] = requestAccept
		}

		if requestNoAuth {
			opts.APIKey = ""
			opts.Token = ""
		} else if opts.APIKey == "" && opts.Token == "" {
			return fmt.Errorf("missing api token (use --api-token, --token, api_token, or --use-auth-token)")
		}
		opts.Headers = headers

		resp, err := cli.DoRequest(
			cmd.Context(),
			strings.ToUpper(requestMethod),
			path,
			body,
			opts,
		)
		if err != nil {
			return err
		}
		defer resp.Body.Close()

		var out io.Writer = os.Stdout
		if requestOut != "" {
			f, err := os.Create(requestOut)
			if err != nil {
				return err
			}
			defer f.Close()
			out = f
		}
		if _, err := io.Copy(out, resp.Body); err != nil {
			return err
		}
		if resp.StatusCode >= 400 {
			return fmt.Errorf("request failed: %s", resp.Status)
		}
		return nil
	},
}

func init() {
	requestCmd.Flags().StringVar(&requestMethod, "method", "GET", "HTTP method")
	requestCmd.Flags().StringVar(&requestBody, "body", "", "Request body as a string")
	requestCmd.Flags().StringVar(&requestBodyFile, "body-file", "", "Request body file ('-' for stdin)")
	requestCmd.Flags().StringVar(&requestContentType, "content-type", "", "Content-Type header")
	requestCmd.Flags().StringVar(&requestAccept, "accept", "", "Accept header")
	requestCmd.Flags().StringVar(&requestOut, "out", "", "Write response to file instead of stdout")
	requestCmd.Flags().BoolVar(&requestNoAuth, "no-auth", false, "Disable Authorization header")
}
