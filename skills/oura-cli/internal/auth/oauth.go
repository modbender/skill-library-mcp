package auth

import (
	"context"
	"fmt"
	"net/http"

	"oura-cli/internal/config"

	"golang.org/x/oauth2"
)

const (
	AuthURL  = "https://cloud.ouraring.com/oauth/authorize"
	TokenURL = "https://api.ouraring.com/oauth/token"
)

func GetOAuthConfig(clientID, clientSecret string) *oauth2.Config {
	return &oauth2.Config{
		ClientID:     clientID,
		ClientSecret: clientSecret,
		Endpoint: oauth2.Endpoint{
			AuthURL:  AuthURL,
			TokenURL: TokenURL,
		},
		RedirectURL: "http://localhost:8080/callback",
		Scopes:      []string{"email", "personal", "daily", "heartrate", "workout", "tag", "session", "spo2", "stress", "ring_configuration", "cardiovascular", "heart_health"},
	}
}

func Login(cfg *config.Config) error {
	oauthConfig := GetOAuthConfig(cfg.ClientID, cfg.ClientSecret)
	url := oauthConfig.AuthCodeURL("state", oauth2.AccessTypeOffline)

	fmt.Printf("Please visit this URL to log in: %s\n", url)

	// Create a channel to wait for the token
	tokenChan := make(chan *oauth2.Token)
	errChan := make(chan error)

	server := &http.Server{Addr: ":8080"}

	http.HandleFunc("/callback", func(w http.ResponseWriter, r *http.Request) {
		code := r.URL.Query().Get("code")
		if code == "" {
			errChan <- fmt.Errorf("code not found")
			http.Error(w, "Code not found", http.StatusBadRequest)
			return
		}

		token, err := oauthConfig.Exchange(context.Background(), code)
		if err != nil {
			errChan <- err
			http.Error(w, "Failed to exchange token", http.StatusInternalServerError)
			return
		}

		tokenChan <- token
		fmt.Fprintf(w, "Login successful! You can close this window.")
	})

	go func() {
		if err := server.ListenAndServe(); err != http.ErrServerClosed {
			errChan <- err
		}
	}()

	// Manual input goroutine
	go func() {
		fmt.Println("\nIf the browser callback fails (e.g. Connection Refused locally), copy the 'code' parameter from the URL you were redirected to and paste it here:")
		fmt.Print("Code > ")
		var code string
		fmt.Scanln(&code)
		if code != "" {
			token, err := oauthConfig.Exchange(context.Background(), code)
			if err != nil {
				errChan <- err
				return
			}
			tokenChan <- token
		}
	}()

	select {
	case token := <-tokenChan:
		cfg.AccessToken = token.AccessToken
		cfg.RefreshToken = token.RefreshToken
		cfg.Expiry = token.Expiry
		if err := config.SaveConfig(cfg); err != nil {
			server.Shutdown(context.Background())
			return err
		}
		fmt.Println("Successfully authenticated and saved token.")
	case err := <-errChan:
		server.Shutdown(context.Background())
		return err
	}

	return server.Shutdown(context.Background())
}
