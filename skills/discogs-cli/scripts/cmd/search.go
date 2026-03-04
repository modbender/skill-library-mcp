package cmd

import (
	"fmt"
	"log"
	"os"
	"strconv"
	"text/tabwriter"

	"github.com/irlndts/go-discogs"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

// searchType will hold the value from the --type flag.
var searchType string

// searchCmd represents the search command.
var searchCmd = &cobra.Command{
	Use:   "search [query]",
	Short: "Search the Discogs database",
	Long:  `Search for releases, artists, or labels on Discogs.`,
	Args:  cobra.ExactArgs(1), // Requires exactly one argument: the search query.
	Run: func(cmd *cobra.Command, args []string) {
		// Ensure the user is configured with an auth token.
		token := viper.GetString("token")
		if token == "" {
			log.Fatalf("Error: 'token' not set in config file. Please run 'discogs-cli config set'.")
		}

		// Initialize the Discogs API client.
		client, err := discogs.New(&discogs.Options{
			UserAgent: "OpenClawDiscogsSkill/1.0",
			Token:     token,
		})
		if err != nil {
			log.Fatalf("Error creating Discogs client: %v", err)
		}

		// Prepare the search request struct.
		searchRequest := discogs.SearchRequest{
			Q:    args[0],    // The search query from the command line.
			Type: searchType, // The type from the --type flag.
		}

		// Execute the search against the Discogs API.
		results, err := client.Search(searchRequest)
		if err != nil {
			log.Fatalf("Error searching: %v", err)
		}

		if len(results.Results) == 0 {
			fmt.Println("No results found.")
			return
		}

		// Format the output into a clean table.
		w := new(tabwriter.Writer)
		w.Init(os.Stdout, 0, 8, 2, ' ', 0)
		fmt.Fprintln(w, "ID\tTITLE\tYEAR\tTYPE")
		fmt.Fprintln(w, "--\t-----\t----\t----")

		for _, result := range results.Results {
			idStr := strconv.Itoa(result.ID)
			fmt.Fprintf(w, "%s\t%s\t%s\t%s\n", idStr, result.Title, result.Year, result.Type)
		}
		w.Flush()
	},
}

// init registers the search command with the root command and sets up its flags.
func init() {
	rootCmd.AddCommand(searchCmd)
	// Defines the --type flag, which can also be used as -t. Defaults to "release".
	searchCmd.Flags().StringVarP(&searchType, "type", "t", "release", "The type of item to search for (release, artist, label)")
}
