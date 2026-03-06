package auth

import (
	"fmt"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var (
	authURLFlag  string
	realmFlag    string
	clientIDFlag string
	apiURLFlag   string
	scopeFlag    string
)

var RootCmd = &cobra.Command{
	Use:   "auth",
	Short: "Authenticate with Labradoc using OAuth PKCE",
}

func init() {
	RootCmd.PersistentFlags().StringVar(&authURLFlag, "auth-url", "https://auth.labradoc.eu", "Keycloak base URL (default from keycloak.url)")
	RootCmd.PersistentFlags().StringVar(&realmFlag, "realm", "labradoc", "Keycloak realm (default from keycloak.realm)")
	RootCmd.PersistentFlags().StringVar(&clientIDFlag, "client-id", "labradoc-openclaw", "OAuth client ID")
	RootCmd.PersistentFlags().StringVar(&apiURLFlag, "api-url", "https://labradoc.eu", "API base URL (default from api_url)")
	RootCmd.PersistentFlags().StringVar(&scopeFlag, "scope", "openid profile email offline_access", "OAuth scopes")

	RootCmd.AddCommand(loginCmd)
	RootCmd.AddCommand(urlCmd)
	RootCmd.AddCommand(exchangeCmd)
	RootCmd.AddCommand(tokenCmd)
	RootCmd.AddCommand(refreshCmd)
	RootCmd.AddCommand(statusCmd)
	RootCmd.AddCommand(logoutCmd)
}

func resolveAuthConfig() (string, string, string, string, error) {
	authURL := authURLFlag
	if authURL == "" {
		authURL = viper.GetString("keycloak.url")
	}
	if authURL == "" {
		authURL = "https://auth.labradoc.eu"
	}
	realm := realmFlag
	if realm == "" {
		realm = viper.GetString("keycloak.realm")
	}
	if realm == "" {
		realm = "labradoc"
	}
	clientID := clientIDFlag
	if clientID == "" {
		clientID = "labradoc-openclaw"
	}
	if authURL == "" || realm == "" || clientID == "" {
		return "", "", "", "", fmt.Errorf("missing auth configuration (auth-url, realm, client-id)")
	}
	return authURL, realm, clientID, scopeFlag, nil
}

func resolveAPIURL() (string, error) {
	apiURL := apiURLFlag
	if apiURL == "" {
		apiURL = viper.GetString("api_url")
	}
	if apiURL == "" {
		return "", fmt.Errorf("missing api url (api_url)")
	}
	return apiURL, nil
}
