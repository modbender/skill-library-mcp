package cmd

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"

	"github.com/jrojas537/hotel-pricer/amadeus"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

// searchCmd represents the search command for finding hotel offers.
var searchCmd = &cobra.Command{
	Use:   "search",
	Short: "Search for hotel availability and pricing.",
	Long: `Search for hotel availability and pricing based on a city, check-in date, and check-out date.
Additional parameters like the number of guests and search radius can also be specified.`,
	Run: func(cmd *cobra.Command, args []string) {
		// --- 1. Get and Validate Flags ---
		city, _ := cmd.Flags().GetString("city")
		checkIn, _ := cmd.Flags().GetString("check-in")
		checkOut, _ := cmd.Flags().GetString("check-out")
		guests, _ := cmd.Flags().GetInt("guests")
		radius, _ := cmd.Flags().GetInt("radius")

		// Cobra's MarkFlagRequired handles the presence check, but we can keep this for safety.
		if city == "" || checkIn == "" || checkOut == "" {
			fmt.Println("Error: --city, --check-in, and --check-out flags are required.")
			return
		}

		// --- 2. Retrieve API Credentials ---
		apiKey := viper.GetString("amadeus.api_key")
		apiSecret := viper.GetString("amadeus.api_secret")

		if apiKey == "" || apiSecret == "" {
			fmt.Println("Error: API key and secret must be set. Use 'hotel-pricer config set --api-key <key> --api-secret <secret>'")
			return
		}

		// --- 3. Obtain OAuth2 Token ---
		fmt.Println("Authenticating with Amadeus...")
		token, err := amadeus.GetAmadeusToken(apiKey, apiSecret)
		if err != nil {
			fmt.Printf("Error getting access token: %v\n", err)
			return
		}

		// --- 4. Construct the API Request ---
		fmt.Println("Searching for hotel offers...")
		client := &http.Client{}
		searchURL := amadeus.APIBaseURL + "/v3/shopping/hotel-offers"
		req, err := http.NewRequest("GET", searchURL, nil)
		if err != nil {
			fmt.Printf("Error creating API request: %v\n", err)
			return
		}

		// Build and encode query parameters.
		q := req.URL.Query()
		q.Add("cityCode", city)
		q.Add("checkInDate", checkIn)
		q.Add("checkOutDate", checkOut)
		q.Add("adults", fmt.Sprintf("%d", guests))
		q.Add("radius", fmt.Sprintf("%d", radius))
		q.Add("radiusUnit", "KM")
		req.URL.RawQuery = q.Encode()

		// Set the Authorization header with the bearer token.
		req.Header.Add("Authorization", "Bearer "+token)

		// --- 5. Execute the Request ---
		resp, err := client.Do(req)
		if err != nil {
			fmt.Printf("Error executing API request: %v\n", err)
			return
		}
		defer resp.Body.Close()

		// --- 6. Read and Format the Response ---
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			fmt.Printf("Error reading API response body: %v\n", err)
			return
		}
		
		if resp.StatusCode != http.StatusOK {
			fmt.Printf("API request failed with status %d:\n", resp.StatusCode)
		}

		// Pretty print JSON response for readability.
		var prettyJSON map[string]interface{}
		if err := json.Unmarshal(body, &prettyJSON); err != nil {
			// If it's not valid JSON, just print the raw body.
			fmt.Println("Error parsing JSON response, showing raw output:")
			fmt.Println(string(body))
			return
		}

		pretty, err := json.MarshalIndent(prettyJSON, "", "  ")
		if err != nil {
			fmt.Printf("Error formatting JSON output: %v\n", err)
			return
		}

		fmt.Println(string(pretty))
	},
}

// init registers the search command and defines its flags.
func init() {
	rootCmd.AddCommand(searchCmd)

	// Define command-line flags for the search.
	searchCmd.Flags().StringP("city", "c", "", "City code (IATA) to search for hotels (e.g., 'NYC')")
	searchCmd.Flags().StringP("check-in", "i", "", "Check-in date (YYYY-MM-DD)")
	searchCmd.Flags().StringP("check-out", "o", "", "Check-out date (YYYY-MM-DD)")
	searchCmd.Flags().IntP("guests", "g", 1, "Number of guests")
	searchCmd.Flags().IntP("radius", "r", 20, "Search radius in kilometers")

	// Mark the essential flags as required.
	searchCmd.MarkFlagRequired("city")
	searchCmd.MarkFlagRequired("check-in")
	searchCmd.MarkFlagRequired("check-out")
}
