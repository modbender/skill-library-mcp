package api

import (
	"fmt"
	"strings"
	"time"

	"github.com/zamedic/labradoc-cli/internal/cli"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var (
	apiURLFlag   string
	tokenFlag    string
	apiTokenFlag string
	useAuthToken bool
	timeout      time.Duration
)

var RootCmd = &cobra.Command{
	Use:   "api",
	Short: "Call Labradoc API endpoints",
}

func init() {
	RootCmd.PersistentFlags().StringVar(&apiURLFlag, "api-url", "https://labradoc.eu", "API base URL (default from api_url)")
	RootCmd.PersistentFlags().StringVar(&apiTokenFlag, "api-token", "", "API token (X-API-Key header; default from api_token)")
	RootCmd.PersistentFlags().StringVar(&tokenFlag, "token", "", "Bearer token (overridden by --api-token)")
	RootCmd.PersistentFlags().BoolVar(&useAuthToken, "use-auth-token", false, "Use the stored OAuth token from labradoc auth login")
	RootCmd.PersistentFlags().DurationVar(&timeout, "timeout", 30*time.Second, "HTTP timeout")

	RootCmd.AddCommand(requestCmd)
	RootCmd.AddCommand(filesCmd)
	RootCmd.AddCommand(tasksCmd)
	RootCmd.AddCommand(apikeysCmd)
	RootCmd.AddCommand(userCmd)
	RootCmd.AddCommand(emailCmd)
	RootCmd.AddCommand(googleCmd)
	RootCmd.AddCommand(microsoftCmd)
	RootCmd.AddCommand(stripeCmd)

	viper.BindPFlag("api_url", RootCmd.PersistentFlags().Lookup("api-url"))
	viper.BindPFlag("api_token", RootCmd.PersistentFlags().Lookup("api-token"))
	viper.BindPFlag("timeout", RootCmd.PersistentFlags().Lookup("timeout"))
	viper.BindPFlag("use_auth_token", RootCmd.PersistentFlags().Lookup("use-auth-token"))

}

func resolveAPIConfig() (cli.RequestOptions, error) {
	apiURL := apiURLFlag
	if apiURL == "" {
		apiURL = viper.GetString("api_url")
	}
	if apiURL == "" {
		return cli.RequestOptions{}, fmt.Errorf("missing api url (api_url)")
	}
	apiToken := strings.TrimSpace(apiTokenFlag)
	bearerToken := strings.TrimSpace(tokenFlag)
	if apiToken == "" && bearerToken == "" {
		if useAuthToken {
			t, err := cli.LoadToken()
			if err != nil {
				return cli.RequestOptions{}, err
			}
			bearerToken = t.AccessToken
		} else {
			apiToken = strings.TrimSpace(viper.GetString("api_token"))
		}
	}
	opts := cli.RequestOptions{
		BaseURL: apiURL,
		Timeout: timeout,
	}
	if apiToken != "" {
		opts.APIKey = apiToken
	} else if bearerToken != "" {
		opts.Token = bearerToken
	}
	return opts, nil
}
