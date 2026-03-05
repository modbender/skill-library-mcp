package cmd

import (
	"fmt"
	"log"

	"github.com/irlndts/go-discogs"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

// listFoldersCmd represents the list-folders command
var listFoldersCmd = &cobra.Command{
	Use:   "list-folders",
	Short: "List all collection folders",
	Long:  `Retrieves and displays all folders in your Discogs collection, along with their record counts.`,
	Run: func(cmd *cobra.Command, args []string) {
		// Get credentials from viper config
		token := viper.GetString("token")
		username := viper.GetString("username")

		if token == "" || username == "" {
			log.Fatalf("Error: 'token' and 'username' not set. Please run 'discogs-cli config set'.")
		}

		// --- CLIENT SETUP ---
		client, err := discogs.New(&discogs.Options{
			UserAgent: "OpenClawDiscogsSkill/1.0",
			Token:     token,
		})
		if err != nil {
			log.Fatalf("Error creating Discogs client: %v", err)
		}

		// --- FETCH DATA ---
		log.Printf("Fetching collection folders for user: %s...", username)
		folders, err := client.CollectionFolders(username)
		if err != nil {
			log.Fatalf("Error fetching collection folders: %v", err)
		}

		// --- DISPLAY RESULTS ---
		if len(folders.Folders) == 0 {
			fmt.Println("No collection folders found.")
			return
		}

		fmt.Println("\\n--- Collection Folders ---")
		for _, folder := range folders.Folders {
			fmt.Printf("- %s (ID: %d, Count: %d)\\n", folder.Name, folder.ID, folder.Count)
		}
	},
}

func init() {
	collectionCmd.AddCommand(listFoldersCmd)
}
