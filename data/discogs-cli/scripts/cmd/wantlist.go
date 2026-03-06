package cmd

import (
	"fmt"
	"log"
	"os"
	"strconv"
	"text/tabwriter"

	"github.com/jrojas537/discogs-cli/discogs"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

// wantlistCmd represents the base command for wantlist operations.
var wantlistCmd = &cobra.Command{
	Use:   "wantlist",
	Short: "Manage your Discogs wantlist",
	Long:  `Provides subcommands to list, add, or remove items from your wantlist.`,
}

// wantlistListCmd handles listing all items in the wantlist.
var wantlistListCmd = &cobra.Command{
	Use:   "list",
	Short: "List items in your wantlist",
	Run: func(cmd *cobra.Command, args []string) {
		username := viper.GetString("username")
		client := discogs.NewClient()
		url := fmt.Sprintf("https://api.discogs.com/users/%s/wants", username)

		var wantlist discogs.Wantlist
		err := client.WantlistRequest("GET", url, &wantlist)
		if err != nil {
			log.Fatalf("Error fetching wantlist: %v", err)
		}

		if len(wantlist.Wants) == 0 {
			fmt.Println("Wantlist is empty.")
			return
		}

		// Format and print the output in a table.
		w := tabwriter.NewWriter(os.Stdout, 0, 0, 3, ' ', 0)
		fmt.Fprintln(w, "ID\tARTIST\tTITLE\tYEAR")
		fmt.Fprintln(w, "--\t------\t-----\t----")
		for _, want := range wantlist.Wants {
			artist := "Unknown Artist"
			if len(want.BasicInformation.Artists) > 0 {
				artist = want.BasicInformation.Artists[0].Name
			}
			fmt.Fprintf(w, "%d\t%s\t%s\t%d\n", want.ID, artist, want.BasicInformation.Title, want.BasicInformation.Year)
		}
		w.Flush()
	},
}

// wantlistAddCmd handles adding a release to the wantlist.
var wantlistAddCmd = &cobra.Command{
	Use:   "add [release_id]",
	Short: "Add a release to your wantlist",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		username := viper.GetString("username")
		client := discogs.NewClient()
		releaseID := args[0]
		url := fmt.Sprintf("https://api.discogs.com/users/%s/wants/%s", username, releaseID)

		err := client.WantlistRequest("PUT", url, nil)
		if err != nil {
			log.Fatalf("Error adding to wantlist: %v", err)
		}
		fmt.Printf("Successfully added release %s to wantlist.\n", releaseID)
	},
}

// wantlistRemoveCmd handles removing a release from the wantlist.
var wantlistRemoveCmd = &cobra.Command{
	Use:   "remove [release_id]",
	Short: "Remove a release from your wantlist",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		username := viper.GetString("username")
		client := discogs.NewClient()
		releaseID := args[0]
		url := fmt.Sprintf("https://api.discogs.com/users/%s/wants/%s", username, releaseID)

		err := client.WantlistRequest("DELETE", url, nil)
		if err != nil {
			log.Fatalf("Error removing from wantlist: %v", err)
		}
		fmt.Printf("Successfully removed release %s from wantlist.\n", releaseID)
	},
}

func init() {
	rootCmd.AddCommand(wantlistCmd)
	wantlistCmd.AddCommand(wantlistListCmd)
	wantlistCmd.AddCommand(wantlistAddCmd)
	wantlistCmd.AddCommand(wantlistRemoveCmd)
}
