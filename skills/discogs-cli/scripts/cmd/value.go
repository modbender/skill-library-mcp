
package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"text/tabwriter"
	"time"

	"github.com/spf13/cobra"
)

// valueCmd represents the value command
var valueCmd = &cobra.Command{
	Use:   "value",
	Short: "Calculate the total estimated value of the collection from cache",
	Long: `Reads the local cache (created by the 'sync' command) to calculate the total
estimated value of the collection based on the 'Lowest Price' for each item.
If the cache is missing or old, it will prompt you to run the sync command.`,
	Run: func(cmd *cobra.Command, args []string) {
		cacheDir, err := os.UserCacheDir()
		if err != nil {
			fmt.Printf("Error getting user cache directory: %v\n", err)
			os.Exit(1)
		}
		cliCacheDir := filepath.Join(cacheDir, "discogs-cli")
		cacheFilePath := filepath.Join(cliCacheDir, cacheFileName)

		file, err := os.Open(cacheFilePath)
		if err != nil {
			fmt.Println("Error: Cache file not found.")
			fmt.Println("Please run 'discogs-cli collection sync' first to build the cache.")
			os.Exit(1)
		}
		defer file.Close()

		var cache Cache
		decoder := json.NewDecoder(file)
		if err := decoder.Decode(&cache); err != nil {
			fmt.Printf("Error reading cache file: %v\n", err)
			os.Exit(1)
		}

		w := new(tabwriter.Writer)
		w.Init(os.Stdout, 0, 8, 2, ' ', 0)

		fmt.Fprintln(w, "ARTIST\tTITLE\tID\tLOWEST PRICE")
		fmt.Fprintln(w, "------\t-----\t--\t------------")
		
		var totalValue float64
		for _, release := range cache.Releases {
			artist := "Unknown"
			if len(release.Artists) > 0 {
				artist = release.Artists[0].Name
			}
			priceStr := "N/A"
			if release.LowestPrice > 0 {
				priceStr = fmt.Sprintf("$%.2f", release.LowestPrice)
				totalValue += release.LowestPrice
			}
			
			fmt.Fprintf(w, "%s\t%s\t%d\t%s\n", artist, release.Title, release.ID, priceStr)
		}
		
		w.Flush()

		fmt.Println("---------------------------------------------------------")
		fmt.Printf("TOTAL ESTIMATED COLLECTION VALUE: $%.2f\n", totalValue)
		fmt.Printf("(Based on cache from: %s)\n", cache.Timestamp.Format(time.RFC1123))

	},
}

func init() {
	collectionCmd.AddCommand(valueCmd)
}
