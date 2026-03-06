
package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/schollz/progressbar/v3"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"github.com/irlndts/go-discogs"
)

const (
	cacheFileName = "discogs_cache.json"
)

type Cache struct {
	Timestamp time.Time         `json:"timestamp"`
	Releases  map[int]*discogs.Release `json:"releases"`
}

// syncCmd represents the sync command
var syncCmd = &cobra.Command{
	Use:   "sync",
	Short: "Sync collection details to a local cache",
	Long: `Fetches detailed information for every release in your Discogs collection and saves it
to a local cache file (~/.cache/discogs-cli/discogs_cache.json).
This will be slow on the first run.`,
	Run: func(cmd *cobra.Command, args []string) {
		client := newDiscogsClient()
		username := viper.GetString("username")

		fmt.Println("Fetching collection item list...")
		collectionItems, err := client.CollectionItemsByFolder(username, 0, nil)
		if err != nil {
			fmt.Printf("Error fetching collection list: %v\n", err)
			os.Exit(1)
		}

		cache := &Cache{
			Releases: make(map[int]*discogs.Release),
		}

		bar := progressbar.NewOptions(len(collectionItems.Items),
			progressbar.OptionSetDescription("Syncing release details..."),
			progressbar.OptionSetRenderBlankState(true),
		)

		for _, item := range collectionItems.Items {
			release, err := client.Release(item.ID)
			if err != nil {
				fmt.Printf("\nWarning: Could not fetch details for release ID %d: %v\n", item.ID, err)
				continue // Skip this item if there's an error
			}
			cache.Releases[item.ID] = release
			bar.Add(1)
		}

		cache.Timestamp = time.Now()
		
		cacheDir, err := os.UserCacheDir()
		if err != nil {
			fmt.Printf("\nError getting user cache directory: %v\n", err)
			os.Exit(1)
		}
		cliCacheDir := filepath.Join(cacheDir, "discogs-cli")
		if err := os.MkdirAll(cliCacheDir, 0755); err != nil {
			fmt.Printf("\nError creating cache directory: %v\n", err)
			os.Exit(1)
		}

		cacheFilePath := filepath.Join(cliCacheDir, cacheFileName)
		file, err := os.Create(cacheFilePath)
		if err != nil {
			fmt.Printf("\nError creating cache file: %v\n", err)
			os.Exit(1)
		}
		defer file.Close()

		encoder := json.NewEncoder(file)
		if err := encoder.Encode(cache); err != nil {
			fmt.Printf("\nError writing to cache file: %v\n", err)
			os.Exit(1)
		}

		fmt.Printf("\nSync complete. Cached %d releases to %s\n", len(cache.Releases), cacheFilePath)
	},
}

func init() {
	collectionCmd.AddCommand(syncCmd)
}
