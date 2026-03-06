package cmd

import (
	"fmt"
	"log"
	"os"
	"strconv"
	"text/tabwriter" // Import the standard library tabwriter

	"github.com/irlndts/go-discogs"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

// listCmd represents the list command
var listCmd = &cobra.Command{
	Use:   "list",
	Short: "List releases in a collection folder",
	Long:  `Lists all the releases within a specific folder of your Discogs collection. By default, it lists from the "All" folder.`,
	Run: func(cmd *cobra.Command, args []string) {
		token := viper.GetString("token")
		username := viper.GetString("username")

		if token == "" || username == "" {
			log.Fatalf("Error: 'token' and 'username' not set in config file. Please run 'discogs-cli config set'.")
		}

		folderID, _ := cmd.Flags().GetInt("folder")

		client, err := discogs.New(&discogs.Options{
			UserAgent: "OpenClawDiscogsSkill/1.0",
			Token:     token,
		})
		if err != nil {
			log.Fatalf("Error creating Discogs client: %v", err)
		}

		log.Printf("Fetching collection for user '%s' in folder %d...", username, folderID)
		items, err := client.CollectionItemsByFolder(username, folderID, nil)
		if err != nil {
			log.Fatalf("Error fetching items from folder %d: %v", folderID, err)
		}

		if len(items.Items) == 0 {
			fmt.Printf("No releases found in folder ID %d.\\n", folderID)
			return
		}

		// --- DISPLAY RESULTS using text/tabwriter ---
		// 1. Initialize a new tabwriter.
		w := new(tabwriter.Writer)
		
		// 2. Set the output destination and formatting parameters.
		//    The minwidth, tabwidth, padding, and padchar control alignment.
		w.Init(os.Stdout, 0, 8, 2, ' ', 0)

		// 3. Print the table headers, separated by tabs.
		fmt.Fprintln(w, "ARTIST\tTITLE\tID")
		fmt.Fprintln(w, "------\t-----\t--")

		// 4. Loop through the data and print each row.
		for _, release := range items.Items {
			artist := "Unknown Artist"
			if len(release.BasicInformation.Artists) > 0 {
				artist = release.BasicInformation.Artists[0].Name
			}
			idStr := strconv.Itoa(release.ID)
			// Each value is separated by a tab `\\t`.
			fmt.Fprintf(w, "%s\t%s\t%s\\n", artist, release.BasicInformation.Title, idStr)
		}
		
		// 5. Flush the writer to ensure all buffered output is written.
		w.Flush()
	},
}

func init() {
	collectionCmd.AddCommand(listCmd)
	listCmd.Flags().IntP("folder", "f", 0, "ID of the folder to list releases from (default: 0 for 'All')")
}
