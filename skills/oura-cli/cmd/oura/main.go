package main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"oura-cli/internal/api"
	"oura-cli/internal/auth"
	"oura-cli/internal/config"

	"github.com/spf13/cobra"
	"golang.org/x/oauth2"
)

var (
	clientID     string
	clientSecret string
	startDate    string
	endDate      string
)

func main() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

var rootCmd = &cobra.Command{
	Use:   "oura",
	Short: "Oura Ring CLI",
	Long:  `A CLI implementation for the Oura Ring V2 API.`,
}

var authCmd = &cobra.Command{
	Use:   "auth",
	Short: "Authenticate with Oura",
	Run: func(cmd *cobra.Command, args []string) {
		// Try to look up env vars if flags not set
		if clientID == "" {
			clientID = os.Getenv("OURA_CLIENT_ID")
		}
		if clientSecret == "" {
			clientSecret = os.Getenv("OURA_CLIENT_SECRET")
		}

		if clientID == "" || clientSecret == "" {
			reader := bufio.NewReader(os.Stdin)
			if clientID == "" {
				fmt.Print("Enter Client ID: ")
				id, _ := reader.ReadString('\n')
				clientID = strings.TrimSpace(id)
			}
			if clientSecret == "" {
				fmt.Print("Enter Client Secret: ")
				secret, _ := reader.ReadString('\n')
				clientSecret = strings.TrimSpace(secret)
			}
		}

		cfg, err := config.LoadConfig()
		if err != nil {
			fmt.Printf("Error loading config: %v\n", err)
			return
		}

		cfg.ClientID = clientID
		cfg.ClientSecret = clientSecret

		if err := auth.Login(cfg); err != nil {
			fmt.Printf("Authentication failed: %v\n", err)
			os.Exit(1)
		}
	},
}

var getCmd = &cobra.Command{
	Use:   "get",
	Short: "Get data from Oura API",
	PersistentPreRunE: func(cmd *cobra.Command, args []string) error {
		return nil
	},
}

func getClient() (*api.Client, error) {
	cfg, err := config.LoadConfig()
	if err != nil {
		return nil, fmt.Errorf("failed to load config: %w", err)
	}

	if cfg.AccessToken == "" {
		return nil, fmt.Errorf("not authenticated. please run 'oura auth'")
	}

	token := &oauth2.Token{
		AccessToken:  cfg.AccessToken,
		RefreshToken: cfg.RefreshToken,
		Expiry:       cfg.Expiry,
		TokenType:    "Bearer",
	}

	// Token source that automatically refreshes
	ts := auth.GetOAuthConfig(cfg.ClientID, cfg.ClientSecret).TokenSource(context.Background(), token)

	// Check if token needs refresh and save if it does
	newToken, err := ts.Token()
	if err != nil {
		return nil, fmt.Errorf("failed to refresh token: %w", err)
	}

	if newToken.AccessToken != cfg.AccessToken {
		cfg.AccessToken = newToken.AccessToken
		cfg.RefreshToken = newToken.RefreshToken
		cfg.Expiry = newToken.Expiry
		config.SaveConfig(cfg)
	}

	return api.NewClient(context.Background(), ts), nil
}

func printJSON(v interface{}) {
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	enc.Encode(v)
}

func init() {
	authCmd.Flags().StringVar(&clientID, "client-id", "", "Oura Client ID")
	authCmd.Flags().StringVar(&clientSecret, "client-secret", "", "Oura Client Secret")
	rootCmd.AddCommand(authCmd)

	getCmd.PersistentFlags().StringVar(&startDate, "start", "", "Start date (YYYY-MM-DD)")
	getCmd.PersistentFlags().StringVar(&endDate, "end", "", "End date (YYYY-MM-DD)")
	rootCmd.AddCommand(getCmd)

	// Subcommands
	getCmd.AddCommand(&cobra.Command{
		Use:   "personal",
		Short: "Get personal info",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetPersonalInfo()
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "sleep",
		Short: "Get daily sleep",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetDailySleep(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "activity",
		Short: "Get daily activity",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetDailyActivity(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "readiness",
		Short: "Get daily readiness",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetDailyReadiness(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "heartrate",
		Short: "Get heart rate",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetHeartRate(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "workout",
		Short: "Get workouts",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetWorkouts(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "spo2",
		Short: "Get SpO2",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetSpO2(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "sleep-details",
		Short: "Get detailed sleep sessions",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetSleep(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "sessions",
		Short: "Get activity sessions",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetSessions(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "sleep-times",
		Short: "Get optimal sleep times",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetSleepTimes(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "stress",
		Short: "Get daily stress",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetDailyStress(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "resilience",
		Short: "Get daily resilience",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetDailyResilience(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "cv-age",
		Short: "Get cardiovascular age",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetCVAge(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "vo2-max",
		Short: "Get VO2 Max",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetVO2Max(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "ring-config",
		Short: "Get ring configuration",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetRingConfiguration(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "rest-mode",
		Short: "Get rest mode periods",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetRestModePeriod(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})

	getCmd.AddCommand(&cobra.Command{
		Use:   "tags",
		Short: "Get enhanced tags",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, err := getClient()
			if err != nil {
				return err
			}
			data, err := client.GetEnhancedTags(startDate, endDate)
			if err != nil {
				return err
			}
			printJSON(data)
			return nil
		},
	})
}
